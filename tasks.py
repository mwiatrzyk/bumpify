import invoke


@invoke.task
def format(ctx):
    """Run code formatting tools."""
    ctx.run("isort --atomic .")
    ctx.run("black --line-length=100 .")


@invoke.task
def test(ctx):
    """Run all tests."""
    ctx.run("pytest")


@invoke.task
def clean(ctx):
    """Clean the workspace from build artifacts."""
    ctx.run("find . -name *.pyc -delete")
    ctx.run("find . -type d -empty -delete")
    ctx.run("rm -rf dist")
