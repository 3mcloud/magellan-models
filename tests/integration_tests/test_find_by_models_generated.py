# pylint: skip-file
from tests.helper import get_testing_spec
import pytest

def test_can_find_by_id(generated_models):
    Faction = generated_models["Faction"]
    assert hasattr(Faction, 'find_by_id') and callable(getattr(Faction, 'find_by_id'))

def test_can_find_by_title(generated_models):
    Faction = generated_models["Faction"]
    assert hasattr(Faction, 'find_by_title') and callable(getattr(Faction, 'find_by_title'))

def test_can_find_by_description(generated_models):
    Faction = generated_models["Faction"]
    assert hasattr(Faction, 'find_by_description') and callable(getattr(Faction, 'find_by_description'))

def test_can_find_by_keywords(generated_models):
    Faction = generated_models["Faction"]
    assert hasattr(Faction, 'find_by_keywords') and callable(getattr(Faction, 'find_by_keywords'))

def test_can_find_unit_by_id(generated_models):
    Unit = generated_models["Unit"]
    assert hasattr(Unit, 'find_by_id') and callable(getattr(Unit, 'find_by_id'))

def test_can_find_by_unit_title(generated_models):
    Unit = generated_models["Unit"]
    assert hasattr(Unit, 'find_by_title') and callable(getattr(Unit, 'find_by_title'))

def test_can_find_by_unit_description(generated_models):
    Unit = generated_models["Unit"]
    assert hasattr(Unit, 'find_by_description') and callable(getattr(Unit, 'find_by_description'))

def test_can_find_by_unit_roster_slot(generated_models):
    Unit = generated_models["Unit"]
    assert hasattr(Unit, 'find_by_roster_slot') and callable(getattr(Unit, 'find_by_roster_slot'))

def test_can_find_by_unit_price(generated_models): 
    Unit = generated_models["Unit"]
    assert hasattr(Unit, 'find_by_price') and callable(getattr(Unit, 'find_by_price'))

def test_faction_cant_find_by_price_or_roster_slot(generated_models):
    Faction = generated_models["Faction"]
    assert not (hasattr(Faction, 'find_by_price') and callable(getattr(Faction, 'find_by_price')))
    assert not (hasattr(Faction, 'find_by_roster_slot') and callable(getattr(Faction, 'find_by_roster_slot')))