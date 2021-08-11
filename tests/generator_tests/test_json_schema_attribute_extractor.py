import pytest
from magellan_models.model_generator.json_schema_attribute_extractor import (
    categorize_relationship,
)
from tests.helper import get_testing_spec
from magellan_models.exceptions import MagellanParserException


def test_categorize_relationship_raises_on_bad_data():
    bad_data = {}
    with pytest.raises(MagellanParserException):
        categorize_relationship("Foobar", bad_data)
    assert True
