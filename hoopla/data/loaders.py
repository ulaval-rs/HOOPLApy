import warnings
from datetime import datetime

import numpy as np
from scipy.io import loadmat

from hoopla.config import Config
from hoopla.data import validation
from hoopla.models.pet_model import BasePETModel
from hoopla.models.sar_model import BaseSARModel


def load_observations(path: str, file_format: str, config: Config, pet_model: BasePETModel, sar_model: BaseSARModel) -> dict:
    if file_format == 'mat':
        observation_dict = loadmat(file_name=path, simplify_cells=True)
        observation_dict = {k: v for k, v in observation_dict.items() if '__' not in k}

        # Transformation specific to the .mat files
        observation_dict['P'] = observation_dict.pop('Pt')
        observation_dict['latitude'] = observation_dict.pop('Lat')
        observation_dict['dates'] = np.array(
            [datetime(year=d[0], month=d[1], day=d[2], hour=d[3], minute=d[4], second=d[5]) for d in observation_dict.pop('Date')]
        )

    else:
        raise ValueError(f'"{file_format}" file_format not supported/not found.')

    # Validations
    validation.general_validation(observation_dict)
    validation.validate_calibration(config.operations.calibration, observation_dict)
    if config.general.compute_pet:
        validation.validate_potential_evapotranspiration(observation_dict, pet_model)
    if config.general.compute_snowmelt:
        validation.validate_snow_accounting(observation_dict, sar_model)

    return observation_dict


def load_forecast_data(filepath: str, file_format: str, config: Config, sar_model: BaseSARModel):
    if file_format == 'mat':
        forecast_data = loadmat(file_name=filepath, simplify_cells=True)

    else:
        raise ValueError(f'"{file_format}" file_format not supported/not found.')

    validation.validate_meteorological_forecast(config, forecast_data, sar_model)

    return forecast_data


def load_model_params_boundaries(filepath: str, model_name: str, file_format: str):
    if file_format == 'mat':
        param_boundaries = loadmat(file_name=filepath, simplify_cells=True)

    else:
        raise ValueError(f'"{file_format}" file_format not supported/not found.')

    warnings.warn('Model params boundaries data are not validated')

    return param_boundaries[model_name]


def load_sar_model_params_boundaries(filepath: str, model_name: str, file_format: str):
    if file_format == 'mat':
        param_boundaries = loadmat(file_name=filepath, simplify_cells=True)

    else:
        raise ValueError(f'"{file_format}" file_format not supported/not found.')

    warnings.warn('SAR model params boundaries data are not validated')

    return param_boundaries[model_name]
