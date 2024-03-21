import abc
import typing


class IFileSystemReader(abc.ABC):
    """A read-only interface to access project files."""

    @abc.abstractmethod
    def abspath(self, path: str = None) -> str:
        """Return absolute path to the file given by relative *path*.

        This is not meant to be used to directly manipulate underlying files,
        but is handy when it comes to printing paths to the user.

        :param path:
            The path for which an absolute path will be returned.

            If ``None`` (the default), then return absolute path to the
            filesystem root directory.
        """

    @abc.abstractmethod
    def scan(self, exclude: typing.Set[str] = None) -> typing.Iterator[str]:
        """Scan through the filesystem, generating paths to existing files.

        Each generate path can later be used with other methods of this API
        object.

        :param exclude:
            Paths to be excluded.

            This can be either full paths, or path prefixes (f.e.
            ``/foo/bar.txt`` or ``/foo``). The only thing that needs to be
            remembered is that each path is treated as relative to file system
            root.
        """

    @abc.abstractmethod
    def modified_paths(self) -> typing.Set[str]:
        """Return set of paths that were modified since this object was created
        or since the last time :meth:`IFileSystemWriter.clear_modified_paths`
        was called.

        Each call to :meth:`IFileSystemWriter.write` adds a path to this set.
        """

    @abc.abstractmethod
    def exists(self, path: str) -> bool:
        """Check if *path* points to an existing file.

        :param path:
            Path to be checked.
        """

    @abc.abstractmethod
    def read(self, path: str) -> bytes:
        """Read file at given *path* and return its content.

        If *path* does not point to an existing file then :exc:`FileNotFound`
        exception is raised.

        :param path:
            Path to a file.
        """


class IFileSystemWriter(abc.ABC):
    """A write-only interface to access project files."""

    @abc.abstractmethod
    def clear_modified_paths(self):
        """Clears set of modified paths returned by
        :meth:`IFileSystemReader.modified_paths` method."""

    @abc.abstractmethod
    def write(self, path: str, content: bytes):
        """Create or overwrite file at given *path*.

        When this method gets called and file is saved successfully, then
        *path* is added to the set of modified paths.

        :param path:
            Path to a file.

        :param content:
            Data to be written to a file.
        """


class IFileSystemReaderWriter(IFileSystemReader, IFileSystemWriter):
    """A read-write interface to access project files."""
