from pydio.api import Provider

from bumpify.core.console.input import StdinConsoleInput
from bumpify.core.console.interface import IConsoleInput, IConsoleOutput
from bumpify.core.console.objects import Severity
from bumpify.core.console.output import StdoutConsoleOutput

provider = Provider()


@provider.provides(IConsoleOutput)
def make_console_output():
    return StdoutConsoleOutput()


@provider.provides(IConsoleInput)
def make_console_input():
    return StdinConsoleInput()
