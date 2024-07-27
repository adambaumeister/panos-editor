from panos_editor.parser.query_functions import ExactOrIn
from panos_editor.parser.query import And, SearchQuery
from panos_editor.tests.fixtures import dummy_xml, lab_xml

import pytest


class TestSelectQuery:
    def test___call__(self, dummy_xml):
        from panos_editor.parser.xml import PanosObject, PanosObjectCollection
        from panos_editor.parser.query import SelectQuery

        c = PanosObjectCollection([PanosObject.from_xml(dummy_xml)])
        q = SelectQuery(["shared", "address"])
        result = q(c)
        assert len(result) == 2
        assert result.objects[0].attrs


class TestSearchQuery:
    @pytest.mark.parametrize(
        "search_query, expected_name",
        [
            ([["tag"], ExactOrIn("DEMO-STATIC")], "testhost_10.100.100.10"),
            ([["tag"], ExactOrIn("DEMO-DYNAMIC")], "testhost_public_ip_DYNAMIC"),
            (
                [["ip-netmask"], ExactOrIn("20.213.243.31")],
                "testhost_public_ip_DYNAMIC",
            ),
        ],
    )
    def test___call___single_result(self, dummy_xml, search_query, expected_name):
        from panos_editor.parser.xml import PanosObject, PanosObjectCollection
        from panos_editor.parser.query import SearchQuery, SelectQuery

        c = PanosObjectCollection([PanosObject.from_xml(dummy_xml)])
        q = SelectQuery(["shared", "address"])
        selected = q(c)

        q = SearchQuery(*search_query)
        result = q(selected)
        assert len(result) == 1
        assert result[0].attrs.get("name") == expected_name


class TestAnd:
    @pytest.mark.parametrize(
        "search_query, expected_name",
        [
            (
                [
                    SearchQuery(["tag"], ExactOrIn("DEMO-STATIC")),
                    SearchQuery(["ip-netmask"], ExactOrIn("10.100.100.10")),
                ],
                "testhost_10.100.100.10",
            ),
        ],
    )
    def test___call___single_match(self, dummy_xml, search_query, expected_name):
        from panos_editor.parser.xml import PanosObject, PanosObjectCollection
        from panos_editor.parser.query import SelectQuery

        c = PanosObjectCollection([PanosObject.from_xml(dummy_xml)])
        q = SelectQuery(["shared", "address"])
        selected = q(c)

        q = And(*search_query)
        result = q(selected)
        assert len(result) == 1
        assert result[0].attrs.get("name") == expected_name


class TestJoin:
    def test_get_value_recursive(self, lab_xml):
        from panos_editor.parser.xml import PanosObject, PanosObjectCollection
        from panos_editor.parser.query import SelectQuery, Join

        c = PanosObjectCollection([PanosObject.from_xml(lab_xml)])

        q = SelectQuery(["shared", "address"])
        left = q(c)

        q = SelectQuery(["devices", "device-group", "post-rulebase", "security", "rules"])
        right = q(c)

        j = Join(["name"], ["destination"])
        result = j(left, right)
        print(result[0].to_dict())
