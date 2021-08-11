""" JSON Schema attribute extraction module """
from typing import Iterable
import re
from warnings import warn
import inflection
from magellan_models.exceptions import MagellanParserException, MagellanParserWarning
from magellan_models.model_generator.helper_funcs import get_reference_value_from_spec

attribute_string_to_type = {
    "string": str,
    "number": float,
    "integer": int,
    "boolean": bool,
    "array": list,
    "object": dict,
}


def extract_attributes(
    json_schema_object: dict, path_to_attributes: Iterable[str]
) -> dict:
    """Extracts attributes for a given JSON schema object

    Arguments:
        json_schema_object {dict} -- JSON Schema definition object
        path_to_attributes {Tuple[String]} -- A list of keys to traverse through the schema object
            into the properties value containing the attribute keys This path is traversed here.
            If the object being passed in is already at the attribute level, pass in an empty list

    Returns:
        attribute_mapping {dict} -- key value pairings of attribute name and type
        values can be:
            str
            int
            float
            bool
            list
            dict
    """
    attributes_object = json_schema_object
    for key in path_to_attributes:
        attributes_object = attributes_object.get(key, {})

    attribute_mapping = {}
    for key in attributes_object.keys():
        attribute_type_string = attributes_object[key].get("type")
        attribute_mapping[key] = attribute_string_to_type.get(
            attribute_type_string, "Unknown, Parser Error"
        )
    return attribute_mapping


def get_response_body_example(
    openapi_schema: dict, resource_name: str, id_separator: str
):
    """Traverses the openapi schema object for the GET /{resource_name}/{identifier separator} path
    And returns that path's response body object

    Arguments:
        openapi_schema {dict} -- OpenAPI JSON loaded up as a python dictionary object
        resource_name {str} -- name of the resource we are looking to get attributes for.
        This resource is case sensitive and should match
            the OpenAPI specification name for the resource
        id_separator {str} -- ID Separator (often just a config value passed down).
            This should be a regex
        that we can use to match paths with
    Returns:
        response_body {dict} -- JSON Schema object pulled from OpenAPI schema
    """
    paths = openapi_schema.get("paths", {})

    singular_get_path = {}  # empty to start
    resource_path_regex = re.compile("/".join(["", resource_name, id_separator]))
    for path in paths.keys():
        # Match completely, downstream routes ignored
        if resource_path_regex.fullmatch(path):
            singular_get_path = paths.get(path, {}).get("get", False)
            if singular_get_path:
                break
    if not singular_get_path:
        raise MagellanParserException(
            f"Unable to find an associated path with resource `{resource_name}` given"
        )
    response_body_schema = (
        singular_get_path.get("responses", {})
        .get("200", {})
        .get("content", {})
        .get("application/json", {})
        .get("schema", {})
    )

    # if response_body_schema is a reference via {"$ref": "path_to_schema"}, return the reference object's value
    if response_body_schema.get("$ref", False):
        response_body_schema = get_reference_value_from_spec(
            openapi_schema, response_body_schema.get("$ref")
        )
    return response_body_schema


def extract_relationships(
    response_body_schema, path_to_relationships: Iterable[str]
) -> dict:
    """Extracts relationships for a given response body
        and returns an easier to read dict containing relationship keys

    Arguments:
        response_body_schema {dict} -- JSON Schema definition object
        path_to_attributes {Tuple[String]} -- A list of keys to traverse through the schema object
            into the properties value containing the attribute keys
        This path is traversed in the function.
            If the object being passed in is already at the relationships level, pass an empty list

    Returns:
        relationship_mapping: a dict with keys being the singularized resource in question
            (lab, test etc instead of labs, tests) and values being either "many" or "one"

    """
    relationships_object = response_body_schema
    for key in path_to_relationships:
        relationships_object = relationships_object.get(key, {})
    relationships_mapping = {}
    for key in relationships_object.keys():
        relationship_type = categorize_relationship(key, relationships_object[key])
        relationships_mapping[key] = relationship_type

    return relationships_mapping


def categorize_relationship(
    relationship_name: str, singular_relationship_schema: dict
) -> str:
    """Categorizes a relationship as a singular or many relationship type
        This is done by recursively going through single key objects until
        we either reach an array or something else

    If we encounter multiple key value pairs in an object
    this will default to inflection to tell us what we want.

    Args:
        relationship_name (str): The name of the relationship
            this doesn't change as we recursively iterate.
        singular_relationship_schema (dict): The json schema object for a current layer
            as we iterate through layers of the relationship

    Returns:
        str: one of "many" or "one"
    """

    # Go deeper if we have multiple layers of single key objects
    try:
        if singular_relationship_schema["type"] == "object":
            if len(singular_relationship_schema["properties"].keys()) != 1:
                # uh oh multiple keys (or no keys at all!)! just default to inflection
                warn(
                    f"Unable to discern relationship type for {relationship_name}. Defaulting to Inflection categorization.",  # pylint: disable=line-too-long
                    MagellanParserWarning,
                )
                if inflection.singularize(relationship_name) == relationship_name:
                    return "one"
                return "many"
            # we have a single key we can now go further down,
            # example: PetStores -> Data -> List, first time we go from PetStores to data
            next_layer_down_key = list(
                singular_relationship_schema["properties"].keys()
            )[0]
            next_layer_down = singular_relationship_schema["properties"][
                next_layer_down_key
            ]
            return categorize_relationship(relationship_name, next_layer_down)

        if singular_relationship_schema["type"] == "array":
            return "many"
        return "one"
    except KeyError as key_err:
        raise MagellanParserException(
            f"Unable to access key `type` when parsing the `{relationship_name}` relationship. Is your JSON Schema malformed?"  # pylint: disable=line-too-long
        ) from key_err
