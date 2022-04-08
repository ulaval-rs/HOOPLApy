import warnings
from typing import Dict

import numpy

from hoopla.config import Config
from hoopla.pet_models.pet_model import PETModel
from hoopla.sar_models import SARModel


def check_data(config: Config, pet_model: PETModel,
               sar_model: SARModel, data_obs: Dict,
               data_meteo_forecast: Dict, for_ini_forecast: bool = False):
    _general_validation(data_obs)
    _calibration_validation(config.operations.calibration, data_obs)

    if config.general.compute_pet:
        _potential_evapotranspiration(data_obs, pet_model)
    elif 'E' not in data_obs:
        raise ValueError('Hydrology:Data, Potential evapotranspiration not provided')

    if config.general.compute_snowmelt:
        _snow_accounting_validation(data_obs, sar_model)

    if for_ini_forecast:
        _meteorological_forecast_validation(config, data_meteo_forecast, sar_model)


def _general_validation(data_obs):
    if len(data_obs['Date']) == 0:
        raise ValueError('Hydrology:Data, Dates not provided')

    if len(data_obs['Pt']) == 0:
        raise ValueError('Hydrology:Data, Precipitations not provided')


def _calibration_validation(need_calibration: bool, data_obs):
    if need_calibration:
        if 'Q' not in data_obs:
            raise ValueError('Q data not provided. No calibration possible')
    else:
        if 'Q' not in data_obs:
            warnings.warn('Hydrology:Data, Q data not provided, set to NaN')
            data_obs['Q'] = numpy.empty(len(data_obs['Date']))
            data_obs['Q'][:] = numpy.NaN


def _potential_evapotranspiration(data_obs: Dict, pet_model: PETModel):
    parameters = pet_model.inputs + pet_model.hyper_parameters
    if len(parameters) == 0:
        raise ValueError(f'PET:Data, data not provided for the {pet_model.name} PET model')

    if 'E' not in data_obs:
        data_obs['E'] = numpy.empty(len(data_obs['Date']))
        data_obs['E'][:] = numpy.NaN


def _snow_accounting_validation(data_obs: Dict, sar_model: SARModel):
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


def _meteorological_forecast_validation(config: Config, data_meteo_forecast: Dict, sar_model: SARModel):
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

        if config.forecast.horizon > len(data_meteo_forecast['Pt'][1]):
            raise ValueError('Hydrology:Data, The specified forecast horizon is longer '
                             'than the meteorological forecast horizon')

        return data_meteo_forecast
