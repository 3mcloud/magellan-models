from magellan_models.interface.abstract_api_model import AbstractApiModel
from magellan_models.exceptions import MagellanParserException, MagellanRuntimeException
import pytest
from magellan_models.config import MagellanConfig
from typing import List, Dict, Any
from unittest.mock import MagicMock, patch
import json

fakeConfig = MagellanConfig()


class FakeModel(AbstractApiModel):
    def __init__(self):
        """Automatically generated model for the Unit resource"""
        self.__representation = {"attributes": {}, "relationships": {}}

    @staticmethod
    def get_patch_schema():
        return {}

    @staticmethod
    def get_post_schema():
        return {}

    @staticmethod
    def configuration():
        return fakeConfig

    @staticmethod
    def resource_name():
        return "test_models"

    @staticmethod
    def list_attributes():
        return {
            "id": str,
            "title": str,
            "description": str,
        }

    @property
    def representation(self):
        return self.__representation

    @representation.setter
    def representation(self, new_val):
        self.__representation = new_val

    @property
    def id(self) -> str:
        """
        Attribute Getter for id returns None if the attribute hasn't been set
        """
        return self.representation.get("attributes", {}).get("id", None)

    @id.setter
    def id(self, new_val: str) -> None:
        self.representation["attributes"]["id"] = new_val

    @property
    def title(self) -> str:
        """
        Attribute Getter for title returns None if the attribute hasn't been set
        """
        return self.representation.get("attributes", {}).get("title", None)

    @title.setter
    def title(self, new_val: str) -> None:
        self.representation["attributes"]["title"] = new_val

    @property
    def description(self) -> str:
        """
        Attribute Getter for description returns None if the attribute hasn't been set
        """
        return self.representation.get("attributes", {}).get("description", None)

    @description.setter
    def description(self, new_val: str) -> None:
        self.representation["attributes"]["description"] = new_val


def test_resource_name_works_when_set_by_child():
    assert FakeModel.resource_name()


def test_model_find_calls_single_get_route(requests_mock):
    route = "/".join(
        [FakeModel.configuration().api_endpoint, FakeModel.resource_name(), "fake_id"]
    )
    requests_mock.get(
        route,
        status_code=200,
        json={
            "data": {
                "attributes": {
                    "id": "fake_id",
                    "title": "fakeTitle",
                    "description": "FakeDescription",
                },
                "relationships": {},
            }
        },
    )
    instance = FakeModel.find("fake_id")
    assert instance.title == "fakeTitle"
    assert instance.id == "fake_id"


def test_model_find_raises_on_not_found(requests_mock):
    route = "/".join(
        [FakeModel.configuration().api_endpoint, FakeModel.resource_name(), "fake_id"]
    )
    requests_mock.get(route, status_code=404, json={})
    with pytest.raises(MagellanRuntimeException) as runtimeerr:
        FakeModel.find("fake_id")
    assert "'error_code': 404" in str(runtimeerr)


def test_model_get_generates_headers_if_not_given_args(requests_mock):
    route = "/".join(
        [FakeModel.configuration().api_endpoint, FakeModel.resource_name(), "fake_id"]
    )
    with patch.object(
        fakeConfig, "create_header", return_value=({}, {})
    ) as mocked_header_func:
        requests_mock.get(route, status_code=200, json={"data": {"attributes": {}}})
        FakeModel.find("fake_id")
    mocked_header_func.assert_called()
    mocked_header_func.assert_called_with()


def test_model_get_calls_config_gen_headers_without_args(requests_mock):
    route = "/".join(
        [FakeModel.configuration().api_endpoint, FakeModel.resource_name(), "fake_id"]
    )
    with patch.object(
        fakeConfig, "create_header", return_value=({}, {})
    ) as mocked_header_func:
        requests_mock.get(route, status_code=200, json={"data": {"attributes": {}}})
        FakeModel.find("fake_id")
    mocked_header_func.assert_called()
    mocked_header_func.assert_called_with()


def test_model_get_generates_headers_with_passed_args(requests_mock):
    route = "/".join(
        [FakeModel.configuration().api_endpoint, FakeModel.resource_name(), "fake_id"]
    )
    with patch.object(
        fakeConfig, "create_header", return_value=({}, {})
    ) as mocked_header_func:
        requests_mock.get(route, status_code=200, json={"data": {"attributes": {}}})
        FakeModel.find(
            "fake_id",
            **{FakeModel.configuration().header_args_separator: {"foo": "bar"}}
        )
    mocked_header_func.assert_called()
    mocked_header_func.assert_called_with(header_args={"foo": "bar"})


