from pydio.api import Provider

from bumpify import utils
from bumpify.core.filesystem.implementation import FileSystemReaderWriter
from bumpify.core.filesystem.interface import IFileSystemReaderWriter

provider = Provider()


@provider.provides(IFileSystemReaderWriter)
def make_filesystem_reader_writer(injector):
    context = utils.inject_context(injector)
    return FileSystemReaderWriter(context.project_root_dir)
