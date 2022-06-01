import warnings
from datetime import datetime, timedelta

import numpy as np

from hoopla.config import Config
from hoopla.models.hydro_model import BaseHydroModel
from hoopla.models.pet_model import BasePETModel
from hoopla.models.sar_model import BaseSARModel


def crop_data(config: Config, observations: dict,
              hydro_model: BaseHydroModel, pet_model: BasePETModel, sar_model: BaseSARModel, ini: str):
    # Cropable data
    hydro_variables = hydro_model.inputs()
    pet_variables = pet_model.inputs() if config.general.compute_pet else []
    sar_variables = sar_model.inputs() if config.general.compute_snowmelt else []

    cropable_data_obs = {'dates', 'Q', *hydro_variables, *pet_variables, *sar_variables}
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

    ## Get indices of the dates of interest
    dates = observations['dates']
    select = np.isin(dates, np.arange(date_begin, date_end, timedelta(hours=time_step / 24)).astype(datetime))

    ## Dates warm up
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
        observations[obs] = observations[obs][select]

    ## Checking ratio of streamflow NaN
    if np.sum(np.isnan(observations['Q'])) / len(observations['Q']) > 0.75:
        warnings.warn(
            f'Hydrology:StreamflowData, Only {100*(1 - np.sum(np.isnan(observations["Q"])) / len(observations["Q"])):.1f} % '
            f'of streamflow are not NaN. Consider changing the period'
        )
        if ini == 'ini_calibration' and np.sum(np.isnan(observations['Q'])) == 0:
            raise ValueError('All streamflow are NaN. The calibration is not possible. Please, change calibration dates')


