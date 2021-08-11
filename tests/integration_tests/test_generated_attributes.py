# pylint: skip-file
from tests.helper import get_testing_spec
import pytest
from magellan_models.exceptions import MagellanRuntimeWarning, MagellanRuntimeException
import warnings


def test_list_attributes_returns_the_right_attributes_for_faction(generated_models):
    Faction = generated_models["Faction"]
    attributes = Faction.list_attributes()
    assert "id" in attributes
    assert "title" in attributes
    assert "description" in attributes
    assert "keywords" in attributes


def test_can_set_id(generated_models):
    Faction = generated_models["Faction"]
    fac = Faction()
    fac.id = "foobar"
    assert fac.id == "foobar"


def test_can_set_fac_title(generated_models):
    Faction = generated_models["Faction"]
    fac = Faction()
    fac.title = "testing title"
    assert fac.title == "testing title"


def test_can_set_fac_description(generated_models):
    Faction = generated_models["Faction"]
    fac = Faction()
    fac.description = "testing description"
    assert fac.description == "testing description"


def test_can_set_fac_keywords(generated_models):
    Faction = generated_models["Faction"]
    fac = Faction()
    fac.keywords = ["bikes", "yams", "apples"]
    assert fac.keywords == ["bikes", "yams", "apples"]


def test_setting_attributes_affects_representation(generated_models):
    Faction = generated_models["Faction"]
    fac = Faction()
    fac.title = "This title is in the representation"
    assert (
        fac.representation["attributes"]["title"]
        == "This title is in the representation"
    )


def test_list_attributes_returns_the_right_attributes_for_units(generated_models):
    Unit = generated_models["Unit"]
    attributes = Unit.list_attributes()
    assert "id" in attributes
    assert "title" in attributes
    assert "description" in attributes
    assert "price" in attributes
    assert "roster_slot" in attributes
    assert "keywords" in attributes


def test_list_methods_returns_a_list(generated_models):
    Unit = generated_models["Unit"]
    funcs = Unit.list_methods()
    assert "list_methods" in funcs
    assert "resource_name" in funcs
    assert "representation" in funcs
    assert "find_by_id" in funcs


def test_can_set_unit_id(generated_models):
    Unit = generated_models["Unit"]
    unit = Unit()
    unit.id = "foobar"
    assert unit.id


def test_can_set_unit_title(generated_models):
    Unit = generated_models["Unit"]
    unit = Unit()
    unit.title = "testing title"
    assert unit.title == "testing title"


def test_can_set_unit_description(generated_models):
    Unit = generated_models["Unit"]
    un = Unit()
    un.description = "testing description"
    assert un.description == "testing description"


def test_can_set_un_keywords(generated_models):
    Unit = generated_models["Unit"]
    un = Unit()
    un.keywords = ["bikes", "yams", "apples"]
    assert un.keywords == ["bikes", "yams", "apples"]


def test_can_set_un_price(generated_models):
    Unit = generated_models["Unit"]
    un = Unit()
    un.price = "$50"
    assert un.price == "$50"


def test_can_set_un_roster_slot(generated_models):
    Unit = generated_models["Unit"]
    un = Unit()
    un.roster_slot = "Core"
    assert un.roster_slot == "Core"


def test_setting_attributes_affects_representation(generated_models):
    Unit = generated_models["Unit"]
    un = Unit()
    un.title = "This title is in the representation"
    assert (
        un.representation["attributes"]["title"]
        == "This title is in the representation"
    )


def test_can_set_attributes_by_modifying_representation(generated_models):
    Unit = generated_models["Unit"]
    un = Unit()
    un.representation["attributes"]["title"] = "Modified Title"
    assert un.title == "Modified Title"


def test_get_attribute_returns_val(generated_models):
    Faction = generated_models["Faction"]
    fac = Faction()
    fac.representation = {"attributes": {"title": "foobar"}}
    assert fac.get_instance_attribute("title") == "foobar"


def test_set_attribute_sets_val(generated_models):
    Faction = generated_models["Faction"]
    fac = Faction()
    fac.representation = {"attributes": {"title": "foobar"}}
    fac.set_instance_attribute("title", "fudge brownies")
    assert fac.title == "fudge brownies"

    assert fac.representation == {"attributes": {"title": "fudge brownies"}}


def test_get_attribute_works_with_custom_routing(generated_models, config):
    Faction = generated_models["Faction"]
    config.model_attributes_path = ("data", "custom_attributes", "further_nesting")
    fac = Faction()
    fac.representation = {
        "data": {"custom_attributes": {"further_nesting": {"title": "fudge"}}}
    }
    # this should traverse down the layers properly
    assert fac.title == "fudge"


def test_relationships_works_when_empty(generated_models):
    Faction = generated_models["Faction"]
    fac = Faction()
    assert fac.relationships()


def test_relationships_adder_remover(generated_models):
    Faction = generated_models["Faction"]
    fac = Faction()
    assert fac.units_json() == []
    fac.add_unit("Asdafasda")
    assert fac.units_json() == [{"id": "Asdafasda", "type": "unit"}]
    fac.remove_unit("Asdafasda")
    assert fac.units_json() == []


