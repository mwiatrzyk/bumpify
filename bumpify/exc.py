import textwrap
import typing


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
