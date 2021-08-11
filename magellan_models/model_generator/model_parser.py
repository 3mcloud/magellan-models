"""
    A collection of functions for the categorization and parsing of
    "model" related information from a given OpenAPI spec
"""
import re
from warnings import warn
import inflection
from magellan_models.model_generator.helper_funcs import get_routes
from magellan_models.exceptions import MagellanParserWarning
from magellan_models.config import MagellanConfig
from .json_schema_attribute_extractor import (
    extract_attributes,
    get_response_body_example,
    extract_relationships,
)


def resource_can_make_a_model(
    resource_routes: list, base_route: str, single_route_regex: re.Pattern
) -> bool:
    """Takes a list of parsed route entities, the base_route value, and a regex pattern
    and discerns whether or not the collection of routes is sufficient to make a MagellanModel

    Currently this logic only looks for a GET MANY and GET ONE route,
    and emits warnings if the other 3 (POST PATCH and DELETE) are missing
    In this future this might become more strict.

    Args:
        resource_routes (list): a list of dicts
            with the following keys: 'action', 'route', and 'request_schema'
        base_route (str): the 'base_route" path,
            This should be where the GET MANY route exists for a given model.
        single_route_regex (re.Pattern): a pattern previously compiled
            which takes in the config's ID separator
            and is used to match for GET ONE routes

    Returns:
        bool: Should the parser continue to generate a Model or not?
    """
    modelifiable = False
    get_list_exists = False
    for resource_route in resource_routes:
        if resource_route["action"] == "get" and resource_route["route"] == base_route:
            get_list_exists = True

    if get_list_exists:
        # iterate thorugh resource_routes again assigning functionality
        postable = False
        patchable = False
        deleteable = False

        for route_entity in resource_routes:
            if route_entity["action"] == "get" and single_route_regex.fullmatch(
                route_entity["route"]
            ):
                modelifiable = True

            if route_entity["action"] == "post" and route_entity["route"] == base_route:
                postable = True

            if (
                route_entity["action"] == "put" or route_entity["action"] == "patch"
            ) and single_route_regex.fullmatch(route_entity["route"]):
                patchable = True

            if route_entity["action"] == "delete" and single_route_regex.fullmatch(
                route_entity["route"]
            ):
                deleteable = True

        if modelifiable:
            # check for POST, PATCH/PUT, and DELETE, emit warnings if missing

            if not postable:
                warn(
                    f"A model for {base_route} will be generated, but it is missing POST functionality. Use POST methods at your own risk.",  # pylint: disable=line-too-long
                    MagellanParserWarning,
                )

            if not patchable:
                warn(
                    f"A model for {base_route} will be generated, but it is missing PATCH functionality. Use at your own risk.",  # pylint: disable=line-too-long
                    MagellanParserWarning,
                )

            if not deleteable:
                warn(
                    f"A model for {base_route} will be generated, but it is missing DELETE functionality. Use DELETE methods at your own risk.",  # pylint: disable=line-too-long
                    MagellanParserWarning,
                )

    return modelifiable


def get_model_downstream_routes(
    open_api_spec: dict, resource_name: str, id_separator: str
):
    """parses routes and returns a list of paths starting with /{resource_name}/{id}/
      for that resource that have an additional endpoint

    example:
        if the route /labs/{id}/studies exists, it'll be returned if resource_name = "labs"
    Arguments:
        open_api_spec {dict} -- open api specification json loaded as dict
        resource_name {str} -- resource name we want downstream routes for
        id_separator {str} -- the Separator for ID in the openAPI specification file
            (ex: {id_} in GET api/labs/{id_})
        This id_separator value should be compilable into a regex for matching purposes.
    Returns:
        downstream_routes {list} -- a list of dict values indicating downstream route paths
        example of stripped an object: {
            "short_path": "labs",
            "route": "/universities/{id}/labs",
            "action": "post",
            "schema": {#someSchmeaObjectHere}
        }
    """
    paths = get_routes(open_api_spec)
    singular_resource_regex = re.compile(
        "/".join(["", resource_name, id_separator, "(.+)"])
    )
    downstream_routes = []
    for path in paths:
        # Here we do match vs fullmatch because we WANT extra stuff at the end
        regex_match = singular_resource_regex.match(path)
        # and open_api_spec.get('paths', {}).get(path, False): #.get('get', False):
        if regex_match:
            for method in open_api_spec.get("paths", {}).get(path, {}).keys():
                # Last capture group which in this case is the (.*)
                schema = (
                    open_api_spec.get("paths", {})
                    .get(path, {})
                    .get(method, {})
                    .get("requestBody", {})
                    .get("content", {})
                    .get("application/json", {})
                    .get("schema", {})
                )

                route_obj = {
                    "short_path": regex_match[regex_match.lastindex],
                    "route": path,
                    "schema": schema,
                    "action": method,
                }
                downstream_routes.append(route_obj)
    return downstream_routes


def get_path_req_schema(
    open_api_spec: dict,
    resource_name: str,
    id_separator: str,
    method: str,
    path_type: str = "singular",
) -> dict:
    """Gets the request body schema for a given entity's path_type and method
        ex: post /{resource} or patch /{resource}/{id}

    Args:
        open_api_spec (dict): the OpenAPI specification object
        resource_name (str): the name of the resource
        id_separator (str): a separator used to create the regex for matching routes
            (generally derived from this parsing instance's MagellanConfig)
        method (str): the REST method being used (OneOf: ["patch", "put", "post", "get", "delete"])
        path_type (str): Either "singular" or "many" where "many" means we ignore the id_separator
    Returns:
        dict: Either {} if the schema isn't found, or the requestBody schema value
    """
    paths = open_api_spec.get("paths", {})

    # don't forget paths are prepended with "/"
    if path_type == "singular":
        entity_regex = re.compile("/".join(["", resource_name, id_separator]))
    else:
        entity_regex = re.compile("/".join(["", resource_name]))

    possible_paths = list(filter(entity_regex.fullmatch, paths.keys()))

    if len(possible_paths) > 0:
        if len(possible_paths) > 1:
            warn(
                "Something went _weird_ with the Request Body schema extraction... Looks like there are multiple viable paths that exist.",  # pylint: disable=line-too-long
                MagellanParserWarning,
            )
        single_entity_path_key = possible_paths.pop()
        single_entity_method = paths.get(single_entity_path_key, {}).get(method, {})
        schema = (
            single_entity_method.get("requestBody", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema", {})
        )
        return schema
    return {}


def get_model_representation(
    spec: dict, model_name: str, configuration: MagellanConfig
) -> dict:
    """Generates a dict storing all information necessary to generate the API Model

    Arguments:
        spec {dict} -- Dict representation of the OpenAPI Specification JSON
        model_name {str} -- model name we're looking to process
        configuration {MagellanConfig} -- The Configuration instance associated with this execution
    """
    response_body = get_response_body_example(
        spec, model_name, configuration.id_separator
    )
    representation = {
        "resource_name": model_name,
        "class_name": inflection.camelize(inflection.singularize(model_name)),
        "attributes": extract_attributes(
            response_body, configuration.schema_attributes_path
        ),
        "relationships": extract_relationships(
            response_body, configuration.schema_relationships_path
        ),
        "downstream_routes": get_model_downstream_routes(
            spec, model_name, configuration.id_separator
        ),
        "patch_req_schema": get_path_req_schema(
            spec, model_name, configuration.id_separator, "patch", "singular"
        ),
        "post_req_schema": get_path_req_schema(
            spec, model_name, configuration.id_separator, "post", "many"
        ),
    }
    return representation
