from typing import Any, Optional

import pytest

from bumpify import utils
from tests.e2e.interface import IBumpifyCliApp


class SUT(IBumpifyCliApp):

    def __init__(
        self,
        project_root_dir: str,
        config_file_path: str = None,
        config_file_encoding: str = "utf-8",
    ):
        self._project_root_dir = project_root_dir
        self._config_file_path = config_file_path
        self._config_file_encoding = config_file_encoding

    @staticmethod
    def _format_option(option_name: str, option_value: Any) -> Optional[str]:
        return f"{option_name}={option_value}" if option_value else None

    def init(self, input: str = None) -> str:
        with utils.cwd(self._project_root_dir):
            return utils.shell_exec(
                "bumpify",
                self._format_option("--config-file-path", self._config_file_path),
                self._format_option("--config-file-encoding", self._config_file_encoding),
                "init",
                input=input.encode() if input else None,
                fail_on_stderr=True,
            ).decode()

    def bump(self) -> str:
        with utils.cwd(self._project_root_dir):
            return utils.shell_exec(
                "bumpify",
                self._format_option("--config-file-path", self._config_file_path),
                self._format_option("--config-file-encoding", self._config_file_encoding),
                "bump",
                fail_on_stderr=True,
            ).decode()


@pytest.fixture(params=[None, "ascii"])
def config_file_encoding(request: pytest.FixtureRequest):
    return request.param


@pytest.fixture(params=[".bumpify/config.toml"])
def config_file_path(request: pytest.FixtureRequest):
    return request.param


@pytest.fixture
def sut(tmpdir, config_file_path, config_file_encoding):
    return SUT(tmpdir, config_file_path, config_file_encoding=config_file_encoding)
