from enum import Enum
from typing import Optional, Type

import click

from .interface import IPrompt

# FIXME: Workaround, as click does not allow to exit from prompt loop if
# default is not provided and it seems not possible to add any flag for
# optionals that does not have default value; create a ticket with feature
# proposal.
_LEAVE_EMPTY_TO_SKIP = "leave empty to skip"


class ClickPrompt(IPrompt):

    def enum(self, text: str, enum_type: Type[Enum]) -> Enum:
        available_values = [x.value for x in enum_type]
        value = click.prompt(text, type=click.Choice(available_values))
        return enum_type(value)

    def confirm(self, question: str) -> bool:
        return click.confirm(question)

    def path(self, text: str) -> str:
        return click.prompt(text, type=click.Path())

    def string(self, text: str, default: str = None, optional: bool = False) -> Optional[str]:
        if default is None and optional:
            default = _LEAVE_EMPTY_TO_SKIP
        value = click.prompt(text, type=str, default=default)
        if value == _LEAVE_EMPTY_TO_SKIP and optional:
            return None
        return value
