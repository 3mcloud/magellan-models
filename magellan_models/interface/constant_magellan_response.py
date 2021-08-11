""" ConstantMagellanResponse definition file """
from __future__ import annotations
from typing import TYPE_CHECKING
from magellan_models.interface.magellan_response import MagellanResponse
from magellan_models.config import MagellanConfig
from magellan_models.exceptions import MagellanRuntimeException

if TYPE_CHECKING:
    from magellan_models.interface.abstract_api_model import AbstractApiModel


class ConstantMagellanResponse(MagellanResponse):
    """This is the immutable MagellanResponse returned by `query` calls"""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        url_path: str,
        raw_params: dict,
        Model: AbstractApiModel,
        config: MagellanConfig,
        limit: int = None,
        **kwargs
    ) -> ConstantMagellanResponse:
        """Generates a new ConstantMagellanResponse

        Args:
            url_path (str): The base path to start with (See MagellanResponse)
            raw_params (dict): The raw params passed to `query`
            Model (AbstractApiModel): A MagellanModel
            config (MagellanConfig): A MagellanConfig associated with the model
            limit (int, optional): The limit for the number of responses. Defaults to None.

        Returns:
            ConstantMagellanResponse: [description]
        """
        self.raw_params = raw_params
        super().__init__(url_path, Model, config, limit, **kwargs)

    def process_next_page_of_results(self):
        """Processes the next page of results using the internal parameters"""
        if self.next_url is None or self.iteration_is_complete():
            # Done iterating, next_url is None when we have no more results to get
            return

        header_and_args = self.__config__.create_header(**self.kwargs)
        header = header_and_args[0]
        if len(self) == 0:  # first call
            route = self.next_url
            resp = self.get_request(route, self.raw_params, header)
            self.iterate_through_response(resp)
        else:
            resp = self.get_request(url=self.next_url, headers=header)
            self.iterate_through_response(resp)

        self.next_url = self.__config__.get_next_link_from_resp(resp)
        self.__meta_data__ = self.__config__.get_meta_data_from_resp(resp)
        return

    def where(self, **kwargs):
        raise MagellanRuntimeException("You can't chain on a ConstantMagellanResponse")

    def __getattr__(self, name):
        raise AttributeError()

    def limit(self, new_limit):
        raise MagellanRuntimeException(
            "You can't set a new limit on a ConstantMagellanResponse"
        )
