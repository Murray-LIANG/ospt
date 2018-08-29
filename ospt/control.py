import itertools
import logging
import math

import storops
from cinderclient import client as c_client
from cinderclient import exceptions as cinder_ex
from glanceclient import client as g_client
from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client as n_client
from novaclient import exceptions as nova_ex

from ospt import exceptions as ospt_ex
from ospt import utils

LOG = logging.getLogger()


def create_control(args):
    nova = cinder = glance = storops_array = None
    username = args.get('--username', None)
    password = args.get('--password', None)

    auth_ip = args.get('--os_auth_ip', None)
    auth_ver = args.get('--os_auth_version', 'v2')
    project = args.get('--os_project', None)

    if all((auth_ip, username, password, project, auth_ver)):
        loader = loading.get_plugin_loader('password')
        if auth_ver == 'v3':
            from keystoneauth1.identity import v3
            auth = v3.Password(
                auth_url='http://{}/identity/v3'.format(auth_ip),
                username=username,
                password=password,
                project_name=project,
                project_domain_name='Default',
                user_domain_name='Default')
        else:
            auth = loader.load_from_options(
                auth_url='http://{}:5000/v2.0'.format(auth_ip),
                username=username,
                password=password,
                project_name=project)
        sess = session.Session(auth=auth)
        nova = n_client.Client(2, session=sess)
        cinder = c_client.Client(2, session=sess)
        glance = g_client.Client('2', session=sess)

    unity = args.get('--storops_unity', None)
    vnx = args.get('--storops_vnx', None)
    if all((unity, vnx)):
        raise ospt_ex.ConnectionError('Cannot specify both Unity and VNX.')
    if all((unity, username, password)):
        storops_array = storops.UnitySystem(unity, username, password)

    if all((vnx, username, password)):
        storops_array = storops.VNXSystem(unity, username, password)

    if all((nova is None, cinder is None, glance is None,
            storops_array is None)):
        raise ospt_ex.ConnectionError('Need to specify connection using '
                                      'OpenStack client or storops.')
    if nova is not None:
        return OpenstackControl(nova, cinder, glance)
    else:
        return StoropsControl(storops_array)


class Resource(object):
    def __init__(self, res_id=None, name=None):
        self._id = res_id
        self._name = name

    def __repr__(self):
        return 'id={},name={}'.format(self._id, self._name)

    @property
    def id(self):
        return '{}'.format(self._id)

    @property
    def name(self):
        return '{}'.format(self._name)


class BaseControl(object):
    @staticmethod
    def tag_volume_name(tag):
        return 'vol-{}'.format(tag)

    @staticmethod
    def tag_server_name(tag):
        return 'host-{}'.format(tag)

    @staticmethod
    def gen_id(tagged_name, number, count):
        return '{t}-{num:0{width}}'.format(t=tagged_name, num=number,
                                           width=len(str(count)))

    def prepare_volumes_to_create(self, tag, count):
        return [Resource(name=self.gen_id(self.tag_volume_name(tag), i, count))
                for i in range(count)]

    def prepare_servers_to_create(self, tag, count):
        return [Resource(name=self.gen_id(self.tag_server_name(tag), i, count))
                for i in range(count)]

    @staticmethod
    def _get_resources_to_delete(resources, count):
        if count and len(resources) < count:
            raise ospt_ex.NotEnoughResourcesToDeleteError(
                '{} exist, but {} to delete.'.format(len(resources), count))
        count = len(resources) if not count else count
        return utils.sort_by_name(resources)[:count]

    def get_volumes_to_delete(self, tag, count=None):
        vols = self.get_volumes(tag)
        return self._get_resources_to_delete(vols, count)

    def get_servers_to_delete(self, tag, count=None):
        servers = self.get_servers(tag)
        return self._get_resources_to_delete(servers, count)

    def pair_servers_volumes(self, tag, count, mapping):
        servers = utils.sort_by_name(self.get_servers(tag))
        volumes = utils.sort_by_name(self.get_volumes(tag))
        mapping_s, mapping_v = int(mapping[0]), int(mapping[1])

        if mapping_s == mapping_v == 1:
            if len(servers) < count or len(volumes) < count:
                raise ospt_ex.CountOfServersVolumesNotMatchError(
                    'servers: {}, volumes: {}, count: {}, mapping: {}'.format(
                        len(servers), len(volumes), count, mapping))
            return zip(servers[:count], volumes[:count])
        else:
            less, more = servers, volumes
            is_more_servers = False
            if mapping_v == 1:
                more, less = less, more
                is_more_servers = True
            if len(more) < count:
                raise ospt_ex.NotEnoughResourcesForMappingError(
                    existing=len(more), required=count)

            n = int(math.ceil(count / len(less)))

            if is_more_servers:
                less_repeat = list(itertools.chain.from_iterable([less] * n))[
                              :count]
                return zip(more[:count], less_repeat)
            else:
                mappings = []
                num_attach_srv = min(len(less), count)
                num_attach_vol = min(len(more),
                                     num_attach_srv * mapping_v / mapping_s)
                for i in range(num_attach_vol):
                    idx = i % num_attach_srv
                    pair = (servers[idx], volumes[i])
                    mappings.append(pair)
                return mappings

    def get_volumes(self, tag):
        raise NotImplementedError()

    def get_servers(self, tag):
        raise NotImplementedError()


