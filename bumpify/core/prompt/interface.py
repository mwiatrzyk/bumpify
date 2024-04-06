import abc
from enum import Enum
from typing import Any, List, Optional, Type


class IPrompt(abc.ABC):

    @abc.abstractmethod
    def enum(self, text: str, enum_type: Type[Enum]) -> Enum:
        pass

    @abc.abstractmethod
    def confirm(self, question: str) -> bool:
        pass

    @abc.abstractmethod
    def path(self, text: str) -> str:
        pass

    @abc.abstractmethod
    def string(self, text: str, default: str = None, optional: bool = False) -> Optional[str]:
        pass
