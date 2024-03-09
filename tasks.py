import invoke


@invoke.task
def format(ctx):
    """Run code formatting tools."""
    ctx.run("black --line-length=120 .")


@invoke.task
def test(ctx):
    """Run all tests."""
    ctx.run("pytest")
