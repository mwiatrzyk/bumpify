from typing import List

import pytest

from bumpify.core.filesystem.interface import IFileSystemReaderWriter
from bumpify.core.vcs import exc as vcs_exc
from bumpify.core.vcs.interface import IVcsConnector, IVcsReaderWriter
from bumpify.core.vcs.implementation.git import GitVcsConnector


@pytest.fixture
def connector(tmpdir_fs):
    return GitVcsConnector(tmpdir_fs)


class TestWithNonExistingRepository:

    @pytest.fixture(autouse=True)
    def setup(self, connector: IVcsConnector, tmpdir_fs: IFileSystemReaderWriter):
        self.sut = connector
        self.tmpdir_fs = tmpdir_fs

    def test_exists_returns_false(self):
        assert not self.sut.exists()

    def test_when_init_called_then_empty_repository_is_created(self):
        assert not self.sut.exists()
        self.sut.init()
        assert self.sut.exists()

    def test_init_can_be_called_twice(self):
        assert not self.sut.exists()
        self.sut.init()
        self.sut.init()
        assert self.sut.exists()

    def test_connect_fails_if_repository_does_not_exist(self):
        with pytest.raises(vcs_exc.RepositoryDoesNotExist) as excinfo:
            self.sut.connect()
        assert excinfo.value.repository_root_dir == self.tmpdir_fs.abspath()

    def test_connect_returns_connection_object_if_repository_exists(self):
        self.sut.init()
        assert isinstance(self.sut.connect(), IVcsReaderWriter)


class TestWithEmptyRepository:

    @pytest.fixture(autouse=True)
    def setup(self, connector: IVcsConnector, tmpdir_fs: IFileSystemReaderWriter):
        connector.init()
        self.sut = connector.connect()
        self.tmpdir_fs = tmpdir_fs

    def test_current_branch_raises_no_commits_found(self):
        with pytest.raises(vcs_exc.NoCommitsFound) as excinfo:
            self.sut.current_branch()
        assert excinfo.value.repository_root_dir == self.tmpdir_fs.abspath()

    def test_find_head_rev_raises_no_commits_found(self):
        with pytest.raises(vcs_exc.NoCommitsFound) as excinfo:
            self.sut.find_head_rev()
        assert excinfo.value.repository_root_dir == self.tmpdir_fs.abspath()

    def test_find_initial_rev_raises_no_commits_found(self):
        with pytest.raises(vcs_exc.NoCommitsFound) as excinfo:
            self.sut.find_initial_rev()
        assert excinfo.value.repository_root_dir == self.tmpdir_fs.abspath()

    def test_list_commits_returns_empty_list(self):
        assert self.sut.list_commits() == []


