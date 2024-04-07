from pydio.api import Provider

from bumpify import utils
from bumpify.core.config.objects import LoadedConfig, LoadedModuleConfig
from bumpify.core.filesystem.interface import IFileSystemReaderWriter
from bumpify.core.semver.implementation import SemVerApi
from bumpify.core.semver.interface import ISemVerApi
from bumpify.core.semver.objects import SemVerConfig
from bumpify.core.vcs.interface import IVcsReaderWriter

provider = Provider()


@provider.provides(ISemVerApi)
def make_semver_api(injector):
    semver_config = utils.inject_type(injector, SemVerConfig)
    filesystem_reader_writer = utils.inject_type(injector, IFileSystemReaderWriter)
    vcs_reader_writer = utils.inject_type(injector, IVcsReaderWriter)
    return SemVerApi(semver_config, filesystem_reader_writer, vcs_reader_writer)


@provider.provides(LoadedModuleConfig[SemVerConfig])
def make_loaded_semver_config(injector):
    loaded_config = utils.inject_type(injector, LoadedConfig)
    semver_config = loaded_config.require_module_config(SemVerConfig)
    return semver_config


@provider.provides(SemVerConfig)
def make_semver_config(injector):
    return utils.inject_type(injector, LoadedModuleConfig[SemVerConfig]).config
