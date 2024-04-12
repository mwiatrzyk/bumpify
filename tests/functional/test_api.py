import click
import pytest
from mockify.api import ABCMock, Mock, Return, ordered, patched, satisfied
from mockify.matchers import Type
from pydio.api import Injector

from bumpify import utils
from bumpify.core.api.interface import IBumpCommand, IInitCommand
from bumpify.core.config.interface import IConfigReaderWriter
from bumpify.core.config.objects import Config
from bumpify.core.filesystem.interface import IFileSystemReader, IFileSystemReaderWriter
from bumpify.core.notifier.objects import Styled
from bumpify.core.semver.objects import SemVerConfig, Version
from bumpify.core.vcs.interface import IVcsConnector, IVcsReaderWriter
from bumpify.di import provider
from tests import helpers
from tests.matchers import ReprEqual


@pytest.fixture
def injector(tmpdir, config_file_path):
    injector = Injector(provider)
    context = utils.inject_context(injector)
    context.project_root_dir = tmpdir
    context.config_file_path = config_file_path
    with injector:
        yield injector


class TestInitCommand:
    UUT = IInitCommand
    Provider = IInitCommand.IInitProvider
    Presenter = IInitCommand.IInitPresenter

    @pytest.fixture
    def uut(self, injector):
        return utils.inject_type(injector, IInitCommand)

    @pytest.fixture
    def click_mock(self):
        mock = Mock("click")
        with satisfied(mock), ordered(mock):
            yield mock

    @pytest.fixture
    def provider(self, injector):
        return utils.inject_type(injector, IInitCommand.IInitProvider)

    @pytest.fixture
    def presenter(self, injector):
        return utils.inject_type(injector, IInitCommand.IInitPresenter)

    @pytest.mark.parametrize("selected_repository_type", ["git"])
    @pytest.mark.parametrize(
        "selected_version_file_1",
        [
            {
                "path": "pyproject.toml",
                "prefix": "version",
                "section": "[tool.poetry]",
                "encoding": "ascii",
            }
        ],
    )
    @pytest.mark.parametrize(
        "selected_version_file_2",
        [{"path": "dummy/__init__.py", "prefix": None, "section": None, "encoding": None}],
    )
    def test_when_init_command_invoked_then_initial_config_is_created(
        self,
        uut: UUT,
        tmpdir_config: IConfigReaderWriter,
        provider: Provider,
        presenter: Presenter,
        click_mock,
        selected_repository_type,
        selected_version_file_1,
        selected_version_file_2,
        config_file_abspath,
        capsys,
    ):
        version_components = click.Choice(["major", "minor", "patch"])
        optional_default = "leave empty to skip"
        click_mock.prompt.expect_call(
            "Choose project's repository type",
            type=ReprEqual(click.Choice(["git"])),
            default=None,
            show_default=False,
        ).will_once(Return(selected_repository_type))
        click_mock.confirm.expect_call("Create semantic versioning configuration?").will_once(
            Return(True)
        )
        click_mock.prompt.expect_call(
            "Branch name/pattern for bump rule #1", default=None, type=str
        ).will_once(Return("prod"))
        click_mock.prompt.expect_call(
            "Version component to bump on breaking change",
            type=ReprEqual(version_components),
            default="major",
            show_default=True,
        ).will_once(Return("major"))
        click_mock.prompt.expect_call(
            "Version component to bump on feature introduction",
            type=ReprEqual(version_components),
            default="minor",
            show_default=True,
        ).will_once(Return("minor"))
        click_mock.prompt.expect_call(
            "Version component to bump on bug fix",
            type=ReprEqual(version_components),
            default="patch",
            show_default=True,
        ).will_once(Return("patch"))
        click_mock.prompt.expect_call(
            "Prerelease name", default=optional_default, type=str
        ).will_once(Return(optional_default))
        click_mock.confirm.expect_call("Add another bump rule?").will_once(Return(False))
        click_mock.prompt.expect_call("Version file #1 path", type=Type(click.Path)).will_once(
            Return(selected_version_file_1["path"])
        )
        click_mock.prompt.expect_call(
            "Version file #1 prefix", default=optional_default, type=str
        ).will_once(Return(selected_version_file_1["prefix"] or optional_default))
        click_mock.prompt.expect_call(
            "Version file #1 section", default=optional_default, type=str
        ).will_once(Return(selected_version_file_1["section"] or optional_default))
        click_mock.prompt.expect_call(
            "Version file #1 encoding", default="utf-8", type=str
        ).will_once(Return(selected_version_file_1["encoding"] or "utf-8"))
        click_mock.confirm.expect_call("Add another version file?").will_once(Return(True))
        click_mock.prompt.expect_call("Version file #2 path", type=Type(click.Path)).will_once(
            Return(selected_version_file_2["path"])
        )
        click_mock.prompt.expect_call(
            "Version file #2 prefix", default=optional_default, type=str
        ).will_once(Return(selected_version_file_2["prefix"] or optional_default))
        click_mock.prompt.expect_call(
            "Version file #2 section", default=optional_default, type=str
        ).will_once(Return(selected_version_file_2["section"] or optional_default))
        click_mock.prompt.expect_call(
            "Version file #2 encoding", default="utf-8", type=str
        ).will_once(Return(selected_version_file_2["encoding"] or "utf-8"))
        click_mock.confirm.expect_call("Add another version file?").will_once(Return(False))
        with patched(click_mock):
            uut.init(provider, presenter)
        loaded_config = tmpdir_config.load()
        assert loaded_config is not None
        config = loaded_config.config
        assert config.vcs.type.value == selected_repository_type
        semver_config = loaded_config.require_module_config(SemVerConfig).config
        assert len(semver_config.version_files) == 2
        version_file_1 = semver_config.version_files[0]
        assert version_file_1.path == selected_version_file_1["path"]
        assert version_file_1.prefix == selected_version_file_1["prefix"]
        assert version_file_1.section == selected_version_file_1["section"]
        assert version_file_1.encoding == selected_version_file_1["encoding"]
        version_file_2 = semver_config.version_files[1]
        assert version_file_2.path == selected_version_file_2["path"]
        assert version_file_2.prefix == selected_version_file_2["prefix"]
        assert version_file_2.section == selected_version_file_2["section"]
        assert version_file_2.encoding == selected_version_file_2["encoding"] or "utf-8"
        captured = capsys.readouterr()
        assert captured.out == (
            helpers.format_info(
                "Creating initial Bumpify configuration file:",
                Styled(config_file_abspath, bold=True),
            )
            + helpers.format_info("Done!")
        )

    def test_when_config_already_exists_then_init_is_terminated_with_a_warning(
        self,
        uut: UUT,
        tmpdir_config: IConfigReaderWriter,
        config: Config,
        provider: IInitCommand.IInitProvider,
        presenter: IInitCommand.IInitPresenter,
        capsys,
    ):
        tmpdir_config.save(config)
        uut.init(provider, presenter)
        captured = capsys.readouterr()
        assert captured.out == helpers.format_warning(
            "Config file already exists:", Styled(tmpdir_config.abspath(), bold=True)
        )


