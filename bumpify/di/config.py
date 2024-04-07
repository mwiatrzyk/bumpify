from pydio.api import Provider

from bumpify import utils
from bumpify.core.config import helpers as config_helpers
from bumpify.core.config.implementation import ConfigReaderWriter
from bumpify.core.config.interface import IConfigReaderWriter
from bumpify.core.config.objects import Config, LoadedConfig
from bumpify.core.filesystem.interface import IFileSystemReaderWriter

provider = Provider()


@provider.provides(IConfigReaderWriter)
def make_config_reader_writer(injector):
    context = utils.inject_context(injector)
    filesystem_reader_writer = utils.inject_type(injector, IFileSystemReaderWriter)
    return ConfigReaderWriter(
        filesystem_reader_writer, context.config_file_path, context.config_file_encoding
    )


@provider.provides(LoadedConfig)
def make_loaded_config(injector):
    config_reader_writer = utils.inject_type(injector, IConfigReaderWriter)
    return config_helpers.require_config(config_reader_writer)


@provider.provides(Config)
def make_config(injector):
    return utils.inject_type(injector, LoadedConfig).config
