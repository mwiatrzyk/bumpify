import re

SEMVER_RE = re.compile(
    r"(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
)

SEMVER_EXACT_RE = re.compile(r"^" + SEMVER_RE.pattern + r"$")

CONVENTIONAL_COMMIT_SUBJECT_RE = re.compile(
    r"^(?P<type>\w+)(\((?P<scope>\w+)\))?(?P<breaking_sign>!)?: (?P<description>.+)$"
)

CONVENTIONAL_COMMIT_FOOTER_TAG_RE = re.compile(
    r"^(((?P<breaking_change>BREAKING CHANGE): )|"
    r"((?P<breaking_change_tag>BREAKING-CHANGE): )|"
    r"((?P<tag>(\w+(-\w+)*)): ))(?P<value>.+)$"
)
