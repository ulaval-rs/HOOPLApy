from typing import Dict, Tuple

from scipy.io import loadmat

from .config import Config
from .initialization import DATA_PATH
from . import validation


def make_calibration(
        config: Config,
        catchment_name: str,
        models: Dict[str, str],
        pet_models: Dict[str, Tuple[str, str]],
        sar_models: Dict[str, Tuple[str, str]]):
    # Data specification for catchment / parameters
    data_obs = loadmat(f'{DATA_PATH}/{config.general.time_step}/Hydromet_obs/Hydromet_obs_{catchment_name}.mat')
    model_param_bound = loadmat(f'{DATA_PATH}/{config.general.time_step}/Model_parameters/model_param_boundaries.mat')
    snow_model_param_bound = loadmat(f'{DATA_PATH}/{config.general.time_step}/Model_parameters/snow_model_param_boundaries.mat')
    data_meteo_forecast = loadmat(f'{DATA_PATH}/{config.general.time_step}/Det_met_fcast/Met_fcast_{catchment_name}.mat')

    validation.check_data(
        config,
        pet_models,
        sar_models,
        data_obs,
        data_meteo_forecast,
    )


def _calibrate():
    pass
