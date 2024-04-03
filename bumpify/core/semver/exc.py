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


class VersionFileNotUpdated(SemVerError):
    """Raised when version file was not, or could not be, updated.

    This may be caused by either wrong configuration of a version file (f.e.
    typo), or by missing valid SemVer string inside a version file.
    """

    __message_template__ = "{self.reason} (version file path: {self.path})"

    #: Path to a version file.
    path: str

    #: Reason text.
    reason: str

    def __init__(self, path: str, reason: str):
        super().__init__()
        self.path = path
        self.reason = reason
