from magellan_models.interface import MagellanResponse
from magellan_models.exceptions import MagellanRuntimeException
import pytest


def test_magellan_response_initialization_calls_first_url(
    requests_mock, generated_models
):
    Faction = generated_models.get("Faction")
    config = Faction.configuration()
    route = f"{config.api_endpoint}/{Faction.resource_name()}"
    generated_params = "?filter=%5B%7B%22and%22%3A+%5B%5D%7D%5D&page%5Bsize%5D=10"
    requests_mock.get(route + generated_params, status_code=200, json={"data": []})
    mag_resp = MagellanResponse(url_path=route, Model=Faction, config=config, limit=10)
    assert mag_resp.iteration_is_complete()
    assert requests_mock.called
    assert requests_mock.call_count == 1
    assert len(mag_resp) == 0


def test_mag_resp_iterates_properly(requests_mock, generated_models):
    Faction = generated_models.get("Faction")
    config = Faction.configuration()
    route = f"{config.api_endpoint}/{Faction.resource_name()}"
    generated_params = "?filter=%5B%7B%22and%22%3A+%5B%5D%7D%5D&page%5Bsize%5D=10"

    payload_entities = []
    for i in range(10):
        payload_entities.append(
            {
                "attributes": {
                    "id": i + 1,
                    "title": f"Fake Data {i}",
                    "description": "Fake Data element",
                    "tags": ["Fake", "Data"],
                }
            }
        )
    sample_payload = {"data": payload_entities, "meta": {"entity_count": 10}}
    requests_mock.get(route + generated_params, status_code=200, json=sample_payload)
    mag_resp = MagellanResponse(url_path=route, Model=Faction, config=config, limit=10)

    assert len(mag_resp) == 10
    for elem in mag_resp:
        print(elem.title)
        assert elem.title
        assert elem.id
    assert mag_resp.get_meta_data().get("meta", {}).get("entity_count") == 10


def test_mag_resp_get_out_of_bounds_errors_out(requests_mock, generated_models):
    Faction = generated_models.get("Faction")
    config = Faction.configuration()
    route = f"{config.api_endpoint}/{Faction.resource_name()}"
    generated_params = "?filter=%5B%7B%22and%22%3A+%5B%5D%7D%5D&page%5Bsize%5D=10"

    payload_entities = []
    for i in range(10):
        payload_entities.append(
            {
                "attributes": {
                    "id": i + 1,
                    "title": f"Fake Data {i}",
                    "description": "Fake Data element",
                    "tags": ["Fake", "Data"],
                }
            }
        )
    sample_payload = {"data": payload_entities, "meta": {"entity_count": 5}}
    requests_mock.get(route + generated_params, status_code=200, json=sample_payload)
    mag_resp = MagellanResponse(url_path=route, Model=Faction, config=config, limit=10)

    with pytest.raises(IndexError) as runtimeerr:
        mag_resp[16]
    assert mag_resp[4]  # this should work


def test_mag_resp_gets_further_pages_to_hit_limit(requests_mock, generated_models):
    Faction = generated_models.get("Faction")
    config = Faction.configuration()
    route = f"{config.api_endpoint}/{Faction.resource_name()}"
    generated_params = "?filter=%5B%7B%22and%22%3A+%5B%5D%7D%5D&page%5Bsize%5D=15"

    payload_entities = []
    for i in range(20):
        payload_entities.append(
            {
                "attributes": {
                    "id": i + 1,
                    "title": f"Fake Data {i}",
                    "description": "Fake Data element",
                    "tags": ["Fake", "Data"],
                }
            }
        )
    first_page = {
        "data": payload_entities[0:10],
        "meta": {"entity_count": 20},
        "links": {"next": route + generated_params + "page2"},
    }
    second_page = {"data": payload_entities[10:19], "meta": {"entity_count": 20}}

    requests_mock.get(route + generated_params, status_code=200, json=first_page)
    requests_mock.get(
        route + generated_params + "page2", status_code=200, json=second_page
    )
    mag_resp = MagellanResponse(url_path=route, Model=Faction, config=config, limit=15)

    assert requests_mock.called
    assert requests_mock.call_count == 1  # Shouldn't hit second page until needed
    assert len(mag_resp) == 10

    mag_resp[12]  # Trigger second page call
    assert requests_mock.called
    assert requests_mock.call_count == 2
    assert len(mag_resp) == 15
    assert mag_resp.iteration_is_complete()


