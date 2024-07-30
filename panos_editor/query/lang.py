import re
from typing import Union, Self
from pyparsing import (
    Word,
    alphanums,
    one_of,
    Regex,
    infix_notation,
    OpAssoc,
    QuotedString,
)
from panos_editor.query.functions import SelectQuery, SearchQuery
from panos_editor.query.query_functions import ExactOrIn


class QuerySyntaxError(Exception):
    """Raises when the provided string query is incorrect for whatever reason"""

    pass


def convert_to_queries(tokens: list[str]):
    """Converts a parsed query into a SearchQuery and SelectQuery objects."""
    token_map = {"==": ExactOrIn}

    relative_path = tokens[0].split(".")[:-1]
    search_path = relative_path[-1]
    search_function = token_map.get(tokens[1])
    if not search_function:
        raise QuerySyntaxError(f"Unknown Operator '{tokens[1]}'")

    return SearchQuery(
        relative_path=relative_path, search_function=search_function
    )


class StringParser:
    """StringParser
    Parses a given string as a panos-editor query by converting it into a series of predicates.

    Examples
        Parse a basic select string

        >>> StringParser("config.shared.address ip-netmask == 10.100.100.10 and name == testlab")

        Parse a basic Join String

        >>> StringParser("config.shared.address join devices.device-group.post-rulebase.security.rules on name == destination")

        Parse a complex Select string with multple predicates

        >>> StringParser("(config.shared.address ip-netmask == 10.100.100.10 AND config.shared.address.name == 'testlab') OR config.shared.address.name == 'other'")
    """

    def parse(self, string: str):
        selector = Regex(r"[a-zA-Z\.\-_0-9]+")
        op = one_of(["==", "incidr"])
        value = Regex(r"[a-zA-Z\.\-_0-9]+") | QuotedString(quote_char='"')

        query = selector + op + value
        query.set_parse_action(convert_to_queries)

        expr = infix_notation(query, [(one_of("AND OR"), 2, OpAssoc.RIGHT)])
        return expr.parse_string(string)
