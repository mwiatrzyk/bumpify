import os
import textwrap
from typing import Iterator, Set

from bumpify import utils
from bumpify.core.console.interface import IConsoleOutput
from bumpify.core.console.objects import Severity, Styled

from . import exc
from .interface import IFileSystemReaderWriter, IFileSystemWriter


def _normalize_path(path: str) -> str:
    if path.startswith(os.path.sep):
        return path[1:]
    return path


class FileSystemReaderWriter(IFileSystemReaderWriter):
    """Default filesystem reader/writer.

    :param root_dir:
        File system root directory.

        This will be set to root directory of the managed project, making this
        class a gateway to project files.
    """

    def __init__(self, root_dir: str):
        self._root_dir = root_dir
        self._modified_paths = set()

    def _abspath(self, path: str) -> str:
        path = _normalize_path(path)
        self._validate_path(path)
        return os.path.join(self._root_dir, path)

    def _validate_path(self, path: str):
        if "./" in path:
            raise exc.RelativePathUsed(path)

    def abspath(self, path: str = None) -> str:
        if path is None:
            return self._root_dir
        return self._abspath(path)

    def scan(self, exclude: Set[str] = None) -> Iterator[str]:

        def gen(abspath: str, path: str):
            for name in os.listdir(abspath):
                name_abspath = os.path.join(abspath, name)
                name_path = os.path.join(path, name)
                if name_path not in exclude:
                    if os.path.isdir(name_abspath):
                        yield from gen(name_abspath, name_path)
                    else:
                        yield name_path

        exclude = set(_normalize_path(x) for x in (exclude or []))
        yield from gen(self._root_dir, "")

    def modified_paths(self) -> Set[str]:
        return set(self._modified_paths)

    def clear_modified_paths(self):
        self._modified_paths.clear()

    def exists(self, path: str) -> bool:
        return os.path.isfile(self._abspath(path))

    def read(self, path: str) -> bytes:
        if not self.exists(path):
            raise exc.FileNotFound(path)
        abspath = self._abspath(path)
        with open(abspath, "rb") as fd:
            return fd.read()

    def write(self, path: str, content: bytes):
        abspath = self._abspath(path)
        os.makedirs(os.path.dirname(abspath), exist_ok=True)
        with open(abspath, "wb") as fd:
            fd.write(content)
        self._modified_paths.add(_normalize_path(path))


class DryRunFileSystemReaderWriterProxy(IFileSystemWriter):
    """A proxy with dry-run mode enabled.

    It will only forward read-type methods to target, printing what would be
    done for write-type methods. As a result, nothing will be changed to the
    underlying filesystem.

    :param target:
        The target filesystem.

    :param notifier:
        Notifier to be informed when write-kind operation is tried to be
        performed.
    """

    def __init__(self, target: IFileSystemReaderWriter, cout: IConsoleOutput):
        self._target = target
        self._cout = cout
        self._modified_paths = set()

    def __getattr__(self, name):
        func = getattr(self._target, name)
        return func

    def modified_paths(self) -> Set[str]:
        return set(self._modified_paths)

    def clear_modified_paths(self):
        self._modified_paths.clear()

    def write(self, path: str, content: bytes):
        action = Styled("overwrite" if self._target.exists(path) else "create", bold=True)
        path = _normalize_path(path)
        self._modified_paths.add(path)
        path = Styled(path, bold=True)
        content = utils.try_decode(content)
        if isinstance(content, str):
            self._write_str(path, action, content)
        else:
            self._write_bytes(path, action, content)

    def _write_str(self, path: str, action: str, content: str):
        content = textwrap.indent(content, "  ")
        content = Styled(content, fg="blue")
        self._cout.emit(
            Severity.INFO,
            "Would",
            action,
            "file at",
            path,
            "and set it with following content:\n",
            content,
        )

    def _write_bytes(self, path: str, action: str, content: bytes):
        content_size_str = Styled(f"{len(content)} bytes", bold=True)
        self._cout.emit(
            Severity.INFO,
            "Would",
            action,
            "file at",
            path,
            "and set it with content having",
            content_size_str,
            "in total",
        )
