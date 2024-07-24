import os
from lxml.etree import fromstring

import pytest

FIXTURE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "test_data",
)


@pytest.fixture
def dummy_xml():
    return fromstring(open(os.path.join(FIXTURE_DIR, "dummy.xml")).read())
