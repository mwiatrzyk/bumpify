import click
import pytest
from mockify.api import ABCMock, satisfied, patched, Mock, Return, ordered
from mockify.matchers import Type
from pydio.api import Injector

from bumpify import utils
from bumpify.core.api.interface import IBumpCommand, IInitCommand
from bumpify.core.config.interface import IConfigReaderWriter
from bumpify.core.config.objects import Config
from bumpify.core.semver.objects import SemVerConfig
from bumpify.di import provider

from tests.matchers import ReprEqual


@pytest.fixture
def injector(tmpdir, config_file_path):
    injector = Injector(provider)
    context = utils.inject_context(injector)
    context.project_root_dir = tmpdir
    context.config_file_path = config_file_path
    return injector


@pytest.fixture(autouse=True)
def configure(tmpdir_config: IConfigReaderWriter, config: Config, semver_config: SemVerConfig):
    config.save_module_config(semver_config)
    return tmpdir_config.save(config)


class TestInitCommand:
    UUT = IInitCommand
    Provider = IInitCommand.IInitProvider
    Presenter = IInitCommand.IInitPresenter

    @pytest.fixture
    def uut(self, injector):
        return utils.inject_type(injector, IInitCommand)

    @pytest.fixture
    def provider(self, injector):
        return utils.inject_type(injector, IInitCommand.IInitProvider)

    @pytest.fixture
    def presenter(self, injector):
        return utils.inject_type(injector, IInitCommand.IInitPresenter)

    def test_when_init_command_invoked_then_initial_config_is_created(self, uut: UUT, provider: Provider, presenter: Presenter):
        mock = Mock("click")
        mock.prompt.expect_call("Choose project's repository type", type=ReprEqual(click.Choice(['git']))).will_once(Return("git"))
        mock.confirm.expect_call("Create semantic versioning configuration?").will_once(Return(True))
        mock.prompt.expect_call("Version file #1 path", type=Type(click.Path)).will_once(Return('pyproject.toml'))
        mock.prompt.expect_call("Version file #1 prefix", default="leave empty to skip", type=str).will_once(Return('version'))
        mock.prompt.expect_call("Version file #1 section", default="leave empty to skip", type=str).will_once(Return('leave empty to skip'))
        mock.prompt.expect_call("Version file #1 encoding", default="utf-8", type=str).will_once(Return('utf-8'))
        mock.confirm.expect_call("Add another version file?").will_once(Return(False))
        with satisfied(mock), ordered(mock):
            with patched(mock):
                uut.init(provider, presenter)


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

    def test_when_bump_invoked_for_a_first_time_then_initial_version_is_created(
        self, uut: UUT, bump_presenter_mock
    ):
        uut.bump(bump_presenter_mock)
