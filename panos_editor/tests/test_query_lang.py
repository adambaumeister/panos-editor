import pytest

from panos_editor.inventory.errors import HostNotFound
from panos_editor.parser.xml import PanosObjectCollection, PanosObject
from panos_editor.tests.fixtures import dummy_xml, lab_xml


class TestStringParser:

    @pytest.mark.parametrize(
        "string, expected",
        [
            # Normal
            ("shared.address ip-netmask == 10.100.100.10", ["testhost_10.100.100.10"]),
            (
                "shared.address ip-netmask == 10.100.100.10 OR name == testhost_public_ip_DYNAMIC",
                ["testhost_10.100.100.10", "testhost_public_ip_DYNAMIC"],
            ),
            (
                "shared.address (ip-netmask == 10.100.100.10 AND name == testhost_10.100.100.10)",
                ["testhost_10.100.100.10"],
            ),
        ],
    )
    def test_parse_and_query_basic_queries(self, string, expected, dummy_xml):
        from panos_editor.query.lang import StringParser

        sp = StringParser()
        r = sp.parse(string)

        c = PanosObjectCollection([PanosObject.from_xml(dummy_xml)])

        statement = r[0]
        result = statement(c)
        try:
            assert [x.attrs.get("name") for x in result] == expected
        except AssertionError:
            print(statement.search.predicates)
            print(result.objects)
            raise

    @pytest.mark.parametrize(
        "string, expected",
        [
            (
                "shared.address ip-netmask == 10.100.100.10 JOIN device.device-group.post-rulebase.security.rules ON name == source",
                ("OUTBOUND", "testhost_10.100.100.10"),
            )
        ],
    )
    def test_parse_and_query_with_join(self, string, expected, dummy_xml):
        from panos_editor.query.lang import StringParser

        sp = StringParser()
        r = sp.parse(string)

        c = PanosObjectCollection([PanosObject.from_xml(dummy_xml)])

        statement = r[0]
        result = statement(c)
        try:
            assert next(x.attrs.get("name") for x in result) == expected[0]
            assert (
                next(x.attrs.get("name") for x in result[0].joined_objects)
                == expected[1]
            )
        except AssertionError:
            raise

    @pytest.mark.parametrize(
        "string, expected",
        [
            (
                "dummy.xml:shared.address ip-netmask == 10.100.100.10",
                "dummy.xml",
            )
        ],
    )
    def test_parse_with_file_loader(self, string, expected):
        from panos_editor.query.lang import StringParser

        sp = StringParser()
        with pytest.raises(HostNotFound):
            sp.parse(string)