def test_model_get_calls_config_generate_headers_func(requests_mock):
    route = "/".join(
        [FakeModel.configuration().api_endpoint, FakeModel.resource_name(), "fake_id"]
    )

    with patch.object(
        fakeConfig, "create_header", return_value=({}, {})
    ) as mocked_header_func:
        requests_mock.get(route, status_code=200, json={"data": {"attributes": {}}})
        FakeModel.find(
            "fake_id",
            **{FakeModel.configuration().header_args_separator: {"foo": "bar"}}
        )
    assert requests_mock.called
    mocked_header_func.assert_called()
    mocked_header_func.assert_called_with(header_args={"foo": "bar"})


def test_query_call_parses_filters_properly(requests_mock):
    # autogenerated route url
    route = "http://localhost:80/api/v1/test_models?filter=%5B%7B%22name%22%3A+%22title%22%2C+%22op%22%3A+%22eq%22%2C+%22val%22%3A+%22testTitle%22%7D%5D"

    requests_mock.get(route, status_code=200, json={"data": []})
    FakeModel.query(
        parameters={
            "filter": json.dumps([{"name": "title", "op": "eq", "val": "testTitle"}])
        }
    )
    assert requests_mock.called
    assert requests_mock.call_count == 1


def test_delete_call_sends_proper_call(requests_mock):
    route = "/".join(
        [FakeModel.configuration().api_endpoint, FakeModel.resource_name(), "fake_id"]
    )
    requests_mock.delete(route, status_code=200, json={})

    FakeModel.delete("fake_id")
    assert requests_mock.called
    assert requests_mock.call_count == 1


def test_delete_self_sends_proper_call(requests_mock):
    inst = FakeModel()
    inst.id = "fake_id"
    route = "/".join(
        [FakeModel.configuration().api_endpoint, FakeModel.resource_name(), "fake_id"]
    )
    requests_mock.delete(route, status_code=200, json={})

    inst.delete_self()
    assert requests_mock.called
    assert requests_mock.call_count == 1


def test_delete_failure_posts_error(requests_mock):
    route = "/".join(
        [FakeModel.configuration().api_endpoint, FakeModel.resource_name(), "fake_id"]
    )
    requests_mock.delete(route, status_code=400, json={})

    with pytest.raises(MagellanRuntimeException) as runtimeerr:
        FakeModel.delete("fake_id")
    assert "'error_code': 400" in str(runtimeerr)
    assert requests_mock.called


def test_setting_id_causes_errors_on_post(requests_mock):
    route = "/".join(
        [FakeModel.configuration().api_endpoint, FakeModel.resource_name(), "fake_id"]
    )
    requests_mock.get(
        route,
        status_code=200,
        json={
            "data": {
                "attributes": {"id": "fake_id"},
                "id": "fake_id",
                "type": "FakeModel",
            }
        },
    )

    with pytest.raises(MagellanRuntimeException) as runtimeerr:
        inst = FakeModel.find("fake_id")
        inst.post()

    assert requests_mock.called
    assert requests_mock.call_count == 1
    assert "Can't post" in str(runtimeerr)


def test_post_error_raises_runtime_exception(requests_mock):
    route = "/".join(
        [FakeModel.configuration().api_endpoint, FakeModel.resource_name()]
    )
    requests_mock.post(route, status_code=500, json={})
    with pytest.raises(MagellanRuntimeException) as runtimeerr:
        inst = FakeModel()
        inst.post()

    assert requests_mock.called
    assert requests_mock.call_count == 1
    assert "'error_code': 500" in str(runtimeerr)


def test_where_with_args_calls_create_filters(requests_mock):
    base_route = "/".join(
        [FakeModel.configuration().api_endpoint, FakeModel.resource_name()]
    )
    options = "?%7B%22filter%22:%20%7B%22title%22:%20%22fauxTitle%22%7D%7D"
    with patch.object(
        fakeConfig,
        "create_filters",
        return_value=json.dumps({"filter": {"title": "fauxTitle"}}),
    ) as mock_filter_func:
        requests_mock.get(base_route + options, status_code=200, json={"data": []})
        FakeModel.where(title="fauxTitle")
    mock_filter_func.assert_called()
    mock_filter_func.assert_called_with(title="fauxTitle")
    assert requests_mock.called


