import abc


class IBumpifyCliApp(abc.ABC):

    @abc.abstractmethod
    def init(self, input: str = None) -> str:
        pass

    @abc.abstractmethod
    def bump(self) -> str:
        pass
