from pydio.api import Provider

from bumpify import utils
from bumpify.core.api.commands import BumpCommand
from bumpify.core.api.interface import IBumpCommand
from bumpify.core.config.objects import LoadedModuleConfig
from bumpify.core.semver.objects import SemVerConfig

provider = Provider()


@provider.provides(IBumpCommand)
def make_bump_command(injector):
    semver_config = utils.inject_type(injector, LoadedModuleConfig[SemVerConfig])
    return BumpCommand(semver_config)
