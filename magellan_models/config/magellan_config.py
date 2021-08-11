""" Main MagellanConfig definition class """
# pylint: disable=line-too-long
# pylint: disable=no-self-use

import json
from typing import Union, Tuple


class MagellanConfig:  # pylint: disable=too-many-instance-attributes
    """
    Master Config / Data Store for The Magellan module
    """

    def __init__(self):
        """
        Initializer
        """
        self.jwt = ""
        self.api_endpoint = "http://localhost:80/api/v1"

        self.experimental_functions = False

        # Make sure that this string when nested in to a regex functions properly
        self.id_separator = "{id_}"

        self.requests_args = {}
        self.header_args_separator = "header_args"
        self.function_naming_style = "pretty"  # "raw" or "pretty"

        self.params_args = [
            "sort"
        ]  # a list of whitelisted kwargs to send to the create_params functions

        # "warning" or "exception", if neither than no validation (set to "none" or something)
        self.validation_output = "warning"

        # Prints things like which models were generated and where the API points to during generation
        self.print_on_init = True

        # The attributes path dictates how to reach the layer of attributes for a given json schema object
        self.schema_attributes_path = (
            "properties",
            "data",
            "properties",
            "attributes",
            "properties",
        )

        # The relationships path tells us how to reach the layer of relationships for a given json schema object
        self.schema_relationships_path = (
            "properties",
            "data",
            "properties",
            "relationships",
            "properties",
        )

        # now these paths are for Magellan Models from a representation to the attribute
        # ex: if I want the title attribute, it should be under representation.get("attributes").get("title")
        # but if I want the "labs" relationship it's under representation.get("relationships").get("labs")
        self.model_attributes_path = ("attributes",)
        self.model_relationships_path = ("relationships",)

        self.disabled_functions = []

    def create_header(self, **kwargs) -> Tuple[dict, dict]:
        """

        Creates the basic Auth Header for all requests. Override this method (with accepting **kwargs) to change how the header should be formed

        Returns a tuple of dicts, the first being the header and the second being the kwargs
        kwargs should have the header_args_separator removed from it in this function
        If you don't, it'll be passed to other functions like the filtering function

        """
        header_args = (  # pylint: disable=unused-variable
            kwargs.pop(self.header_args_separator)
            if self.header_args_separator in kwargs
            else {}
        )

        # header_args is unused in this case, but can be if you override this function
        return ({"authorizationtoken": f"Bearer {self.jwt}"}, kwargs)

    def create_filters(  # pylint: disable=dangerous-default-value
        self, filtering_arguments: dict = {}, **kwargs
    ) -> dict:  # pylint: disable=dangerous-default-value
        """Initial Create function to make filters for a given GET request
        Currently this function defaults to the flask-rest-jsonapi example filtering

        https://flask-rest-jsonapi.readthedocs.io/en/latest/filtering.html

        Args:
            filtering_arguments (dict, optional): a mapping of the attribute name to the attribute's filter operation value. This is a String -> String mapping. Defaults to {}.
            If no key exists for a given attribute, the default value of "eq" is used

        Returns:
            {"filter": []}: A dict with the "filter" key pointing to a json dumped array of filtering operations
        """
        filters = []
        for attribute, value in kwargs.items():
            operation = filtering_arguments.get(attribute, "eq")
            filters.append({"name": attribute, "op": operation, "val": value})
        return {"filter": json.dumps([{"and": filters}])}

    def create_params(self, limit: int = None, **kwargs) -> dict:
        """Generates the params value to pass to the requests package a limit value, and arbitrary kwargs

        This function needs to pull out any value in the `params_args` attribute above from kwargs
        Then kwargs need to be passed to `create_filters` in order to generate any filters in params
        Finally if you have additional params to set up, you can add them to the output dict before returning the resulting params

        Args:
            limit (int, optional): A limit value specified in `where`. Defaults to None.
            kwargs (dict): kwargs (filtering args etc)

        Returns:
            dict: a set of params
        """
        param_args = {}
        for caught_arg in self.params_args:
            if caught_arg in kwargs:
                param_args[caught_arg] = kwargs.pop(caught_arg)

        params = self.create_filters(**kwargs)
        if limit:
            params["page[size]"] = limit
        if kwargs.get("sort"):
            params["sort"] = kwargs.get("sort")
        return params

    def api_response_to_representation(self, payload: dict) -> dict:
        """Converts the api response into a representation that's easily accessible

        Args:
            payload (dict): API response object

        Returns:
            dict: representation dict object
        """
        # if the response is nested inside "data", we get it, otherwise we return the response (say if it was pulled from an array)
        return payload.get("data", payload)

    def representation_to_api(self, representation: dict) -> dict:
        """Converts the model's internal representation into a json payload to send to the API

        Args:
            representation (dict): the internal representation of a model instance

        Returns:
            dict: the representation converted into an API expected format
        """

        return {"data": representation.get("data", representation)}

    def relationship_id_to_json_entry(
        self, relationship_id: str, **kwargs
    ) -> Union[dict, str]:
        """Converts a relationship ID into the format it's supposed to be stored in the relationships portion of the representation

        Args:
            relationship_id (str): ID being converted
        kwargs:
            relationship_type (str): The type of the object being added. This is specific for json:api
            additional_args (dict): A dictionary of additional arguments passed from other helper functions. Assume this defaults to {}
        Returns:
            Union[dict, str]: [description]
        """
        entry = {
            "id": relationship_id,
            "type": kwargs.get("relationship_type", "TypeUndefined"),
        }
        if kwargs.get("additional_args", False):
            entry["meta"] = kwargs.get("additional_args", {})
        return entry

    def get_list_from_resp(self, json_resp: dict) -> list:
        """Helper function to override for non json:api schema responses

        This function is called when parsing GET MANY requests, it takes the API response, and returns the list of "entities"
        if "data" is missing from the default function, an empty list is returned instead

        Args:
            json_resp (dict): json response object

        Returns:
            list: a list of entities that map to model instances
        """
        return json_resp.get("data", [])

    def get_next_link_from_resp(self, request_resp) -> str:
        """Helper function that takes a requests Response object
        and returns the next page to access for pagination

        By default this function follows JSON:API's method of following the "next" key value
        in the "links" object.

        Args:
            request_resp (requests.Response): A response object from a prior request

        Returns:
            str: The next URL to request to if we choose to follow the next page or
            None if the next URL doesn't exist
        """
        return request_resp.json().get("links", {}).get("next", None)

    def get_meta_data_from_resp(self, request_resp) -> dict:
        """Helper function for MagellanResponse, returns the metadata for a response

        Args:
            request_resp (requests.Response): a response object

        Returns:
            dict: a metadata dict (though technically any value is valid)
        """
        body = request_resp.json()
        return {"meta": body.get("meta", {}), "links": body.get("links", {})}
