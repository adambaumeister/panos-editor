import pytest

from panos_editor.parser.xml import PanosObjectCollection, PanosObject
from panos_editor.tests.fixtures import dummy_xml


class TestStringParser:

    @pytest.mark.parametrize(
        "string, expected",
        [
            ("x y == 1", ""),
            ("x y == 1 AND z == 2", ""),
        ],
    )
    def test_simple_parse(self, string, expected):
        from panos_editor.query.lang import StringParser

        sp = StringParser()
        r = sp.parse(string)
        print(r)

    @pytest.mark.parametrize(
        "string, expected",
        [
            # Normal
           # ("shared.address ip-netmask == 10.100.100.10", ["testhost_10.100.100.10"]),
            ("shared.address ip-netmask == 10.100.100.10 OR name == testhost_public_ip_DYNAMIC", ["testhost_10.100.100.10", "testhost_public_ip_DYNAMIC"])
        ]
    )
    def test_parse_and_query(self, string, expected, dummy_xml):
        from panos_editor.query.lang import StringParser

        sp = StringParser()
        r = sp.parse(string)

        c = PanosObjectCollection([PanosObject.from_xml(dummy_xml)])

        statement = r[0]
        result = statement(c)
        try:
            assert [x.attrs.get('name') for x in result] == expected
        except AssertionError:
            print(statement.search.predicates)
            print(result.objects)
            raise