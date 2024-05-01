from bumpify import utils
from bumpify.core.config.interface import IConfigReaderWriter
from bumpify.core.config.objects import LoadedSection
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
        semver_config: LoadedSection[SemVerConfig],
        semver_api: ISemVerApi,
        filesystem_reader_writer: IFileSystemReaderWriter,
        vcs_reader_writer: IVcsReaderWriter,
    ):
        self._semver_config = semver_config
        self._semver_api = semver_api
        self._filesystem_reader_writer = filesystem_reader_writer
        self._vcs_reader_writer = vcs_reader_writer

    def bump(self, presenter: IBumpCommand.IBumpPresenter):
        # TODO: Also update version field in config
        current_branch = self._vcs_reader_writer.current_branch()
        bump_rule = self._semver_config.config.find_bump_rule(current_branch)
        if bump_rule is None:
            presenter.no_bump_rule_found(current_branch)
            return
        self._filesystem_reader_writer.clear_modified_paths()
        version_tags = self._semver_api.list_version_tags()
        if not version_tags:
            version = Version.from_str(self._semver_config.config.version)
            utcnow = utils.utcnow()
            changelog = Changelog()
            changelog.add_entry(ChangelogEntry(version=version, released=utcnow))
            self._semver_api.update_changelog_files(changelog)
            self._semver_api.update_version_files(version)
            self._commit(version)
            presenter.version_bumped(version)
            return
        unreleased_changes = self._semver_api.fetch_unreleased_changes(version_tags[-1])
        if unreleased_changes is None:
            presenter.no_changes_found(version_tags[-1].version)
            return
        if unreleased_changes.breaking_changes:
            component = bump_rule.when_breaking
        elif unreleased_changes.feats:
            component = bump_rule.when_feat
        elif unreleased_changes.fixes:
            component = bump_rule.when_fix
        else:
            presenter.no_changes_found(version_tags[-1].version)
            return
        changelog = self._semver_api.fetch_changelog(version_tags)
        prev_version = changelog.entries[-1].version
        version = prev_version.bump(
            component, prerelease=bump_rule.prerelease
        )  # TODO: bump_rule.buildmetadata_template
        changelog.add_entry(
            ChangelogEntry(
                version=version,
                prev_version=prev_version,
                released=utils.utcnow(),
                data=unreleased_changes,
            )
        )
        self._semver_api.update_changelog_files(changelog)
        self._semver_api.update_version_files(version)
        self._commit(version, prev_version=prev_version)
        presenter.version_bumped(version, prev_version=prev_version)

    def _commit(self, version: Version, prev_version: Version = None):
        version_str = version.to_str()
        prev_version_str = prev_version.to_str() if prev_version else "(null)"
        self.__add_modified_paths_to_bump_commit()
        bump_commit_rev = self.__create_bump_commit(version_str, prev_version_str)
        self.__create_version_tag(bump_commit_rev, version_str)

    def __add_modified_paths_to_bump_commit(self):
        modified_paths = sorted(self._filesystem_reader_writer.modified_paths())
        self._vcs_reader_writer.add(*modified_paths)

    def __create_bump_commit(self, version_str: str, prev_version_str: str) -> str:
        bump_commit_message = utils.format_str(
            self._semver_config.config.bump_commit_message_template,
            version_str=version_str,
            prev_version_str=prev_version_str,
        )
        return self._vcs_reader_writer.commit(bump_commit_message)

    def __create_version_tag(self, bump_commit_rev: str, version_str: str):
        version_tag_name = utils.format_str(
            self._semver_config.config.version_tag_name_template, version_str=version_str
        )
        self._vcs_reader_writer.tag(bump_commit_rev, version_tag_name)
