import abc
from typing import List, Optional

from .objects import Changelog, ChangelogEntryData, ConventionalCommit, Version, VersionTag


class ISemVerQueryApi(abc.ABC):
    """Query API for semantic versioning."""

    @abc.abstractmethod
    def list_version_tags(self) -> List[VersionTag]:
        """Filter out version tags reachable from the HEAD of currently checked
        out branch and return sorted by semantic version rules in ascending
        order.

        If no version tags are found, then empty list is returned.
        """

    @abc.abstractmethod
    def list_conventional_commits(
        self, start_rev: str = None, end_rev: str = None
    ) -> List[ConventionalCommit]:
        """Filter out conventional commits from list of commits.

        The meaning of the *start_rev* and *end_rev* parameters is the same as
        for :meth:`IVcsReader.list_commits` method.

        Returns empty list if no conventional commits were found.

        :param start_rev:
            See :meth:`IVcsReader.list_commits` method.

        :param end_rev:
            See :meth:`IVcsReader.list_commits` method.
        """

    @abc.abstractmethod
    def fetch_unreleased_changes(self, version_tag: VersionTag) -> Optional[ChangelogEntryData]:
        """Fetch unreleased changes made between *version_tag* (exclusive) and
        current HEAD.

        If no unreleased changes are found, then return ``None``. Otherwise
        return new instance of :class:`ChangelogEntryData` that can later be
        added to a changelog.

        :param version_tag:
            Version tag pointing to a commit to start search from (exclusive).

            This should be the most recent version tag to load unreleased
            changes that should go to a next version's changelog.
        """

    @abc.abstractmethod
    def fetch_changelog(self, version_tags: List[VersionTag]) -> Changelog:
        """Fetch changelog for given list of version tags.

        :param version_tags:
            List of version tags to load changelog for.

            It is assumed that the list is in the right order, sorted ascending by
            semantic version rules, and that the ordering is the same as it
            would be if the tags were sorted by their creation date.

            The list must not be empty.
        """


class ISemVerCommandApi(abc.ABC):
    """Command API for semantic versioning."""

    @abc.abstractmethod
    def update_changelog_files(self, changelog: Changelog):
        """Update all configured changelog files by encoding and writing
        provided *changelog*.

        :param changelog:
            The changelog object to be used to replace current content of
            changelog files.
        """

    @abc.abstractmethod
    def update_version_files(self, version: Version):
        """Update version in all user-defined version files and in Bumpify
        config file.

        :param version:
            The version to be written.
        """


class ISemVerApi(ISemVerCommandApi, ISemVerQueryApi):
    """Command/query API for semantic versioning."""
