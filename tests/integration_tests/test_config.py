import pytest
from magellan_models.config import MagellanConfig
import requests


def test_meta_generator_default(requests_mock):
    requests_mock.get(
        "http://foobarbiz.jpeg/nonsense_url",
        json={"meta": {"hello": "world"}},
        status_code=200,
    )
    conf = MagellanConfig()
    meta = conf.get_meta_data_from_resp(
        requests.get("http://foobarbiz.jpeg/nonsense_urL")
    )
    assert meta.get("meta") == {"hello": "world"}
    assert meta.get("links") == {}
