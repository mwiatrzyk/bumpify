import abc
from typing import Any, Callable

from .objects import Severity


class IConsoleOutput(abc.ABC):
    """Output interface for the console."""

    @abc.abstractmethod
    def count_by_severity(self, severity: Severity) -> int:
        """Return total number of messages emitted with given *severity* since
        this object was created.

        For example, if this is called with ``Severity.ERROR``, then returned
        number will be total number of error messages.

        :param severity:
            Severity to be counted.
        """

    @abc.abstractmethod
    def emit(self, severity: Severity, *message):
        """Emit a message to the console.

        :param severity:
            The severity of a message emitted.

        :param `*message`:
            Message components.

            Final message is calculated in similar manner as for :func:`print`
            built-in function.
        """


class IConsoleInput(abc.ABC):
    """Input interface for the console.

    Used to provide interactive user prompts whenever needed.
    """

    @abc.abstractmethod
    def input(self, prompt: list, parse_func: Callable[[str], Any]) -> Any:
        """Get interactive input from the user.

        The user is prompt interactively for as long as *parse_func* raises
        :exc:`ValueError` exception. Once *parse_func* returns a value
        successfully, that value is also used as method's return value.

        :param prompt:
            Message prompt.

            Formatting rules are the same as for :meth:`IConsoleOutput.emit`
            method.

        :param parse_func:
            Function to be used to parse user's input.

            Should return a value or raise :exc:`ValueError` if provided value
            is not valid.
        """
