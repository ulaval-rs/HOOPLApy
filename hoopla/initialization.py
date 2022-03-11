from typing import Dict, List

import scipy.io

from .config import Config

DATA_PATH = './data'


def list_catchments(config: Config) -> List:
    """Load catchment names and returns list of names"""
    catchments = scipy.io.loadmat(f'{DATA_PATH}/{config.general.time_step}/Misc/catchment_names.mat')

    return [i[0][0] for i in catchments['nameC']]


def list_models(config: Config) -> Dict:
    """Load hydrological models {model_name: parameters}"""
    models = scipy.io.loadmat(f'{DATA_PATH}/{config.general.time_step}/Misc/hydro_model_names.mat')

    # ex. {'HydroMod1': 'Pt_E'}
    return {i[0][0]: i[1][0] for i in models['nameM']}


def list_evaporation_models(config: Config) -> Dict:
    """Load potential evaporation models {model_name: (parameters_group_1, parameters_group_2)}"""
    if config.general.compute_snowmelt:
        models = scipy.io.loadmat(f'{DATA_PATH}/{config.general.time_step}/Misc/pet_model_names.mat')

        # ex. {'Oudin': ('Date_T', 'Lat')}
        return {i[0][0]: (i[1][0], i[2][0]) for i in models['nameE']}

    return {}


def list_snow_models(config: Config) -> Dict:
    """Load snow accounting model {model_name: (parameters_group_1, parameters_group_2)}"""
    if config.general.compute_snowmelt:
        models = scipy.io.loadmat(f'{DATA_PATH}/{config.general.time_step}/Misc/snow_model_names.mat')

        # ex. {'CemaNeige': ('Pt_T_Tmin_Tmax', 'Beta_gradT_T_Zz5')}
        return {i[0][0]: (i[1][0], i[2][0]) for i in models['nameS']}

    return {}
