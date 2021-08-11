""" Generates the non rest functions unassociated with Magellan Models """
import re
from warnings import warn
from typing import Tuple, Callable, List
import requests
from jsonschema import validate, ValidationError
from magellan_models.exceptions import (
    MagellanParserException,
    MagellanRuntimeWarning,
    MagellanRuntimeException,
)


def get_function_name_and_params_from_path(
    path: dict, naming_method: str
) -> Tuple[str, List[str]]:
    """creates a function name for a non restful route and returns the input parameters expected

    Ex: {action: "get", route: "/healthcheck"} would yield 'get_from_healthcheck(req_body)'

    Args:
        path (dict(action: str, route: str), request_schema: dict): a route dict
        naming_method: str either "pretty" or "raw"
    """
    action = path["action"]
    path_elements = path["route"].split("/")
    # ignore [0] because it'll be empty due to prepended "/"
    main_path = path_elements[1]
    potential_params = path_elements[2:]
    param_names = []
    non_params = []
    for param in potential_params:
        match = re.match("{(.*)}", param)
        if match:
            param_names.append(match.group(1))
        else:
            non_params.append(param)

    name = ""
    if naming_method == "pretty":
        non_params_string = ""
        if len(non_params) > 0:
            non_params_string = "_" + "_".join(non_params)

        if len(param_names) > 0:
            name = f"{action}_{'from' if action == 'get' else 'to'}_{main_path}{non_params_string}_with_{'_'.join(param_names)}"  # pylint: disable=line-too-long
        else:
            # TODO: TA: should mainpath here be "_".join(path_elements)
            name = f"{action}_{'from' if action == 'get' else 'to'}_{main_path}{non_params_string}"
    elif naming_method == "raw":
        name = f"{action.upper()} {path['route']}"
    else:
        raise MagellanParserException("naming_method must be 'raw' or 'pretty'")
    return name, param_names


def generate_func_for_route(route: dict, configuration) -> Tuple[str, Callable]:
    """Generates a function to access a given route

    Args:
        route (dict["str" => "str"]): a non restful route declaration parsed earlier.
            includes a "action" and a "route" key along with a "request_schema" => dict key
        configuration (MagellanConfig): A magellanConfig that's user defined

    Returns:
        tuple(str, Callable): a function name and the function associated / generated
    """
    (func_name, params) = get_function_name_and_params_from_path(
        route, configuration.function_naming_style
    )

    def semi_anon_function(  # pylint: disable=dangerous-default-value
        request_body={},
        __param_names=tuple(params),
        action=route["action"],
        function_path=route["route"],
        request_schema=route.get("request_schema", {}),
        **kwargs,
    ):
        header, kwargs = configuration.create_header(**kwargs)
        api_route = f"{configuration.api_endpoint}{function_path}"
        for param_name in __param_names:
            # This is such a hack for now... triple curlies to render "{keyname}"
            api_route = api_route.replace(f"{{{param_name}}}", kwargs.pop(param_name))

        # Validation block
        try:
            validate(request_body, request_schema)
        except ValidationError as validation_err:
            if configuration.validation_output == "warning":
                warn(validation_err.message, MagellanRuntimeWarning)
            elif configuration.validation_output == "exception":
                raise (
                    MagellanRuntimeException(validation_err.message)
                ) from validation_err

        # by now kwargs should have popped out all param_names, and header_args
        # We should let users pass in anything else to the requests library they would want
        if action == "get":
            return requests.get(
                api_route,
                json=request_body,
                headers=header,
                **kwargs,
                **configuration.requests_args,
            )
        if action == "delete":
            return requests.delete(
                api_route,
                json=request_body,
                headers=header,
                **kwargs,
                **configuration.requests_args,
            )
        if action == "post":
            return requests.post(
                api_route,
                json=request_body,
                headers=header,
                **kwargs,
                **configuration.requests_args,
            )
        if action == "patch":
            return requests.patch(
                api_route,
                json=request_body,
                headers=header,
                **kwargs,
                **configuration.requests_args,
            )
        if action == "put":
            return requests.put(
                api_route,
                json=request_body,
                headers=header,
                **kwargs,
                **configuration.requests_args,
            )
        return None

    return (func_name, semi_anon_function)