def test_mag_resp_stops_iterating_even_if_limitless_at_end(
    requests_mock, generated_models
):
    Faction = generated_models.get("Faction")
    config = Faction.configuration()
    route = f"{config.api_endpoint}/{Faction.resource_name()}"
    generated_params = "?filter=%5B%7B%22and%22%3A+%5B%5D%7D%5D&"

    payload_entities = []
    for i in range(20):
        payload_entities.append(
            {
                "attributes": {
                    "id": i + 1,
                    "title": f"Fake Data {i}",
                    "description": "Fake Data element",
                    "tags": ["Fake", "Data"],
                }
            }
        )
    first_page = {
        "data": payload_entities[0:10],
        "meta": {"entity_count": 20},
        "links": {"next": route + generated_params + "page2"},
    }
    second_page = {"data": payload_entities[10:], "meta": {"entity_count": 20}}

    requests_mock.get(route + generated_params, status_code=200, json=first_page)
    requests_mock.get(
        route + generated_params + "page2", status_code=200, json=second_page
    )
    mag_resp = MagellanResponse(
        url_path=route, Model=Faction, config=config, limit=None
    )

    assert requests_mock.called
    assert requests_mock.call_count == 1  # Shouldn't hit second page until needed
    assert len(mag_resp) == 10

    mag_resp[12]  # Trigger second page call

    assert requests_mock.called
    assert requests_mock.call_count == 2
    assert len(mag_resp) == 20

    mag_resp.process_next_page_of_results()  # -> shouldn't do much
    assert requests_mock.call_count == 2
    assert len(mag_resp) == 20


def test_set_mag_resp_elem(requests_mock, generated_models):
    Faction = generated_models.get("Faction")
    config = Faction.configuration()
    route = f"{config.api_endpoint}/{Faction.resource_name()}"
    generated_params = "?filter=%5B%7B%22and%22%3A+%5B%5D%7D%5D&"

    payload_entities = []
    for i in range(20):
        payload_entities.append(
            {
                "attributes": {
                    "id": i + 1,
                    "title": f"Fake Data {i}",
                    "description": "Fake Data element",
                    "tags": ["Fake", "Data"],
                }
            }
        )
    first_page = {
        "data": payload_entities[0:10],
        "meta": {"entity_count": 20},
        "links": {"next": route + generated_params + "page2"},
    }
    second_page = {"data": payload_entities[10:], "meta": {"entity_count": 20}}

    requests_mock.get(route + generated_params, status_code=200, json=first_page)
    requests_mock.get(
        route + generated_params + "page2", status_code=200, json=second_page
    )
    mag_resp = MagellanResponse(
        url_path=route, Model=Faction, config=config, limit=None
    )

    mag_resp[1] = None
    assert mag_resp[1] is None


def test_mag_resp_yields_all_elems(requests_mock, generated_models):
    Faction = generated_models.get("Faction")
    config = Faction.configuration()
    route = f"{config.api_endpoint}/{Faction.resource_name()}"
    generated_params = "?filter=%5B%7B%22and%22%3A+%5B%5D%7D%5D&"

    payload_entities = []
    for i in range(20):
        payload_entities.append(
            {
                "attributes": {
                    "id": i + 1,
                    "title": f"Fake Data {i}",
                    "description": "Fake Data element",
                    "tags": ["Fake", "Data"],
                }
            }
        )
    first_page = {
        "data": payload_entities[0:10],
        "meta": {"entity_count": 20},
        "links": {"next": route + generated_params + "page2"},
    }
    second_page = {"data": payload_entities[10:], "meta": {"entity_count": 20}}

    requests_mock.get(route + generated_params, status_code=200, json=first_page)
    requests_mock.get(
        route + generated_params + "page2", status_code=200, json=second_page
    )
    mag_resp = MagellanResponse(
        url_path=route, Model=Faction, config=config, limit=None
    )
    resp_count = 0
    for elem in mag_resp:
        resp_count += 1
    assert len(mag_resp) == resp_count