class TestBumpCommand:
    UUT = IBumpCommand

    @pytest.fixture
    def uut(self, injector):
        return utils.inject_type(injector, IBumpCommand)

    @pytest.fixture(autouse=True)
    def tmpdir_vcs_connector(self, tmpdir_vcs_connector: IVcsConnector, default_branch: str):
        tmpdir_vcs_connector.init()
        connection = tmpdir_vcs_connector.connect()
        connection.commit("chore: initial commit", allow_empty=True)
        connection.branch(default_branch)
        connection.checkout(default_branch)
        return tmpdir_vcs_connector

    @pytest.fixture(autouse=True)
    def verify_version_files(
        self,
        tmpdir_fs: IFileSystemReaderWriter,
        data_fs: IFileSystemReader,
        semver_config: SemVerConfig,
        expected_version_str: str,
    ):
        for vf in semver_config.version_files:
            template = data_fs.read(f"templates/dummy-project/{vf.path}.txt").decode()
            tmpdir_fs.write(vf.path, template.format(version="0.0.0").encode())
        yield
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
    ):
        yield
        for cf in semver_config.changelog_files:
            assert expected_version_str in tmpdir_fs.read(cf.path).decode()

    @pytest.fixture(autouse=True)
    def verify_bump_commit(
        self,
        tmpdir_vcs: IVcsReaderWriter,
        semver_config: SemVerConfig,
        expected_version_str,
        expected_prev_version_str,
    ):
        yield
        commits = tmpdir_vcs.list_commits()
        assert commits[-1].message == utils.format_str(
            semver_config.bump_commit_message_template,
            version_str=expected_version_str,
            prev_version_str=expected_prev_version_str,
        )

    @pytest.fixture(autouse=True)
    def verify_version_tag(
        self, tmpdir_vcs: IVcsReaderWriter, semver_config: SemVerConfig, expected_version_str
    ):
        yield
        tags = tmpdir_vcs.list_merged_tags()
        assert tags[-1].name == utils.format_str(
            semver_config.version_tag_name_template, version_str=expected_version_str
        )

    @pytest.fixture
    def bump_presenter_mock(self):
        mock = ABCMock("bump_presenter_mock", IBumpCommand.IBumpPresenter)
        with satisfied(mock):
            yield mock

    @pytest.fixture(autouse=True)
    def tmpdir_config(self, tmpdir_config: IConfigReaderWriter, config: Config):
        tmpdir_config.save(config)
        return tmpdir_config

    @pytest.mark.parametrize(
        "expected_version_str, expected_prev_version_str",
        [
            ("0.0.1", "(null)"),
        ],
    )
    def test_when_bump_invoked_for_a_first_time_then_initial_version_is_created(
        self, uut: UUT, bump_presenter_mock, expected_version_str
    ):
        bump_presenter_mock.version_bumped.expect_call(Version.from_str(expected_version_str))
        uut.bump(bump_presenter_mock)

    @pytest.mark.parametrize(
        "commit_message, expected_version_str, expected_prev_version_str",
        [
            ("fix!: a breaking fix", "1.0.0", "0.0.1"),
            ("feat: a feature", "0.1.0", "0.0.1"),
            ("fix: a fix", "0.0.2", "0.0.1"),
        ],
    )
    def test_when_bump_invoked_for_a_second_time_then_another_version_is_created(
        self,
        uut: UUT,
        tmpdir_vcs: IVcsReaderWriter,
        bump_presenter_mock,
        commit_message,
        expected_version_str,
        expected_prev_version_str,
    ):
        expected_version = Version.from_str(expected_version_str)
        expected_prev_version = Version.from_str(expected_prev_version_str)
        bump_presenter_mock.version_bumped.expect_call(expected_prev_version)
        uut.bump(bump_presenter_mock)
        tmpdir_vcs.commit(commit_message, allow_empty=True)
        bump_presenter_mock.version_bumped.expect_call(
            expected_version, prev_version=expected_prev_version
        )
        uut.bump(bump_presenter_mock)

    @pytest.mark.parametrize("verify_bump_commit", [None])
    @pytest.mark.parametrize(
        "commit_message, expected_version_str, expected_prev_version_str",
        [
            ("non conventional commit", "0.0.1", "0.0.1"),
            ("chore: no breking, feature or fix commit", "0.0.1", "0.0.1"),
        ],
    )
    def test_when_non_conventional_commit_found_then_no_version_is_updated(
        self,
        uut: UUT,
        tmpdir_vcs: IVcsReaderWriter,
        bump_presenter_mock,
        commit_message,
        expected_prev_version_str,
    ):
        expected_prev_version = Version.from_str(expected_prev_version_str)
        bump_presenter_mock.version_bumped.expect_call(expected_prev_version)
        uut.bump(bump_presenter_mock)
        tmpdir_vcs.commit(commit_message, allow_empty=True)
        bump_presenter_mock.no_changes_found.expect_call(expected_prev_version)
        uut.bump(bump_presenter_mock)
        assert tmpdir_vcs.list_commits()[-1].message == commit_message

    @pytest.mark.parametrize("verify_bump_commit", [None])
    @pytest.mark.parametrize("verify_version_tag", [None])
    @pytest.mark.parametrize("verify_changelog_files", [None])
    @pytest.mark.parametrize("expected_version_str", ["0.0.0"])
    def test_when_bump_rule_is_not_found_then_bump_is_skipped(self, uut: UUT, tmpdir_vcs: IVcsReaderWriter, bump_presenter_mock):
        tmpdir_vcs.branch("dummy-branch")
        tmpdir_vcs.checkout("dummy-branch")
        bump_presenter_mock.no_bump_rule_found.expect_call("dummy-branch")
        uut.bump(bump_presenter_mock)
