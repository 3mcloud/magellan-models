""" MagellanResponse definition file """
from __future__ import annotations
from typing import TYPE_CHECKING
import re
import requests
from magellan_models.config import MagellanConfig
from magellan_models.exceptions import MagellanRuntimeException

if TYPE_CHECKING:
    # see handling cyclical dependencies:
    # https://stackoverflow.com/questions/39740632/python-type-hinting-without-cyclic-imports
    from magellan_models.interface.abstract_api_model import AbstractApiModel


class MagellanResponse:  # pylint: disable=too-many-instance-attributes
    """The base Response class for Magellan calls to an API

    This is returned when a user calls `where` or 'query' (See ConstantMagellanResponse for query)

    """

    def __init__(
        self,
        url_path: str,
        Model: AbstractApiModel,
        config: MagellanConfig,
        limit: int = None,
        **kwargs
    ):
        """Initializer method for the MagellanResponse class

        Creates a MagellanResponse object, assigns basic information to it
        and evaluates the first page, adding results to the internal current_entities element

        Args:
            url_path (str): Base route for accessing a request
                (this will often not have any filters / additional params).
                By default this tends to be f"{api_path}/{resource}"
            Model (AbstractApiModel): The MagellanModel associated with this Response
                (assigned by the model itself)
            config (MagellanConfig): The MagellanConfig associated with the Model
                and therefore the Response
            limit (int, optional): [description]. Defaults to None.
            kwargs (dict): A dict of arguments,
                passed to the config's `create_params` function and create_header function
        """
        self.next_url = url_path
        self.__config__ = config
        self.__limit__ = limit  # if the limit is None it is limitless
        self.kwargs = kwargs
        # Everything here should be private (in theory)
        self.__iter_index__ = 0
        self.__current_entities__ = []  # store a list of models
        self.__Model__ = Model  # pylint: disable=invalid-name
        self.__meta_data__ = {}  # config sets this up on each page call
        self.__original_path__ = (
            url_path  # saved for when resetting due to chained where
        )

        # Process a page to start off the resposne lifecycle thingy
        self.process_next_page_of_results()

    def iteration_is_complete(self) -> bool:
        """Checks if iteration through the API response pages is complete

        Returns:
            bool: True if this MagellanResponse is done requesting data from the API,
                False otherwise
        """
        return len(self) == self.__limit__ or not self.next_url

    def evaluate_fully(self) -> None:
        """
        Evaluates every page of API results
        (potentially blocking the application depending on how many pages there are)

        returns None
        """
        while not self.iteration_is_complete():
            self.process_next_page_of_results()

    def process_next_page_of_results(self) -> None:
        """
        Calls the next_url route, parses entities,
        adds them to current_entities,
        sets the next_url route to hit (DOESN'T ACTUALLY REQUEST IT)
        and updates the meta_data
        Returns None
        If next_url is None, this function does NOTHING
        """
        if not self.next_url or self.iteration_is_complete():
            # Done iterating, next_url is None when we have no more results to get
            return

        (header, kwargs) = self.__config__.create_header(**self.kwargs)
        if len(self) == 0:  # first call
            parameters = self.__config__.create_params(self.__limit__, **kwargs)
            route = self.next_url
            resp = self.get_request(route, parameters, header)
            self.iterate_through_response(resp)
        else:
            resp = self.get_request(url=self.next_url, headers=header)
            self.iterate_through_response(resp)

        self.next_url = self.__config__.get_next_link_from_resp(resp)
        self.__meta_data__ = self.__config__.get_meta_data_from_resp(resp)

    def iterate_through_response(self, resp: requests.Response) -> None:
        """Iterates through a Requests Response element, appending values to current_entities

        Args:
            resp (requests.Response): A response from a request call
        """
        for payload in self.__config__.get_list_from_resp(resp.json()):
            if (
                self.__limit__ is None
                or len(self.__current_entities__) < self.__limit__
            ):
                self.__current_entities__.append(self.__Model__.from_json(payload))
            else:
                # Hit the limit!
                break

    def get_request(
        self, url: str, params={}, headers={}
    ):  # pylint: disable=dangerous-default-value
        """Helper method for all GET requests to a resource
        All 'requests_args' from the CONFIG object are passed in as arguments to the requests lib
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
            url, params=params, headers=headers, **self.__config__.requests_args
        )
        if resp.status_code != requests.codes.ok:  # pylint: disable=no-member
            raise MagellanRuntimeException(
                {"route": resp.url, "error_code": resp.status_code, "body": resp.json()}
            )
        return resp

    def __len__(self):
        """Return the lenght of the MagellanResponse
        This value is NOT the final length untless completed_iteration == True

        Returns:
            int: the number of elements currently stored in the MagellanResponse
        """
        return len(self.__current_entities__)

    def __getitem__(self, index):
        """A getter function to get an item at an index

        Args:
            index (int): an index

        Raises:
            IndexError: The item was not found because the MagellanResponse doesn't reach that index

        Returns:
            [AbstractApiModel]: The Magellan object at that index
        """
        try:
            return self.__current_entities__[index]
        except IndexError as ind_err:
            # we don't have that entity but it MIGHT exist in a later page.
            # We need to iterate through to find it
            if self.iteration_is_complete():
                raise IndexError from ind_err

            while len(self) < index + 1 and not self.iteration_is_complete():
                self.process_next_page_of_results()
            return self.__getitem__(index)

    def __setitem__(self, index, item):
        """If for some reason you want to set the value of an item at an index...

        Args:
            index (int): the index
            item ([AbstractApiModel]): the value you want to set at that index
        """
        # https://stackoverflow.com/questions/43627405/understanding-getitem-method
        self.__current_entities__[index] = item

    def __iter__(self):
        """A custom iter function that returns self

        Returns:
            MagellanResponse: A MagellanResponse instance (itself)
        """
        self.__iter_index__ = 0
        return self

    def __next__(self) -> AbstractApiModel:
        """__next__ method for iteration

        Returns:
            AbstractApiModel: [description]
        """
        if self.iteration_is_complete() and self.__iter_index__ >= len(self):
            # No more pages to get and the iteration has reached the end
            raise StopIteration

        elem = self.__getitem__(self.__iter_index__)
        self.__iter_index__ += 1
        return elem

    def __getattr__(self, name):
        """Overrides default getattr functionality to provide for "experimental" functionality

        Args:
            name (str): The name of the function or attribute getting called
        Returns:
            (any): the attribute or function returned if experimental features are enabled
        Raises:
            AttributeError: if the attribute still isn't found or experimental features are disabled
        """
        if self.__config__.experimental_functions:
            # experimental functions: `filter_title__eq(value="")`, `sort_by_title`

            filter_regex = re.compile("filter_(.*)__(.*)")
            simple_filter_regex = re.compile("filter_by_(.*)")
            sort_regex = re.compile("sort_by_(.*)")

            filter_match = filter_regex.fullmatch(name)
            if filter_match:
                # create wrapper function that calls where
                key = filter_match[1]
                attribute_operation = filter_match[2]

                def filter_func(value):
                    return self.where(
                        **{
                            key: value,
                            "filtering_arguments": {key: attribute_operation},
                        }
                    )

                return filter_func

            simple_filter_match = simple_filter_regex.fullmatch(name)
            if simple_filter_match:
                key = simple_filter_match[1]

                def simple_filter_func(val, filtering_arg="eq"):
                    return self.where(
                        **{key: val, "filtering_arguments": {key: filtering_arg}}
                    )

                return simple_filter_func

            sort_match = sort_regex.fullmatch(name)
            if sort_match:
                # create wrapper function that calls sort
                key = sort_match[1]

                def sort_func():
                    return self.where(sort=key)

                return sort_func

        raise AttributeError()

    def get_meta_data(self):
        """Returns the meta_data for a given MagellanResponse Object

        Returns:
            [dict]: the meta data from the last API call
        """
        return self.__meta_data__

    def where(self, **kwargs) -> MagellanResponse:
        """Chain multiple Where clauses with this helper function

        This call IS DESTRUCTIVE and resets the internal store of Magellan Models
        stored in the MagellanResponse
        this prevents pollution inside the internal data structures

        if you want to just update the limit, just call limit() instead
        which truncates elements instead of resetting everything

        Returns:
            MagellanResponse: returns self with modified kwargs and/or limit
        """

        # Check if filtering_arguments are provided
        # update them first to prevent overwriting
        if "limit" in kwargs.keys():
            self.__limit__ = kwargs.pop("limit", None)

        if "filtering_arguments" in kwargs.keys():
            # update the filtering_arguments to augment them instead of replacement
            new_filtering_args = kwargs.pop("filtering_arguments")
            original_filtering_args = self.kwargs.get("filtering_arguments", {})
            original_filtering_args.update(new_filtering_args)
            self.kwargs["filtering_arguments"] = original_filtering_args

        self.kwargs.update(kwargs)

        # We've updated our internal kwargs, this means we need to reset our state
        self.__iter_index__ = 0
        self.__current_entities__ = []
        self.next_url = self.__original_path__

        # time to get new results and return self
        self.process_next_page_of_results()
        return self

    def limit(self, new_limit) -> MagellanResponse:
        """Modifies this request's internal limit value

        This call will truncate the internal representation
        if the new limit is smaller than the previous one

        If the new limit is larger than the previous one, this call is destructive
        (otherwise it'll potentially get stuck thinking it's done iterating when it's not)

        Args:
            new_limit (int): The new limit to set for this MagellanResponse

        Returns:
            MagellanResponse: The original MagellanResponse post modifications
        """

        self.__limit__ = new_limit
        if self.__limit__ < len(self):
            # truncate current_entities
            self.__current_entities__ = self.__current_entities__[0 : self.__limit__]
        else:
            # new limit is larger than the original, destructive op
            self.__iter_index__ = 0
            self.__current_entities__ = []
            self.next_url = self.__original_path__
            self.process_next_page_of_results()
        return self
