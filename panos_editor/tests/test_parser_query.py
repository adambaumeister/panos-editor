from panos_editor.parser.query_functions import ExactOrIn
from panos_editor.tests.fixtures import dummy_xml

import pytest


class TestSelectQuery:
    def test___call__(self, dummy_xml):
        from panos_editor.parser.xml import PanosObject, PanosObjectCollection
        from panos_editor.parser.query import SelectQuery
        c = PanosObjectCollection(
            [PanosObject.from_xml(dummy_xml)]
        )
        q = SelectQuery(["shared", "address"])
        result = q(c)
        assert len(result) == 2
        assert result.objects[0].attrs


class TestSearchQuery:
    @pytest.mark.parametrize(
        "search_query, expected_name",
        [
            (
                    [["tag"], ExactOrIn("DEMO-STATIC")],
                    "testhost_10.100.100.10"
            ),
            (
                    [["tag"], ExactOrIn("DEMO-DYNAMIC")],
                    "testhost_public_ip_DYNAMIC"
            )
        ]
    )
    def test___call___single_result(self, dummy_xml, search_query, expected_name):
        from panos_editor.parser.xml import PanosObject, PanosObjectCollection
        from panos_editor.parser.query import SearchQuery, SelectQuery
        c = PanosObjectCollection(
            [PanosObject.from_xml(dummy_xml)]
        )
        q = SelectQuery(["shared", "address"])
        selected = q(c)

        q = SearchQuery(*search_query)
        result = q(selected)
        assert len(result) == 1
        assert result[0].attrs.get("name") == expected_name
