from panos_editor.parser.query_functions import ExactOrIn
from panos_editor.tests.fixtures import dummy_xml


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


class TestSearchQuery:
    def test___call__(self, dummy_xml):
        from panos_editor.parser.xml import PanosObject, PanosObjectCollection
        from panos_editor.parser.query import SearchQuery, SelectQuery
        c = PanosObjectCollection(
            [PanosObject.from_xml(dummy_xml)]
        )
        q = SelectQuery(["shared", "address"])
        selected = q(c)

        q = SearchQuery(["tag"], ExactOrIn("DEMO-STATIC"))
        result = q(selected)
        assert len(result) == 1
        assert result[0].elements.get("ip-netmask") == "10.100.100.10"
