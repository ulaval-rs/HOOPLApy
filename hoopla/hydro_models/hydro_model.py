from typing import List

import scipy.io

from hoopla.config import Config, DATA_PATH
from hoopla.hydro_models.hydro_model_1 import HydroModel1

HYDRO_MODELS = {
    'HydroMod1': HydroModel1,
    'HydroMod2': HydroModel1,
    'HydroMod3': HydroModel1,
    'HydroMod4': HydroModel1,
    'HydroMod5': HydroModel1,
    'HydroMod6': HydroModel1,
    'HydroMod7': HydroModel1,
    'HydroMod8': HydroModel1,
    'HydroMod9': HydroModel1,
    'HydroMod10': HydroModel1,
    'HydroMod11': HydroModel1,
    'HydroMod12': HydroModel1,
    'HydroMod13': HydroModel1,
    'HydroMod14': HydroModel1,
    'HydroMod15': HydroModel1,
    'HydroMod16': HydroModel1,
    'HydroMod17': HydroModel1,
    'HydroMod18': HydroModel1,
    'HydroMod19': HydroModel1,
    'HydroMod20': HydroModel1,
}


class HydroModel:

    def __init__(self, name: str, parameters: List):
        self.name = name
        self.parameters = parameters
        self.model = HYDRO_MODELS[name]


def load_hydrological_models(time_step: str) -> List[HydroModel]:
    """Load the available hydrological models.

    Parameters
    ----------
    time_step
        Time Step string ('24h' or '3h')

    Returns
    -------
    List[HydroModel]
        List of available hydrological models.
    """
    models = scipy.io.loadmat(f'{DATA_PATH}/{time_step}/Misc/hydro_model_names.mat')

    return [HydroModel(name=i[0][0], parameters=i[1][0].split('_')) for i in models['nameM']]