def test_where_iterates_through_response(requests_mock):
    base_route = "/".join(
        [FakeModel.configuration().api_endpoint, FakeModel.resource_name()]
    )
    requests_mock.get(
        base_route,
        status_code=200,
        json={
            "data": [
                {"attributes": {"title": "Foobar"}},
                {"attributes": {"title": "AnotherFoobar"}},
                {"attributes": {"title": "last element"}},
            ]
        },
    )

    instances = FakeModel.where()
    assert requests_mock.called

    assert len(instances) == 3


def test_where_with_header_args_doesnt_put_them_in_the_filter(requests_mock):
    base_route = "/".join(
        [FakeModel.configuration().api_endpoint, FakeModel.resource_name()]
    )

    with patch.object(
        fakeConfig, "create_filters", return_value={"filter": json.dumps([{"and": []}])}
    ) as mocked_filters:
        FakeModel.configuration().header_args_separator = "header"
        requests_mock.get(base_route, status_code=200, json={"data": []})
        FakeModel.where(header="foobar")

    mocked_filters.assert_called()
    mocked_filters.assert_called_with()
    assert requests_mock.called


def test_where_sends_args_to_filter_func(requests_mock):
    base_route = "/".join(
        [FakeModel.configuration().api_endpoint, FakeModel.resource_name()]
    )
    with patch.object(
        fakeConfig, "create_filters", return_value={"filter": json.dumps([{"and": []}])}
    ) as mocked_filters:
        requests_mock.get(base_route, status_code=200, json={"data": []})
        FakeModel.where(name="foobar")
    mocked_filters.assert_called()
    mocked_filters.assert_called_with(name="foobar")


def test_sync_updates_rep(requests_mock):
    fake = FakeModel()
    fake.title = "in sync"
    fake.description = "in sync"
    base_route = "/".join(
        [FakeModel.configuration().api_endpoint, FakeModel.resource_name()]
    )
    requests_mock.post(
        base_route,
        status_code=201,
        json={
            "data": {
                "attributes": {
                    "id": "myuuid",
                    "title": "in sync",
                    "description": "in sync",
                }
            }
        },
    )
    fake.post()
    assert fake.id
    assert fake.id == "myuuid"

    fake.title = "now not in sync"
    title = "now not in sync"
    assert fake.title == title

    requests_mock.get(
        base_route + "/" + fake.id,
        status_code=200,
        json={
            "data": {
                "attributes": {
                    "id": "myuuid",
                    "title": "we back in sync",
                    "description": "in sync",
                }
            }
        },
    )
    fake.sync()
    assert fake.title == "we back in sync"


def test_sync_fails_without_id(requests_mock):
    fake = FakeModel()
    with pytest.raises(MagellanRuntimeException) as excinfo:
        fake.sync()
    assert "Can't sync without an assigned ID" in str(excinfo.value)


def test_patch_updates_representation(requests_mock):
    fake = FakeModel.from_json(
        {"data": {"attributes": {"title": "to patch", "id": "foobar"}}}
    )
    base_route = "/".join(
        [FakeModel.configuration().api_endpoint, FakeModel.resource_name(), fake.id]
    )
    requests_mock.patch(
        base_route,
        status_code=200,
        json={
            "data": {
                "attributes": {
                    "id": "foobar",
                    "title": "patched",
                    "description": "newly patched",
                }
            }
        },
    )
    assert not fake.description
    assert fake.title == "to patch"
    fake.patch()
    assert fake.title == "patched"
    assert fake.description
    assert requests_mock.called


def test_patch_fails_if_errors_out(requests_mock):
    fake = FakeModel.from_json(
        {"data": {"attributes": {"title": "to patch", "id": "foobar"}}}
    )
    base_route = "/".join(
        [FakeModel.configuration().api_endpoint, FakeModel.resource_name(), fake.id]
    )
    requests_mock.patch(
        base_route,
        status_code=400,
        json={"data": {"attributes": {"id": "foobar", "title": "shouldn't change"}}},
    )
    with pytest.raises(MagellanRuntimeException) as excinfo:
        fake.patch()
    assert "400" in str(excinfo.value)
    assert requests_mock.called
    assert fake.title == "to patch"
