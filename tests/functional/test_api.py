import pytest
from mockify.api import ABCMock, satisfied
from pydio.api import Injector

from bumpify import utils
from bumpify.core.api.interface import IBumpCommand
from bumpify.core.config.interface import IConfigReaderWriter
from bumpify.core.config.objects import Config
from bumpify.core.semver.objects import SemVerConfig
from bumpify.providers import provider


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
