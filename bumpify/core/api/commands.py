from bumpify.core.config.interface import IConfigReaderWriter
from bumpify.core.config.objects import LoadedModuleConfig
from bumpify.core.semver.objects import SemVerConfig

from .interface import IBumpCommand, IInitCommand


class InitCommand(IInitCommand):

    def __init__(self, config_reader_writer: IConfigReaderWriter):
        self._config_reader_writer = config_reader_writer

    def init(self, provider: IInitCommand.IInitProvider, presenter: IInitCommand.IInitPresenter):
        config_file_abspath = self._config_reader_writer.abspath()
        if self._config_reader_writer.exists():
            presenter.notify_skipped(config_file_abspath)
            return
        presenter.notify_started(config_file_abspath)
        config = provider.provide_config()
        self._config_reader_writer.save(config)
        presenter.notify_done()


class BumpCommand(IBumpCommand):

    def __init__(self, semver_config: LoadedModuleConfig[SemVerConfig]):
        self._semver_config = semver_config

    def bump(self, presenter: IBumpCommand.IBumpPresenter):
        return super().bump(presenter)
