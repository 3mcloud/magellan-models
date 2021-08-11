"""
    Module for initializing with a API spec url
"""
from typing import Tuple
import requests
from magellan_models.config import MagellanConfig
from magellan_models.model_generator.generate_from_spec import generate_from_spec
from magellan_models.exceptions import MagellanParserException


def initialize_with_endpoint(
    api_spec_url: str, model_config: MagellanConfig = None
) -> Tuple[dict, dict, MagellanConfig]:
    """Generates models using an openapi spec URL, endpoint URL, and optional JWT token string

    Arguments:
        api_spec_url {str} -- URL to the specific openAPI yaml / json file
        model_config {MagellanConfig} -- a configuration instance

    Raises:
        Exception: Throws an exception if retrieving the openapi.json file errors out
    """
    if not model_config:
        model_config = MagellanConfig()

    spec_resp = requests.get(api_spec_url)
    if spec_resp.status_code != 200:
        raise MagellanParserException(
            f"Error retrieving the json schema. Error code: {spec_resp.status_code}"
        )

    return generate_from_spec(spec_resp.json(), configuration=model_config)
