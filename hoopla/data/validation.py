import warnings

import numpy

from hoopla.config import Config
from hoopla.data.observations import Observations
from hoopla.pet_models.pet_model import PETModel
from hoopla.sar_models import SARModel


def check_data(config: Config, pet_model: PETModel,
               sar_model: SARModel, observations: Observations,
               data_meteo_forecast: dict, for_ini_forecast: bool = False):
    if config.general.compute_pet:
        potential_evapotranspiration(observations, pet_model)
    elif 'E' not in observations:
        raise ValueError('Hydrology:Data, Potential evapotranspiration not provided')

    if config.general.compute_snowmelt:
        snow_accounting_validation(observations, sar_model)

    if for_ini_forecast:
        meteorological_forecast_validation(config, data_meteo_forecast, sar_model)


def general_validation(observation_dict: dict):
    if 'dates' not in observation_dict:
        raise ValueError('Hydrology:Data, Dates not provided')

    if 'P' not in observation_dict:
        raise ValueError('Hydrology:Data, Precipitations not provided')


def calibration_validation(need_calibration: bool, observation_dict: dict):
    if need_calibration:
        if 'Q' not in observation_dict:
            raise ValueError('Q data not provided. No calibration possible')
    else:
        if 'Q' not in observation_dict:
            warnings.warn('Hydrology:Data, Q data not provided, set to NaN')
            observation_dict['Q'] = numpy.empty(len(observation_dict['dates']))
            observation_dict['Q'][:] = numpy.NaN


def potential_evapotranspiration(data_obs: dict, pet_model: PETModel):
    parameters = pet_model.inputs + pet_model.hyper_parameters
    if len(parameters) == 0:
        raise ValueError(f'PET:Data, data not provided for the {pet_model.name} PET model')

    if 'E' not in data_obs:
        data_obs['E'] = numpy.empty(len(data_obs['dates']))
        data_obs['E'][:] = numpy.NaN


def snow_accounting_validation(data_obs: dict, sar_model: SARModel):
    parameters = sar_model.inputs + sar_model.hyper_parameters
    if len(parameters) == 0:
        raise ValueError(f'SAR:Data, data not provided for the {sar_model.name} SAR model')

    if 'Tmin' not in data_obs and 'CemaNeige' == sar_model.name:
        warnings.warn(
            'Hydrology:Data, Tmin not provided, Tmin set to NaN. '
            'CemaNeige: Because Tmin is missing, the USGS function is used to compute snow fraction.'
        )
        data_obs['Tmin'] = numpy.empty(len(data_obs['Date']))
        data_obs['Tmin'][:] = numpy.NaN

    if 'Tmax' not in data_obs and 'CemaNeige' == sar_model.name:
        warnings.warn(
            'Hydrology:Data, Tmax not provided, Tmax set to NaN. '
            'CemaNeige: Because Tmax is missing, the USGS function is used to compute snow fraction.'
        )
        data_obs['Tmax'] = numpy.empty(len(data_obs['Date']))
        data_obs['Tmax'][:] = numpy.NaN


def meteorological_forecast_validation(config: Config, data_meteo_forecast: dict, sar_model: SARModel):
    if config.forecast.perfect_forecast == 0:
        if config.forecast.meteo_ens:
            raise NotImplemented(
                """Implement this: if Switches.forecast.metEns.on == 1
                    metFile=matfile(DataPath.dataMetFcast);
                    DataMetFcast=metFile.Met_fcast(1,DataPath.dataMetFcastEnsMb);"""
            )

        if 'Date' not in data_meteo_forecast:
            raise ValueError('Hydrology:Data, Meteorological date matrix not provided.')

        if 'leadTime' not in data_meteo_forecast:
            raise ValueError('Hydrology:Data, Meteorological lead times not provided.')

        if 'Pt' not in data_meteo_forecast:
            raise ValueError('Hydrology:Data, Meteorological precipitation forecast not provided.')

        if 'T' not in data_meteo_forecast:
            raise ValueError('Hydrology:Data, Meteorological mean temperature not provided.')

        if 'Tmin' not in data_meteo_forecast:
            warnings.warn('Hydrology:Data, Tmin meteorological forecast not provided. Tmin set to NaN.')
            data_meteo_forecast['Tmin'] = numpy.empty(len(data_meteo_forecast['T']))
            data_meteo_forecast['Tmin'][:] = numpy.NaN

            if config.general.compute_snowmelt and 'CemaNeige' == sar_model.name:
                warnings.warn('Hydrology:Data, because the meteorological forecast for Tmin is missing, '
                              'the USGS function is used to compute snow fraction. '
                              'This may result in a decrease of performance, especially if the '
                              'Hydrodel function was used during calibration')

        if 'Tmax' not in data_meteo_forecast:
            warnings.warn('Hydrology:Data, Tmax meteorological forecast not provided. Tmin set to NaN.')
            data_meteo_forecast['Tmax'] = numpy.empty(len(data_meteo_forecast['T']))
            data_meteo_forecast['Tmax'][:] = numpy.NaN

            if config.general.compute_snowmelt and 'CemaNeige' == sar_model.name:
                warnings.warn('Hydrology:Data, because the meteorological forecast for Tmax is missing, '
                              'the USGS function is used to compute snow fraction. '
                              'This may result in a decrease of performance, especially if the '
                              'Hydrodel function was used during calibration')

        if config.forecast.horizon > len(data_meteo_forecast['Pt']):
            raise ValueError('Hydrology:Data, The specified forecast horizon is longer '
                             'than the meteorological forecast horizon')

        return data_meteo_forecast
