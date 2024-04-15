import colorama

from bumpify.core.notifier.objects import Styled as _Styled
from bumpify.core.console.objects import Styled


def format_styled_param(value: Styled) -> str:
    if value.bold:
        return f"{colorama.Style.BRIGHT}{value.value}{colorama.Style.NORMAL}"
    return value.obj


def format_styled_old_param(value: Styled) -> str:
    if value.bold:
        return f"{colorama.Style.BRIGHT}{value.obj}{colorama.Style.NORMAL}"
    return value.obj


def format_message_params(*params) -> str:
    out = []
    for param in params:
        if isinstance(param, str):
            out.append(param)
        elif isinstance(param, _Styled):
            out.append(format_styled_old_param(param))
        elif isinstance(param, Styled):
            out.append(format_styled_param(param))
        else:
            out.append(str(param))
    return " ".join(out)


def format_info(*params) -> str:
    return f"{colorama.Fore.CYAN}{format_message_params(*params)}{colorama.Fore.RESET}\n"


def format_warning(*params) -> str:
    return f"{colorama.Fore.MAGENTA}{format_message_params(*params)}{colorama.Fore.RESET}\n"


def format_error(*params) -> str:
    return f"{colorama.Fore.RED}{format_message_params(*params)}{colorama.Fore.RESET}\n"
