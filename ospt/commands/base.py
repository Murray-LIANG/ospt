import docopt

from ospt import control
from ospt import utils


class BaseCommand(object):
    """Base class for the commands"""
    name = 'base-command'

    # Flag whether to log to stdout when log file path is not set.
    log_to_stdout = True

    def __init__(self, cmd_args, global_args):
        """ Initialize the commands.

        :param cmd_args: arguments of the command
        :param global_args: arguments of the program
        """
        self.cmd_args = docopt.docopt(self.__doc__, argv=cmd_args)
        self.args = global_args
        self.args.update(self.cmd_args)
        self.args = {k: v for k, v in self.args.items() if v is not None}
        utils.setup_log(file_path=self.args.get('--log', None),
                        to_stdout=self.log_to_stdout)

        self.controller = control.create_control(self.args)

    def do(self):
        """Execute the commands"""
        raise NotImplementedError()
