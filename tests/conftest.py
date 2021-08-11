from magellan_models import MagellanConfig
import pytest
from unittest.mock import patch
from magellan_models.initializers import initialize_with_spec
from .helper import get_testing_spec


@pytest.fixture(scope="module")
def conf():
    endpoint_url = "https://localhost:3000/api/v1"
    conf = MagellanConfig()
    conf.api_endpoint = endpoint_url
    return conf


@pytest.fixture(scope="module")
def generated_models(conf):
    (models, funcs, config) = initialize_with_spec(get_testing_spec(), conf)
    return models


@pytest.fixture(scope="module")
def generated_funcs(conf):
    (models, funcs, config) = initialize_with_spec(get_testing_spec(), conf)
    return funcs


@pytest.fixture(scope="module")
def config(conf):
    # this is the linked Config from generation
    (models, funcs, config) = initialize_with_spec(get_testing_spec(), conf)
    return config
