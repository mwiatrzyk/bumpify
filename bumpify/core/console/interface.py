import abc

from .objects import Severity


class IConsoleOutput(abc.ABC):
    """Output interface for the console."""

    @abc.abstractmethod
    def emit(self, severity: Severity, *args):
        """Emit a message to the console.

        :param severity:
            The severity of a message emitted.

        :param `*args`:
            Message arguments.

            Final message is calculated in similar manner as for :func:`print`
            built-in function.
        """
