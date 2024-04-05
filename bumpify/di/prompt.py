from pydio.api import Provider

from bumpify.core.prompt.implementation import ClickPrompt
from bumpify.core.prompt.interface import IPrompt

provider = Provider()


@provider.provides(IPrompt)
def make_prompt():
    return ClickPrompt()
