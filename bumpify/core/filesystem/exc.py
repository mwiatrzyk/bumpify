from bumpify import exc


class FileSystemError(exc.BumpifyError):
    """Base class for file system errors."""


class PathError(FileSystemError):
    """Base class for path-related errors."""

    __message_template__ = "{self.path}"

    #: The path that caused error.
    path: str

    def __init__(self, path: str):
        super().__init__()
        self.path = path


class RelativePathUsed(PathError):
    """Raised when relative path is used.

    Relative paths are not supported to avoid accessing files outside of
    project's root directory.
    """


class FileNotFound(PathError):
    """Raised when trying to read a file from a non-existing path."""
