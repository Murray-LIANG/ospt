import logging

from ospt import exceptions as ospt_ex
from ospt import flow
from ospt.commands import base

LOG = logging.getLogger()


class AttachVolume(base.BaseCommand):
    """
Dell-EMC OpenStack Performance Test: Attach volumes.

usage:
    ospt attach-volumes --tag <tag> --count <count> [--mapping <mapping>]

options:
    --tag <tag>             A tag string contained in the volume name
    --count <count>         The number of server-volume pairs to attach
    --mapping <mapping>     The mapping of server and volume. If omitted, 1:1 will be used

examples:
    # To attach volumes:
    # vol-ml-test-00 to server-ml-test-00 and vol-ml-test-01 to server-ml-test-01
    ospt attach-volumes --tag ml-test --count 2
    """
    name = 'attach-volumes'

    def do(self):
        mapping_str = self.args.get('--mapping', '1:1')
        mapping = mapping_str.split(':')
        if len(mapping) != 2 or all((mapping[0] != 1, mapping[1] != 1)):
            raise ospt_ex.MappingNotSupportedError(mapping_str)
        pairs_server_vol = self.controller.pair_servers_volumes(
            self.args['--tag'], self.args['--count'], mapping)
        f = flow.Flow(self.controller.attach_volume)
        f.map(pairs_server_vol)


class DetachVolume(base.BaseCommand):
    """
Dell-EMC OpenStack Performance Test: Detach volumes.

usage:
    ospt detach-volumes --tag <tag> --count <count> [--mapping <mapping>]

options:
    --tag <tag>             A tag string contained in the volume name
    --count <count>         The number of server-volume to detach
    --mapping <mapping>     The mapping of server and volume. If omitted, 1:1 will be used

examples:
    # To detach the first two volumes from hosts:
    ospt detach-volumes --tag ml-test --count 2
    """
    name = 'detach-volumes'

    def do(self):
        mapping_str = self.args.get('--mapping', '1:1')
        mapping = mapping_str.split(':')
        if len(mapping) != 2 or all((mapping[0] != 1, mapping[1] != 1)):
            raise ospt_ex.MappingNotSupportedError(mapping_str)
        pairs_server_vol = self.controller.pair_servers_volumes(
            self.args['--tag'], self.args['--count'], mapping)
        f = flow.Flow(self.controller.detach_volume)
        f.map(pairs_server_vol)
