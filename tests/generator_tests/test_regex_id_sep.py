from tests.helper import get_testing_spec
from magellan_models.initializers.initialize_with_endpoint import (
    initialize_with_endpoint,
)
from magellan_models.config import MagellanConfig
import re
from copy import deepcopy


def test_regex_id_sep_finds_and_parses_models(requests_mock):

    config = MagellanConfig()
    config.id_separator = "{(unitId|factionId)}"
    # deep copy because we have a reference
    spec = deepcopy(get_testing_spec())
    spec["paths"]["/factions/{factionId}"] = spec["paths"].pop("/factions/{id_}")
    spec["paths"]["/units/{unitId}"] = spec["paths"].pop("/units/{id_}")

    requests_mock.get(
        "http://localhost/api/v1/openapi.json", status_code=200, json=spec
    )
    models, funcs, config = initialize_with_endpoint(
        "http://localhost/api/v1/openapi.json", config
    )
    assert "Unit" in models.keys()
    assert "Faction" in models.keys()
