"""
    Helper functions that are stored in a separate file to prevent circular dependencies
"""


def get_routes(open_api_spec: dict) -> list:
    """Returns the specific route names for an openapi spec

    Args:
        open_api_spec (dict): an OpenAPI specification

    Returns:
        list: a list of strings representing the paths found,
        no information about what methods are available for a path are returned
    """
    return open_api_spec["paths"].keys()


def get_endpoints(open_api_spec: dict) -> set:
    """Returns a set of endpoints
    an endpoint is a path or collection of paths where the first "element'
        when separated off of "/"s is the same

    Args:
        open_api_spec (dict): and OpenAPI specification

    Returns:
        set: a set of endpoints
    """
    routes = get_routes(open_api_spec)
    endpoints = set()
    for key in routes:
        endpoints.add("/" + key.split("/")[1])
    return endpoints


def get_reference_value_from_spec(openapi_spec: dict, reference_path: str) -> dict:
    """Follows the reference path passed in and returns the object at the end of the path

    Args:
        openapi_spec (dict): The openapi.json specification object
        reference_path (str): a path formatted as "#/foo/bar/baz"

    Returns:
        dict: The object if you follow the path
    """
    path_elements = reference_path.split("/")
    reference_val = openapi_spec

    for elem in path_elements:
        if elem == "#":
            continue
        else:
            reference_val = reference_val.get(elem, {})
    return reference_val
