# pylint: skip-file
from tests.helper import get_testing_spec
import pytest
from magellan_models.initializers import initialize_with_spec
from unittest.mock import MagicMock, patch
from magellan_models.interface import AutoDict


def test_auto_dict_searches_when_not_exists(generated_models, requests_mock):
    Faction = generated_models["Faction"]
    faction_dict = AutoDict(Faction)
    route = "/".join(
        [Faction.configuration().api_endpoint, Faction.resource_name(), "fake_id"]
    )
    requests_mock.get(
        route, status_code=200, json={"data": {"attributes": {"title": "found it!"}}}
    )
    faction_dict["fake_id"]
    assert requests_mock.called


def test_auto_dict_searches_only_once(generated_models, requests_mock):
    Faction = generated_models["Faction"]
    faction_dict = AutoDict(Faction)
    route = "/".join(
        [Faction.configuration().api_endpoint, Faction.resource_name(), "fake_id"]
    )
    requests_mock.get(
        route, status_code=200, json={"data": {"attributes": {"title": "found it!"}}}
    )
    faction_dict["fake_id"]
    assert requests_mock.called

    faction_dict["fake_id"]
    assert requests_mock.called_once
    assert requests_mock.call_count == 1
