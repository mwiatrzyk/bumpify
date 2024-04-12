import dataclasses
from typing import Any, Optional


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

    #: Render using underlined (True) or normal (False) font.
    underline: bool = False

    #: Set foreground color for a value.
    fore: Optional[str] = None
