import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

from hoopla.models.hydro_model import BaseHydroModel
from hoopla.models.pet_model import BasePETModel
from hoopla.models.sar_model import BaseSARModel


def load_hydro_model(name_or_path: str, from_path: bool = False) -> BaseHydroModel:
    if from_path:
        module = _load_module_form_path(name_or_path)

        return module.HydroModel()

    models = list_hydro_models()

    return models[name_or_path]


def load_pet_model(name_or_path: str, from_path: bool = False) -> BasePETModel:
    if from_path:
        module = _load_module_form_path(name_or_path)

        return module.PETModel()

    models = list_pet_models()

    return models[name_or_path]


def load_sar_model(name_or_path: str, from_path: bool = False) -> BaseSARModel:
    if from_path:
        module = _load_module_form_path(name_or_path)

        return module.SARModel()

    models = list_sar_models()

    return models[name_or_path]


def list_hydro_models() -> dict[str, BaseHydroModel]:
    """Returns dict of {model_name: model_instance}"""
    hydro_models_path = Path(__file__).parent.resolve() / 'hydro'

    models = {}
    for filepath in hydro_models_path.iterdir():
        if filepath.stem not in ['__init__', '__pycache__']:
            module = _load_module_form_path(str(filepath))
            model: BaseHydroModel = module.HydroModel()

            models[model.name()] = model

    return models


def list_pet_models() -> dict[str, BasePETModel]:
    """Returns dict of {model_name: model_instance}"""
    models_path = Path(__file__).parent.resolve() / 'PET'

    models = {}
    for filepath in models_path.iterdir():
        if filepath.stem not in ['__init__', '__pycache__']:
            module = _load_module_form_path(str(filepath))
            model: BasePETModel = module.PETModel()

            models[model.name()] = model

    return models


def list_sar_models() -> dict[str, BaseSARModel]:
    """Returns dict of {model_name: model_instance}"""
    models_path = Path(__file__).parent.resolve() / 'SAR'

    models = {}
    for filepath in models_path.iterdir():
        if filepath.stem not in ['__init__', '__pycache__']:
            module = _load_module_form_path(str(filepath))
            model: BaseSARModel = module.SARModel()

            models[model.name()] = model

    return models


def _load_module_form_path(path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location('_module', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules['_module'] = module
    spec.loader.exec_module(module)

    return module
