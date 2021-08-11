"""
    Yaml based initialization module
"""
import yaml
import requests
from magellan_models.config import MagellanConfig
from magellan_models.model_generator.generate_from_spec import generate_from_spec
from magellan_models.exceptions import MagellanParserException


def initialize_with_yaml_file(path: str, model_config: MagellanConfig = None):
    """Initializes Magellan with a yaml file path

    Args:
        path (str): The path to a yaml file
        model_config (MagellanConfig, optional): A Magellan Config instance. Defaults to None.

    Returns:
        [type]: [description]
    """
    if not model_config:
        model_config = MagellanConfig()

    with open(path) as yaml_file:
        specification = yaml.load(yaml_file, Loader=yaml.FullLoader)
        return generate_from_spec(specification, configuration=model_config)


def initialize_with_yaml_url(api_spec_url: str, model_config: MagellanConfig = None):
    """Initializes Magellan with a Yaml URL

    Args:
        api_spec_url (str): the URL path to a YAML file
        model_config (MagellanConfig, optional): The Magellan Config object. Defaults to None.

    Raises:
        MagellanParserException: Raises if the request fails

    Returns:
        tuple(dict, dict): The Magellan objects and functions generated
    """
    if not model_config:
        model_config = MagellanConfig()

    spec_resp = requests.get(api_spec_url)
    if spec_resp.status_code != 200:
        raise MagellanParserException(
            f"Error retrieving the json schema .yaml. Error code: {spec_resp.status_code}"
        )

    return generate_from_spec(
        yaml.load(spec_resp.content, Loader=yaml.FullLoader), configuration=model_config
    )
