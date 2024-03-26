import io
from typing import List

from .objects import Changelog, ChangelogEntry


def format_as_json(changelog: Changelog) -> str:
    """Formats changelog to JSON string."""
    return changelog.model_dump_json(indent=2, exclude_none=True)


def format_as_markdown(changelog: Changelog) -> str:
    """Formats changelog to Markdown string."""

    def write_heading(entry: ChangelogEntry):
        buf.write(f"## {entry.version.to_str()} ({entry.released.strftime('%Y-%m-%d')})\n\n")

    def write_group(label: str, items: List[str]):
        buf.write(f"### {label}\n\n")
        for item in items:
            buf.write(f"- {item}\n")
        buf.write("\n")

    def write_initial_release(entry: ChangelogEntry):
        write_heading(entry)
        buf.write("Initial release.\n\n")

    def write_release(entry: ChangelogEntry):
        write_heading(entry)
        if entry.data is None:
            return
        if entry.data.breaking_changes:
            write_group("BREAKING CHANGES", entry.data.breaking_changes)
        if entry.data.fixes:
            write_group("Fix", [x.data.description for x in entry.data.fixes])
        if entry.data.feats:
            write_group("Feat", [x.data.description for x in entry.data.feats])

    if not changelog.entries:
        return ""
    buf = io.StringIO()
    for entry in reversed(changelog.entries[1:]):
        write_release(entry)
    write_initial_release(changelog.entries[0])
    return buf.getvalue()
