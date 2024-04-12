from pydio.api import Provider, Variant

from bumpify import utils
from bumpify.core.console.interface import IConsoleOutput
from bumpify.core.console.output import BufferedConsoleOutput

provider = Provider()


@provider.provides(Variant(list, what="console-buffer"), env="testing")
def make_console_buffer():
    return []


@provider.provides(IConsoleOutput, env="testing")
def make_console_output(injector):
    console_buffer = utils.inject_variant(injector, list, what="console-buffer")
    return BufferedConsoleOutput(console_buffer)
