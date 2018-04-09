import logging

from ospt import flow
from ospt.commands import base

LOG = logging.getLogger()


class CreateVolume(base.BaseCommand):
    """
Dell-EMC OpenStack Performance Test: Create volumes.

usage:
    ospt create-volumes --tag <tag> --count <count>

options:
    --tag <tag>             A tag string used in the volume name
    --count <count>         The number of volumes to create

examples:
    # To create volumes with name: vol-ml-test-00 and vol-ml-test-01.
    ospt create-volumes --tag ml-test --count 2
    """
    name = 'create-volumes'

    def do(self):
        vols_to_create = self.controller.prepare_volumes_to_create(
            self.args['--tag'], int(self.args['--count']))
        f = flow.Flow(self.controller.create_volume)
        f.map(vols_to_create)


class DeleteVolume(base.BaseCommand):
    """
Dell-EMC OpenStack Performance Test: Delete volumes.

usage:
    ospt delete-volumes --tag <tag> [--count <count>]

options:
    --tag <tag>             A tag string contained in the volume name
    --count <count>         The number of volumes to delete. If omitted, all
                            volumes matched will be deleted

examples:
    # To delete the first two volumes with name starting with `vol-ml-test`:
    ospt delete-volumes --tag ml-test --count 2
    """
    name = 'delete-volumes'

    def do(self):
        vols_to_delete = self.controller.get_volumes_to_delete(
            self.args['--tag'], int(self.args.get('--count', 0)))
        f = flow.Flow(self.controller.delete_volume)
        f.map(vols_to_delete)
