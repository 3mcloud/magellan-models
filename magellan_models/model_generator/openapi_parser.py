""" Parser Module """
import re
from typing import Tuple, List
from magellan_models.model_generator.model_parser import resource_can_make_a_model
from magellan_models.model_generator.helper_funcs import get_routes, get_endpoints


def get_resource_mapping(open_api_spec: dict) -> dict:
    """
    A resource is defined as a collection of endpoints that share the beginning of the route
        (ex "/pets", "/pets/{id}", "/pets/{id}/related_pets", "/pets/find_nearest")
    This function takes in an open api spec and returns a list of resources
    where each resource is an object with a base_route url, and a list of route entities
    route entities are defined as objects with an 'action' key (GET PATCH POST etc),
    and 'route' key specifying the url
    along with a 'request_schema' key related to the requestBody schema
    """
    routes = get_routes(open_api_spec)
    endpoints = get_endpoints(open_api_spec)
    resources = {}
    for endpoint in endpoints:
        endpoint_routes = []
        for route in routes:
            if route.startswith(endpoint):
                actions = open_api_spec["paths"][route].keys()
                for action in actions:
                    # todo: refactor to move requestBody schema retrieval into a helper function.
                    # There are 3 places where this code could be pulled from
                    request_schema = (
                        open_api_spec["paths"][route][action]
                        .get("requestBody", {})
                        .get("content", {})
                        .get("application/json", {})
                        .get("schema", {})
                    )
                    endpoint_routes.append(
                        {
                            "action": action,
                            "route": route,
                            "request_schema": request_schema,
                        }
                    )
        resource = endpoint.split("/")[1]
        resources[resource] = {"base_route": endpoint, "routes": endpoint_routes}
    return resources


def parse_resource_names_and_other_routes_from_mapping(
    resource_mapping: dict, id_separator: str
) -> Tuple[List[str], List[dict]]:
    """
    Processes the resource mapping passed in and returns a list of strings
    These strings are the labels which should have a the full set of CRUD operations available
    (Currently we only look for being about do a GET resource_name/{ID} path assume the rest exist)
    Additionally for routes that aren't parsed as downstream_routes by a model,
        and which otherwise would be inaccessible, this function returns those routes as well

    Arguments:
        resource_mapping {dict} -- A mapping of resources from the get_resource_mapping function
        keys the resource name and their value is a dict with two keys:
            base_route: str (root endpoint of all routes)
            routes: List of dict {"action": post put etc, "route": route url str}
        id_separator {str} -- the Separator for ID in the openAPI specification file
            (ex: {id_} in GET api/labs/{id_})
        This id_separator value should be compilable into a regex for matching purposes.
    Returns (list(str), list(dict)) -- a tuple, the first value being the resource names in question
    while the second value is a list of restful routes in {'action': action, 'route': route} format
    """
    model_names = []
    non_model_routes = []
    for resource in resource_mapping.keys():
        # Only want resources where theres an "api_endpoint/{resource}/{id separator}" path.
        # this lets us avoid things like Version, Health, Auth etc
        # those avoided routes are appended to the non_model_routes object for future parsing
        # gosh these variable names need an update...
        current_resource_map = resource_mapping[resource]
        endpoint = current_resource_map.get("base_route")

        single_get_regex = re.compile("/".join([endpoint, id_separator]))

        resource_routes = current_resource_map.get("routes", [])
        resource_can_be_a_model = resource_can_make_a_model(
            resource_routes, endpoint, single_get_regex
        )

        if resource_can_be_a_model:
            model_names.append(resource)

        else:
            # add non restful routes
            for route in current_resource_map.get("routes", []):
                non_model_routes.append(route)
    return (model_names, non_model_routes)
