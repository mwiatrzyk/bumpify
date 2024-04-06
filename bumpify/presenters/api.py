from bumpify.core.api.interface import IInitCommand
from bumpify.core.notifier.interface import INotifier
from bumpify.core.notifier.objects import Styled


class InitPresenter(IInitCommand.IInitPresenter):

    def __init__(self, status_listener: INotifier):
        self._status_listener = status_listener

    def notify_skipped(self, config_file_abspath: str):
        self._status_listener.warning(
            "Config file already exists:", Styled(config_file_abspath, bold=True)
        )

    def notify_started(self, config_file_abspath: str):
        self._status_listener.info(
            "Creating initial Bumpify configuration file:", Styled(config_file_abspath, bold=True)
        )

    def notify_done(self):
        self._status_listener.info("Done!")
