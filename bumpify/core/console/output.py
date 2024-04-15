import colorama

from .interface import IConsoleOutput
from .objects import Severity, Styled


class StdoutConsoleOutput(IConsoleOutput):

    def _find_fore_color_for_severity(self, severity: Severity) -> str:
        if severity == Severity.DEBUG:
            return colorama.Fore.BLUE
        if severity == Severity.INFO:
            return colorama.Fore.CYAN
        if severity == Severity.WARNING:
            return colorama.Fore.MAGENTA
        return colorama.Fore.RED

    def _format_message(self, *args) -> str:
        parts = []
        for arg in args:
            if isinstance(arg, str):
                parts.append(arg)
            elif isinstance(arg, Styled):
                parts.append(self._format_styled(arg))
            else:
                parts.append(str(arg))
        return " ".join(parts)

    def _format_styled(self, styled: Styled) -> str:
        if styled.bold:
            return f"{colorama.Style.BRIGHT}{styled.value}{colorama.Style.NORMAL}"
        return str(styled.obj)

    def emit(self, severity: Severity, *args):
        fore = self._find_fore_color_for_severity(severity)
        message = self._format_message(*args)
        print(f"{fore}{message}{colorama.Fore.RESET}")
