import importlib
import importlib.util
import sys
from pathlib import Path

from hoopla.models.hydro_model import BaseHydroModel


def load_hydro_model(name_or_path: str, from_path: bool = False) -> BaseHydroModel:
    if from_path:
        spec = importlib.util.spec_from_file_location('_module_imported_from_path', name_or_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules['_module_imported_from_path'] = module
        spec.loader.exec_module(module)


        return module.HydroModel()

    module = importlib.import_module(f'hoopla.models.hydro.{name_or_path}')

    return module.HydroModel()


def load_pet_model(name_or_path: str):
    raise NotImplementedError


def load_sar_model(name_or_path: str):
    raise NotImplementedError


def list_hydro_models():
    hydro_models_path = Path(__file__).parent.resolve() / 'hydro'
    model_names = [filename.stem for filename in hydro_models_path.iterdir() if filename.stem not in ['__init__', '__pycache__']]

    return model_names


def list_pet_models():
    raise NotImplementedError


def list_sar_models():
    raise NotImplementedError
