import dataclasses


@dataclasses.dataclass
class Context:
    """A context object grouping together all core settings required by
    providers.

    It must be filled in with values shortly after creation and before any
    provider uses it.
    """

    #: Underlying project's root directory absolute path.
    project_root_dir: str = None

    #: Path to a config file (relative to :attr:`project_root_dir`).
    config_file_path: str = None

    #: Encoding used to encode/decode config file.
    config_file_encoding: str = "utf-8"

    #: Flag telling if we're running in a "dry run" mode.
    dry_run: bool = False
