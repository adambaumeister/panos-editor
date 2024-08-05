from panos_editor.tests.fixtures import dummy_xml


class TestTableOutput:
    def get_collection(self, xml):
        from panos_editor.parser.xml import PanosObject, PanosObjectCollection
        from panos_editor.query.functions import SelectQuery

        c = PanosObjectCollection([PanosObject.from_xml(xml)])
        q = SelectQuery(["shared", "address"])
        return q(c)

    def test___call__(self, dummy_xml):
        from panos_editor.output.table import TableOutput

        result = self.get_collection(dummy_xml)

        table_output = TableOutput(["name", "ip-netmask"])
        table = table_output(result)
        assert table == [['testhost_10.100.100.10', '10.100.100.10'], ['testhost_public_ip_DYNAMIC', '20.213.243.31']]

    def test___call__with_tag(self, dummy_xml):
        from panos_editor.output.table import TableOutput

        result = self.get_collection(dummy_xml)

        table_output = TableOutput(["name", "tag"])
        table = table_output(result)
        assert table == [['testhost_10.100.100.10', 2], ['testhost_public_ip_DYNAMIC', 2]]

