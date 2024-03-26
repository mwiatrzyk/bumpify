from bumpify import exc


class SemVerError(exc.BumpifyError):
    """Base class for semantic versioning errors."""


class UnsupportedChangelogFormat(SemVerError):
    """Raised when configured changelog file is not supported."""
    __message_template__ = "{self.path}"

    #: Path to a changelog file.
    path: str

    def __init__(self, path: str):
        super().__init__()
        self.path = path
