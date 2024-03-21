import dataclasses
from typing import Any, Optional


@dataclasses.dataclass
class Styled:
    """An object to annotate some other object with some basic styles.

    Thanks to this, styles can be evaluated later, with no need to worry about
    that earlier.
    """

    #: The object to add style for.
    obj: Any

    #: Render object using bold font (True) or normal (False).
    bold: bool = False

    #: Set foreground color for a value.
    fg: Optional[str] = None
