from magellan_models.interface import ConstantMagellanResponse
from magellan_models.exceptions import MagellanRuntimeException
import pytest


def test_const_mag_resp_gets_further_pages_to_hit_limit(
    requests_mock, generated_models
):
    Faction = generated_models.get("Faction")
    config = Faction.configuration()
    route = f"{config.api_endpoint}/{Faction.resource_name()}"
    generated_params = "?"

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
    mag_resp = ConstantMagellanResponse(
        url_path=route, Model=Faction, config=config, limit=15, raw_params={}
    )

    assert requests_mock.called
    assert requests_mock.call_count == 1  # Shouldn't hit second page until needed
    assert len(mag_resp) == 10

    count = 0
    for elem in mag_resp:
        count += 1

    assert requests_mock.call_count == 2
    assert len(mag_resp) == 15


def test_const_mag_resp_exceptions_on_where_and_limit(requests_mock, generated_models):
    Faction = generated_models.get("Faction")
    config = Faction.configuration()
    route = f"{config.api_endpoint}/{Faction.resource_name()}"
    generated_params = "?"

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

    requests_mock.get(route + generated_params, status_code=200, json=first_page)
    mag_resp = ConstantMagellanResponse(
        url_path=route, Model=Faction, config=config, limit=9, raw_params={}
    )

    assert requests_mock.called
    assert requests_mock.call_count == 1  # Shouldn't hit second page until needed
    assert len(mag_resp) == 9

    with pytest.raises(MagellanRuntimeException):
        mag_resp.where(id=12)

    with pytest.raises(MagellanRuntimeException):
        mag_resp.limit(5)


def test_const_mag_resp_returns_when_next_page_is_none(requests_mock, generated_models):
    Faction = generated_models.get("Faction")
    config = Faction.configuration()
    route = f"{config.api_endpoint}/{Faction.resource_name()}"
    generated_params = "?"

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

    requests_mock.get(route + generated_params, status_code=200, json=first_page)
    mag_resp = ConstantMagellanResponse(
        url_path=route, Model=Faction, config=config, limit=9, raw_params={}
    )

    assert requests_mock.called
    assert requests_mock.call_count == 1  # Shouldn't hit second page until needed

    assert mag_resp.next_url is None
    assert mag_resp.process_next_page_of_results() is None
