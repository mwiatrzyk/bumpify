from typing import TextIO

import colorama

from .interface import INotifier
from .objects import Styled


class StdoutNotifier(INotifier):

    def _format(self, *values) -> str:
        parts = []
        for v in values:
            if isinstance(v, str):
                parts.append(v)
            elif isinstance(v, Styled):
                parts.append(self._format_styled(v))
            else:
                parts.append(str(v))
        return " ".join(parts)

    def _format_styled(self, styled: Styled) -> str:
        if styled.bold:
            return f"{colorama.Style.BRIGHT}{styled.obj}{colorama.Style.NORMAL}"
        return str(styled.obj)

    def _message(self, *values, fg=None):
        formatted = self._format(*values)
        print(f"{fg}{formatted}{colorama.Fore.RESET}")

    def debug(self, *values):
        return super().debug(*values)

    def info(self, *values):
        self._message(*values, fg=colorama.Fore.CYAN)

    def warning(self, *values):
        self._message(*values, fg=colorama.Fore.MAGENTA)

    def error(self, *values):
        return super().error(*values)
