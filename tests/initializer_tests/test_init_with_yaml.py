#pylint: skip-file
import pytest
from magellan_models import initialize_with_yaml_file, initialize_with_yaml_url

"""
        swagger.yaml requires an updated MagellanConfig to ensure that the config's ID regex is accurate
        as such no models are generated
    """


def test_init_with_yaml_file_path_works():
    models, funcs, config = initialize_with_yaml_file(
        "./tests/initializer_tests/swagger.yaml")
    assert True


def test_init_with_yaml_url_works(requests_mock):
    example_path = "https://localhost/api/v1/swagger.yaml"
    with open("./tests/initializer_tests/swagger.yaml", mode='rb') as swagger_file:
        requests_mock.get(example_path, status_code=200,
                          content=swagger_file.read())
        initialize_with_yaml_url(example_path)
        assert requests_mock.called


def test_init_with_yaml_throws_on_error(requests_mock):
    example_path = "https://localhost/api/v1/swagger.yaml"
    with open("./tests/initializer_tests/swagger.yaml", mode='rb') as swagger_file:
        requests_mock.get(example_path, status_code=9000,
                          content=swagger_file.read())
        with pytest.raises(Exception):
            initialize_with_yaml_url(example_path)
        assert requests_mock.called


def test_init_without_conf_returns_a_new_one(requests_mock):
    models, funcs, config = initialize_with_yaml_file(
        "./tests/initializer_tests/swagger.yaml")
    assert config is not None

    example_path = "https://localhost/api/v1/swagger.yaml"
    with open("./tests/initializer_tests/swagger.yaml", mode='rb') as swagger_file:
        requests_mock.get(example_path, status_code=200,
                          content=swagger_file.read())
        models, funcs, config = initialize_with_yaml_url(example_path)
        assert config is not None
        assert requests_mock.called
