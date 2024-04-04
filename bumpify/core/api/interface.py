import abc


class IBumpCommand(abc.ABC):

    class IBumpPresenter(abc.ABC):
        pass

    @abc.abstractmethod
    def bump(self, presenter: IBumpPresenter):
        pass
