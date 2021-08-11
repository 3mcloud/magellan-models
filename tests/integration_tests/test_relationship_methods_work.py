# pylint: skip-file
from tests.helper import get_testing_spec
import pytest


def test_faction_can_get_units_json(generated_models):
    Faction = generated_models["Faction"]
    fac = Faction()
    assert hasattr(fac, 'units_json') and callable(getattr(fac, 'units_json'))


def test_faction_has_add_unit_by_id(generated_models):
    Faction = generated_models["Faction"]
    fac = Faction()
    assert hasattr(fac, "add_unit") and callable(getattr(fac, "add_unit"))


def test_faction_has_remove_unit_by_id(generated_models):
    Faction = generated_models["Faction"]
    fac = Faction()
    assert hasattr(fac, "remove_unit") and callable(
        getattr(fac, "remove_unit"))


def test_faction_has_get_Units_method(generated_models):
    Faction = generated_models["Faction"]
    fac = Faction()
    assert hasattr(fac, "units") and callable(getattr(fac, "units"))


def test_faction_add_unit_by_id_modifies_representation(generated_models):
    Faction = generated_models["Faction"]
    fac = Faction()
    fac.add_unit("new id", additional_args={"role": "heavy support"})
    assert {"id": "new id",
            "type": "unit", "meta": {"role": "heavy support"}} in fac.representation["relationships"]["units"]["data"]

#
# Singular relationships now
#


def test_unit_can_get_faction_json(generated_models):
    Unit = generated_models["Unit"]
    un = Unit()
    assert hasattr(un, "faction_json") and callable(
        getattr(un, "faction_json"))


def test_unit_can_set_faction_by_id(generated_models):
    Unit = generated_models["Unit"]
    un = Unit()
    assert hasattr(un, "set_faction_id") and callable(
        getattr(un, "set_faction_id"))


def test_unit_can_set_faction_with_instance(generated_models):
    Unit = generated_models["Unit"]
    un = Unit()

    class FauxFaction(object):
        id = "foobar"
    faction = FauxFaction()
    un.set_faction(faction)
    assert un.faction_json() == {"type": "faction", "id": "foobar"}


def test_unit_set_faction_by_id_modifies_repr(generated_models):
    Unit = generated_models["Unit"]
    un = Unit()
    un.set_faction_id("foo")
    assert un.representation["relationships"]["faction"]["data"]["id"] == "foo"


#
# Downstream Functions Exist
#

def test_faction_has_downstream_method(generated_models):
    Faction = generated_models["Faction"]
    fac = Faction()
    assert "downstream_get_units" in dir(fac)
    assert (hasattr(fac, 'downstream_get_units')
            and callable(getattr(fac, 'downstream_get_units')))


def test_downstream_methods_call_correct_routes(generated_models, config, requests_mock):
    path = "/".join([config.api_endpoint, "factions", "fake_id", "units"])
    requests_mock.get(path, status_code=200, json={})
    Faction = generated_models["Faction"]
    fac = Faction()
    fac.id = "fake_id"
    fac.downstream_get_units()
    assert requests_mock.called


def test_downstream_list_works(generated_models):
    Faction = generated_models["Faction"]
    output = Faction.list_downstream_functions()
    assert 'downstream_get_units' in output


def test_downstream_list_works_for_unit_as_well(generated_models):
    Unit = generated_models["Unit"]
    output = Unit.list_downstream_functions()
    assert 'downstream_get_get_skus' in output


def test_relationships_list_wroks(generated_models):
    Faction = generated_models["Faction"]
    output = Faction.list_relationship_functions()
    assert 'units_json' in output
    assert "units" in output
    assert "add_unit" in output
    assert "remove_unit" in output
