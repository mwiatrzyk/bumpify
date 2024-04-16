from typing import Union

import colorama

from .objects import Styled


def format_message(message: Union[str, list]) -> str:
    out = []
    message = [message] if isinstance(message, str) else message
    for item in message:
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, Styled):
            out.append(format_styled(item))
        else:
            out.append(str(item))
    return " ".join(out)


def format_styled(styled: Styled) -> str:
    if styled.bold:
        return f"{colorama.Style.BRIGHT}{styled.value}{colorama.Style.NORMAL}"
    return str(styled.value)
