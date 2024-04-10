import pytest

from bumpify import utils
from bumpify.core.filesystem.interface import IFileSystemReaderWriter
from bumpify.core.semver.objects import SemVerConfig


class SUT:

    def __init__(self, project_root_dir: str):
        self._project_root_dir = project_root_dir

    def init(self, input: str = None, config_file_path: str = None) -> str:
        with utils.cwd(self._project_root_dir):
            return utils.shell_exec(
                "bumpify",
                f"--config-file-path={config_file_path}" if config_file_path else None,
                "init",
                input=input.encode() if input else None,
                fail_on_stderr=True,
            ).decode()


@pytest.fixture
def sut(tmpdir):
    return SUT(tmpdir)


@pytest.fixture()
def selected_repository_type():
    return "git"


@pytest.fixture
def selected_version_file():
    return SemVerConfig.VersionFile(path="dummy/__init__.py", prefix="__version__")


def test_create_initial_config_file_at_default_location(
    sut: SUT,
    tmpdir_fs: IFileSystemReaderWriter,
    selected_repository_type,
    selected_version_file: SemVerConfig.VersionFile,
):
    input = (
        f"{selected_repository_type}\n"
        "y\n"  # Create semantic versioning configuration
        "prod\n"  # Bump rule #1 branch name
        "\n\n\n"  # major, minor, patch - leave the defaults
        "\n"  # Don't use prerelease
        "n\n"  # Don't add more rules
        f"{selected_version_file.path}\n"  # Path to first version file
        f"{selected_version_file.prefix}\n"
        "\n"  # Skip version file section
        "\n"  # Use default encoding
        "n\n"  # Do not add more version files
    )
    stdout = sut.init(input)
    assert "Done!" in stdout
    assert tmpdir_fs.exists(".bumpify.toml")


def test_create_initial_config_file_at_provided_location(
    sut: SUT,
    tmpdir_fs: IFileSystemReaderWriter,
    selected_repository_type,
    selected_version_file: SemVerConfig.VersionFile,
):
    input = (
        f"{selected_repository_type}\n"
        "y\n"  # Create semantic versioning configuration
        "prod\n"  # Bump rule #1 branch name
        "\n\n\n"  # major, minor, patch - leave the defaults
        "\n"  # Don't use prerelease
        "n\n"  # Don't add more rules
        f"{selected_version_file.path}\n"  # Path to first version file
        f"{selected_version_file.prefix}\n"
        "\n"  # Skip version file section
        "\n"  # Use default encoding
        "n\n"  # Do not add more version files
    )
    stdout = sut.init(input, config_file_path=".bumpify/config.toml")
    assert "Done!" in stdout
    assert tmpdir_fs.exists(".bumpify/config.toml")


def test_when_file_already_exists_then_init_ends_with_warning(
    sut: SUT, tmpdir_fs: IFileSystemReaderWriter
):
    tmpdir_fs.write(".bumpify.toml", b"")
    stdout = sut.init("")
    assert "Config file already exists" in stdout
