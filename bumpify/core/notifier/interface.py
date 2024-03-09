import abc


class INotifier(abc.ABC):
    """An interface for notifying user about operation progress, status etc.

    This is very similar to logging, but it is meant to be used for testable
    messages.
    """

    @abc.abstractmethod
    def debug(self, *values):
        """Emit a debug notification."""

    @abc.abstractmethod
    def info(self, *values):
        """Emit an info notification."""

    @abc.abstractmethod
    def warning(self, *values):
        """Emit a warning notification."""

    @abc.abstractmethod
    def error(self, *values):
        """Emit an error notification."""

    @abc.abstractmethod
    def critical(self, *values):
        """Emit a critical error notification."""


class INotifierFactory(abc.ABC):
    """Factory interface for creating named notifiers.

    Think of it as a named logger factory.
    """

    @abc.abstractmethod
    def create_notifier(self, name: str) -> INotifier:
        """Create a named notifier.

        :param name:
            Notifier name.
        """
