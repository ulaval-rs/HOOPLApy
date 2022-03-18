import warnings
from datetime import datetime, timedelta
from typing import Dict

import numpy as np

from hoopla.config import Config
from hoopla.hydro_models.hydro_model import HydroModel
from hoopla.pet_models.pet_model import PETModel
from hoopla.sar_models import SARModel


def crop_data(config: Config, data_obs: Dict, model: HydroModel, pet_model: PETModel, sar_model: SARModel, ini: str):
    # Cropable data
    hydro_variables = model.parameters
    pet_variables = pet_model.parameter_group_1 if config.general.compute_pet else []
    sar_variables = sar_model.parameter_group_1 if config.general.compute_snowmelt else []

    cropable_data_obs = {'Date', 'Q', *hydro_variables, *pet_variables, *sar_variables}
    cropable_data_forecast = {'Pt', 'T', 'Tmax', 'Tmin'}

    # Dates
    ## Retrieve calibration/validation/forecast start and end dates
    if ini == 'ini_calibration':
        date_begin = config.dates.calibration.begin
        date_end = config.dates.calibration.end
    elif ini == 'ini_simulation':
        date_begin = config.dates.simulation.begin
        date_end = config.dates.simulation.end
    elif ini == 'ini_forecast':
        date_begin = config.dates.forecast.begin
        date_end = config.dates.forecast.end
    else:
        raise ValueError(
            f"Wrong ini value: {ini}. Should be one of ['ini_calibration', 'ini_simulation', 'ini_forecast']."
        )

    ## Numerical time
    time_step = float(config.general.time_step.replace('h', ''))

    ## Dates to date objects
    dates = np.array([datetime(year=d[0], month=d[1], day=d[2], hour=d[3], minute=d[4], second=d[5]) for d in data_obs['Date']])

    ## Get indices of the dates of interest
    # TODO: Question, why time step (3h or 24h) is always divided by 24?
    select = np.isin(dates, np.arange(date_begin, date_end, timedelta(hours=time_step / 24)).astype(datetime))

    ## Dates warm up
    # TODO: Question, why those division on the time step?
    date_begin_warm_up = date_begin - timedelta(hours=time_step) / 3 * 365
    date_end_warm_up = date_begin - timedelta(hours=time_step) / 24
    # select_warm = np.isin(dates, np.arange(date_begin_warm_up, date_end_warm_up, timedelta(hours=time_step / 24)).astype(datetime))

    if date_begin < min(dates) or date_begin > max(dates) or date_end > max(dates) or date_end < min(dates):
        raise ValueError(
            'Hydrology:Dates, The specified calibration/simulation/forecasting dates are out of the available period'
        )

    ## Croping data for forecast
    if ini == 'ini_forecast':
        # TODO: implement this https://github.com/ulaval-rs/HOOPLA/blob/master/Tools/Misc/cropData.m
        if not config.forecast.perfect_forecast:
            raise NotImplementedError

        if config.forecast.perfect_forecast:
            raise NotImplementedError

        raise NotImplementedError

    ## Croping data for warm up
    if config.general.compute_warm_up:
        raise NotImplementedError

    for obs in cropable_data_obs:
        data_obs[obs] = data_obs[obs][select]

    ## Checking ratio of streamflow NaN
    if np.sum(np.isnan(data_obs['Q'])) / len(data_obs['Q']) > 0.75:
        warnings.warn(
            f'Hydrology:StreamflowData, Only {100*(1- np.sum(np.isnan(data_obs["Q"])) / len(data_obs["Q"])):.1f} % '
            f'of streamflow are not NaN. Consider changing the period'
        )
        if ini == 'ini_calibration' and np.sum(np.isnan(data_obs['Q'])) == 0:
            raise ValueError('All streamflow are NaN. The calibration is not possible. Please, change calibration dates')


