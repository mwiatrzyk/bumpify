import os

import colorama
import pytest
from mockify.api import ABCMock, satisfied

from bumpify.core.config.implementation import ConfigReaderWriter
from bumpify.core.config.interface import IConfigReaderWriter
from bumpify.core.config.objects import Config, LoadedConfig, LoadedSection
from bumpify.core.console.interface import IConsoleOutput
from bumpify.core.filesystem.implementation import FileSystemReaderWriter
from bumpify.core.filesystem.interface import IFileSystemReaderWriter
from bumpify.core.hook.implementation import AlwaysDefaultHookApiLoader
from bumpify.core.semver.objects import SemVerConfig
from bumpify.core.vcs.implementation.git import GitVcsConnector
from bumpify.core.vcs.interface import IVcsConnector, IVcsReaderWriter
from bumpify.core.vcs.objects import VCSConfig

colorama.init()


@pytest.fixture
def filesystem_reader_writer_mock():
    mock = ABCMock("filesystem_reader_writer_mock", IFileSystemReaderWriter)
    with satisfied(mock):
        yield mock


@pytest.fixture
def console_output_mock():
    mock = ABCMock("console_output_mock", IConsoleOutput)
    with satisfied(mock):
        yield mock


@pytest.fixture
def vcs_reader_writer_mock():
    mock = ABCMock("vcs_reader_writer_mock", IVcsReaderWriter)
    with satisfied(mock):
        yield mock


@pytest.fixture
def config_reader_writer_mock():
    mock = ABCMock("config_reader_writer_mock", IConfigReaderWriter)
    with satisfied(mock):
        yield mock


@pytest.fixture
def hook_api_stub():
    return AlwaysDefaultHookApiLoader().load()


@pytest.fixture
def default_branch():
    return "production"


@pytest.fixture
def vcs_type():
    return VCSConfig.Type.GIT


@pytest.fixture
def vcs_config(vcs_type):
    return VCSConfig(type=vcs_type)


@pytest.fixture
def semver_config(default_branch):
    return SemVerConfig(
        version_files=[
            SemVerConfig.VersionFile(
                path="pyproject.toml", prefix="version", section="[tool.poetry]"
            )
        ],
        changelog_files=[
            SemVerConfig.ChangelogFile(path="CHANGELOG.md"),
        ],
        bump_rules=[SemVerConfig.BumpRule(branch=f"^{default_branch}$")],
    )


@pytest.fixture
def loaded_semver_config(semver_config, config_file_abspath):
    return LoadedSection(config_file_abspath, semver_config)


@pytest.fixture
def config(semver_config, vcs_config):
    config = Config()
    config.save_section(vcs_config)
    config.save_section(semver_config)
    return config


@pytest.fixture
def loaded_config(config_file_abspath, config):
    return LoadedConfig(config_file_abspath=config_file_abspath, config=config)


@pytest.fixture
def config_file_path():
    return ".bumpify.toml"


@pytest.fixture
def config_file_abspath(tmpdir_fs: IFileSystemReaderWriter, config_file_path):
    return tmpdir_fs.abspath(config_file_path)


@pytest.fixture
def tmpdir_fs(tmpdir):
    return FileSystemReaderWriter(tmpdir)


@pytest.fixture
def tmpdir_config(tmpdir_fs, config_file_path):
    return ConfigReaderWriter(tmpdir_fs, config_file_path)


@pytest.fixture
def tmpdir_vcs_connector(tmpdir_fs):
    return GitVcsConnector(tmpdir_fs)


@pytest.fixture
def tmpdir_vcs(tmpdir_vcs_connector: IVcsConnector):
    return tmpdir_vcs_connector.connect()


@pytest.fixture
def data_fs():
    tests_dir = os.path.abspath(os.path.dirname(__file__))
    return FileSystemReaderWriter(os.path.join(tests_dir, "data"))
