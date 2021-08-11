import pytest
from tests.helper import get_testing_spec
from magellan_models.initializers.initialize_with_endpoint import (
    initialize_with_endpoint,
)
from magellan_models.config import MagellanConfig
from magellan_models.exceptions import MagellanParserException
import re


def test_initialize_with_endpoint_generates_models(requests_mock):
    config = MagellanConfig()
    config.id_separator = re.escape("{id_}")
    config.jwt = "Token"

    requests_mock.get(
        "http://localhost/api/v1/openapi.json", status_code=200, json=get_testing_spec()
    )
    models, funcs, config = initialize_with_endpoint(
        "http://localhost/api/v1/openapi.json", config
    )
    Faction = models["Faction"]
    Unit = models["Unit"]
    assert Faction.resource_name()
    assert "id" in Faction.list_attributes()
    assert "title" in Faction.list_attributes()
    assert "keywords" in Faction.list_attributes()
    assert Unit.resource_name()
    assert Faction.list_attributes()
    assert Unit.list_attributes()
    assert "id" in Unit.list_attributes()
    assert "title" in Unit.list_attributes()
    assert "keywords" in Unit.list_attributes()
    assert requests_mock.called
    assert requests_mock.call_count == 1


def test_init_with_invalid_naming_fails(requests_mock):
    config = MagellanConfig()
    config.id_separator = re.escape("{id_}")
    config.jwt = "Token"
    config.function_naming_style = "baaaaah don't do it"
    requests_mock.get(
        "http://localhost/api/v1/openapi.json", status_code=200, json=get_testing_spec()
    )

    with pytest.raises(MagellanParserException):
        models, funcs, config = initialize_with_endpoint(
            "http://localhost/api/v1/openapi.json", config
        )
    assert True
