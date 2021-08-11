from magellan_models.model_generator.json_schema_attribute_extractor import (
    categorize_relationship,
)
import pytest


def test_categorize_relationship_returns_many_when_finds_an_array():
    model = "PetStore"
    schema = {"type": "array", "items": {"type": "string"}}
    assert categorize_relationship(model, schema) == "many"


def test_cat_rel_uses_inflection_when_confused():
    schema = {
        "type": "object",
        "properties": {"fudge": "foo", "dooeybob": "thing", "quantum": "Physics"},
    }
    assert categorize_relationship("PetStore", schema) == "one"
    assert categorize_relationship("petStores", schema) == "many"


def test_cat_rel_returns_one_when_not_a_list():
    schema = {"type": "string"}
    assert categorize_relationship("Stories", schema) == "one"


def test_cat_rel_returns_many_even_if_plural():
    schema = {"type": "array"}
    assert categorize_relationship("SingleObject", schema) == "many"
