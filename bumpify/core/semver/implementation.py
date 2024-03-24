from typing import List, Optional

from bumpify.core.semver.objects import (
    Changelog,
    ChangelogEntry,
    ChangelogEntryData,
    ConventionalCommit,
    VersionTag,
)
from bumpify.core.vcs.interface import IVcsReaderWriter

from .interface import ISemVerApi


class SemVerApi(ISemVerApi):
    """Default implementation of the semantic versioning API."""

    def __init__(self, vcs_reader_writer: IVcsReaderWriter):
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

    def load_unreleased_changes(self, version_tag: VersionTag) -> Optional[ChangelogEntryData]:
        conventional_commits = self.list_conventional_commits(start_rev=version_tag.tag.rev)
        if not conventional_commits:
            return None
        result = ChangelogEntryData()
        for item in conventional_commits:
            result.update(item)
        return result

    def load_changelog(self, version_tags: List[VersionTag]) -> Optional[Changelog]:
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
