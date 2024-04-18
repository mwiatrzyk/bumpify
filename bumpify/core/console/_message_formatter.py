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
    out = styled.value
    if styled.bold:
        out = f"{colorama.Style.BRIGHT}{out}{colorama.Style.NORMAL}"
    if styled.fg:
        out = f"{getattr(colorama.Fore, styled.fg.upper(), colorama.Fore.RESET)}{out}{colorama.Fore.RESET}"
    return out
