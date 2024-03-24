from typing import List, Optional

from bumpify.core.semver.objects import ChangelogEntryData, ConventionalCommit, VersionTag
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
