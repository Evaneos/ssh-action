# coding: utf-8

import sys
import uuid

from fabric import ThreadingGroup, Connection
from fabric.exceptions import GroupException


def upload_command_file_to_remotes(connections: ThreadingGroup) -> str:
    """
    Upload the command file to execute remotely on each remote host.

    :param connections: The remote connections
    :return: The remote path of the command file
    """

    remote_commands_file = '/tmp/{base_filename}.sh'.format(
        base_filename=str(uuid.uuid4())
    )

    connection: Connection
    for connection in connections:
        connection.put(
            '/var/local/github-actions/commands',
            remote_commands_file
        )

    connections.run(
        'chmod a+x {file}'.format(file=remote_commands_file)
    )

    return remote_commands_file


def remote_cleanup(connections: ThreadingGroup, commands_file: str) -> None:
    """
    Cleans up remote hosts' filesystem.

    :param connections: The remote connections
    :param commands_file: The command file to delete
    """
    connections.run(
        'rm {file}'.format(file=commands_file)
    )
    connections.run(
        'rm /tmp/evaneos_ssh__fabric_host'.format(file=commands_file)
    )


def run_commands(connections: ThreadingGroup, commands_file) -> None:
    """
    Run commands on each remote host and prefix the output (stdout + stderr)
    with the hostname.

    **Note about the host prefix**

    Cf. http://www.fabfile.org/upgrading.html, the "env.output_prefix" option
    has not been ported to fabric 2.X

    We by-pass this by writing the current hostname to a file and we prefix
    each output of the commands run with the hostname

    :param connections:
    :param commands_file:
    :return:
    """

    connection: Connection
    for connection in connections:
        connection.run(
            'echo "{host}" > /tmp/evaneos_ssh__fabric_host'.format(host=connection.host)
        )

    try:
        connections.run(
            '{commands} 2>&1 | sed "s/^/[$(cat /tmp/evaneos_ssh__fabric_host)] /"'.format(commands=commands_file)
        )
    except GroupException:
        sys.exit(1)
    finally:
        remote_cleanup(connections, commands_file)
