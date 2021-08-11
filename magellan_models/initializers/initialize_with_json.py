"""
    Module for intiializing with a specification dict
"""
from magellan_models.config import MagellanConfig
from magellan_models.model_generator.generate_from_spec import generate_from_spec


def initialize_with_spec(open_api_spec: dict, model_config: MagellanConfig = None):
    """Initializes Magellan Models with a given OPEN API specification dict

    Args:
        open_api_spec (dict): OpenAPI spec json as a dict
        model_config (MagellanConfig, optional): A MagellanConfig (or inheriting class) instance
        containing settings and information for a given set of models. Defaults to None.
    """
    if not model_config:
        model_config = MagellanConfig()
    return generate_from_spec(open_api_spec, configuration=model_config)
