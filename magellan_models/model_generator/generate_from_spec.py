"""
    Main entry point for Parser and model generator
"""
from typing import Tuple
import inflection
from magellan_models.config import MagellanConfig
from .openapi_parser import (
    get_resource_mapping,
    parse_resource_names_and_other_routes_from_mapping,
)
from .model_parser import get_model_representation
from .generate_dynamic_model import generate_model
from .generate_nonrest_functions import generate_func_for_route
from .generic_functions_generator import get_generic_function


def generate_from_spec(
    spec: dict, configuration: MagellanConfig
) -> Tuple[dict, dict, MagellanConfig]:
    """Generates Models from an OpenAPI specification json body
    These models are defined via the template file under templates
    and inherit from the abstractApiModel class

    upon generation, models can be imported via src.models.endpoint_models

    Arguments:
        spec {Dict} -- Dict representation of the open api specification json
        configuration {MagellanConfig} -- Configuration instance containing user settings
    Output:
        tuple(dict, dict, MagellanConfig)
            First dict: str => AbstractApiModel mapping of class names to Models
            Second dict: str => function, a mapping of non-Model functions that are accessible.
            MagellanConfig: configuration instance linked to all Models and Functions generated
    """
    resource_mapping = get_resource_mapping(spec)
    resource_names, other_routes = parse_resource_names_and_other_routes_from_mapping(
        resource_mapping, configuration.id_separator
    )
    model_representations = []
    model_names = []
    for resource_name in resource_names:
        model_names.append(inflection.camelize(inflection.singularize(resource_name)))
        model_representations.append(
            get_model_representation(spec, resource_name, configuration)
        )
    model_definitions = {}
    for repres in model_representations:
        model_definitions[repres["class_name"]] = generate_model(
            repres, model_names, model_definitions, configuration
        )

    functional_routes = {}
    for route in other_routes:
        func_name, function = generate_func_for_route(route, configuration)
        functional_routes[func_name] = function
    functional_routes["_generic_api_function"] = get_generic_function(configuration)

    if configuration.print_on_init:
        print("Completed Model and Function Generation")
        print("The following Models were generated:")
        for key in model_definitions:
            print(key)
        print("The following Functions were generated:")
        for key in functional_routes:
            print(key)
        print(
            "You can access https://github.mmm.com/MMM/magellan/tree/master/docs for the latest Documentation"  # pylint: disable=line-too-long
        )

    return (model_definitions, functional_routes, configuration)
