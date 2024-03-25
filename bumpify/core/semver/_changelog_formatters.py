from .objects import Changelog


def format_as_json(changelog: Changelog) -> str:
    return changelog.model_dump_json(indent=2, exclude_none=True)
