import json
from panos_editor.tests.fixtures import dummy_xml


class TestPanosObject:
    def test_from_xml(self, dummy_xml):
        from panos_editor.parser.xml import PanosObject

        result = PanosObject.from_xml(dummy_xml)
        assert result.xpath == ["config"]

        print(result.to_dict())