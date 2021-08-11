import pytest

generic_func_key = "_generic_api_function"
def test_generic_func_exists(generated_funcs):
    assert generic_func_key in generated_funcs
    assert callable(generated_funcs[generic_func_key])

def test_generic_func_get_returns_request_obj(generated_funcs, config, requests_mock):
    generic_api_func = generated_funcs[generic_func_key]
    path = "/".join([config.api_endpoint, "healthcheck"])
    
    requests_mock.get(path, status_code=200, json={"hello": "world"})
    resp = generic_api_func("/healthcheck", "GET")
    assert requests_mock.called 
    assert resp.json() == {"hello": "world"}

def test_generic_post_also_calls_endpoint(generated_funcs, config, requests_mock):
    generic_api_func = generated_funcs[generic_func_key]
    path = "/".join([config.api_endpoint, "echo"])
    requests_mock.post(path, status_code=201, json={"hello": "world"})
    resp = generic_api_func("/echo", "POST")
    assert requests_mock.called 
    assert resp.status_code == 201

def test_generic_patch_also_calls_endpoint(generated_funcs, config, requests_mock):
    generic_api_func = generated_funcs[generic_func_key]
    path = "/".join([config.api_endpoint, "update"])
    requests_mock.patch(path, status_code=200, json={"id": "123"})
    resp = generic_api_func("/update", "PATCH")
    assert requests_mock.called 
    assert resp.status_code == 200
    assert resp.json() == {"id": "123"}

def test_generic_delete_also_calls_endpoint(generated_funcs, config, requests_mock):
    generic_api_func = generated_funcs[generic_func_key]
    path = "/".join([config.api_endpoint, "purge"])
    requests_mock.delete(path, status_code=200, json={})
    resp = generic_api_func("/purge", "DELETE")
    assert requests_mock.called 
    assert resp.status_code == 200
    assert resp.json() == {}

def test_generic_nonREST_returns_none(generated_funcs):
    generic_api_func = generated_funcs[generic_func_key]
    resp = generic_api_func("/foobar", "ASDASFDA")
    assert resp is None

def test_generic_nonREST_can_send_data(generated_funcs, config, requests_mock): 
    generic_api_func = generated_funcs[generic_func_key]
    path = "/".join([config.api_endpoint, "foobar"])
    requests_mock.post(path, status_code=200)
    resp = generic_api_func("/foobar", "POST", data="ASDAFASDA")
    assert requests_mock.called 
