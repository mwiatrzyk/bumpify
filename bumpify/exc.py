import textwrap
import typing
import dataclasses

import pydantic


class BumpifyError(Exception):
    """Common base class for all Bumpify specific exceptions."""

    __message_template__: str = None

    #: The root cause of this error.
    original_exc: typing.Optional[Exception]

    def __init__(self, original_exc: Exception = None):
        super().__init__()
        self.original_exc = original_exc

    def __str__(self) -> str:
        if self.__message_template__ is None:
            return super().__str__()
        return self.__message_template__.format(self=self)


class ShellCommandError(BumpifyError):
    """Raised when execution of underlying shell command ends with an error."""

    #: Shell command that failed to execute successfully.
    args: typing.Tuple[str]

    #: Command's return code.
    returncode: int

    #: Raw command's STDOUT.
    stdout: bytes

    #: Raw command's STDERR.
    stderr: bytes

    def __init__(self, args: typing.Tuple[str], returncode: int, stdout: bytes, stderr: bytes):
        super().__init__()
        self.args = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    def _format_property(self, name: str, value: typing.Any) -> str:
        indent = " " * 2
        return f"\n{textwrap.indent(name, indent)}:\n{textwrap.indent(str(value), indent*2)}"

    def __str__(self) -> str:
        out = [
            self._format_property("args", self.args),
            self._format_property("returncode", self.returncode),
        ]
        if self.stdout:
            out.append(self._format_property("stdout", self.stdout_str))
        if self.stderr:
            out.append(self._format_property("stderr", self.stderr_str))
        return "".join(out)

    @property
    def stdout_str(self) -> str:
        """Command's STDOUT decoded to string."""
        return self.stdout.decode()

    @property
    def stderr_str(self) -> str:
        """Command's STDERR decoded to string."""
        return self.stderr.decode()


class ValidationError(BumpifyError):
    """Generic model validation error class.

    This is mostly used for wrapping 3rd party validation errors behind
    Bumpify-specific exception interface, allowing those to be handled in user
    friendly way.
    """

    @dataclasses.dataclass
    class ErrorItem:
        """Object containing information about single error."""

        #: Error location in a model that failed validation.
        loc: tuple

        #: Error message text.
        msg: str

        @property
        def loc_str(self) -> str:
            """Error location formatted as string."""
            return ".".join(str(x) for x in self.loc)

    #: List of validation errors.
    errors: typing.List[ErrorItem]

    def __init__(self, errors: typing.List[ErrorItem], original_exc: Exception=None):
        super().__init__(original_exc)
        self.errors = errors

    def find_msg_by_loc(self, *loc) -> typing.Optional[str]:
        """Return message for error location given via positional args.

        If given location does not exist in error list, then ``None`` is
        returned.
        """
        for item in self.errors:
            if item.loc == loc:
                return item.msg

    def __str__(self):
        rows = []
        for e in self.errors:
            rows.append(textwrap.indent(e.loc_str, " "*2))
            rows.append(textwrap.indent(e.msg, " "*4))
        return "\n" + "\n".join(rows)
