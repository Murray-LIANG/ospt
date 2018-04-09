"""
Dell EMC OpenStack Performance Test.

usage:
    ospt [-hV] [--os_auth_ip <auth_ip>] [--os_project <project>]
         [--storops_vnx <vnx>] [--storops_unity <unity>]
         [--username <username>] [--password <password>]
         [--pattern <pattern>] [--log <log_file>]
      <command> [<args>...]

options:
    -h --help                       Show the help, could be used for commands
    -V --version                    Show the version
    --os_auth_ip <auth_ip>          OpenStack auth (Keystone) IP address
    --os_project <project>          OpenStack project name
    --storops_vnx <vnx>             VNX IP to which storops connects
    --storops_unity <unity>         Unity IP to which storops connects
    --username <username>           User name to login OpenStack or Array
    --password <password>           Password to login OpenStack or Array
    --pattern <number>              Concurrence pattern, i.e. 2 means to
                                    sleep 2 sec before starting next thread
    --log <log_file>                Log file path

supported commands:
    create-volumes          Collect the time of creating volumes
    delete-volumes          Collect the time of deleting volumes
    create-servers          Collect the time of creating servers
    delete-servers          Collect the time of deleting servers
    attach                  Collect the time of attaching volumes
    detach                  Collect the time of detaching volumes

examples:
    ospt --help
    ospt create-volumes --help
"""

import docopt
from pbr import version

from ospt import commands


def main():
    """Main cli entry point for distributing cli commands."""
    args = docopt.docopt(__doc__, options_first=True,
                         version=version.VersionInfo('ospt').release_string())
    cmd_name = args.pop('<command>')
    cmd_args = args.pop('<args>')

    cmd_class = commands.CMD_DICT.get(cmd_name, None)
    if cmd_class is None:
        raise docopt.DocoptExit(
            message="Not supported command: {}".format(cmd_name))

    cmd_args = [cmd_name] + cmd_args
    cmd = cmd_class(cmd_args, args)
    return cmd.do()
