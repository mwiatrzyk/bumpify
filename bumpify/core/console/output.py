import colorama

from . import _message_formatter
from .interface import IConsoleOutput
from .objects import Severity


class StdoutConsoleOutput(IConsoleOutput):

    def __init__(self):
        self._severity_counter = {}

    def _find_fore_color_for_severity(self, severity: Severity) -> str:
        if severity == Severity.DEBUG:
            return colorama.Fore.BLUE
        if severity == Severity.INFO:
            return colorama.Fore.CYAN
        if severity == Severity.WARNING:
            return colorama.Fore.MAGENTA
        return colorama.Fore.RED

    def count_by_severity(self, severity: Severity) -> int:
        return self._severity_counter.get(severity, 0)

    def emit(self, severity: Severity, *args):
        self._severity_counter.setdefault(severity, 0)
        self._severity_counter[severity] += 1
        fore = self._find_fore_color_for_severity(severity)
        message = _message_formatter.format_message(args)
        print(f"{fore}{message}{colorama.Fore.RESET}")
