from bumpify import exc


class HookError(exc.BumpifyError):
    """Base class for hook module errors."""


class HookExecFailed(HookError):
    """Raised when it was not possible to execute hook file, most likely due to
    the fact that the hook does not contain a valid Python code."""

    __message_template__ = "in file: {self.abspath}\n{self.traceback}"

    #: Absolute path to failed hook file.
    abspath: str

    #: The traceback (originating at hook file) with detailed reason.
    traceback: str

    def __init__(self, abspath: str, traceback: str, original_exc: Exception):
        super().__init__(original_exc)
        self.abspath = abspath
        self.traceback = traceback
