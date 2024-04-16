from bumpify.core.console.interface import IConsoleOutput
from bumpify.core.console.objects import Severity, Styled
from bumpify.core.vcs.helpers import make_dummy_rev
from bumpify.core.vcs.interface import IVcsReaderWriter, IVcsWriter


class DryRunVcsReaderWriterProxy(IVcsWriter):

    def __init__(self, target: IVcsReaderWriter, cout: IConsoleOutput):
        self._target = target
        self._cout = cout

    def __getattr__(self, name):
        return getattr(self._target, name)

    def add(self, *paths: str):
        add = Styled("add", bold=True)
        for path in paths:
            self._cout.emit(
                Severity.INFO,
                "Would",
                add,
                "following file to the next commit:",
                Styled(path, bold=True),
            )

    def branch(self, name: str):
        create = Styled("create", bold=True)
        name = Styled(name, bold=True)
        head_rev = Styled(self._target.find_head_rev(), bold=True)
        self._cout.emit(Severity.INFO, "Would", create, "a branch named", name, "at", head_rev)

    def checkout(self, rev_or_name: str):
        checkout = Styled("checkout", bold=True)
        rev_or_name = Styled(rev_or_name, bold=True)
        self._cout.emit(Severity.INFO, "Would", checkout, "HEAD at", rev_or_name)

    def commit(self, message: str, allow_empty: bool = False) -> str:
        result = make_dummy_rev(message)
        commit = Styled("commit", bold=True)
        message = Styled(message, bold=True)
        result_styled = Styled(result, bold=True)
        self._cout.emit(
            Severity.INFO,
            "Would create a",
            commit,
            "with message",
            message,
            "and return",
            result_styled,
        )
        return result

    def tag(self, rev: str, name: str):
        tag = Styled("tag", bold=True)
        rev = Styled(rev, bold=True)
        name = Styled(name, bold=True)
        self._cout.emit(Severity.INFO, "Would create a", tag, "named", name, "at", rev)
