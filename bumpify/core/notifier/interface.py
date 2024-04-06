import abc


class INotifier(abc.ABC):
    """An interface for receiving notifications from commands being executed.

    This is very similar to logging, but is meant to be easily testable and
    pluggable depending on presence of various configuration options.
    """

    @abc.abstractmethod
    def debug(self, *values):
        """Emit a debug notification.

        Use this for more detailed debug information only.
        """

    @abc.abstractmethod
    def info(self, *values):
        """Emit an info notification.

        This is a neutral level of notification and should be used in most
        situations.
        """

    @abc.abstractmethod
    def warning(self, *values):
        """Emit a warning notification.

        Warnings should be used to signal a non-fatal situations.
        """

    @abc.abstractmethod
    def error(self, *values):
        """Emit an error notification.

        This method should only be used to emit a notification signalling that
        the operation was not able to succeed and the process should end with
        failure.
        """
