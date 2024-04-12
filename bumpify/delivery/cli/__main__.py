import os

import click
from click_help_colors import HelpColorsGroup
from pydio.api import Injector
from pydio.base import IInjector

from bumpify import utils
from bumpify.core.api.interface import IInitCommand
from bumpify.di import provider


@click.group(
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="green",
)
@click.option(
    "-c",
    "--config-file-path",
    default=".bumpify.toml",
    show_default=True,
    type=click.Path(dir_okay=False, writable=True),
    help="Path to the config file to use.\n\nThis is relative to current working directory.",
)
@click.option(
    "-ce",
    "--config-file-encoding",
    default="utf-8",
    show_default=True,
    help="Encoding to be used when saving or reading config file.",
)
@click.pass_context
def bumpify(ctx: click.Context, config_file_path: str, config_file_encoding: str):
    """Automated semantic versioning and changelog generation for software
    projects.

    Bumpify works by analyzing VCS log to detect the severity of changes made.
    Then, it bumps either major, minor or patch number and produces a new
    version by creating version bump commit and new version tag.

    Bumpify by default works with conventional commits documented here:

        https://www.conventionalcommits.org/en/v1.0.0/

    And follows semantic versioning rules that can be found here:

        https://semver.org/
    """
    injector = Injector(provider)
    bumpify_context = utils.inject_context(injector)
    bumpify_context.project_root_dir = os.getcwd()
    bumpify_context.config_file_path = config_file_path
    bumpify_context.config_file_encoding = config_file_encoding
    ctx.obj = ctx.with_resource(injector)


@bumpify.command()
@click.pass_obj
def init(injector: IInjector):
    """Create initial configuration file interactively."""
    command = utils.inject_type(injector, IInitCommand)
    provider = utils.inject_type(injector, IInitCommand.IInitProvider)
    presenter = utils.inject_type(injector, IInitCommand.IInitPresenter)
    command.init(provider, presenter)


def main():
    bumpify()


if __name__ == "__main__":
    main()