import pytest
from mockify.api import ABCMock, satisfied

from bumpify.core.config.objects import Config, LoadedConfig, VCSConfig
from bumpify.core.filesystem.implementation import FileSystemReaderWriter
from bumpify.core.filesystem.interface import IFileSystemReaderWriter
from bumpify.core.semver.objects import SemVerConfig
from bumpify.core.status.interface import IStatusListener
from bumpify.core.vcs.interface import IVcsReaderWriter


@pytest.fixture
def filesystem_reader_writer_mock():
    mock = ABCMock("filesystem_reader_writer_mock", IFileSystemReaderWriter)
    with satisfied(mock):
        yield mock


@pytest.fixture
def status_listener_mock():
    mock = ABCMock("status_listener_mock", IStatusListener)
    with satisfied(mock):
        yield mock


@pytest.fixture
def vcs_reader_writer_mock():
    mock = ABCMock("vcs_reader_writer_mock", IVcsReaderWriter)
    with satisfied(mock):
        yield mock


@pytest.fixture
def config():
    return Config(vcs=VCSConfig(type=VCSConfig.Type.GIT))


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
def semver_config():
    return SemVerConfig(
        version_files=[
            SemVerConfig.VersionFile(
                path="pyproject.toml", prefix="version", section="[tool.poetry]"
            )
        ],
        changelog_files=[
            SemVerConfig.ChangelogFile(path="CHANGELOG.md"),
        ],
    )
