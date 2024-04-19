from pydio.api import Provider, Variant

from bumpify import utils
from bumpify.core.config.objects import Config, VCSConfig
from bumpify.core.console.interface import IConsoleOutput
from bumpify.core.filesystem.interface import IFileSystemReader
from bumpify.core.vcs.implementation.git import GitVcsConnector
from bumpify.core.vcs.implementation.proxy import DryRunVcsReaderWriterProxy
from bumpify.core.vcs.interface import IVcsConnector, IVcsReaderWriter

provider = Provider()


@provider.provides(Variant(IVcsConnector, what=VCSConfig.Type.AUTO))
@provider.provides(Variant(IVcsConnector, what=VCSConfig.Type.GIT))
def make_git_vcs_connector(injector):
    filesystem_reader = utils.inject_type(injector, IFileSystemReader)
    return GitVcsConnector(filesystem_reader)


@provider.provides(IVcsReaderWriter)
def make_vcs_reader_writer(injector):
    context = utils.inject_context(injector)
    config = utils.inject_type(injector, Config)
    connector = utils.inject_variant(injector, IVcsConnector, what=config.vcs.type)
    obj = connector.connect()
    if not context.dry_run:
        return obj
    cout = utils.inject_type(injector, IConsoleOutput)
    return DryRunVcsReaderWriterProxy(obj, cout)
