import contextlib
import datetime
import enum
import logging
import os
import subprocess
import sys
from typing import Any, Sequence, Type, TypeVar, Union

from pydio.base import IInjector
from pydio.keys import Variant

from bumpify.context import Context

from . import exc

logger = logging.getLogger(__name__)

T = TypeVar("T")


def shell_exec(*args, input: bytes = None, fail_on_stderr: bool = False, env: dict = None) -> bytes:
    """Execute shell command and return command's STDOUT as return value.

    If command execution fails, then :exc:`ShellCommandError` exception is
    raised with STDERR and return code of a failing command.

    :param `*args`:
        The command to be executed.

    :param fail_on_stderr:
        Flag telling to raise :exc:`ShellCommandError` when non empty STDERR is
        found, no matter what return code was.

    :param env:
        Additional environment variables to pass to the command being executed.
    """
    if env is not None:
        tmp = dict(os.environ)
        tmp.update(env)
        env = tmp
    args = tuple(x for x in args if x is not None)
    logger.debug("Running shell command: %r", args)
    p = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, env=env
    )
    stdout, stderr = (x.strip() for x in p.communicate(input=input))
    if p.returncode != 0 or (fail_on_stderr and stderr):
        logger.error("Shell command %r failed with returncode %d", args, p.returncode)
        logger.error(stderr.decode())
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


def try_decode(data: bytes, encodings: Sequence[str] = None) -> Union[str, bytes]:
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


def json_any(v: Any, exclude_none: bool = False) -> Any:
    """Convert value *v* of any type to a closest JSON-compatible type.

    :param v:
        The value to be converted.

    :param exclude_none:
        Specify if ``None`` values should be excluded.

        Applicable only if *v* is a dict object.
    """
    if isinstance(v, dict):
        return json_dict(v, exclude_none=exclude_none)
    if isinstance(v, list):
        return json_list(v, exclude_none=exclude_none)
    if isinstance(v, enum.Enum):
        return v.value
    return v


def json_list(l: list, exclude_none: bool = False) -> list:
    """Convert all *l* list items into JSON-compatible types and return new
    list object.

    :param l:
        The list to be converted.

    :param exclude_none:
        Specify if ``None`` values should be excluded.

        Applicable only for dict items.
    """
    return [json_any(x, exclude_none=exclude_none) for x in l]


def json_dict(d: dict, exclude_none: bool = False) -> dict:
    """Convert all values of dict *d* to JSON-compatible types and return new
    dict object.

    :param d:
        The dict to be converted.

    :param exclude_none:
        Specify if ``None`` values should be excluded from resulting dict.
    """
    out = {}
    for k, v in d.items():
        v = json_any(v, exclude_none=exclude_none)
        if exclude_none and v is None:
            continue
        out[k] = v
    return out


def inject_type(injector: IInjector, type: Type[T]) -> T:
    """Inject object of given *type* using provided *injector*.

    This helper is basically used only to add type annotation to returned
    value.

    :param injector:
        Injector object.

    :param type:
        Type object.

        This acts as both the key for injector, and a type of returned value.
    """
    return injector.inject(type)


def inject_variant(injector: IInjector, type: Type[T], **kwargs) -> T:
    """Inject variation of given type according to *kwargs* given.

    :param injector:
        Injector object.


    :param type:
        Type object.

    :param `**kwargs`:
        Keyword arguments to choose implementation variant for a *type*.
    """
    return inject_type(injector, Variant(type, **kwargs))


def inject_context(injector: IInjector) -> Context:
    """Injects context object.

    :param injector:
        The injector to use.
    """
    return inject_type(injector, Context)


def utcnow() -> datetime.datetime:
    """Create current UTC non-naive datetime object."""
    # TODO: Fix deprecation warning
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)


def format_str(template: str, **params) -> str:
    """Format string template.

    This is used to convert built-in :exc:`KeyError` if formatting fails into a
    more meaningful Bumpify specific error.

    :param template:
        Template string.

    :param `**params`:
        Template parameters.
    """
    # TODO: Wrap KeyError with custom exception
    return template.format(**params)