class OpenstackControl(BaseControl):
    def __init__(self, nova, cinder, glance):
        self.nova = nova
        self.cinder = cinder
        self.glance = glance
        self.image = [each for each in self.glance.images.list()
                      if each.name.startswith('cirros')][0]
        self.flavor = self.nova.flavors.get(1)

    def get_volumes(self, tag):
        return [each for each in self.cinder.volumes.list()
                if each.name.startswith(self.tag_volume_name(tag))]

    def get_servers(self, tag):
        return [each for each in self.nova.servers.list()
                if each.name.startswith(self.tag_server_name(tag))]

    @utils.timeit
    def create_volume(self, volume):
        vol = self.cinder.volumes.create(name=volume.name, size=3)
        utils.wait_until(self.cinder.volumes, vol.id, 'available')

    @utils.timeit
    def delete_volume(self, volume):
        volume.delete()
        utils.wait_until(self.cinder.volumes, volume.id, cinder_ex.NotFound)

    @utils.timeit
    def create_server(self, server):
        vm = self.nova.servers.create(name=server.name, image=self.image,
                                      flavor=self.flavor)
        utils.wait_until(self.nova.servers, vm.id, 'ACTIVE')

    @utils.timeit
    def delete_server(self, server):
        server.delete()
        utils.wait_until(self.nova.servers, server.id, nova_ex.NotFound)

    @utils.timeit
    def attach(self, server, volume):
        self.nova.volumes.create_server_volume(server.id, volume.id)
        utils.wait_until(self.cinder.volumes, volume.id, 'in-use')

    @utils.timeit
    def detach(self, server, volume):
        self.nova.volumes.delete_server_volume(server.id, volume.id)
        utils.wait_until(self.cinder.volumes, volume.id, 'available')


class StoropsControl(BaseControl):
    def __init__(self, array):
        self.array = array
        self.pool = self.array.get_pool()[0]
        self.is_unity = isinstance(self.array, storops.UnitySystem)

    def get_volumes(self, tag):
        return [each for each in self.array.get_lun()
                if each.name.startswith(self.tag_volume_name(tag))]

    def get_servers(self, tag):
        return [each for each in self.array.get_host()
                if each.name.startswith(self.tag_server_name(tag))]

    @utils.timeit
    def create_volume(self, volume):
        self.pool.create_lun(lun_name=volume.name, size_gb=3)

    @utils.timeit
    def delete_volume(self, volume):
        volume.delete()

    @utils.timeit
    def attach(self, server, volume):
        if self.is_unity:
            server.attach(volume, skip_hlu_0=True)
        else:
            server.attach_alu(volume)

    @utils.timeit
    def detach(self, server, volume):
        if self.is_unity:
            server.detach(volume)
        else:
            server.detach_alu(volume)

    @utils.timeit
    def create_server(self, server):
        if self.is_unity:
            self.array.create_host(name=server.name)
        else:
            self.array.create_sg(name=server.name)

    @staticmethod
    @utils.timeit
    def delete_server(server):
        server.delete()
