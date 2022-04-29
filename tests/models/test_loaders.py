import pytest

from hoopla.models.hydro_model import BaseHydroModel
from hoopla.models.loaders import list_hydro_models, load_hydro_model


@pytest.mark.parametrize('name, from_path', [
    ('hydro_model_1', False),
    ('./hoopla/models/hydro/hydro_model_1.py', True),
])
def test_load_hydro_model(name, from_path):
    result = load_hydro_model(name, from_path)

    assert issubclass(result, BaseHydroModel)


def test_list_hydro_models():
    result = list_hydro_models()

    assert 'hydro_model_1' in result
