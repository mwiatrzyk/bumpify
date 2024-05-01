from pydio.api import Provider

from bumpify import utils
from bumpify.core.api.commands import BumpCommand, InitCommand
from bumpify.core.api.interface import IBumpCommand, IInitCommand
from bumpify.core.api.presenters import BumpCommandPresenter, InitPresenter
from bumpify.core.api.providers import InitProvider
from bumpify.core.config.interface import IConfigReaderWriter
from bumpify.core.config.objects import LoadedSection
from bumpify.core.console.interface import IConsoleInput, IConsoleOutput
from bumpify.core.filesystem.interface import IFileSystemReaderWriter
from bumpify.core.semver.interface import ISemVerApi
from bumpify.core.semver.objects import SemVerConfig
from bumpify.core.vcs.interface import IVcsReaderWriter

provider = Provider()


@provider.provides(IInitCommand)
def make_init_command(injector):
    config_reader_writer = utils.inject_type(injector, IConfigReaderWriter)
    return InitCommand(config_reader_writer)


@provider.provides(IInitCommand.IInitProvider)
def make_init_provider(injector):
    cin = utils.inject_type(injector, IConsoleInput)
    return InitProvider(cin)


@provider.provides(IInitCommand.IInitPresenter)
def make_init_presenter(injector):
    cout = utils.inject_type(injector, IConsoleOutput)
    return InitPresenter(cout)


@provider.provides(IBumpCommand)
def make_bump_command(injector):
    semver_config = utils.inject_type(injector, LoadedSection[SemVerConfig])
    semver_api = utils.inject_type(injector, ISemVerApi)
    filesystem_reader_writer = utils.inject_type(injector, IFileSystemReaderWriter)
    vcs_reader_writer = utils.inject_type(injector, IVcsReaderWriter)
    return BumpCommand(semver_config, semver_api, filesystem_reader_writer, vcs_reader_writer)


@provider.provides(IBumpCommand.IBumpPresenter)
def make_bump_command_presenter(injector):
    cout = utils.inject_type(injector, IConsoleOutput)
    return BumpCommandPresenter(cout)
