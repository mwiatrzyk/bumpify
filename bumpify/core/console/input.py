from typing import Any, Callable

import click
import colorama

from . import _message_formatter
from .interface import IConsoleInput


class StdinConsoleInput(IConsoleInput):

    def input(self, prompt: list, parse_func: Callable[[str], Any]) -> Any:
        formatted_prompt = _message_formatter.format_message(prompt)
        formatted_prompt = f"{colorama.Fore.CYAN}{formatted_prompt}{colorama.Fore.RESET}"
        while True:
            data = input(formatted_prompt + ": ")
            try:
                return parse_func(data.strip())
            except ValueError as e:
                print(f"{colorama.Fore.RED}Error: {e}{colorama.Fore.RESET}")
