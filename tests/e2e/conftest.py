from typing import Any, Optional

import pytest

from bumpify import utils
from bumpify.core.vcs.objects import VCSConfig
from tests.e2e.interface import IBumpifyCliApp


class SUT(IBumpifyCliApp):

    def __init__(
        self,
        project_root_dir: str,
        config_file_path: str = None,
        config_file_encoding: str = "utf-8",
        dry_run: bool = False,
    ):
        self._project_root_dir = project_root_dir
        self._config_file_path = config_file_path
        self._config_file_encoding = config_file_encoding
        self._dry_run = dry_run

    def _run(self, *args, input: str = None) -> str:
        with utils.cwd(self._project_root_dir):
            return utils.shell_exec(
                "bumpify",
                f"--config-file-path={self._config_file_path}" if self._config_file_path else None,
                (
                    f"--config-file-encoding={self._config_file_encoding}"
                    if self._config_file_encoding
                    else None
                ),
                "--dry-run" if self._dry_run else None,
                *args,
                input=input.encode() if input else None,
                fail_on_stderr=True,
            ).decode()

    def __call__(self, version: bool = False) -> str:
        return self._run("--version" if version else None)

    def init(self, input: str = None) -> str:
        return self._run("init", input=input)

    def bump(self) -> str:
        return self._run("bump")


@pytest.fixture
def dry_run():
    return None


@pytest.fixture(params=[None, "ascii"])
def config_file_encoding(request: pytest.FixtureRequest):
    return request.param


@pytest.fixture(params=[".bumpify/config.toml"])
def config_file_path(request: pytest.FixtureRequest):
    return request.param


@pytest.fixture(
    params=[
        VCSConfig.Type.AUTO,
        VCSConfig.Type.GIT,
    ]
)
def vcs_type(request: pytest.FixtureRequest):
    return request.param


@pytest.fixture
def sut(tmpdir, config_file_path, config_file_encoding, dry_run):
    return SUT(
        tmpdir,
        config_file_path=config_file_path,
        config_file_encoding=config_file_encoding,
        dry_run=dry_run,
    )
