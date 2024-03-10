import abc
from typing import Optional

from .objects import Config, LoadedConfig


class IConfigReader(abc.ABC):
    """Configuration reader interface."""

    @abc.abstractmethod
    def abspath(self) -> str:
        """Return absolute path to the underlying configuration file.

        Please don't use this to directly manipulate file underneath; it is
        rather meant to be used as a handy helpers to print real path to the
        user whenever needed (f.e. when error happens).
        """

    @abc.abstractmethod
    def exists(self) -> bool:
        """Check if config file exists.

        This only checks if a file is present, it does not check if file is
        valid; for that purpose use :meth:`load`.
        """

    @abc.abstractmethod
    def load(self) -> Optional[LoadedConfig]:
        """Load configuration and return as :class:`LoadedConfig` object.

        When config file is missing, then ``None`` is returned. However, if
        config file exists but it is invalid, then :exc:`InvalidConfigFile`
        exception will be raised.
        """


class IConfigWriter(abc.ABC):
    """Configuration writer interface."""

    @abc.abstractmethod
    def save(self, config: Config):
        """Save configuration to a file.

        This either creates or overwrites existing configuration.

        :param config:
            Config model to be saved.
        """


class IConfigReaderWriter(IConfigReader, IConfigWriter):
    """Configuration reader/writer interface."""
