from tests.helper import get_testing_spec
from magellan_models.model_generator.json_schema_attribute_extractor import (
    extract_attributes,
    get_response_body_example,
    extract_relationships,
)


def test_update_attributes_path_changes_where_to_look():
    # response attributes are in the root of our response body
    schema_attributes_path = ["properties"]
    sample_spec = get_testing_spec()
    # we're saying our response body is the attributes object of our Faction sample response body from the testing config, this way "data" never shows up in the response body being parsed
    # the code should just get the "attributes" object nested inside data instead
    path_to_resp_body = [
        "components",
        "FactionSchema",
        "properties",
        "data",
        "properties",
        "attributes",
    ]
    resp_body = sample_spec
    for path in path_to_resp_body:
        resp_body = resp_body.get(path, {})

    attribute_mapping = extract_attributes(resp_body, schema_attributes_path)
    assert "id" in attribute_mapping
    assert "title" in attribute_mapping
    assert "description" in attribute_mapping
    assert "keywords" in attribute_mapping


def test_update_relationships_path_changes_where_to_look():
    # response attributes are in the root of our response body
    schema_relationships_path = ["relationships", "properties"]
    sample_spec = get_testing_spec()
    path_to_resp_body = [
        "components",
        "FactionSchema",
        "properties",
        "data",
        "properties",
    ]
    resp_body = sample_spec
    for path in path_to_resp_body:
        resp_body = resp_body.get(path, {})
    relationships = extract_relationships(resp_body, schema_relationships_path)
    assert "units" in relationships
    assert relationships.get("units") == "many"
