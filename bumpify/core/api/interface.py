import abc

from bumpify.core.config.objects import Config
from bumpify.core.semver.objects import Version


class IInitCommand(abc.ABC):
    """An interface for initialization command.

    Initialization command is used to create initial configuration file for a
    project.
    """

    class IInitProvider(abc.ABC):
        """Provider interface for the :meth:`IInitCommand.init` method."""

        @abc.abstractmethod
        def provide_config(self) -> Config:
            """Provide configuration object to be written to the initial
            configuration file.

            The way how the config object is created is totally implementation
            specific.
            """

    class IInitPresenter(abc.ABC):
        """Presenter interface for the :meth:`IInitCommand.init` method."""

        @abc.abstractmethod
        def notify_started(self, config_file_abspath: str):
            """Should be called shortly after command is invoked and before
            data is collected from the user.

            Can be used to display welcome message.

            :param config_file_abspath:
                Absolute path to the config file that is about to be created.
            """

        @abc.abstractmethod
        def notify_skipped(self, config_file_abspath: str):
            """Notify that initialization is skipped due to config file already
            existing.

            This informs the user that the project already is configured and
            otherwise existing config would be replaced by initial one.

            :param config_file_abspath:
                Absolute path to the existing config file that otherwise would
                be replaced.
            """

        @abc.abstractmethod
        def notify_done(self):
            """Called when config file was successfully created."""

    @abc.abstractmethod
    def init(self, provider: IInitProvider, presenter: IInitPresenter):
        """Create initial configuration file for a project.

        :param provider:
            Data provider.

        :param presenter:
            Status presenter.
        """


class IBumpCommand(abc.ABC):

    class IBumpPresenter(abc.ABC):

        @abc.abstractmethod
        def no_bump_rule_found(self, branch: str):
            pass

        @abc.abstractmethod
        def no_changes_found(self, prev_version: Version):
            pass

        @abc.abstractmethod
        def version_bumped(self, version: Version, prev_version: Version = None):
            pass

    @abc.abstractmethod
    def bump(self, presenter: IBumpPresenter):
        pass
