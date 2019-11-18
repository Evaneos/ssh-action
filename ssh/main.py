# coding: utf-8

from fabric import ThreadingGroup

from ssh.github_actions.input import parse_input
from ssh.ssh_utils.command import upload_command_file_to_remotes, run_commands
from ssh.ssh_utils.test_reachable import test_hosts_are_reachable

if __name__ == '__main__':
    action_input = parse_input()

    connection_config = {}
    if action_input.password is not None:
        connection_config = {
            'password': action_input.password
        }

    connections = ThreadingGroup(
        *action_input.hostnames,
        user=action_input.user,
        port=action_input.port,
        connect_timeout=20,
        connect_kwargs=connection_config
    )

    test_hosts_are_reachable(connections)
    remote_command_file = upload_command_file_to_remotes(connections)
    run_commands(connections, remote_command_file)
