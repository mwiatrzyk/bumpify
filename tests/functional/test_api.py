import click
import pytest
from mockify.api import ABCMock, Mock, Return, ordered, patched, satisfied
from mockify.matchers import Type
from pydio.api import Injector

from bumpify import utils
from bumpify.core.api.interface import IBumpCommand, IInitCommand
from bumpify.core.config.interface import IConfigReaderWriter
from bumpify.core.config.objects import Config
from bumpify.core.notifier.objects import Styled
from bumpify.core.semver.objects import SemVerConfig
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
        optional_default = "leave empty to skip"
        click_mock.prompt.expect_call(
            "Choose project's repository type", type=ReprEqual(click.Choice(["git"]))
        ).will_once(Return(selected_repository_type))
        click_mock.confirm.expect_call("Create semantic versioning configuration?").will_once(
            Return(True)
        )
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

    @pytest.fixture
    def bump_presenter_mock(self):
        mock = ABCMock("bump_presenter_mock", IBumpCommand.IBumpPresenter)
        with satisfied(mock):
            yield mock

    @pytest.fixture(autouse=True)
    def tmpdir_config(self, tmpdir_config: IConfigReaderWriter, config: Config):
        tmpdir_config.save(config)
        return tmpdir_config

    def test_when_bump_invoked_for_a_first_time_then_initial_version_is_created(
        self, uut: UUT, bump_presenter_mock
    ):
        uut.bump(bump_presenter_mock)
