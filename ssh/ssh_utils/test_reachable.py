# coding: utf-8

import sys

from fabric import ThreadingGroup, Connection
from fabric.exceptions import GroupException

from ssh.github_actions.log import print_github_action_error


def test_hosts_are_reachable(connections_to_test: ThreadingGroup) -> None:
    """
    Run a dummy command on remote host to make sure they are reachable.

    If an issue arise at connection, display the exception for each connection in error.

    :param connections_to_test: The connections we make sure are reachable
    """

    try:
        connections_to_test.run('echo "dry-run"', hide=True)
    except GroupException as error:
        result: Connection
        for error_connection, error in error.result.items():
            if isinstance(error, Exception):
                print_github_action_error(
                    'Error on "{host}": {message}'.format(
                        host=error_connection.host,
                        message=str(error)
                    )
                )
        sys.exit(1)