def test_mag_resp_throws_runtime_error_on_failed_call(requests_mock, generated_models):
    Faction = generated_models.get("Faction")
    config = Faction.configuration()
    route = f"{config.api_endpoint}/{Faction.resource_name()}"
    generated_params = "?filter=%5B%7B%22and%22%3A+%5B%5D%7D%5D&"

    requests_mock.get(route + generated_params, status_code=500, json={})

    with pytest.raises(MagellanRuntimeException):
        mag_resp = MagellanResponse(
            url_path=route, Model=Faction, config=config, limit=None
        )
    assert requests_mock.called
    assert requests_mock.call_count == 1


def test_chained_where_updates_kwargs(requests_mock, generated_models):
    Faction = generated_models.get("Faction")
    config = Faction.configuration()
    route = f"{config.api_endpoint}/{Faction.resource_name()}"
    default_generated_params = "?filter=%5B%7B%22and%22%3A+%5B%5D%7D%5D&"
    new_params = "?filter=%5B%7B%22and%22%3A+%5B%7B%22name%22%3A+%22id%22%2C+%22op%22%3A+%22gt%22%2C+%22val%22%3A+10%7D%5D%7D%5D"
    payload_entities = []
    for i in range(20):
        payload_entities.append(
            {
                "attributes": {
                    "id": i + 1,
                    "title": f"Fake Data {i}",
                    "description": "Fake Data element",
                    "tags": ["Fake", "Data"],
                }
            }
        )
    first_page = {"data": payload_entities[0:10], "meta": {"entity_count": 20}}
    second_page = {"data": payload_entities[10:], "meta": {"entity_count": 10}}

    requests_mock.get(
        route + default_generated_params, status_code=200, json=first_page
    )
    requests_mock.get(route + new_params, status_code=200, json=second_page)
    mag_resp = MagellanResponse(
        url_path=route, Model=Faction, config=config, limit=None
    )

    assert requests_mock.call_count == 1
    assert mag_resp.kwargs == {}

    mag_resp.where(id=10, filtering_arguments={"id": "gt"})
    assert mag_resp.kwargs == {"id": 10, "filtering_arguments": {"id": "gt"}}
    assert requests_mock.call_count == 2
    assert mag_resp.get_meta_data().get("meta").get("entity_count") == 10
    assert len(mag_resp) == 10


def test_chained_where_limit_nukes_internal_state(requests_mock, generated_models):
    Faction = generated_models.get("Faction")
    config = Faction.configuration()
    route = f"{config.api_endpoint}/{Faction.resource_name()}"
    default_generated_params = "?filter=%5B%7B%22and%22%3A+%5B%5D%7D%5D&"
    payload_entities = []
    for i in range(20):
        payload_entities.append(
            {
                "attributes": {
                    "id": i + 1,
                    "title": f"Fake Data {i}",
                    "description": "Fake Data element",
                    "tags": ["Fake", "Data"],
                }
            }
        )
    first_page = {"data": payload_entities[0:10], "meta": {"entity_count": 20}}

    requests_mock.get(
        route + default_generated_params, status_code=200, json=first_page
    )
    mag_resp = MagellanResponse(
        url_path=route, Model=Faction, config=config, limit=None
    )

    assert requests_mock.call_count == 1
    assert len(mag_resp) == 10
    mag_resp.where(limit=5)
    assert requests_mock.call_count == 2
    assert len(mag_resp) == 5


def test_limit_truncates(requests_mock, generated_models):
    Faction = generated_models.get("Faction")
    config = Faction.configuration()
    route = f"{config.api_endpoint}/{Faction.resource_name()}"
    default_generated_params = "?filter=%5B%7B%22and%22%3A+%5B%5D%7D%5D&"
    payload_entities = []
    for i in range(20):
        payload_entities.append(
            {
                "attributes": {
                    "id": i + 1,
                    "title": f"Fake Data {i}",
                    "description": "Fake Data element",
                    "tags": ["Fake", "Data"],
                }
            }
        )
    first_page = {"data": payload_entities[0:10], "meta": {"entity_count": 20}}

    requests_mock.get(
        route + default_generated_params, status_code=200, json=first_page
    )
    mag_resp = MagellanResponse(
        url_path=route, Model=Faction, config=config, limit=None
    )

    assert requests_mock.call_count == 1
    assert len(mag_resp) == 10
    mag_resp.limit(15)
    assert len(mag_resp) == 10  # Shouldn't truncate
    assert requests_mock.call_count == 2  # destructive op means redoing a call

    mag_resp.limit(5)
    assert requests_mock.call_count == 2
    assert len(mag_resp) == 5  # should truncate


