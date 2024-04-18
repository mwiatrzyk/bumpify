import pytest

from bumpify import exc, utils
from bumpify.core.config.exc import ConfigFileNotFound
from bumpify.core.config.interface import IConfigReaderWriter
from bumpify.core.config.objects import Config
from bumpify.core.console.objects import Styled
from bumpify.core.filesystem.interface import IFileSystemReader, IFileSystemReaderWriter
from bumpify.core.semver.objects import SemVerConfig
from bumpify.core.vcs.exc import NoCommitsFound, RepositoryDoesNotExist
from bumpify.core.vcs.interface import IVcsConnector, IVcsReaderWriter
from tests import helpers
from tests.e2e.interface import IBumpifyCliApp

SUT = IBumpifyCliApp


def test_bump_fails_if_config_file_is_missing(sut: SUT, config_file_abspath: str):
    with pytest.raises(exc.ShellCommandError) as excinfo:
        sut.bump()
    e = excinfo.value
    assert e.returncode == 1
    assert e.stdout_str == helpers.format_exception(ConfigFileNotFound(config_file_abspath)).strip()


def test_bump_fails_if_repository_does_not_exist(
    sut: SUT, tmpdir, tmpdir_config: IConfigReaderWriter, config: Config
):
    tmpdir_config.save(config)
    with pytest.raises(exc.ShellCommandError) as excinfo:
        sut.bump()
    e = excinfo.value
    assert e.returncode == 1
    assert e.stdout_str == helpers.format_exception(RepositoryDoesNotExist(tmpdir)).strip()


class TestWithExistingAndConfiguredProject:

    @pytest.fixture(autouse=True)
    def tmpdir_config(self, tmpdir_config: IConfigReaderWriter, config: Config):
        tmpdir_config.save(config)
        return tmpdir_config

    @pytest.fixture(autouse=True)
    def tmpdir_vcs_connector(self, tmpdir_vcs_connector: IVcsConnector, default_branch: str):
        tmpdir_vcs_connector.init()
        return tmpdir_vcs_connector

    def test_bump_fails_if_no_commits_added_yet(self, sut: SUT, tmpdir):
        with pytest.raises(exc.ShellCommandError) as excinfo:
            sut.bump()
        e = excinfo.value
        assert e.returncode == 1
        assert e.stdout_str == helpers.format_exception(NoCommitsFound(tmpdir)).strip()

    def test_bump_fails_if_no_branch_rule_defined(
        self, sut: SUT, tmpdir_vcs: IVcsReaderWriter, default_branch
    ):
        tmpdir_vcs.commit("initial commit", allow_empty=True)
        tmpdir_vcs.branch(default_branch + "2")
        tmpdir_vcs.checkout(default_branch + "2")
        with pytest.raises(exc.ShellCommandError) as excinfo:
            sut.bump()
        e = excinfo.value
        assert e.returncode == 1
        assert (
            e.stdout_str
            == helpers.format_error(
                "No bump rule found for branch:", Styled(default_branch + "2", bold=True)
            ).strip()
        )

    class TestWithProjectHavingVersionFiles:

        @pytest.fixture(autouse=True)
        def tmpdir_vcs(self, tmpdir_vcs: IVcsReaderWriter, default_branch: str):
            tmpdir_vcs.commit("initial commit", allow_empty=True)
            tmpdir_vcs.branch(default_branch)
            tmpdir_vcs.checkout(default_branch)
            return tmpdir_vcs

        @pytest.fixture(autouse=True)
        def verify_version_files(
            self,
            tmpdir_fs: IFileSystemReaderWriter,
            data_fs: IFileSystemReader,
            semver_config: SemVerConfig,
            expected_version_str: str,
            dry_run: bool
        ):
            for vf in semver_config.version_files:
                template = data_fs.read(f"templates/dummy-project/{vf.path}.txt").decode()
                tmpdir_fs.write(vf.path, template.format(version="0.0.0").encode())
            yield
            if dry_run:
                return
            for vf in semver_config.version_files:
                expected_content = (
                    data_fs.read(f"templates/dummy-project/{vf.path}.txt")
                    .decode()
                    .format(version=expected_version_str)
                )
                assert tmpdir_fs.read(vf.path).decode() == expected_content

        @pytest.fixture(autouse=True)
        def verify_changelog_files(
            self,
            tmpdir_fs: IFileSystemReaderWriter,
            semver_config: SemVerConfig,
            expected_version_str: str,
            dry_run: bool
        ):
            yield
            if dry_run:
                return
            for cf in semver_config.changelog_files:
                assert expected_version_str in tmpdir_fs.read(cf.path).decode()

        @pytest.fixture(autouse=True)
        def verify_version_tag(
            self, tmpdir_vcs: IVcsReaderWriter, semver_config: SemVerConfig, expected_version_str, dry_run: bool
        ):
            yield
            if dry_run:
                return
            tags = tmpdir_vcs.list_merged_tags()
            assert tags[-1].name == utils.format_str(
                semver_config.version_tag_name_template, version_str=expected_version_str
            )

        @pytest.mark.parametrize("expected_version_str", ["0.0.1"])
        def test_create_initial_version(self, sut: SUT, expected_version_str: str):
            stdout = sut.bump()
            assert (
                stdout
                == helpers.format_info(
                    "Version was bumped:",
                    Styled("(null)", bold=True),
                    "->",
                    Styled(expected_version_str, bold=True),
                ).strip()
            )

        @pytest.mark.parametrize(
            "commit_message, expected_version_str, expected_prev_version_str",
            [
                ("fix!: a breaking fix", "1.0.0", "0.0.1"),
                ("feat: a feature", "0.1.0", "0.0.1"),
                ("fix: a fix", "0.0.2", "0.0.1"),
            ],
        )
        def test_create_next_version(
            self,
            sut: SUT,
            tmpdir_vcs: IVcsReaderWriter,
            expected_version_str: str,
            expected_prev_version_str: str,
            commit_message: str,
        ):
            stdout = sut.bump()
            assert (
                stdout
                == helpers.format_info(
                    "Version was bumped:",
                    Styled("(null)", bold=True),
                    "->",
                    Styled(expected_prev_version_str, bold=True),
                ).strip()
            )
            tmpdir_vcs.commit(commit_message, allow_empty=True)
            stdout = sut.bump()
            assert (
                stdout
                == helpers.format_info(
                    "Version was bumped:",
                    Styled(expected_prev_version_str, bold=True),
                    "->",
                    Styled(expected_version_str, bold=True),
                ).strip()
            )

        @pytest.mark.parametrize("dry_run", [True])
        @pytest.mark.parametrize("expected_version_str", ["0.0.1"])
        def test_bump_with_dry_run_enabled(self, sut: SUT):
            stdout = sut.bump()
            assert "Would" in stdout
