# pylint: skip-file
from tests.helper import get_testing_spec
import pytest
from magellan_models import MagellanConfig
from magellan_models.initializers import initialize_with_spec
from magellan_models.exceptions import MagellanRuntimeException, MagellanRuntimeWarning
from unittest.mock import MagicMock, patch
import warnings


def test_call_healthcheck_works(generated_funcs, config, requests_mock):
    get_from_healthcheck = generated_funcs["get_from_healthcheck"]
    route = "/".join([config.api_endpoint, "healthcheck"])
    requests_mock.get(route, status_code=200, json={"hello": "world"})
    get_from_healthcheck()
    assert requests_mock.called


def test_call_post_convert_name(generated_funcs, config, requests_mock):
    print(generated_funcs.keys())
    post_to_convert_name = generated_funcs["post_to_convert_name_with_name"]

    route = "/".join([config.api_endpoint, "convert_name", "ChickiNuggez"])
    requests_mock.post(route, status_code=200, json={"newName": "Chicken Nuggets"})

    post_to_convert_name(name="ChickiNuggez")
    assert requests_mock.called


def test_call_put_convert_name(generated_funcs, config, requests_mock):
    print(generated_funcs)
    put_to_convert_name = generated_funcs["put_to_convert_name_with_name"]

    route = "/".join([config.api_endpoint, "convert_name", "ChickiNuggez"])
    requests_mock.put(route, status_code=200, json={"newName": "Chicken Nuggets"})

    put_to_convert_name(name="ChickiNuggez")
    assert requests_mock.called
    assert requests_mock.call_count == 1


def test_can_override_action_type(generated_funcs, config, requests_mock):
    put_to_convert_name = generated_funcs["put_to_convert_name_with_name"]

    route = "/".join([config.api_endpoint, "convert_name", "ChickiNuggez"])
    requests_mock.put(route, status_code=200, json={"newName": "Chicken Nuggets"})

    resp = put_to_convert_name(name="ChickiNuggez", action="putterino")
    assert resp is None
    assert requests_mock.called is False
    assert requests_mock.call_count == 0


def test_healthcheck_and_healthcheck_message_are_generated(generated_funcs):
    assert "get_from_healthcheck" in generated_funcs
    assert "get_from_healthcheck_with_msg_" in generated_funcs


def test_duplicate_paths_point_to_diff_funcs(generated_funcs, config, requests_mock):
    post_to_convert_name = generated_funcs["get_from_healthcheck_with_msg_"]

    route = "/".join([config.api_endpoint, "healthcheck", "HelloWorld"])
    requests_mock.get(route, status_code=200, json={"message": "HelloWorld"})

    post_to_convert_name(msg_="HelloWorld")
    assert requests_mock.called


def test_raw_routes_generation():
    endpoint_url = "https://localhost:3000/api/vi/"
    conf = MagellanConfig()
    conf.function_naming_style = "raw"
    conf.api_endpoint = endpoint_url
    (models, funcs, conf) = initialize_with_spec(get_testing_spec(), conf)
    assert "GET /healthcheck" in funcs


def test_validation_warnings(requests_mock):
    conf = MagellanConfig()
    conf.validation_output = "exception"
    conf.api_endpoint = "https://localhost:3000/api/v1"
    (models, funcs, conf) = initialize_with_spec(get_testing_spec(), conf)

    post_to_convert_name = funcs["post_to_convert_name_with_name"]

    route = "/".join([conf.api_endpoint, "convert_name", "ChickiNuggez"])
    requests_mock.post(route, status_code=200, json={"newName": "Chicken Nuggets"})
    with pytest.raises(MagellanRuntimeException):
        post_to_convert_name(
            name="ChickiNuggez", request_body={"method_to_madness": "fudge"}
        )

    conf.validation_output = "warning"

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        with pytest.raises(MagellanRuntimeWarning):
            post_to_convert_name(
                name="ChickiNuggez", request_body={"method_to_madness": "fudge"}
            )
    assert True


def test_patching_works(generated_funcs, config, requests_mock):
    patch_func = generated_funcs["patch_to_arbitrary_patch"]
    route = "/".join([config.api_endpoint, "arbitrary_patch"])
    requests_mock.patch(route, status_code=200, json={})

    patch_func()
    assert requests_mock.called


def test_deletion_works(config, requests_mock, generated_funcs):
    deletion_func = generated_funcs["delete_to_delete_mapping_with_mapping_name"]
    route = "/".join([config.api_endpoint, "delete_mapping", "toDelete"])
    requests_mock.delete(
        route, status_code=200, json={"message": "toDelete was Deleted"}
    )

    deletion_func(mapping_name="toDelete")
    assert requests_mock.called


def overriding_method_returns_none(generated_funcs):
    get_from_healthcheck = generated_funcs["get_from_healthcheck"]
    assert get_from_healthcheck(action="BAAAHHAHAHHAH") == None
