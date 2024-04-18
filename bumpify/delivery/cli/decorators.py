import functools
import sys

from pydio.base import IInjector

from bumpify import exc, utils
from bumpify.core.console import helpers as console_helpers
from bumpify.core.console.interface import IConsoleOutput
from bumpify.core.console.objects import Severity, Styled


def catch_errors(func):

    @functools.wraps(func)
    def proxy(injector: IInjector, *args, **kwargs):
        cout = utils.inject_type(injector, IConsoleOutput)
        try:
            func(injector, *args, **kwargs)
        except exc.BumpifyError as e:
            console_helpers.print_exception(cout, e)
            sys.exit(1)
        else:
            if cout.count_by_severity(Severity.ERROR):
                sys.exit(1)

    return proxy
