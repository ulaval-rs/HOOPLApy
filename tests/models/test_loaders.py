import pytest

from hoopla.models.hydro_model import BaseHydroModel
from hoopla.models.loaders import list_hydro_models, list_pet_models, load_hydro_model, load_pet_model, load_sar_model, list_sar_models
from hoopla.models.pet_model import BasePETModel
from hoopla.models.sar_model import BaseSARModel


@pytest.mark.parametrize('name, from_path', [
    ('HydroMod1', False),
    ('./hoopla/models/hydro/hydro_model_1.py', True),
])
def test_load_hydro_model(name, from_path):
    result = load_hydro_model(name, from_path)

    assert isinstance(result, BaseHydroModel)


def test_list_hydro_models():
    result = list_hydro_models()

    assert 'HydroMod1' in result


@pytest.mark.parametrize('name, from_path', [
    ('Oudin', False),
    ('./hoopla/models/PET/oudin.py', True),
])
def test_load_pet_model(name, from_path):
    result = load_pet_model(name, from_path)

    assert isinstance(result, BasePETModel)


def test_list_pet_models():
    result = list_pet_models()

    assert 'Oudin' in result
    assert isinstance(result['Oudin'], BasePETModel)


@pytest.mark.parametrize('name, from_path', [
    ('CemaNeige', False),
    ('./hoopla/models/SAR/cema_neige.py', True),
])
def test_load_sar_model(name, from_path):
    result = load_sar_model(name, from_path)

    assert isinstance(result, BaseSARModel)


def test_list_sar_models():
    result = list_sar_models()

    assert 'CemaNeige' in result
    assert isinstance(result['CemaNeige'], BaseSARModel)
