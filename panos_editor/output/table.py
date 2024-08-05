from typing import Union

from panos_editor.parser.xml import PanosObjectCollection, PanosObject
from panos_editor.query.functions import get_value_recursive


class TableOutput:
    def __init__(self, headers: list[str]):
        """
        Tabular output of a `PanosObjectCollection`. This Output specifically is designed to support the writing to other
        formats like a CLI terminal (as a table) or a CSV file.

        This output will flatten the objects so they can fit into a tabular format and when an object contains children,
        it will count them and return the count.

        Arguments:
            headers: The list of columns to display in the table.
        """

        self.headers = headers

    def __call__(self, collection: PanosObjectCollection) -> list[list[Union[str, int]]]:
        table = []
        for obj in collection:
            row = []
            for header in self.headers:
                result = get_value_recursive(obj, header.split("."))
                if isinstance(result, list):
                    result = len(result)

                row.append(result)
            table.append(row)

        return table