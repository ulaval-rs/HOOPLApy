from typing import Dict, List

import scipy.io

from .config import Config
from .models import HydroModel, PETModel, SARModel

DATA_PATH = './data'


def list_catchments(config: Config) -> List:
    """Load catchment names and returns list of names"""
    catchments = scipy.io.loadmat(f'{DATA_PATH}/{config.general.time_step}/Misc/catchment_names.mat')

    return [i[0][0] for i in catchments['nameC']]


def list_models(config: Config) -> List[HydroModel]:
    """Load hydrological models"""
    models = scipy.io.loadmat(f'{DATA_PATH}/{config.general.time_step}/Misc/hydro_model_names.mat')

    return [HydroModel(name=i[0][0], parameters=i[1][0].split('_')) for i in models['nameM']]


def list_evaporation_models(config: Config) -> List[PETModel]:
    """Load potential evaporation models"""
    if config.general.compute_pet:
        models = scipy.io.loadmat(f'{DATA_PATH}/{config.general.time_step}/Misc/pet_model_names.mat')
        pet_models = []

        for model in models['nameE']:
            pet_models.append(
                PETModel(
                    name=model[0][0],
                    parameters_group_1=model[1][0].split('_'),
                    parameters_group_2=model[2][0].split('_')
                )
            )

        return pet_models

    return []


def list_snow_models(config: Config) -> List[SARModel]:
    """Load snow accounting model"""
    if config.general.compute_snowmelt:
        models = scipy.io.loadmat(f'{DATA_PATH}/{config.general.time_step}/Misc/snow_model_names.mat')
        sar_models = []

        for model in models['nameS']:
            sar_models.append(
                SARModel(
                    name=model[0][0],
                    parameters_group_1=model[1][0].split('_'),
                    parameters_group_2=model[2][0].split('_')
                )
            )

        return sar_models

    return []
