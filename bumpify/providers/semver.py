from pydio.api import Provider

from bumpify import utils
from bumpify.core.config.objects import LoadedConfig, LoadedModuleConfig
from bumpify.core.semver.objects import SemVerConfig

provider = Provider()


@provider.provides(LoadedModuleConfig[SemVerConfig])
def make_semver_config(injector):
    loaded_config = utils.inject_type(injector, LoadedConfig)
    semver_config = loaded_config.require_module_config(SemVerConfig)
    return semver_config
