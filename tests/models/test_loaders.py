import pytest

from hoopla.models.hydro_model import BaseHydroModel
from hoopla.models.loaders import list_hydro_models, list_pet_models, load_hydro_model, load_pet_model
from hoopla.models.pet_model import BasePETModel


@pytest.mark.parametrize('name, from_path', [
    ('hydro_model_1', False),
    ('./hoopla/models/hydro/hydro_model_1.py', True),
])
def test_load_hydro_model(name, from_path):
    result = load_hydro_model(name, from_path)

    assert isinstance(result, BaseHydroModel)


def test_list_hydro_models():
    result = list_hydro_models()

    assert 'hydro_model_1' in result


@pytest.mark.parametrize('name, from_path', [
    ('oudin', False),
    ('./hoopla/models/PET/oudin.py', True),
])
def test_load_pet_model(name, from_path):
    result = load_pet_model(name, from_path)

    assert isinstance(result, BasePETModel)


def test_list_pet_models():
    result = list_pet_models()

    assert 'oudin' in result
