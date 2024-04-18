from pydio.api import Provider

from bumpify import utils
from bumpify.core.console.interface import IConsoleOutput
from bumpify.core.filesystem.implementation import (
    DryRunFileSystemReaderWriterProxy,
    FileSystemReaderWriter,
)
from bumpify.core.filesystem.interface import IFileSystemReader, IFileSystemReaderWriter

provider = Provider()


@provider.provides(IFileSystemReaderWriter)
def make_filesystem_reader_writer(injector):
    context = utils.inject_context(injector)
    out = FileSystemReaderWriter(context.project_root_dir)
    if not context.dry_run:
        return out
    cout = utils.inject_type(injector, IConsoleOutput)
    return DryRunFileSystemReaderWriterProxy(out, cout)


@provider.provides(IFileSystemReader)
def make_filesystem_reader(injector):
    # TODO: Currently this returns same object as for IFileSystemReaderWriter,
    # but generally it would be good to wrap this with additional read-only
    # proxy to avoid calling write methods from behind of read-only interface.
    return utils.inject_type(injector, IFileSystemReaderWriter)
