from pydio.api import Provider, Variant

from bumpify import utils
from bumpify.core.config.objects import Config, VCSConfig
from bumpify.core.filesystem.interface import IFileSystemReader
from bumpify.core.vcs.implementation.git import GitVcsConnector
from bumpify.core.vcs.interface import IVcsConnector, IVcsReaderWriter

provider = Provider()


@provider.provides(Variant(IVcsConnector, what=VCSConfig.Type.AUTO))
@provider.provides(Variant(IVcsConnector, what=VCSConfig.Type.GIT))
def make_git_vcs_connector(injector):
    filesystem_reader = utils.inject_type(injector, IFileSystemReader)
    return GitVcsConnector(filesystem_reader)


@provider.provides(IVcsReaderWriter)
def make_vcs_reader_writer(injector):
    config = utils.inject_type(injector, Config)
    connector = utils.inject_variant(
        injector, IVcsConnector, what=config.vcs.type
    )  # NOTE: This will fail for unsupported VCS given in config
    return connector.connect()