def test_iterate_all(requests_mock, generated_models):
    Faction = generated_models.get("Faction")
    config = Faction.configuration()
    route = f"{config.api_endpoint}/{Faction.resource_name()}"
    generated_params = "?filter=%5B%7B%22and%22%3A+%5B%5D%7D%5D&"

    payload_entities = []
    for i in range(20):
        payload_entities.append(
            {
                "attributes": {
                    "id": i + 1,
                    "title": f"Fake Data {i}",
                    "description": "Fake Data element",
                    "tags": ["Fake", "Data"],
                }
            }
        )
    first_page = {
        "data": payload_entities[0:10],
        "meta": {"entity_count": 20},
        "links": {"next": route + generated_params + "page2"},
    }
    second_page = {"data": payload_entities[10:], "meta": {"entity_count": 20}}

    requests_mock.get(route + generated_params, status_code=200, json=first_page)
    requests_mock.get(
        route + generated_params + "page2", status_code=200, json=second_page
    )
    mag_resp = MagellanResponse(
        url_path=route, Model=Faction, config=config, limit=None
    )

    assert len(mag_resp) == 10
    mag_resp.evaluate_fully()
    assert len(mag_resp) == 20
    assert mag_resp.iteration_is_complete()


def test_magellan_response_experimental_filtering(
    requests_mock, generated_models, mocker
):
    Faction = generated_models.get("Faction")
    config = Faction.configuration()
    route = f"{config.api_endpoint}/{Faction.resource_name()}"
    generated_params = "?filter=%5B%7B%22and%22%3A+%5B%5D%7D%5D&page%5Bsize%5D=10"
    requests_mock.get(route + generated_params, status_code=200, json={"data": []})
    mag_resp = MagellanResponse(url_path=route, Model=Faction, config=config, limit=10)
    mag_resp.__config__.experimental_functions = True
    mocker.patch.object(mag_resp, "where")

    mag_resp.filter_title__eq("foo")
    mag_resp.where.assert_called_once_with(
        title="foo", filtering_arguments={"title": "eq"}
    )


def test_mag_resp_experimentals_false_leads_to_attribute_errors(
    requests_mock, generated_models
):
    Faction = generated_models.get("Faction")
    config = Faction.configuration()
    route = f"{config.api_endpoint}/{Faction.resource_name()}"
    generated_params = "?filter=%5B%7B%22and%22%3A+%5B%5D%7D%5D&page%5Bsize%5D=10"
    requests_mock.get(route + generated_params, status_code=200, json={"data": []})
    mag_resp = MagellanResponse(url_path=route, Model=Faction, config=config, limit=10)

    with pytest.raises(AttributeError):
        mag_resp.filter_title_eq("foo")
    assert True


def test_mag_resp_experimental_sort(requests_mock, generated_models, mocker):
    Faction = generated_models.get("Faction")
    config = Faction.configuration()
    route = f"{config.api_endpoint}/{Faction.resource_name()}"
    generated_params = "?filter=%5B%7B%22and%22%3A+%5B%5D%7D%5D&page%5Bsize%5D=10"
    requests_mock.get(route + generated_params, status_code=200, json={"data": []})
    mag_resp = MagellanResponse(url_path=route, Model=Faction, config=config, limit=10)
    mag_resp.__config__.experimental_functions = True
    mocker.patch.object(mag_resp, "where")

    mag_resp.sort_by_title()
    mag_resp.where.assert_called_once_with(sort="title")


def test_mag_resp_experimental_filter_simple(requests_mock, generated_models, mocker):
    Faction = generated_models.get("Faction")
    config = Faction.configuration()
    route = f"{config.api_endpoint}/{Faction.resource_name()}"
    generated_params = "?filter=%5B%7B%22and%22%3A+%5B%5D%7D%5D&page%5Bsize%5D=10"
    requests_mock.get(route + generated_params, status_code=200, json={"data": []})
    mag_resp = MagellanResponse(url_path=route, Model=Faction, config=config, limit=10)
    mag_resp.__config__.experimental_functions = True

    mocker.patch.object(mag_resp, "where")

    mag_resp.filter_by_title("foo")
    mag_resp.where.assert_called_once_with(
        title="foo", filtering_arguments={"title": "eq"}
    )
