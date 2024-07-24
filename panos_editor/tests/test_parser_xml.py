import json
from panos_editor.tests.fixtures import dummy_xml


class TestPanosObject:
    def test_from_xml(self, dummy_xml):
        from panos_editor.parser.xml import PanosObject

        result = PanosObject.from_xml(dummy_xml)
        print(json.dumps(result.to_dict(), indent=4, sort_keys=True))
