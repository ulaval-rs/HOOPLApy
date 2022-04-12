from typing import List

import scipy.io

from hoopla.config import Config, DATA_PATH
from hoopla.hydro_models import HydroModel
from hoopla.hydro_models.hydro_model_1 import HydroModel1

HYDRO_MODELS = {
    'HydroMod1': HydroModel1,
    'HydroMod2': HydroModel,
    'HydroMod3': HydroModel,
    'HydroMod4': HydroModel,
    'HydroMod5': HydroModel,
    'HydroMod6': HydroModel,
    'HydroMod7': HydroModel,
    'HydroMod8': HydroModel,
    'HydroMod9': HydroModel,
    'HydroMod10': HydroModel,
    'HydroMod11': HydroModel,
    'HydroMod12': HydroModel,
    'HydroMod13': HydroModel,
    'HydroMod14': HydroModel,
    'HydroMod15': HydroModel,
    'HydroMod16': HydroModel,
    'HydroMod17': HydroModel,
    'HydroMod18': HydroModel,
    'HydroMod19': HydroModel,
    'HydroMod20': HydroModel,
}


def load_hydrological_models(config: Config) -> List[HydroModel]:
    """Load the available hydrological models.

    Parameters
    ----------
    config
        Config object.

    Returns
    -------
    List[HydroModel]
        List of available hydrological models.
    """
    models = scipy.io.loadmat(f'{DATA_PATH}/{config.general.time_step}/Misc/hydro_model_names.mat', simplify_cells=True)
    hydro_models = []
    
    for i in models['nameM']:
        name = i[0]
        inputs = i[1].split('_')

        hydro_model = HYDRO_MODELS[name](name=name, inputs=inputs, config=config)
        hydro_models.append(hydro_model)

    return hydro_models
