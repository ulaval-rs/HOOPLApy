import datetime
import warnings
from typing import Optional, Tuple

import numpy as np

from hoopla.config import Config
from hoopla.models.hydro_model import BaseHydroModel
from hoopla.models.pet_model import BasePETModel
from hoopla.models.sar_model import BaseSARModel
from hoopla.models.util import find_day_of_year


def crop_data(config: Config,
              observations: dict,
              hydro_model: BaseHydroModel,
              pet_model: BasePETModel,
              sar_model: BaseSARModel,
              ini_type: str,
              forecast_data: Optional[dict] = None) -> Tuple[dict, dict, dict]:
    # Initializing variables to be returned
    observations_for_forecast = {} if forecast_data is None else forecast_data
    observations_for_warm_up = {}

    # Cropable data
    hydro_variables = hydro_model.inputs()
    pet_variables = pet_model.inputs() if config.general.compute_pet else []
    sar_variables = sar_model.inputs() if config.general.compute_snowmelt else []

    cropable_data_obs = {'dates', 'Q', *hydro_variables, *pet_variables, *sar_variables}
    cropable_data_forecast = {'Pt', 'T', 'Tmax', 'Tmin'}

    # Dates
    ## Retrieve calibration/validation/forecast start and end dates
    if ini_type == 'ini_calibration':
        date_begin = config.dates.calibration.begin
        date_end = config.dates.calibration.end
    elif ini_type == 'ini_simulation':
        date_begin = config.dates.simulation.begin
        date_end = config.dates.simulation.end
    elif ini_type == 'ini_forecast':
        date_begin = config.dates.forecast.begin
        date_end = config.dates.forecast.end
    else:
        raise ValueError(
            f"Wrong ini value: {ini_type}. Should be one of ['ini_calibration', 'ini_simulation', 'ini_forecast']."
        )

    ## Numerical time
    time_step = float(config.general.time_step.replace('h', ''))

    ## Get indices of the dates of interest
    dates = observations['dates']
    select = np.array([date_begin <= d <= date_end for d in dates])  # Array of True and False corresponding to the indexes to keep.

    if date_begin < min(dates) or date_begin > max(dates) or date_end > max(dates) or date_end < min(dates):
        raise ValueError(
            'Hydrology:Dates, The specified calibration/simulation/forecasting dates are out of the available period'
        )

    ## Croping data for forecast
    if ini_type == 'ini_forecast':
        # TODO: implement this https://github.com/ulaval-rs/HOOPLA/blob/master/Tools/Misc/cropData.m
        if not config.forecast.perfect_forecast:
            # Forecast dates
            select_forecast_1 = np.array([config.dates.forecast.begin <= d <= config.dates.forecast.end for d in observations_for_forecast['dates']])  # Array of True and False corresponding to the indices of dates between forecast start and forecast end.
            dates_without_hours = [datetime.datetime(year=d.year, month=d.month, day=d.day) for d in observations_for_forecast['dates']]
            select_forecast_2 = np.array([d == datetime.timedelta(hours=config.forecast.issue_time) for d in (observations_for_forecast['dates'] - dates_without_hours)])  # indices of dates corresponding to hydrological issue time
            select_forecast = select_forecast_1 & select_forecast_2

            forecast_dates = observations_for_forecast['dates'][select_forecast]

            raise NotImplementedError

        if config.forecast.perfect_forecast:
            raise NotImplementedError

        raise NotImplementedError

    ## Croping data for warm up
    if config.general.compute_warm_up:
        ## Dates warm up
        # date_begin_warm_up = datetime.datetime.fromordinal(int(date_begin.toordinal() - time_step / 3 * 365))
        # date_end_warm_up = datetime.datetime.fromordinal(int(date_begin.toordinal() - time_step / 24))

        date_begin_warm_up = date_begin - datetime.timedelta(days=time_step / 3 * 365)
        date_end_warm_up = date_begin - datetime.timedelta(days=time_step / 24)
        select_warm = np.array([date_begin_warm_up <= d <= date_end_warm_up for d in dates])  # Array of True and False corresponding to the indexes to keep.

        # Check if one year (3h time step) or 8 years (24h time step) is available prior to date -- case YES
        if np.sum(select_warm) == 365 * 8:
            for obs in cropable_data_obs:
                observations_for_warm_up[obs] = observations[obs][select_warm]

            observations_for_warm_up = {**observations, **observations_for_warm_up}  # Here the observations_for_warm_up data overwrite the observations ones in the new dict.

        elif (np.sum(select_warm) - np.sum(select)) < 365 * 8:
            warnings.warn(
                f'Hydrology:Continuity\nNo data available before calibration/simulation/forecasting dates'
                f'or available time period preceding date shorter than {time_step / 3} year (~3000 time steps).'
                'Calibration/Simulation/Forecasting period data are used to create a  mean year for warm up.'
                'Please check for hydrological continuity between the end of warm up and '
                'the beginning of forecast period.'
            )

            # Creation of sliding years which ends by the day of the year that just precedes the beginning of the simulation
            days_of_year = np.array([find_day_of_year(date) for date in observations['dates']])  # days of the year of the entire period where catchment data are available.
            day_of_year_start = (date_begin - datetime.datetime(year=date_begin.year, month=1, day=1)).seconds / 60 / 60 / 24  # Days of the year of the first day of simulation
            day_of_year_end_warm_up = (day_of_year_start - time_step / 24) % 365  # Day of the year of the last timestep of the warm up.

            index_warmup_end = np.argwhere(days_of_year == day_of_year_end_warm_up)  # Indices of the end of each sliding year.
            index_warmup_start = index_warmup_end - 365 * 24 / time_step + 1  # indices of the start of each sliding year.
            raise NotImplementedError

    for obs in cropable_data_obs:
        observations[obs] = observations[obs][select]

    ## Checking ratio of streamflow NaN
    if np.sum(np.isnan(observations['Q'])) / len(observations['Q']) > 0.75:
        warnings.warn(
            f'Hydrology:StreamflowData, Only {100*(1 - np.sum(np.isnan(observations["Q"])) / len(observations["Q"])):.1f} % '
            f'of streamflow are not NaN. Consider changing the period'
        )
        if ini_type == 'ini_calibration' and np.sum(np.isnan(observations['Q'])) == 0:
            raise ValueError('All streamflow are NaN. The calibration is not possible. Please, change calibration dates')

    return observations, observations_for_forecast, observations_for_warm_up
