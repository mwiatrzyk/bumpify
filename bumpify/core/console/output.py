from .interface import IConsoleOutput


class BufferedConsoleOutput(IConsoleOutput):

    def __init__(self, buffer: list):
        self._buffer = buffer

    def _emit(self, *values, level: str):
        self._buffer.append((level, *values))

    def debug(self, *values):
        self._emit(*values, level="debug")

    def info(self, *values):
        self._emit(*values, level="info")

    def warning(self, *values):
        self._emit(*values, level="warning")

    def error(self, *values):
        self._emit(*values, level="error")
