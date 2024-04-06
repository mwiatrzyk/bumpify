from pydio.api import Provider

from bumpify import utils
from bumpify.core.api.commands import BumpCommand, InitCommand
from bumpify.core.api.interface import IBumpCommand, IInitCommand
from bumpify.core.config.interface import IConfigReaderWriter
from bumpify.core.config.objects import LoadedModuleConfig
from bumpify.core.notifier.interface import INotifier
from bumpify.core.prompt.interface import IPrompt
from bumpify.core.semver.objects import SemVerConfig
from bumpify.presenters.api import InitPresenter
from bumpify.providers.api import InitProvider

provider = Provider()


@provider.provides(IInitCommand)
def make_init_command(injector):
    config_reader_writer = utils.inject_type(injector, IConfigReaderWriter)
    return InitCommand(config_reader_writer)


@provider.provides(IInitCommand.IInitProvider)
def make_init_provider(injector):
    prompt = utils.inject_type(injector, IPrompt)
    return InitProvider(prompt)


@provider.provides(IInitCommand.IInitPresenter)
def make_init_presenter(injector):
    status_listener = utils.inject_type(injector, INotifier)
    return InitPresenter(status_listener)


@provider.provides(IBumpCommand)
def make_bump_command(injector):
    semver_config = utils.inject_type(injector, LoadedModuleConfig[SemVerConfig])
    return BumpCommand(semver_config)
