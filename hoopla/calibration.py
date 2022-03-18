from typing import Dict

from scipy.io import loadmat

from hoopla.config import Config
from hoopla.hydro_models.hydro_model import HydroModel
from hoopla.initialization import DATA_PATH
from hoopla.pet_models.pet_model import PETModel
from hoopla.sar_models.sar_model import SARModel
from hoopla.util import validation
from hoopla.util.croping import crop_data


def make_calibration(config: Config, catchment_name: str, model: HydroModel, pet_model: PETModel, sar_model: SARModel):
    # Data specification for catchment / parameters
    data_obs = loadmat(f'{DATA_PATH}/{config.general.time_step}/Hydromet_obs/Hydromet_obs_{catchment_name}.mat')
    data_meteo_forecast = loadmat(f'{DATA_PATH}/{config.general.time_step}/Det_met_fcast/Met_fcast_{catchment_name}.mat')

    # Validate that all necessary data are provided
    validation.check_data(config, pet_model, sar_model, data_obs, data_meteo_forecast)

    # Crop observed data according to specified dates and warm up
    crop_data(config, data_obs, model, pet_model, sar_model, ini='ini_calibration')

    # Launch calibration
    if config.general.compute_snowmelt:
        if config.general.compute_warm_up:
            raise NotImplementedError
        else:
            calibrate(config, data_obs, model, pet_model, sar_model)


def calibrate(config: Config, data_obs: Dict, model: HydroModel, pet_model: PETModel, sar_model: SARModel):
    model_param_bound = loadmat(f'{DATA_PATH}/{config.general.time_step}/Model_parameters/model_param_boundaries.mat')
    snow_model_param_bound = loadmat(f'{DATA_PATH}/{config.general.time_step}/Model_parameters/snow_model_param_boundaries.mat')