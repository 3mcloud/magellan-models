#pylint: skip-file
import pytest
from magellan_models import initialize_with_endpoint
from tests.helper import get_testing_spec

def test_init_with_endpoint_works(requests_mock):
    example_path = "https://localhost/api/v1/swagger.yaml"
    requests_mock.get(example_path, status_code=200,
                        json=get_testing_spec())
    models, funcs, conf = initialize_with_endpoint(example_path)
    assert models is not None 
    assert funcs is not None
    assert conf is not None
    assert requests_mock.called

def test_init_with_endpoint_throws_on_error(requests_mock):
    example_path = "https://localhost/api/v1/swagger.yaml"
    requests_mock.get(example_path, status_code=9000,
                        json=get_testing_spec())
    with pytest.raises(Exception):
        initialize_with_endpoint(example_path)
    assert requests_mock.called