class TestWithInitialCommit:

    @pytest.fixture
    def branch_name(self):
        return "dummy"

    @pytest.fixture
    def commit_message(self):
        return "chore: initial commit"

    @pytest.fixture
    def committed_paths(self):
        return [
            "foo.txt",
            "bar/baz.txt",
            "spam/more/spam.txt",
        ]

    @pytest.fixture(autouse=True)
    def setup(self, connector: IVcsConnector, tmpdir_fs: IFileSystemReaderWriter, branch_name, commit_message, committed_paths):
        connector.init()
        self.sut = connector.connect()
        self.tmpdir_fs = tmpdir_fs
        for path in committed_paths:
            self.tmpdir_fs.write(path, f"content of {path}".encode())
            self.sut.add(path)
        self.initial_rev = self.sut.commit(commit_message)
        self.sut.branch(branch_name)
        self.sut.checkout(branch_name)

    def test_check_current_branch(self, branch_name: str):
        assert self.sut.current_branch() == branch_name

    def test_find_head_rev(self):
        assert self.sut.find_head_rev() == self.initial_rev

    def test_find_initial_rev(self):
        assert self.sut.find_initial_rev() == self.initial_rev

    def test_list_commits_called_without_args_returns_one_commit(self, commit_message):
        commits = self.sut.list_commits()
        assert len(commits) == 1
        commit, = commits
        assert commit.rev == self.initial_rev
        assert commit.message == commit_message

    def test_list_commits_with_start_rev_returns_empty_list(self):
        assert self.sut.list_commits(start_rev=self.initial_rev) == []

    def test_list_commits_with_start_rev_and_end_rev_returns_empty_list(self):
        assert self.sut.list_commits(start_rev=self.initial_rev, end_rev=self.initial_rev) == []

    def test_list_commits_with_end_rev_returns_one_commit(self):
        commits = self.sut.list_commits()
        assert len(commits) == 1
        assert self.sut.list_commits(end_rev=self.initial_rev) == commits

    def test_list_committed_paths_returns_paths_that_were_modified_in_given_commit(self, committed_paths):
        paths = self.sut.list_committed_paths(self.initial_rev)
        assert set(paths) == set(committed_paths)

    def test_list_reachable_tags_returns_empty_list_if_no_tags_are_found(self):
        assert self.sut.list_merged_tags(self.initial_rev) == []

    @pytest.mark.parametrize("tag_name", ["dummy"])
    def test_list_merged_tags_for_head(self, tag_name):
        self.sut.tag(self.initial_rev, tag_name)
        tags = self.sut.list_merged_tags()
        assert len(tags) == 1
        assert tags[0].name == tag_name

    @pytest.mark.parametrize("tag_name", ["dummy"])
    def test_list_reachable_tags_returns_tag_if_it_exists_for_head(self, tag_name):
        self.sut.tag(self.initial_rev, tag_name)
        tags = self.sut.list_merged_tags(self.initial_rev)
        assert len(tags) == 1
        assert tags[0].name == tag_name

    def test_if_invalid_rev_provided_then_list_reachable_tags_return_empty_list(self):
        assert self.sut.list_merged_tags("not a valid ref") == []

    @pytest.mark.parametrize("tag_name", ["dummy"])
    def test_tag_cannot_be_created_twice(self, tag_name, tmpdir):
        self.sut.tag(self.initial_rev, tag_name)
        with pytest.raises(vcs_exc.TagAlreadyExists) as excinfo:
            self.sut.tag(self.initial_rev, tag_name)
        assert excinfo.value.repository_root_dir == str(tmpdir)
        assert excinfo.value.tag_name == tag_name

    def test_branch_cannot_be_created_twice(self, branch_name, tmpdir):
        with pytest.raises(vcs_exc.BranchAlreadyExists) as excinfo:
            self.sut.branch(branch_name)
        assert excinfo.value.repository_root_dir == str(tmpdir)
        assert excinfo.value.branch_name == branch_name


class TestWithMultipleCommits:

    @pytest.fixture
    def commit_count(self):
        return 10

    @pytest.fixture(autouse=True)
    def setup(self, connector: IVcsConnector, commit_count: int):
        connector.init()
        self.sut = connector.connect()
        for i in range(commit_count):
            self.sut.commit(f"chore: commit message #{i}", allow_empty=True)
        self.all_commits = self.sut.list_commits()

    def test_list_commits_with_start_rev_only(self):
        commits = self.sut.list_commits(start_rev=self.all_commits[0].rev)
        assert len(commits) == len(self.all_commits) - 1
        assert commits == self.all_commits[1:]

    def test_list_commits_with_end_rev_only(self):
        commits = self.sut.list_commits(end_rev=self.all_commits[-2].rev)
        assert len(commits) == len(self.all_commits) - 1
        assert commits == self.all_commits[:-1]

    def test_list_commits_with_both_start_and_end_revs(self):
        commits = self.sut.list_commits(start_rev=self.all_commits[0].rev, end_rev=self.all_commits[-2].rev)
        assert len(commits) == len(self.all_commits) - 2
        assert commits == self.all_commits[1:-1]
