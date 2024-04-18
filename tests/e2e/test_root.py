from bumpify import __version__

from .interface import IBumpifyCliApp

SUT = IBumpifyCliApp


def test_when_called_with_version_option_then_version_is_displayed(sut: SUT):
    stdout = sut("--version")
    assert stdout == f"bumpify, version {__version__}"
