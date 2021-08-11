import pytest
from tests.helper import get_testing_spec
from magellan_models.initializers.initialize_with_endpoint import (
    initialize_with_endpoint,
)
from magellan_models.config import MagellanConfig
from magellan_models.exceptions import MagellanRuntimeException
import re


def test_initialize_with_endpoint_generates_models(requests_mock):
    config = MagellanConfig()
    config.id_separator = re.escape("{id_}")
    config.jwt = "Token"
    config.disabled_functions = ["post", "delete", "find"]

    requests_mock.get(
        "http://localhost/api/v1/openapi.json", status_code=200, json=get_testing_spec()
    )
    models, funcs, config = initialize_with_endpoint(
        "http://localhost/api/v1/openapi.json", config
    )
    Faction = models["Faction"]
    with pytest.raises(MagellanRuntimeException):
        Faction.find("123")
    assert True
