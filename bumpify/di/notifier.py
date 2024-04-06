from pydio.api import Provider

from bumpify.core.notifier.implementation import StdoutNotifier
from bumpify.core.notifier.interface import INotifier

provider = Provider()


@provider.provides(INotifier)
def make_notifier():
    notifier = StdoutNotifier()
    yield notifier
