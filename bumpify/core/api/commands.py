from bumpify.core.semver.objects import SemVerConfig

from .interface import IBumpCommand


class BumpCommand(IBumpCommand):

    def __init__(self, semver_config: SemVerConfig):
        self._semver_config = semver_config

    def bump(self, presenter: IBumpCommand.IBumpPresenter):
        return super().bump(presenter)
