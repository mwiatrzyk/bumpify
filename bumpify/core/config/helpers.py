from . import exc as config_exc
from .interface import IConfigReader
from .objects import LoadedConfig


def require_config(config_reader: IConfigReader) -> LoadedConfig:
    """Load config file, failing with :exc:`ConfigFileNotFound` if it does not
    exist.

    :param config_reader:
        Config reader to be used.
    """
    maybe_loaded_config = config_reader.load()
    if maybe_loaded_config is None:
        raise config_exc.ConfigFileNotFound(config_reader.abspath())
    return maybe_loaded_config
