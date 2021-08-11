""" Module to generate the generic API call function """
import requests


def get_generic_function(configuration):
    """Returns a generic requests querying function that calls whatever path the user passes in.
    Takes in a configuration object to ensure that this function remains in sync with the config

    Args:
        configuration (MagellanConfig): a MagellanConfig instance used by the rest of the API
    """

    def nonunique_func(
        path, method="GET", request_body={}, **kwargs
    ):  # pylint: disable=dangerous-default-value
        """Makes a request to a given path
        This function has very little additional functionality or help
        All it'll do for you is generate a route and a header
        The rest is up to you

        Args:
            path (str): API path after teh config's API endpoint value. May need to begin with a "/"
            method (str, optional): HTTP request type. Defaults to "GET".
            request_body (dict, optional): JSON request body if relevant. Defaults to {}.

        Returns:
            [type]: [description]
        """
        header, kwargs = configuration.create_header(**kwargs)
        api_route = f"{configuration.api_endpoint}{path}"

        if method == "GET":
            return requests.get(
                api_route,
                json=request_body,
                headers=header,
                **kwargs,
                **configuration.requests_args,
            )
        if method == "DELETE":
            return requests.delete(
                api_route,
                json=request_body,
                headers=header,
                **kwargs,
                **configuration.requests_args,
            )
        if method == "POST":
            return requests.post(
                api_route,
                json=request_body,
                headers=header,
                **kwargs,
                **configuration.requests_args,
            )
        if method == "PATCH":
            return requests.patch(
                api_route,
                json=request_body,
                headers=header,
                **kwargs,
                **configuration.requests_args,
            )
        return None

    return nonunique_func
