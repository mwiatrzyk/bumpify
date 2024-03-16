import abc
import typing

from .objects import Commit, Tag


class IVcsReader(abc.ABC):
    """A read-only interface to interact with underlying VCS repository."""

    @abc.abstractmethod
    def current_branch(self) -> str:
        """Return the name of current branch."""

    @abc.abstractmethod
    def find_head_rev(self) -> str:
        """Find revision number for the current HEAD."""

    @abc.abstractmethod
    def find_initial_rev(self) -> str:
        """Find revision number for the initial commit."""

    @abc.abstractmethod
    def list_commits(self, start_rev: str = None, end_rev: str = None) -> typing.List[Commit]:
        """Return list of commits from current branch, ordered by
        creation time in ascending order.

        When called without parameters, then all reachable commits are
        returned (for current branch).

        Otherwise, a range of commits is returned, according to following spec:

        * ``(start_rev, HEAD]`` when only *start_rev* given,
        * ``[INITIAL, end_rev]`` when only *end_rev* given,
        * ``(start_rev, end_rev]`` when both params given.

        :param start_rev:
            Start revision (exclusive).

        :param end_rev:
            End revision (inclusive).
        """

    @abc.abstractmethod
    def list_committed_paths(self, rev: str) -> typing.List[str]:
        """List paths that were modified in commit given by *rev*.

        :param rev:
            Commit revision.
        """

    @abc.abstractmethod
    def list_merged_tags(self, rev: str = None) -> typing.List[Tag]:
        """List all tags reachable from given *rev* or ``HEAD`` if *rev* is
        omitted.

        :param rev:
            Commit revision.
        """


class IVcsWriter(abc.ABC):
    """A write-only interface to interact with underlying VCS repository."""

    @abc.abstractmethod
    def add(self, *paths: str):
        """Add files to be committed.

        :param `*paths`:
            Paths to be added to the index (to be committed on next call to
            :meth:`commit`).

            These must be paths relative to repository root dir.
        """

    @abc.abstractmethod
    def commit(self, message: str, allow_empty: bool = False) -> str:
        """Commit previously added files to the VCS repository and return
        revision of a newly created commit.

        Newly created commit becomes a new HEAD.

        :param message:
            Commit message.

        :param allow_empty:
            Allow creating commit object without any tree changes.

            .. note:: This is mostly useful for testing.
        """

    @abc.abstractmethod
    def tag(self, rev: str, name: str):
        """Create a tag.

        :param rev:
            Revision to be tagged.

        :param name:
            Tag's name.
        """

    @abc.abstractmethod
    def branch(self, name: str):
        """Create a new branch on current HEAD.

        :param name:
            Name of a branch to create.
        """

    @abc.abstractmethod
    def checkout(self, rev_or_name: str):
        """Checkout HEAD at given revision, branch or tag.

        :param rev_or_name:
            Commit revision, branch or tag name to move HEAD to.
        """


class IVcsReaderWriter(IVcsReader, IVcsWriter):
    """A read-write interface to interact with underlying VCS repository."""


class IVcsConnector(abc.ABC):
    """An entry point interface to access VCS repository."""

    @abc.abstractmethod
    def exists(self) -> bool:
        """Check if repository exists."""

    @abc.abstractmethod
    def init(self):
        """Initialize a new, empty repository.

        If repository already exists, then :exc:`RepositoryAlreadyExists` exception
        will be raised.
        """

    @abc.abstractmethod
    def connect(self) -> IVcsReaderWriter:
        """Connect with an existing repository and return API object to
        interact with it.

        Raises :exc:`RepositoryDoesNotExist` if there is no existing VCS
        repository underneath.
        """
