#pylint: skip-file
import pytest
from magellan_models import initialize_with_spec
from tests.helper import get_testing_spec

def test_init_with_json_works():
    models, funcs, config = initialize_with_spec(get_testing_spec())
    assert config is not None
    assert funcs is not None
    assert models is not None
    assert True
