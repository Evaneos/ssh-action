from __future__ import annotations

import os
import socket
import sys
from pathlib import Path
from typing import Optional

from ssh.github_actions.log import print_github_action_error, print_github_action_warning


class GithubActionInput(object):
    hostnames: Optional[str]
    commands: Optional[str]
    user: Optional[str]
    port: Optional[int]
    private_key: Optional[str]
    password: Optional[str]
    known_hosts: Optional[str]
    knock_sequence: Optional[str]
    ssh_config: Optional[str]

    @staticmethod
    def from_environment(environment: dict) -> GithubActionInput:
        """
        :param environment: Environment containing the INPUT_ variables
        :return: A fresh instance of Github action input from the environment variables
        """

        instance = GithubActionInput()

        instance.hostnames = environment.get('INPUT_HOSTS', None)

        if instance.hostnames is not None:
            instance.hostnames = instance.hostnames.splitlines()
            instance.hostnames = list(filter(None, instance.hostnames))  # Remove empty lines

        instance.user = environment.get('INPUT_USER', None)
        instance.port = environment.get('INPUT_PORT', 22)
        instance.commands = environment.get('INPUT_COMMANDS', None)
        instance.private_key = environment.get('INPUT_PRIVATE_KEY', None)
        instance.password = environment.get('INPUT_PASSWORD', None)
        instance.knock_sequence = environment.get('INPUT_KNOCK_SEQUENCE', None)
        instance.ssh_config = environment.get('INPUT_SSH_CONFIG', None)
        instance.known_hosts = environment.get('INPUT_KNOWN_HOSTS', None)

        instance.validate()

        return instance

    def validate(self):
        """
        Validate the input contract for this Github action.
        """

        if self.hostnames is None:
            raise ValueError('"hosts" input is required')

        if self.commands is None:
            raise ValueError('"commands" input is required')

        if self.private_key is None and self.password is None:
            raise ValueError('"password" input is required if "private_key" is not provided')

        if self.ssh_config is None and self.user is None:
            raise ValueError('"user" input is required if "ssh_config" is not provided')

        if self.private_key is not None and self.password is not None:
            self.password = None
            # FIXME: use a proper logger for this warning
            print_github_action_warning('"password" input is ignored since "private_key" is provided')

        if self.ssh_config is not None:
            if self.user is not None:
                self.user = None
                # FIXME: use a proper logger for this warning
                print_github_action_warning('"user" input is ignored since "ssh_config" is provided.')
            if self.port is not None:
                self.port = None
                # FIXME: use a proper logger for this warning
                print_github_action_warning('"port" input is ignored since "ssh_config" is provided.')
            if self.knock_sequence is not None:
                self.knock_sequence = None
                # FIXME: use a proper logger for this warning
                print_github_action_warning('"knock_sequence" input is ignored since "ssh_config" is provided.')


def initialize_file_system() -> None:
    """
    Prepare the filesystem for SSH use.
    """

    dirs_to_create = {
        str(Path.home()) + '/.ssh',  # SSH directory
        '/var/local/github-actions'  # Command file
    }

    for directory in dirs_to_create:
        if not os.path.exists(directory):
            os.makedirs(directory, mode=644)

        os.chmod(directory, 0o700)


def write_commands_to_file(actions_input: GithubActionInput) -> None:
    """
    Writes every command to run in a local file
    so it can be uploaded to the remote hosts later.

    :param actions_input: The parsed input
    """

    with open('/var/local/github-actions/commands', 'w') as command_file:
        command_file.write('set -euxo pipefail\n')
        command_file.write(actions_input.commands + '\n')


def handle_ssh_private_key(actions_input: GithubActionInput) -> None:
    """
    Writes the SSH private key to ~/.ssh/id_rsa
    if it has been provided in the input.

    :param actions_input: The parsed input
    """

    if actions_input.private_key is None:
        return

    ssh_private_key_path = str(Path.home()) + '/.ssh/id_rsa'

    with open(ssh_private_key_path, 'w') as ssh_private_key:
        ssh_private_key.write(actions_input.private_key + '\n')

    os.chmod(ssh_private_key_path, 0o600)


def handle_internal_ssh_config(actions_input: GithubActionInput) -> None:
    """
    If no SSH config has been provided, create an SSH config
    with a ProxyCommand that includes the knock

    :param actions_input: The parsed input
    """

    if actions_input.ssh_config is not None:
        return

    strict_host_checking_opt = 'StrictHostKeyChecking yes'
    if actions_input.known_hosts is None:
        strict_host_checking_opt = 'StrictHostKeyChecking no'

    ssh_config = ''
    for hostname in actions_input.hostnames:
        ssh_config += (
            "Host {hostname}\n"
            "    {strict_host_checking_opt}\n"
            "    ProxyCommand /bin/sh -c 'until nc -zv %h %p -w 1 2>&1 ; "
            "do knock %h {knock_sequence} ; done; exec nc %h %p'\n\n"
        ).format(
            knock_sequence=actions_input.knock_sequence,
            hostname=hostname,
            strict_host_checking_opt=strict_host_checking_opt
        )

    ssh_config_path = str(Path.home()) + '/.ssh/config'

    with open(ssh_config_path, 'w') as ssh_private_key:
        ssh_private_key.write(ssh_config)

    os.chmod(ssh_config_path, 0o644)


def handle_custom_ssh_config(actions_input: GithubActionInput) -> None:
    """
    If SSH config has been provided, create it.

    :param actions_input: The parsed input
    """

    if actions_input.ssh_config is None:
        return

    ssh_config_path = str(Path.home()) + '/.ssh/config'

    with open(ssh_config_path, 'w') as ssh_private_key:
        ssh_private_key.write(actions_input.ssh_config + '\n')

    os.chmod(ssh_config_path, 0o644)


def handle_known_hosts(actions_input: GithubActionInput) -> None:
    """
    If known hosts keys have been provided, put them in ~/.ssh/known_hosts.

    :param actions_input: The parsed input
    """

    if actions_input.known_hosts is None:
        return

    ssh_known_host_path = str(Path.home()) + '/.ssh/known_hosts'

    with open(ssh_known_host_path, 'w') as ssh_private_key:
        ssh_private_key.write(actions_input.known_hosts + '\n')

    os.chmod(ssh_known_host_path, 0o600)


def parse_input() -> GithubActionInput:
    """
    Parses the Github Actions input environment variables.

    See http://bit.ly/37akePj.

    :return: The parsed input
    """

    initialize_file_system()

    try:
        actions_input = GithubActionInput.from_environment(os.environ)
    except ValueError as error:
        print_github_action_error(str(error))
        sys.exit(1)  # FIXME: use an dedicated exception to catch in main

    # FIXME: move this outside of this file
    write_commands_to_file(actions_input)
    validate_hostname_resolves(actions_input)
    handle_ssh_private_key(actions_input)
    handle_internal_ssh_config(actions_input)
    handle_custom_ssh_config(actions_input)
    handle_known_hosts(actions_input)

    return actions_input


def validate_hostname_resolves(actions_input: GithubActionInput) -> None:
    """
    Validate each each hostname can be resolved.

    :param actions_input: The parsed input
    """

    error = False

    for hostname in actions_input.hostnames:
        try:
            socket.gethostbyname(hostname)
        except socket.error:
            print_github_action_error('Unable to resolve host "{hostname}"'.format(hostname=hostname))
            error = True

    if error:
        sys.exit(1)  # FIXME: use an dedicated exception to catch in main
