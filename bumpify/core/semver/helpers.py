import datetime
from typing import List

from bumpify.core.vcs.helpers import make_dummy_commit, make_dummy_tag

from .objects import ChangelogEntry, ChangelogEntryData, ConventionalCommit, Version, VersionTag


def make_dummy_version_tag(version: Version, rev: str = None) -> VersionTag:
    """Create dummy version tag.

    This helper is useful mostly for testing purposes.

    :param version:
        The version to be attached and encoded in resulting tag's name.

    :param rev:
        Commit revision.

        This overrides default random revision.
    """
    return VersionTag(
        tag=make_dummy_tag(f"v{version.to_str()}", rev=rev),
        version=version,
    )


def make_dummy_conventional_commit(
    message: str, rev: str = None, author_date: datetime.datetime = None
) -> ConventionalCommit:
    """Create dummy conventional commit.

    This can be used whenever fake data is needed for testing of the upper
    layers.

    Raises :exc:`ValueError` if *message* could not be interpreted as
    conventional commit message.

    :param message:
        Commit message.

    :param rev:
        Commit revision.

        Will be picked at random if not given.

    :param author_date:
        Author's date.

        Current UTC datetime will be used if not given.
    """
    commit = make_dummy_commit(message, rev=rev, author_date=author_date)
    maybe_conventional_commit = ConventionalCommit.from_commit(commit)
    if maybe_conventional_commit is None:
        raise ValueError(f"not a conventional commit message: {message}")
    return maybe_conventional_commit
