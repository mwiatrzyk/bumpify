import io
import re
from typing import List, Optional

from bumpify.core.filesystem.interface import IFileSystemReaderWriter
from bumpify.core.semver.objects import (
    Changelog,
    ChangelogEntry,
    ChangelogEntryData,
    ConventionalCommit,
    Version,
    VersionTag,
)
from bumpify.core.vcs.interface import IVcsReaderWriter

from . import _changelog_formatters, _constants
from .exc import UnsupportedChangelogFormat, VersionFileNotUpdated
from .interface import ISemVerApi
from .objects import SemVerConfig


class SemVerApi(ISemVerApi):
    """Default implementation of the semantic versioning API."""

    def __init__(
        self,
        semver_config: SemVerConfig,
        filesystem_reader_writer: IFileSystemReaderWriter,
        vcs_reader_writer: IVcsReaderWriter,
    ):
        self._semver_config = semver_config
        self._filesystem_reader_writer = filesystem_reader_writer
        self._vcs_reader_writer = vcs_reader_writer

    def list_version_tags(self) -> List[VersionTag]:
        result = []
        for tag in self._vcs_reader_writer.list_merged_tags():
            maybe_version_tag = VersionTag.from_tag(tag)
            if maybe_version_tag:
                result.append(maybe_version_tag)
        result.sort(key=lambda x: x.version)
        return result

    def list_conventional_commits(
        self, start_rev: str = None, end_rev: str = None
    ) -> List[ConventionalCommit]:
        result = []
        for commit in self._vcs_reader_writer.list_commits(start_rev=start_rev, end_rev=end_rev):
            maybe_conventional_commit = ConventionalCommit.from_commit(commit)
            if maybe_conventional_commit:
                result.append(maybe_conventional_commit)
        return result

    def fetch_unreleased_changes(self, version_tag: VersionTag) -> Optional[ChangelogEntryData]:
        conventional_commits = self.list_conventional_commits(start_rev=version_tag.tag.rev)
        if not conventional_commits:
            return None
        result = ChangelogEntryData()
        for item in conventional_commits:
            result.update(item)
        return result

    def fetch_changelog(self, version_tags: List[VersionTag]) -> Optional[Changelog]:
        result = Changelog()
        result.add_entry(
            ChangelogEntry(version=version_tags[0].version, released=version_tags[0].tag.created)
        )
        prev_version_tag = version_tags[0]
        for version_tag in version_tags[1:]:
            conventional_commits = self.list_conventional_commits(
                start_rev=prev_version_tag.tag.rev, end_rev=version_tag.tag.rev
            )
            changelog_entry_data = ChangelogEntryData()
            for item in conventional_commits:
                changelog_entry_data.update(item)
            result.add_entry(
                ChangelogEntry(
                    version=version_tag.version,
                    prev_version=prev_version_tag.version,
                    released=version_tag.tag.created,
                    data=changelog_entry_data if not changelog_entry_data.is_empty() else None,
                )
            )
            prev_version_tag = version_tag
        return result

    def update_changelog_files(self, changelog: Changelog):
        for changelog_file in self._semver_config.changelog_files:
            if changelog_file.path.endswith(".json"):
                changelog_data = _changelog_formatters.format_as_json(changelog)
            elif changelog_file.path.endswith(".md"):
                changelog_data = _changelog_formatters.format_as_markdown(changelog)
            else:
                raise UnsupportedChangelogFormat(changelog_file.path)
            self._filesystem_reader_writer.write(
                changelog_file.path, changelog_data.encode(changelog_file.encoding)
            )

    def update_version_files(self, version: Version):

        class VersionFileUpdater:

            def __init__(
                self, version_file: SemVerConfig.VersionFile, version: Version, out: io.StringIO
            ):
                self._vf = version_file
                self._version = version
                self._out = out
                if self._vf.prefix is not None:
                    self._next_state = self._st_looking_by_prefix
                else:
                    self._next_state = self._st_looking_everywhere

            def feed(self, line: str):
                next_state = self._next_state(line)
                self._next_state = next_state

            def _repl(self, m):
                return self._version.to_str()

            def _st_looking_by_prefix(self, line: str):
                if not line:
                    raise VersionFileNotUpdated(self._vf.path, f"line prefix not found: {self._vf.prefix}")
                if not line.lstrip().startswith(self._vf.prefix):
                    self._out.write(line)
                    return self._st_looking_by_prefix
                new_line = re.sub(_constants.SEMVER_RE, self._repl, line)
                self._out.write(new_line)
                return self._st_done

            def _st_looking_everywhere(self, line: str):
                if not line:
                    raise VersionFileNotUpdated(self._vf.path, "no semantic version string found")
                new_line = re.sub(_constants.SEMVER_RE, self._repl, line)
                self._out.write(new_line)
                if new_line != line:
                    return self._st_done
                return self._st_looking_everywhere

            def _st_done(self, line: str):
                self._out.write(line)
                return self._st_done

        for vf in self._semver_config.version_files:
            dest = io.StringIO()
            updater = VersionFileUpdater(vf, version, dest)
            initial_content = self._filesystem_reader_writer.read(vf.path).decode(vf.encoding)
            for line in io.StringIO(initial_content):
                updater.feed(line)
            updater.feed("")
            self._filesystem_reader_writer.write(vf.path, dest.getvalue().encode(vf.encoding))
