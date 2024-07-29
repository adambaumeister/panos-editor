import re
from typing import Union, Self
from pyparsing import Word, alphanums, one_of, Regex, infix_notation, OpAssoc, printables, Combine

class QuerySyntaxError(Exception):
    """Raises when the provided string query is incorrect for whatever reason"""

    pass


class StringParser:
    """StringParser
    Parses a given string as a panos-editor query by converting it into a series of predicates.

    Examples
        Parse a basic select string

        >>> StringParser("config.shared.address.ip-netmask == 10.100.100.10")

        Parse a basic Join String

        >>> StringParser("config.shared.address join devices.device-group.post-rulebase.security.rules on name == destination")

        Parse a complex Select string with multple predicates

        >>> StringParser("(config.shared.address.ip-netmask == 10.100.100.10 AND config.shared.address.name == 'testlab') OR config.shared.address.name == 'other'")

        # Probably go with this format, its not that much longer and its clearer and easier to parse
        >>> StringParser("SELECT config.shared.address WHERE ip-netmask == '10.100.100.10'")
    """

    def __init__(self, string: str):
        self.string = string

        self.RE_WORD = re.compile(r"[a-zA-Z.\-_0-9]+|==")
        self.PREDICATE_START = "("
        pass

    def parse(self, string: str, current_predicate=None, current_query=None):
        selector = Regex(r"[a-zA-Z\.\-_0-9]+")
        op = one_of(["=="])
        value = Regex(r"[a-zA-Z\.\-_0-9]+")

        query = selector + op + value
        expr = infix_notation(
            query,
            [
                (one_of("AND OR"), 2, OpAssoc.RIGHT)
            ]
        )
        expr.run_tests(string, full_dump=False)