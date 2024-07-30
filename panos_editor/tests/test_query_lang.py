import pytest


class TestStringParser:

    @pytest.mark.parametrize(
        "string, expected",
        [
            ("(x.y==1 AND a.b==2) OR v.v==3", ""),
        ],
    )
    def test_simple_parse(self, string, expected):
        from panos_editor.query.lang import StringParser

        sp = StringParser(string)
        r = sp.parse(string)



    @pytest.mark.parametrize(
        "string, expected",
        [
            # Normal
            ("config.shared.address.ip-netmask == 10.100.100.10", ""),
            # Nested and ordered predicate
            ("(config.shared.address.ip-netmask == 10.100.100.10 OR config.shared.address.name == testlab) AND config.shared.address.tag == whatever", ""),
            # Quoted string
            ('config.shared.address.tag == "whatever"', ""),
        ],
    )
    def test_parse(self, string, expected):
        from panos_editor.query.lang import StringParser

        sp = StringParser()
        r = sp.parse(string)
        print(r)