import contextlib
import os
import subprocess
import sys
import typing
import logging

from . import exc

logger = logging.getLogger(__name__)

T = typing.TypeVar("T")


def shell_exec(*args, input: bytes = None, fail_on_stderr: bool = False) -> bytes:
    """Execute shell command and return command's STDOUT as return value.

    If command execution fails, then :exc:`ShellCommandError` exception is
    raised with STDERR and return code of a failing command.

    :param `*args`:
        The command to be executed.

    :param fail_on_stderr:
        Flag telling to raise :exc:`ShellCommandError` when non empty STDERR is
        found, no matter what return code was.
    """
    args = tuple(x for x in args if x is not None)
    logger.debug("Running shell command: %r", args)
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    stdout, stderr = (x.strip() for x in p.communicate(input=input))
    if p.returncode != 0 or (fail_on_stderr and stderr):
        raise exc.ShellCommandError(args, p.returncode, stdout, stderr)
    return stdout


@contextlib.contextmanager
def cwd(path: str):
    """Temporarily change current working directory to *path*."""
    cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(cwd)


def try_decode(data: bytes, encodings: typing.Sequence[str] = None) -> typing.Union[str, bytes]:
    """Try to decode given *data* into string.

    If decoding is successful, then return decoded string.

    Otherwise return *data* in unchanged form.

    :param data:
        Bytes to decode.

    :param encodings:
        Encodings to try.

        Encodings are applied from left to right until either successful one is
        found or no more are available.

        Defaults to ``utf-8`` if omitted.
    """
    for encoding in encodings or ["utf-8"]:
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            pass
    else:
        return data


def debug(*values):
    """Same as :func:`print`, but prints to STDERR."""
    print(*values, file=sys.stderr, flush=True)
