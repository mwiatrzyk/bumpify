import dataclasses


@dataclasses.dataclass
class Styled:
    value: str
    name: str = None


@dataclasses.dataclass
class StyledMultiline:
    value: str
    indent: str = ""
    name: str = None
