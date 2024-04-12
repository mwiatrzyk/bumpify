from bumpify.core.console.interface import IConsoleOutput
from bumpify.core.console.objects import Styled
from bumpify.core.notifier.interface import INotifier
from bumpify.core.notifier.objects import Styled as _Styled  # TODO: Replace with the one from above; I want to make single common module for console-related stuff
from bumpify.core.semver.objects import Version

from .interface import IBumpCommand, IInitCommand


class InitPresenter(IInitCommand.IInitPresenter):

    def __init__(self, status_listener: INotifier):
        self._status_listener = status_listener

    def notify_skipped(self, config_file_abspath: str):
        self._status_listener.warning(
            "Config file already exists:", _Styled(config_file_abspath, bold=True)
        )

    def notify_started(self, config_file_abspath: str):
        self._status_listener.info(
            "Creating initial Bumpify configuration file:", _Styled(config_file_abspath, bold=True)
        )

    def notify_done(self):
        self._status_listener.info("Done!")


class BumpCommandPresenter(IBumpCommand.IBumpPresenter):

    def __init__(self, cout: IConsoleOutput):
        self._cout = cout

    def no_bump_rule_found(self, branch: str):
        self._cout.warning("No bump rule found for branch:", Styled(branch, bold=True))

    def no_changes_found(self, prev_version: Version):
        self._cout.warning("No changes found between version", Styled(prev_version.to_str(), bold=True), "and current", Styled("HEAD", bold=True))

    def version_bumped(self, version: Version, prev_version: Version = None):
        self._cout.info(
            "Version was bumped:",
            Styled("(null)" if prev_version is None else prev_version.to_str(), bold=True),
            "->",
            Styled(version.to_str(), bold=True)
        )
