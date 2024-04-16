from bumpify.core.console.interface import IConsoleOutput
from bumpify.core.console.objects import Severity, Styled
from bumpify.core.semver.objects import Version

from .interface import IBumpCommand, IInitCommand


class InitPresenter(IInitCommand.IInitPresenter):

    def __init__(self, cout: IConsoleOutput):
        self._cout = cout

    def notify_skipped(self, config_file_abspath: str):
        self._cout.emit(
            Severity.WARNING, "Config file already exists:", Styled(config_file_abspath, bold=True)
        )

    def notify_started(self, config_file_abspath: str):
        self._cout.emit(
            Severity.INFO,
            "Creating initial Bumpify configuration file:",
            Styled(config_file_abspath, bold=True),
        )

    def notify_done(self):
        self._cout.emit(Severity.INFO, "Done!")


class BumpCommandPresenter(IBumpCommand.IBumpPresenter):

    def __init__(self, cout: IConsoleOutput):
        self._cout = cout

    def no_bump_rule_found(self, branch: str):
        self._cout.emit(Severity.ERROR, "No bump rule found for branch:", Styled(branch, bold=True))

    def no_changes_found(self, prev_version: Version):
        self._cout.emit(
            Severity.WARNING,
            "No changes found between version",
            Styled(prev_version.to_str(), bold=True),
            "and current",
            Styled("HEAD", bold=True),
        )

    def version_bumped(self, version: Version, prev_version: Version = None):
        self._cout.emit(
            Severity.INFO,
            "Version was bumped:",
            Styled("(null)" if prev_version is None else prev_version.to_str(), bold=True),
            "->",
            Styled(version.to_str(), bold=True),
        )
