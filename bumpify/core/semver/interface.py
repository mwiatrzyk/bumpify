import abc
from typing import List, Optional

from .objects import ChangelogEntryData, VersionTag


class ISemVerQueryApi(abc.ABC):
    """Query API for semantic versioning."""

    @abc.abstractmethod
    def list_version_tags(self) -> List[VersionTag]:
        """Filter out version tags reachable from the HEAD of currently checked
        out branch and return sorted by semantic version rules in ascending
        order.

        If no version tags are found, then empty list is returned.
        """


class ISemVerCommandApi(abc.ABC):
    """Command API for semantic versioning."""


class ISemVerApi(ISemVerCommandApi, ISemVerQueryApi):
    """Command/query API for semantic versioning."""
