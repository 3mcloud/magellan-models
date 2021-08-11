""" Abstract API Model class definition file """

# Automagic attributes on requests cause pylint warnings so I'm disabling no-member
# pylint: disable=dangerous-default-value, no-member
from abc import ABC, abstractmethod
from typing import Any, Union
from warnings import warn
from jsonschema import validate, ValidationError
import requests
from magellan_models.exceptions import MagellanRuntimeException, MagellanRuntimeWarning
from magellan_models.config import MagellanConfig
from magellan_models.interface.magellan_response import MagellanResponse
from magellan_models.interface.constant_magellan_response import (
    ConstantMagellanResponse,
)


class AbstractApiModel(ABC):  # pylint: disable=too-many-public-methods
    """The AbstractApiModel is the main template for each Magellan Model

    Any models generated via the initializers will inherit from AbstractApiModel

    """

    @staticmethod
    @abstractmethod
    def resource_name() -> str:
        """
        Resource Name defining the endpoint we want to hit
        example: http://example-api-url.com/api/v1/${this value here}/misc_args
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_post_schema() -> dict:
        "Returns the POST request's requestBody schema for this resource"
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_patch_schema() -> dict:
        "Returns the PATCH request's requestBody schema for this resource"
        raise NotImplementedError

    @classmethod
    def convert_representation(cls, representation: dict) -> dict:
        """Converts the Representation dict into the format the API expects.
        You can override this by changing the config's representation_to_api function
        Arguments:
            representation {dict} -- Internal instance representation

        Returns:
            [dict] -- [data matching API expectations]
        """
        return cls.configuration().representation_to_api(representation)

    @staticmethod
    @abstractmethod
    def list_attributes() -> None:
        """Returns a dictionary of key value pairs where the key maps to the Attribute name,
        and value corresponds to the data type of the attribute

        Returns:
            [attributes] -- [dict]
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def configuration() -> MagellanConfig:
        """Return the MagellanConfiguration instance associated with this class
        This is set during runtime initialization of each model
        And contains settings regarding how the response schema is set up, the API endpoint, etc

        Raises:
            NotImplementedError
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def id(self):
        "Resources require some sort of ID"
        raise NotImplementedError

    @id.setter
    def id(self, newval):  # pylint: disable=no-self-use
        """Raises an error if you try to set the ID field

        Arguments:
            newval {str} -- [new ID a user is trying to set up]
        """
        raise MagellanRuntimeException("ID should only be set by the backend")

    @classmethod
    def find(cls, id: str, **kwargs):
        """
        Class Method that facilitates GET queries between the API and the client

        This is useful for things like hitting /api/model/uuid with a GET request

        returns a class instance if the resource returns an object matching the ID,
        or None if the response 404s.
        Raises if any other status code beyond OK or 404 is hit
        """
        (header, kwargs) = cls.configuration().create_header(**kwargs)
        api_endpoint = cls.configuration().api_endpoint
        resp = cls.get_request(
            f"{api_endpoint}/{cls.resource_name()}/{id}", headers=header
        )
        # get_request throws an exception if the status code isn't OK,
        # so we can assume if we reach this bottom line that the response is fine
        return cls.from_json(resp.json())

    @classmethod
    def query(cls, parameters={}, limit=None, **kwargs) -> ConstantMagellanResponse:
        """
        Method that takes in a list of filters and returns a page of parsed object instances
        inputs:
            parameters: dict (default {}): a dict object mapping parameter key value pairs.
            Specify things like page_number or page_size here
            limit: int (default None): The limit for how many results to return (defaults to None)
        output:
            ConstantMagellanResponse: A MagellanResponse object without chaining support
        """
        api_endpoint = cls.configuration().api_endpoint
        route = f"{api_endpoint}/{cls.resource_name()}"
        return ConstantMagellanResponse(
            route, parameters, cls, cls.configuration(), limit, **kwargs
        )

    @classmethod
    def where(cls, limit=None, **kwargs) -> MagellanResponse:
        """ActiveRecord inspired 'where' method that takes in a set of attribute assignments
        and converts them into filters.
        By default, all attributes are filtered using the "eq" operation.

        You can optionally pass in a dict for 'filtering_arguments'
        which is a mapping of attributes (as strings) to operations (as strings).
        This only works if you haven't overridden the filtering mechanism provided by default
        an example of this usage:
            Model.where(title="blahblahblah",
                       filtering_arguments={"title": "ilike"})
        In this instance, we'll use the ilike operation to match the passed
        "blahblahblah" value on the back end.
        Excluding the filtering_arguments dict
        or not including an attribute in the dict will lead to a default value of "eq"

        Keyword Arguments:
            limit {int} -- [Number of entities to return. If this limit isn't reached
                in a single GET call, additional calls to the server will occur] (default: {None})
            header_args {Dict} -- A list of arguments specific for creating a header.
                This defaults to empty but if you need to generate a header, pass arguments in here
            **kwargs {any} -- Arguments mapping {attribute}={value},
                additionally the "sort" kwarg can be set to define ordering

        Returns:
            entities {MagellanResponse} -- A MagellanResponse object
        """
        route = f"{cls.configuration().api_endpoint}/{cls.resource_name()}"
        return MagellanResponse(
            url_path=route, Model=cls, config=cls.configuration(), limit=limit, **kwargs
        )

    @classmethod
    def get_request(cls, url: str, params={}, headers={}):
        """Helper method for all GET requests to a resource
        All 'requests_args' from the CONFIG object are passed in
            as arguments to the requests library
        Arguments:
            url {str} -- The full URL to send a get request to
            params {dict} -- parameters being passed into the request
            headers {dict} -- headers for the request
        Returns:
            requests Response object

        Raises:
            Exception if server response is not an OK status
        """
        resp = requests.get(
            url, params=params, headers=headers, **cls.configuration().requests_args
        )
        if resp.status_code != requests.codes.ok:
            raise MagellanRuntimeException(
                {"route": resp.url, "error_code": resp.status_code, "body": resp.json()}
            )
        return resp

    @classmethod
    def delete(cls, id: str, **kwargs) -> None:
        "sends a delete request for a given object id"
        api_endpoint = cls.configuration().api_endpoint

        header, kwargs = cls.configuration().create_header(**kwargs)

        resp = requests.delete(
            f"{api_endpoint}/{cls.resource_name()}/{id}", headers=header
        )
        if resp.status_code == requests.codes.ok:
            return
        raise MagellanRuntimeException(
            {"route": resp.url, "error_code": resp.status_code, "body": resp.json()}
        )

    def delete_self(self, **kwargs) -> None:
        """
        sends a delete request for an instance of an object.
        This object instance will still exist in the python interpreter,
        but the backend will have deleted the record
        """
        return self.__class__.delete(self.id, **kwargs)

    def patch(self, **kwargs) -> None:
        """
        Send a PATCH request to the backend with the current object's JSON
        If successful, we update the instance's internal representation with the server response
        """
        api_endpoint = self.configuration().api_endpoint
        endpoint_url = f"{api_endpoint}/{self.resource_name()}/{self.id}"

        header, kwargs = self.configuration().create_header(**kwargs)

        payload = self.convert_representation(self.representation)
        self.__class__.validate_payload(payload, self.get_patch_schema())

        resp = requests.patch(endpoint_url, json=payload, headers=header)
        if resp.status_code != requests.codes.ok:
            raise MagellanRuntimeException(
                {"route": resp.url, "error_code": resp.status_code, "body": resp.json()}
            )
        self.representation = self.__class__.from_json(resp.json()).representation

    @classmethod
    def validate_payload(cls, payload: dict, validation_schema: dict) -> None:
        """Validates a payload against a schema
         raises MagellanRuntime Exceptions or Warnings depending on config

        Args:
            payload (dict): the payload to validate
            validation_schema (dict): json schema to compare against

        Raises:
            MagellanRuntimeException: Exception with validation errors
            MagellanRuntimeWarning: Warning with validation errors

        Returns:
            None: None
        """
        try:
            validate(payload, validation_schema)
        except ValidationError as validation_err:
            if cls.configuration().validation_output == "warning":
                warn(validation_err.message, MagellanRuntimeWarning)
            elif cls.configuration().validation_output == "exception":
                raise (
                    MagellanRuntimeException(validation_err.message)
                ) from validation_err

    @classmethod
    def post_payload(cls, payload, **kwargs):
        """
        Posts the raw json payload and returns an instance of the record if successful
        """
        cls.validate_payload(payload, cls.get_post_schema())

        header, kwargs = cls.configuration().create_header(**kwargs)
        api_endpoint = cls.configuration().api_endpoint
        resp = requests.post(
            f"{api_endpoint}/{cls.resource_name()}", json=payload, headers=header
        )
        if (
            resp.status_code != requests.codes.created
            and resp.status_code != requests.codes.ok
        ):
            raise MagellanRuntimeException(
                {"route": resp.url, "error_code": resp.status_code, "body": resp.json()}
            )
        return cls.from_json(resp.json())

    def post(self, **kwargs):
        """Sends a POST request with the model instance's internal representation as a payload.
            If the POST is successful, this updates the instance's internal representation
            with the payload return values

        Raises:
            RuntimeError: [description]
        """
        if self.id:
            raise MagellanRuntimeException("Can't post if already have an assigned ID")
        new_instance = self.__class__.post_payload(
            self.__class__.convert_representation(self.representation), **kwargs
        )

        self.representation = new_instance.representation

    def sync(self, **kwargs):
        """Makes a GET call to the resource/{id} route
        and updates this instance's internal representation with the response.
        This is useful when data may have come out of sync,
        or relationships are updated via other Model class instances

        This is an overwriting operation!
        If you made changes to an instance and haven't patched them,
        your changes will be overwritten with the server response

        Returns:
            None: [None]
        """
        if not self.id:
            raise MagellanRuntimeException("Can't sync without an assigned ID")
        backend_instance = self.__class__.find(self.id, **kwargs)
        self.representation = backend_instance.representation

    @property
    @abstractmethod
    def representation(self):
        """
        JSON serialized representation of the model instance.
        This should conform / match the specs of the server response
        for a singular instance of a resource

        This is also the root source of truth for all attributes and resources
        """
        raise NotImplementedError

    @representation.setter
    @abstractmethod
    def representation(self, new_representation):
        """
        Set the representation of an instance.
        """
        raise NotImplementedError

    def relationships(self):
        "returns a raw list of relationships between self and other entities"
        return self.get_instance_relationships()

    @classmethod
    def from_json(cls, payload):
        "Creates an instance object via an open api json response"
        instance = cls()
        instance.representation = cls.configuration().api_response_to_representation(
            payload
        )
        return instance

    def get_instance_attribute(self, attribute_name: str) -> Union[Any, None]:
        """Helper function to get the instance model attribute specified.
        This is helpful because a model might have a custom path to
        the attributes object of its representation.
        This method traverses that path, and then searches for the attribute
        key and returns the value, or None if the value is missing

        Args:
            attribute_name (str): The name of the attribute being searched

        Returns:
            Union[Any, None]: The value of the attribute, or None if the attribute is missing
        """
        attr_object = self.representation
        for stepping in self.configuration().model_attributes_path:
            attr_object = attr_object.get(stepping, {})
        return attr_object.get(attribute_name, None)

    def set_instance_attribute(self, attribute_name: str, attribute_value: Any) -> None:
        """Set an instance object's attribute value for a given attribute name.
        Used internally by the setter functions

        Args:
            attribute_name (str): name of the attribute
            attribute_value (Any): [value you want to set]
        """
        attr_object = (
            self.representation
        )  # woohoo attr_object is assigned by reference not value!
        for stepping in self.configuration().model_attributes_path:
            attr_object = attr_object.get(stepping, {})
        attr_object[attribute_name] = attribute_value

    def get_instance_relationships(self) -> dict:
        """Gets the relationships object by traversing down the representation path as needed

        Returns:
            Dict: the relationships object
        """
        relationships_object = self.representation
        for stepping in self.configuration().model_relationships_path:
            relationships_object = relationships_object.get(stepping, {})
        return relationships_object

    def get_instance_relationship_value(
        self, relationship_name: str
    ) -> Union[Any, None]:
        """Returns a given relationship from the instance relationships

        Args:
            relationship_name (str): name of relationships

        Returns:
            Union[Any, None]: relationship object value for the name, could be a single value
            or list of values or None if it's not set
        """
        relationships_object = self.representation
        for stepping in self.configuration().model_relationships_path:
            relationships_object = relationships_object.get(stepping, {})
        return relationships_object.get(relationship_name, None)

    def set_instance_relationship_value(
        self, relationship_name: str, relationship_value: Any
    ) -> None:
        """Sets the instance's relationship object's value such that the relationship_name
        key yields the relationship_value

        Args:
            relationship_name (str): name of the relationship
            relationship_value (Any): new value to set it to.
        """
        relationships_object = self.representation
        for stepping in self.configuration().model_relationships_path:
            relationships_object = relationships_object.get(stepping, {})
        relationships_object[relationship_name] = relationship_value
