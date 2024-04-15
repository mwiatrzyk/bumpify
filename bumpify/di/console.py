from pydio.api import Provider

from bumpify.core.console.interface import IConsoleOutput
from bumpify.core.console.output import StdoutConsoleOutput

provider = Provider()


@provider.provides(IConsoleOutput)
def make_console_output():
    return StdoutConsoleOutput()
