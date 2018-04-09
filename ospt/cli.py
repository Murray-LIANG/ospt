"""
Dell EMC Openstack Performance Test.

usage:
    ospt [-hV --os_auth_url <auth_url> --os_username <username>
          --os_password <password> --os_project <project> --storops_vnx <vnx>
          --storops_unity <unity> --storops_username <username>
          --storops_password <password> --pattern <pattern>]
        <command> [<args>...]

options:
    -h --help                       Show the help, could be used for commands
    -V --version                    Show the version
    --os_auth_url <auth_url>        OpenStack auth URL
    --os_username <username>        OpenStack user name
    --os_password <password>        OpenStack api password
    --os_project <project>          OpenStack project name
    --storops_vnx <vnx>             The VNX IP to which storops connects
    --storops_unity <unity>         The Unity IP to which storops connects
    --storops_username <username>   Storops user name
    --storops_password <password>   Storops password
    --pattern <number>              The concurrence pattern, i.e. 2 means to sleep 2 sec before starting next thread.

supported commands:
    create-volumes          Collect the time of creating volumes

examples:
    ospt --help
    ospt create-volumes --help
"""

import docopt

import ospt
from ospt import commands


def main():
    """Main cli entry point for distributing cli commands."""
    args = docopt.docopt(__doc__, version=ospt.__version__, options_first=True,
                         help=True)
    cmd_name = args.pop('<command>')
    cmd_args = args.pop('<args>')

    cmd_class = commands.CMD_DICT.get(cmd_name, None)
    if cmd_class is None:
        raise docopt.DocoptExit(
            message="Not supported command: {}".format(cmd_name))

    cmd_args = [cmd_name] + cmd_args
    cmd = cmd_class(cmd_args, args)
    return cmd.do()
