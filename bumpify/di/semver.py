from pydio.api import Provider

from bumpify import utils
from bumpify.core.config.objects import LoadedConfig, LoadedSection
from bumpify.core.filesystem.interface import IFileSystemReaderWriter
from bumpify.core.hook.interface import IHookApi
from bumpify.core.semver.implementation import SemVerApi
from bumpify.core.semver.interface import ISemVerApi
from bumpify.core.semver.objects import SemVerConfig
from bumpify.core.vcs.interface import IVcsReaderWriter

provider = Provider()


@provider.provides(ISemVerApi)
def make_semver_api(injector):
    semver_config = utils.inject_type(injector, LoadedSection[SemVerConfig])
    filesystem_reader_writer = utils.inject_type(injector, IFileSystemReaderWriter)
    vcs_reader_writer = utils.inject_type(injector, IVcsReaderWriter)
    hook_api = utils.inject_type(injector, IHookApi)
    return SemVerApi(semver_config, filesystem_reader_writer, vcs_reader_writer, hook_api)


@provider.provides(LoadedSection[SemVerConfig])
def make_loaded_semver_config(injector):
    loaded_config = utils.inject_type(injector, LoadedConfig)
    loaded_semver_config = loaded_config.require_section(SemVerConfig)
    return loaded_semver_config
