from typing import Any

from mockify.matchers import Matcher


class ReprEqual(Matcher):

    def __init__(self, reference: Any):
        self._reference = reference

    def __eq__(self, other):
        return repr(other) == repr(self._reference)

    def __repr__(self):
        return repr(self._reference)
