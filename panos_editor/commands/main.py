import enum
import sys
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table
from loguru import logger

from importlib.metadata import version, PackageNotFoundError

from panos_editor.commands.utils import query_string_callback, list_string_callback
from panos_editor.output.table import TableOutput

HELP_STR = """:hammer: panos-editor is a multifunction CLI application and python package for interacting with PAN-OS configurations.

:fearful: Do you need help? check out the project on Github: https://github.com/adambaumeister/panos-editor
"""

app = typer.Typer(
    help=HELP_STR,
    rich_markup_mode="rich",
)

console = Console()

@app.command(
    rich_help_panel=":fire: Configuration Commands",
    help="Displays items from PAN-OS Configurations"
)
def show(
    query: Annotated[str, typer.Argument(help="Selection and Search query string.", callback=query_string_callback)],
    fields: Annotated[str, typer.Option(help="Fields to display from within the search result.", callback=list_string_callback)] = "name",
):
    collection = query()
    table = TableOutput(fields)

    print_table = Table()
    for x in fields:
        print_table.add_column(x)

    for row in table(collection):
        print_table.add_row(*[str(x) for x in row])

    console.print(print_table)


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
    log_level: Annotated[
        LogLevel, typer.Option(help="The log level for stdout logging.")
    ] = LogLevel.WARNING.value
):
    logger.remove(0)
    logger.add(sys.stdout, level=log_level.value)
    logger.debug(f"Log level set to {log_level}")
