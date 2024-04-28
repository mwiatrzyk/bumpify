from pydio.api import Provider

from bumpify import utils
from bumpify.core.config.objects import LoadedConfig
from bumpify.core.filesystem.interface import IFileSystemReader
from bumpify.core.hook.implementation import HookApiLoader
from bumpify.core.hook.interface import IHookApi, IHookApiLoader

provider = Provider()


@provider.provides(IHookApiLoader)
def make_hook_file_loader(injector):
    loaded_config = utils.inject_type(injector, LoadedConfig)
    filesystem_reader = utils.inject_type(injector, IFileSystemReader)
    return HookApiLoader(loaded_config, filesystem_reader)


@provider.provides(IHookApi)
def make_hook_file(injector):
    hook_file_loader = utils.inject_type(injector, IHookApiLoader)
    return hook_file_loader.load()
