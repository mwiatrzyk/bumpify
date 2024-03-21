import abc


class IStatusListener(abc.ABC):
    """An interface for receiving notifications from commands being executed.

    This is very similar to logging, but is meant to be easily testable and
    pluggable depending on presence of various configuration options.
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


class IStatusListenerFactory(abc.ABC):
    """Factory interface for creating named status listeners.

    Think of it as a named logger factory.
    """

    @abc.abstractmethod
    def create_status_listener(self, name: str) -> IStatusListener:
        """Create a named notifier.

        :param name:
            Notifier name.
        """
