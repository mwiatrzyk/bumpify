from bumpify import exc


class VcsError(exc.BumpifyError):
    """Base class for all VCS repository related errors."""

    #: Repository root directory.
    repository_root_dir: str

    def __init__(self, repository_root_dir: str, original_exc: Exception = None):
        super().__init__(original_exc=original_exc)
        self.repository_root_dir = repository_root_dir


class RepositoryDoesNotExist(VcsError):
    """Raised when repository is tried to be opened but it does not exist."""

    __message_template__ = "{self.repository_root_dir}"


class NoCommitsFound(VcsError):
    """Raised when trying to read from a repository that does not have commits yet."""

    __message_template__ = "{self.repository_root_dir}"


class TagAlreadyExists(VcsError):
    """Raised when trying to create a tag that already exists."""

    __message_template__ = "{self.tag_name} (in repository at: {self.repository_root_dir})"

    #: Name of a duplicated tag.
    tag_name: str

    def __init__(self, tag_name: str, **kwargs):
        super().__init__(**kwargs)
        self.tag_name = tag_name


class BranchAlreadyExists(VcsError):
    """Raised when trying to create a branch that already exists."""

    __message_template__ = "{self.branch_name} (in repository at: {self.repository_root_dir})"

    #: Name of a duplicated branch.
    branch_name: str

    def __init__(self, branch_name: str, **kwargs):
        super().__init__(**kwargs)
        self.branch_name = branch_name
