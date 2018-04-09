import logging

from ospt import flow
from ospt.commands import base

LOG = logging.getLogger()


class CreateServer(base.BaseCommand):
    """
Dell-EMC OpenStack Performance Test: Create servers.

usage:
    ospt create-servers --tag <tag> --count <count>

options:
    --tag <tag>             A tag string used in the server name
    --count <count>         The number of servers to create

examples:
    # To create servers with name: server-ml-test-00 and server-ml-test-01.
    ospt create-servers --tag ml-test --count 2
    """
    name = 'create-servers'

    def do(self):
        servers_to_create = self.controller.prepare_servers_to_create(
            self.args['--tag'], int(self.args['--count']))
        f = flow.Flow(self.controller.create_server)
        f.map(servers_to_create)


class DeleteServer(base.BaseCommand):
    """
Dell-EMC OpenStack Performance Test: Delete servers.

usage:
    ospt delete-servers --tag <tag> [--count <count>]

options:
    --tag <tag>             A tag string contained in the server name
    --count <count>         The number of servers to delete. If omitted, all
                            servers matched will be deleted

examples:
    # To delete the first two servers with name starting with `server-ml-test`:
    ospt delete-servers --tag ml-test --count 2
    """
    name = 'delete-servers'

    def do(self):
        servers_to_delete = self.controller.get_servers_to_delete(
            self.args['--tag'], int(self.args.get('--count', 0)))
        f = flow.Flow(self.controller.delete_server)
        f.map(servers_to_delete)
