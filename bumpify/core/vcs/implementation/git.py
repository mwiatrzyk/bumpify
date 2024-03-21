from typing import List

from bumpify import exc, utils
from bumpify.core.filesystem.interface import IFileSystemReader
from bumpify.core.vcs import exc as vcs_exc
from bumpify.core.vcs.interface import IVcsConnector, IVcsReaderWriter
from bumpify.core.vcs.objects import Commit, Tag


def _shell_exec(root_dir: str, *args) -> bytes:
    with utils.cwd(root_dir):
        return utils.shell_exec(*args, env={"LANG": "en_GB"})


class GitVcsConnector(IVcsConnector):
    """Implementation of the Git repository connector.

    :param filesystem_reader:
        Filesystem to be used as a repository root.

        .. note::
            This is only used to get root directory from and to validate paths.
            All commands are underneath executed directly by Git executable.
    """

    def __init__(self, filesystem_reader: IFileSystemReader):
        self._filesystem_reader = filesystem_reader

    @property
    def _root_dir(self) -> str:
        return self._filesystem_reader.abspath()

    def exists(self) -> bool:
        try:
            _shell_exec(self._root_dir, "git", "status")
        except exc.ShellCommandError:
            return False
        else:
            return True

    def init(self):
        _shell_exec(self._root_dir, "git", "init")

    def connect(self) -> IVcsReaderWriter:
        root_dir = self._root_dir
        if not self.exists():
            raise vcs_exc.RepositoryDoesNotExist(root_dir)
        return self._ReaderWriter(self._root_dir)

    class _ReaderWriter(IVcsReaderWriter):
        def __init__(self, root_dir: str):
            self._root_dir = root_dir

        def _rev_list(self) -> List[str]:
            try:
                stdout = _shell_exec(
                    self._root_dir, "git", "rev-list", "--reverse", "HEAD"
                ).decode()
            except exc.ShellCommandError as e:
                raise vcs_exc.NoCommitsFound(self._root_dir, original_exc=e)
            return stdout.split()

        def current_branch(self) -> str:
            try:
                return _shell_exec(
                    self._root_dir, "git", "rev-parse", "--abbrev-ref", "HEAD"
                ).decode()
            except exc.ShellCommandError as e:
                raise vcs_exc.NoCommitsFound(self._root_dir, original_exc=e)

        def find_head_rev(self) -> str:
            return self._rev_list()[-1]

        def find_initial_rev(self) -> str:
            return self._rev_list()[0]

        def add(self, path: str, *more_paths: str):
            _shell_exec(self._root_dir, "git", "add", path, *more_paths)

        def commit(self, message: str, allow_empty: bool = False) -> str:
            _shell_exec(
                self._root_dir,
                "git",
                "commit",
                "--allow-empty" if allow_empty else None,
                "-m",
                message,
            )
            return self.find_head_rev()

        def tag(self, rev: str, name: str):
            try:
                _shell_exec(self._root_dir, "git", "tag", name, rev)
            except exc.ShellCommandError as e:
                raise vcs_exc.TagAlreadyExists(
                    name, repository_root_dir=self._root_dir, original_exc=e
                )

        def branch(self, name: str):
            try:
                _shell_exec(self._root_dir, "git", "branch", name)
            except exc.ShellCommandError as e:
                raise vcs_exc.BranchAlreadyExists(
                    name, repository_root_dir=self._root_dir, original_exc=e
                )

        def checkout(self, rev_or_name: str):
            _shell_exec(self._root_dir, "git", "checkout", rev_or_name)

        def list_commits(self, start_rev: str = None, end_rev: str = None) -> List[Commit]:
            def format_range() -> str:
                if start_rev is not None and end_rev is not None:
                    return f"{start_rev}..{end_rev}"
                if start_rev is not None:
                    return f"{start_rev}..HEAD"
                if end_rev is not None:
                    return end_rev

            result = []
            try:
                stdout = _shell_exec(
                    self._root_dir,
                    "git",
                    "log",
                    "--reverse",
                    "--format=%H%x00%an%x00%ae%x00%aI%x00%B%x01",
                    format_range(),
                )
            except exc.ShellCommandError:
                pass
            else:
                for raw_commit in filter(lambda x: x, stdout.split(b"\x01")):
                    (
                        commit_id,
                        author,
                        author_email,
                        author_date,
                        message,
                    ) = raw_commit.strip().split(b"\x00")
                    result.append(
                        Commit(
                            rev=commit_id,
                            author=author,
                            author_email=author_email,
                            author_date=author_date,
                            message=message,
                        )
                    )
            return result

        def list_committed_paths(self, rev: str) -> List[str]:
            stdout = _shell_exec(self._root_dir, "git", "show", "--name-only", rev).decode()
            parts = stdout.split("\n\n")
            return parts[-1].splitlines()

        def list_merged_tags(self, rev: str = None) -> List[Tag]:
            try:
                stdout = _shell_exec(
                    self._root_dir,
                    "git",
                    "tag",
                    "-l",
                    "--sort=creatordate",
                    "--format=%(objectname)\t%(refname:strip=2)\t%(creatordate:iso)",
                    "--merged",
                    rev or "HEAD",
                )
            except exc.ShellCommandError:
                return []
            result = []
            if not stdout:
                return result
            for row in stdout.split(b"\n"):
                rev, name, created = row.split(b"\t")
                # TODO: Check if Git can output strict iso here instead of: YYYY-MM-DD HH:MM:SS Z
                created_strict = created.replace(b" ", b"T", 1).replace(b" ", b"", 1)
                result.append(
                    Tag(
                        rev=rev,
                        name=name,
                        created=created_strict,
                    )
                )
            return result


# class DryRunRepositoryReaderWriterProxy:
#     def __init__(self, target: IRepositoryReaderWriter, console: Console):
#         self._target = target
#         self._console = console

#     def __getattr__(self, name):
#         return getattr(self._target, name)

#     def _bold(self, text: str) -> str:
#         return self._console.style(text, bold=True)

#     def branch(self, name: str):
#         self._console.out.info(f"Would {self._bold('create')} a new branch {self._bold(name)} at current HEAD")

#     def add(self, path: str, *more_paths: str):
#         paths = tuple([path]) + more_paths
#         paths = ", ".join([self._bold(x) for x in paths])
#         self._console.out.info(f"Would {self._bold('add')} following paths for next commit: {paths}")

#     def commit(self, message: str) -> Revision:
#         commit_rev = helpers.make_dummy_commit_rev()
#         self._console.out.info(
#             f"Would {self._bold('commit')} changes with message {self._bold(message)} and return {self._bold(commit_rev)}"
#         )
#         return commit_rev

#     def checkout(self, rev_or_name: str):
#         self._console.out.info(f"Would {self._bold('checkout')} HEAD at {self._bold(rev_or_name)}")

#     def tag(self, rev: Revision, name: str):
#         self._console.out.info(f"Would {self._bold('tag')} a commit at {self._bold(rev)} with name {self._bold(name)}")
