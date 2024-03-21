import hashlib
import uuid


def make_dummy_rev(seed: str = None) -> str:
    """Make a random commit revision.

    This helper is mostly useful for testing purposes.

    :param seed:
        The seed to use when generating revision.

        For given *seed* there will always be same revision created. If this is
        omitted, then random revision is created.
    """
    if seed is None:
        seed = str(uuid.uuid4())
    return hashlib.sha1(seed.encode()).hexdigest()