def test_relationships_helper_getter(generated_models, requests_mock):
    Faction = generated_models["Faction"]
    Unit = generated_models["Unit"]

    fac = Faction()
    fac.add_unit("ABC")
    base_route = "/".join([Unit.configuration().api_endpoint, Unit.resource_name()])
    requests_mock.get(
        base_route
        + "?filter=%5B%7B%22and%22%3A+%5B%7B%22name%22%3A+%22id%22%2C+%22op%22%3A+%22in%22%2C+%22val%22%3A+%5B%22ABC%22%5D%7D%5D%7D%5D&page%5Bsize%5D=1",
        status_code=200,
        json={"data": []},
    )

    fac.units()
    assert requests_mock.called
    assert len(fac.units()) == 0
    elem_count = 0
    for elem in fac.units():
        elem_count += 1
    assert elem_count == 0


def test___representation_getter_setter(generated_models):
    Faction = generated_models["Faction"]
    fac = Faction()
    assert fac.__representation is not None

    fac.__representation = {"Data": "with a capital D"}
    assert fac.__representation == {"Data": "with a capital D"}


def test_fake_attribute_raises_attribute_error(generated_models):
    Faction = generated_models["Faction"]
    fac = Faction()

    with pytest.raises(AttributeError):
        fac.super_duper_title

    with pytest.raises(AttributeError):
        fac.super_duper_title = "Foobar"
    assert True


def test_find_by_func(generated_models, requests_mock):
    Faction = generated_models["Faction"]
    base_route = "/".join(
        [Faction.configuration().api_endpoint, Faction.resource_name()]
    )
    requests_mock.get(
        base_route
        + "?filter=%5B%7B%22and%22%3A+%5B%7B%22name%22%3A+%22title%22%2C+%22op%22%3A+%22eq%22%2C+%22val%22%3A+%22Asdafasda%22%7D%5D%7D%5D&page%5Bsize%5D=1",
        status_code=200,
        json={"data": []},
    )
    fac = Faction.find_by_title("Asdafasda")
    assert fac is None


def test_post_schema_set_for_faction(generated_models):
    Faction = generated_models["Faction"]
    assert Faction.get_post_schema() != {}


def test_patch_schema_set_to_empty_for_faction(generated_models):
    assert generated_models["Faction"].get_patch_schema() == {}


def test_schema_validation_raises_warning_or_exception_on_misformed_post(
    generated_models, requests_mock
):
    Faction = generated_models["Faction"]
    fac = Faction()
    fac.title = None

    base_route = "/".join(
        [Faction.configuration().api_endpoint, Faction.resource_name()]
    )
    requests_mock.post(
        base_route, status_code=201, json={"data": {"attributes": {"title": {}}}}
    )
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        with pytest.raises(MagellanRuntimeWarning):
            fac.post()

    Faction.configuration().validation_output = "exception"
    with pytest.raises(MagellanRuntimeException):
        fac.post()

    assert True


def test_schema_validation_kicks_on_patch(generated_models, requests_mock):
    arbitrary_testing_patch_schmea = {
        "type": "object",
        "properties": {
            "data": {
                "type": "object",
                "properties": {
                    "attributes": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "publication_number": {"type": "integer"},
                            "random_value": {"type": "object"},
                        },
                        "required": ["title", "random_value"],
                    },
                },
                "required": ["attributes"],
            }
        },
        "required": ["data"],
    }
    Faction = generated_models["Faction"]

    @staticmethod
    def schema_getter():
        return arbitrary_testing_patch_schmea

    Faction.get_patch_schema = schema_getter
    fac_id = "fudge"

    base_route = "/".join(
        [Faction.configuration().api_endpoint, Faction.resource_name(), fac_id]
    )
    requests_mock.get(
        base_route, status_code=200, json={"data": {"attributes": {"id": "fudge"}}}
    )
    config = Faction.configuration()
    config.model_attributes_path = ("attributes",)
    fac = Faction.find(fac_id)

    requests_mock.patch(base_route, status_code=200, json={"data": {"attributes": {}}})

    Faction.configuration().validation_output = "warning"
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        with pytest.raises(MagellanRuntimeWarning):
            fac.patch()

    Faction.configuration().validation_output = "exception"
    with pytest.raises(MagellanRuntimeException):
        fac.patch()

    assert True


def test_single_get_relationship_func(generated_models, requests_mock):
    Unit = generated_models["Unit"]
    unit = Unit()

    assert unit.faction() is None
    unit.set_faction_id("ABC")
    base_route = "/".join([Unit.configuration().api_endpoint, "factions", "ABC"])
    requests_mock.get(
        base_route,
        status_code=200,
        json={
            "data": {
                "attributes": {
                    "id": "ABC",
                    "title": "foobar",
                    "description": "sample payload",
                }
            }
        },
    )

    fac = unit.faction()
    assert requests_mock.called
    assert requests_mock.call_count == 1
    assert fac.id == "ABC"
