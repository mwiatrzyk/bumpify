import abc

from bumpify.core.config.objects import Config


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
        def config_file_created(self, config_file_abspath: str):
            """Called when config file was successfully created.

            :param config_file_abspath:
                Absolute path to created config file.
            """

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
        pass

    @abc.abstractmethod
    def bump(self, presenter: IBumpPresenter):
        pass
