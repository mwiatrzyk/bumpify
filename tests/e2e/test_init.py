import pytest

from bumpify.core.console.objects import Styled
from bumpify.core.filesystem.interface import IFileSystemReaderWriter
from bumpify.core.semver.objects import SemVerConfig
from tests import helpers
from tests.e2e.interface import IBumpifyCliApp

SUT = IBumpifyCliApp


@pytest.fixture()
def selected_repository_type():
    return "git"


@pytest.fixture
def selected_version_file():
    return SemVerConfig.VersionFile(path="dummy/__init__.py", prefix="__version__")


@pytest.mark.parametrize("config_file_path", [None])
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
    config_file_path: str,
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
    assert tmpdir_fs.exists(config_file_path)


def test_when_file_already_exists_then_init_ends_with_warning(
    sut: SUT, tmpdir_fs: IFileSystemReaderWriter, config_file_path: str
):
    tmpdir_fs.write(config_file_path, b"")
    stdout = sut.init()
    assert "Config file already exists" in stdout


@pytest.mark.parametrize("dry_run", [True])
def test_when_command_called_with_dry_run_then_no_config_is_created(
    sut: SUT, selected_repository_type, selected_version_file, config_file_path
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
    assert (
        helpers.format_message_params(
            "Would", Styled("create", bold=True), "file at", Styled(config_file_path, bold=True)
        )
        in stdout
    )
    assert "Done!" in stdout
