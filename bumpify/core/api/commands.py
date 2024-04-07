from bumpify import utils
from bumpify.core.config.interface import IConfigReaderWriter
from bumpify.core.config.objects import LoadedModuleConfig
from bumpify.core.filesystem.interface import IFileSystemReader, IFileSystemReaderWriter
from bumpify.core.semver.interface import ISemVerApi
from bumpify.core.semver.objects import Changelog, ChangelogEntry, SemVerConfig, Version
from bumpify.core.vcs.interface import IVcsReaderWriter

from .interface import IBumpCommand, IInitCommand


class InitCommand(IInitCommand):

    def __init__(self, config_reader_writer: IConfigReaderWriter):
        self._config_reader_writer = config_reader_writer

    def init(self, provider: IInitCommand.IInitProvider, presenter: IInitCommand.IInitPresenter):
        config_file_abspath = self._config_reader_writer.abspath()
        if self._config_reader_writer.exists():
            presenter.notify_skipped(config_file_abspath)
            return
        presenter.notify_started(config_file_abspath)
        config = provider.provide_config()
        self._config_reader_writer.save(config)
        presenter.notify_done()


class BumpCommand(IBumpCommand):

    def __init__(
        self,
        semver_config: LoadedModuleConfig[SemVerConfig],
        semver_api: ISemVerApi,
        filesystem_reader_writer: IFileSystemReaderWriter,
        vcs_reader_writer: IVcsReaderWriter,
    ):
        self._semver_config = semver_config
        self._semver_api = semver_api
        self._filesystem_reader_writer = filesystem_reader_writer
        self._vcs_reader_writer = vcs_reader_writer

    def bump(self, presenter: IBumpCommand.IBumpPresenter):
        self._filesystem_reader_writer.clear_modified_paths()
        initial_version = Version.from_str(self._semver_config.config.version)
        utcnow = utils.utcnow()
        changelog = Changelog()
        changelog.add_entry(ChangelogEntry(version=initial_version, released=utcnow))
        self._semver_api.update_changelog_files(changelog)
        self._semver_api.update_version_files(initial_version)
        self._create_bump_commit(initial_version)

    def _create_bump_commit(self, version: Version):
        self.__add_modified_paths_to_bump_commit()

    def __add_modified_paths_to_bump_commit(self):
        modified_paths = sorted(self._filesystem_reader_writer.modified_paths())
        self._vcs_reader_writer.add(*modified_paths)
