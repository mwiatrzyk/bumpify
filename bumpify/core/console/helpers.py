import enum
from typing import Optional, Type, Union

from .interface import IConsoleInput, IConsoleOutput
from .objects import Severity, Styled


def prompt_confirm(cin: IConsoleInput, question: Union[str, list], default: bool = None) -> bool:
    """Ask the user for confirmation.

    Return True if the user answered Yes or False if the user answered No to
    provided *question*.

    :param cin:
        Console input object.

    :param question:
        Question message.

        Can be either a string or a list of objects to be formatted as string
        (supports styling).

    :param default:
        Default value to return in case of no answer.
    """

    def parser(data: str) -> bool:
        if not data and default is not None:
            return default
        if data in true_answers:
            return True
        if data in false_answers:
            return False
        raise ValueError("wrong input")

    true_answers = {"y", "Y"}
    false_answers = {"n", "N"}
    prompt_help = "[y/N]" if default is False else "[Y/n]"
    question = [question] if isinstance(question, str) else list(question)
    question.append(Styled(prompt_help, bold=True))
    return cin.input(question, parser)


def prompt_enum(
    cin: IConsoleInput,
    prompt: Union[str, list],
    enum_type: Type[enum.Enum],
    default: enum.Enum = None,
) -> enum.Enum:

    def parser(input: str):
        if not input and default is not None:
            return default
        return enum_type(input)

    values_supported = [x.value for x in enum_type]
    values_supported_str = ", ".join(x for x in values_supported)
    prompt = [prompt] if isinstance(prompt, str) else list(prompt)
    prompt.append(Styled(f"[{values_supported_str}]", bold=True))
    if default is not None:
        prompt.append(Styled(f"(default: {default.value})", bold=True))
    return cin.input(prompt, parser)


def prompt_string(
    cin: IConsoleInput, prompt: Union[str, list], optional: bool = False, default: str = None
) -> Optional[str]:

    def parser(input: str):
        if not input and optional:
            return None
        if not input and default is not None:
            return default
        if input:
            return input
        raise ValueError("a value is required")

    prompt = [prompt] if isinstance(prompt, str) else list(prompt)
    if optional:
        prompt.append(Styled("[leave empty to skip]", bold=True))
    if default:
        prompt.append(Styled(f"(default: {default})", bold=True))
    return cin.input(prompt, parser)


def print_exception(cout: IConsoleOutput, e: Exception):
    """Emit exception to the console.

    :param cout:
        Console output object.

    :param e:
        Exception object.
    """
    cout.emit(
        Severity.ERROR, Styled(f"{e.__module__}.{e.__class__.__qualname__}:", bold=True), str(e)
    )


def print_error(cout: IConsoleOutput, *values):
    cout.emit(Severity.ERROR, *values)
