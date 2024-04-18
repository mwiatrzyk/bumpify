import abc


class IBumpifyCliApp(abc.ABC):

    @abc.abstractmethod
    def __call__(self, version: bool=False) -> str:
        pass

    @abc.abstractmethod
    def init(self, input: str = None) -> str:
        pass

    @abc.abstractmethod
    def bump(self) -> str:
        pass
