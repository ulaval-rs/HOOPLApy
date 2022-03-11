from datetime import datetime
from typing import Dict

from scipy.io import loadmat

from .config import Config
from .initialization import DATA_PATH
from . import validation
from .models import HydroModel, PETModel, SARModel


def make_calibration(
        config: Config,
        catchment_name: str,
        model: HydroModel,
        pet_model: PETModel,
        sar_model: SARModel):
    # Data specification for catchment / parameters
    data_obs = loadmat(f'{DATA_PATH}/{config.general.time_step}/Hydromet_obs/Hydromet_obs_{catchment_name}.mat')
    model_param_bound = loadmat(f'{DATA_PATH}/{config.general.time_step}/Model_parameters/model_param_boundaries.mat')
    snow_model_param_bound = loadmat(f'{DATA_PATH}/{config.general.time_step}/Model_parameters/snow_model_param_boundaries.mat')
    data_meteo_forecast = loadmat(f'{DATA_PATH}/{config.general.time_step}/Det_met_fcast/Met_fcast_{catchment_name}.mat')

    # Validate that all necessary data are provided
    validation.check_data(config, pet_model, sar_model, data_obs, data_meteo_forecast)

    # Crop observed data according to specified dates and warm up
    crop_data(config, data_obs, model, pet_model, sar_model, ini='ini_calibration')


def crop_data(config: Config, data_obs: Dict, model: HydroModel, pet_model: PETModel, sar_model: SARModel, ini: str):
    # Cropable data
    hydro_variables = model.parameters
    pet_variables = pet_model.parameters_group_1 if config.general.compute_pet else []
    sar_variables = sar_model.parameters_group_1 if config.general.compute_snowmelt else []

    cropable_data_obs = {'Date', 'Q', *hydro_variables, *pet_variables, *sar_variables}
    cropable_data_forecast = {'Pt', 'T', 'Tmax', 'Tmin'}

    # Dates
    ## Retrieve calibration/validation/forecast start and end dates
    if ini not in ['ini_calibration', 'ini_simulation', 'ini_forecast']:
        raise ValueError(
            f"Wrong ini value: {ini}. Should be one of ['ini_calibration', 'ini_simulation', 'ini_forecast']."
        )

    if ini == 'ini_calibration':
        date_begin = config.dates.calibration.begin
        date_end = config.dates.calibration.end
    elif ini == 'ini_simulation':
        date_begin = config.dates.simulation.begin
        date_end = config.dates.simulation.end
    elif ini == 'ini_forecast':
        date_begin = config.dates.forecast.begin
        date_end = config.dates.forecast.end

    ## Numerical time
    time_step = float(config.general.time_step.replace('h', ''))

    ## Dates to date objects
    date = [datetime(year=d[0], month=d[1], day=d[2], hour=d[3], minute=d[4], second=d[5]) for d in data_obs['Date']]
    # TODO

    ## Dates warm up


