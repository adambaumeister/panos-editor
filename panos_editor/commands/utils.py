import typer
from pyparsing import ParseException
from panos_editor.query.lang import StringParser


def query_string_callback(query: str):
    try:
        sp = StringParser()
        return sp.parse(query)[0]
    except ParseException as e:
        raise typer.BadParameter(f"Invalid query string: {e}")


def list_string_callback(list_str: str):
    return [x.strip() for x in list_str.split(",")]