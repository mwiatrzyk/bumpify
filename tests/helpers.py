import colorama

from bumpify.core.console.objects import Styled


def format_styled_param(value: Styled) -> str:
    if value.bold:
        return f"{colorama.Style.BRIGHT}{value.value}{colorama.Style.NORMAL}"
    return value.value


def format_message_params(*params) -> str:
    out = []
    for param in params:
        if isinstance(param, str):
            out.append(param)
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


def format_exception(e: Exception) -> str:
    return format_error(Styled(f"{e.__module__}.{e.__class__.__qualname__}:", bold=True), str(e))


def format_prompt(*params) -> str:
    return f"{colorama.Fore.CYAN}{format_message_params(*params)}{colorama.Fore.RESET}: "
