# coding: utf-8

import sys
from inspect import getframeinfo, stack


def print_github_action_error(message: str) -> None:
    """
    Wraps the message with syntax from Github actions in order
    to display the message as an error in the Github workflow UI.

    See http://bit.ly/2Okz3Gv

    :param message: Message to display on stderr as a Github action error
    """

    caller = getframeinfo(stack()[1][0])

    print(
        "::error file={file},line={line}:: {message}".format(
            file=caller.filename,
            line=caller.lineno,
            message=message
        ),
        file=sys.stderr
    )


def print_github_action_warning(message: str) -> None:
    """
    Wraps the message with syntax from Github actions in order
    to display the message as a warning in the Github workflow UI.

    See http://bit.ly/33WWY5x

    :param message: Message to display on stdout as a Github action warning
    """

    caller = getframeinfo(stack()[1][0])

    print(
        "::warning file={file},line={line}:: {message}".format(
            file=caller.filename,
            line=caller.lineno,
            message=message
        ),
        file=sys.stdout
    )
