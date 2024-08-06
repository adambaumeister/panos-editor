import re
from typing import Union, Self, Callable

import pyparsing.results
from pyparsing import (
    Word,
    alphanums,
    one_of,
    Regex,
    infix_notation,
    OpAssoc,
    QuotedString,
    ZeroOrMore,
    ParseException,
)

from panos_editor.inventory.loader import get_inventory
from panos_editor.query.functions import (
    SelectQuery,
    SearchQuery,
    And,
    Or,
    Statement,
    InnerJoin,
)
from panos_editor.query.query_functions import ExactOrIn


class QuerySyntaxError(Exception):
    """Raises when the provided string query is incorrect for whatever reason"""

    pass


def convert_to_queries(tokens):
    """Converts a parsed query into a SearchQuery and SelectQuery objects."""
    token_map = {"==": ExactOrIn}

    search_path = tokens[0].split(".")
    search_value = tokens[2]
    search_function = token_map.get(tokens[1])
    if not search_function:
        raise QuerySyntaxError(f"Unknown Operator '{tokens[1]}'")

    return SearchQuery(
        relative_path=search_path, search_function=search_function(search_value)
    )


class PredicateParser:
    def __init__(self):
        self.queries: list[SearchQuery] = []
        self.query_func: Callable = And
        self.children: list[PredicateParser] = []

    def add_query(self, query: SearchQuery):
        self.queries.append(query)

    def add_child(self, p: list[Self]):
        self.children += p

    def convert_to_prdedicates(self):
        queries = self.queries
        for child in self.children:
            queries.append(child.convert_to_prdedicates())

        return self.query_func(*queries)


def convert_to_predicates_recursive(
    q_list: Union[list, SearchQuery], predicate_parser: PredicateParser = None
):
    if not predicate_parser:
        predicate_parser = PredicateParser()

    predicate_parsers = [predicate_parser]

    if type(q_list) is not pyparsing.ParseResults:
        predicate_parser.add_query(q_list)
        return predicate_parsers

    for sq_or_list in q_list:

        if isinstance(sq_or_list, pyparsing.results.ParseResults):
            next_parser = PredicateParser()
            predicate_parser.add_child(
                convert_to_predicates_recursive(sq_or_list, next_parser)
            )
        elif sq_or_list == "OR":
            predicate_parser.query_func = Or
        elif type(sq_or_list) is SearchQuery:
            predicate_parser.add_query(sq_or_list)

    return predicate_parsers


def convert_to_joins_or_statement(tokens):
    join_func_map = {"JOIN": InnerJoin}
    token_map = {"==": ExactOrIn}
    # If this is a normal statement
    if len(tokens) == 1:
        return tokens
    else:
        left_statement = tokens[0]
        join_func = join_func_map.get(tokens[1])
        right_statement = tokens[2]

        left_path = tokens[4]
        match_func = token_map.get(tokens[5])
        right_path = tokens[6]

        return join_func(
            left_statement, right_statement, left_path, right_path, match_func
        )


def convert_to_statement(tokens):
    selector = tokens[0]
    queries = tokens[1]
    predicates = []
    predicate_parsers = convert_to_predicates_recursive(queries)
    for pp in predicate_parsers:
        predicates.append(pp.convert_to_prdedicates())

    return Statement(select=selector, search=predicates[0])


def convert_to_loader(tokens):
    inventory = get_inventory()
    return inventory.get_by_id(tokens[0])


def string_to_select(tokens):
    path = tokens[0]
    return SelectQuery(path.split("."))


def pairwise(it):
    it = iter(it)
    while True:
        try:
            yield next(it), next(it)
        except StopIteration:
            # no more elements in the iterator
            return


class StringParser:
    """StringParser
    Parses a given string as a panos-editor query by converting it into a series of predicates.
    """

    def parse(self, string: str):
        """

        Examples
            Parse a basic select string

            >>> StringParser().parse("config.shared.address ip-netmask == 10.100.100.10 and name == testlab")

            Parse a basic Join String

            >>> StringParser().parse("config.shared.address join devices.device-group.post-rulebase.security.rules on name == destination")

            Parse a complex Select string with multple predicates

            >>> StringParser().parse("(config.shared.address ip-netmask == 10.100.100.10 AND config.shared.address.name == 'testlab') OR config.shared.address.name == 'other'")

            Parse a Join query

            >>> StringParser().parse("config.shared.address ip-netmask == 10.100.100.10 JOIN devices.device-group.post-rulebase.security.rules ON name == source")

        """
        host_id = Regex(r"[a-zA-Z\.\-_0-9]+")
        host_id_seperator = ":"
        host_def = host_id + host_id_seperator
        host_def.set_parse_action(convert_to_loader)

        selector = Regex(r"[a-zA-Z\.\-_0-9]+")
        selector.add_parse_action(string_to_select)

        relative_path = Regex(r"[a-zA-Z\.\-_0-9]+")

        op = one_of(["==", "incidr"])
        value = Regex(r"[a-zA-Z\.\-_0-9]+") | QuotedString(quote_char='"')

        query = relative_path + op + value
        expr = infix_notation(query, [(one_of("AND OR"), 2, OpAssoc.RIGHT)])

        statement = ZeroOrMore(host_def) + selector + expr
        statement.set_parse_action(convert_to_statement)

        join_definition = (
            "JOIN"
            + selector
            + ZeroOrMore(expr)
            + "ON"
            + relative_path
            + op
            + relative_path
        )

        complete_statement = statement + ZeroOrMore(join_definition)
        complete_statement.set_parse_action(convert_to_joins_or_statement)
        query.set_parse_action(convert_to_queries)

        result = complete_statement.parse_string(string)
        return result
