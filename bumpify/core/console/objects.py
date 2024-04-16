import dataclasses
import enum
from typing import Any, Optional


class Severity(enum.Enum):
    """Severity used for events emitted to the console."""

    DEBUG = -1
    INFO = 0  # The default value
    WARNING = 1
    ERROR = 2


@dataclasses.dataclass
class Styled:
    """Annotates value with style.

    Thanks to this, real console styles can be applied later, making it easier
    to test when styles are applied. This is meant to be used with
    :class:`IConsoleOutput` interface.
    """

    #: The value to add style for.
    value: Any

    #: Render using bold (True) or normal (False) font.
    bold: bool = False

    #: Set foreground color for a value.
    fg: Optional[str] = None
