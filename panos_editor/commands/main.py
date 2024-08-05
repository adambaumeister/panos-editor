import enum
import sys
from typing import Annotated

import typer
import panos_editor.commands.show
from loguru import logger

from importlib.metadata import version, PackageNotFoundError

HELP_STR = """:hammer: panos-editor is a multifunction CLI application and python package for interacting with PAN-OS configurations.

:fearful: Do you need help? check out the project on Github: https://github.com/adambaumeister/panos-editor
"""

app = typer.Typer(
    help=HELP_STR,
    rich_markup_mode="rich",
)

app.add_typer(
    panos_editor.commands.show.app,
    name="show",
    rich_help_panel=":fire: Manipulating Configs",
)


@app.command(rich_help_panel="General", name="version")
def get_version():
    """Returns the currently installed panos_editor version."""
    try:
        v = version("panos_editor")
    except PackageNotFoundError:
        v = "Unknown (panos_editor is not installed locally)"
    print(v)


class LogLevel(enum.Enum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@app.callback()
def main(
        log_level: Annotated[LogLevel, typer.Option(help="The log level for stdout logging.")] = LogLevel.WARNING.value
):
    logger.remove(0)
    logger.add(sys.stdout, level=log_level.value)
    logger.debug(f"Log level set to {log_level}")
