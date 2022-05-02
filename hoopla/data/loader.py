from datetime import datetime

import numpy as np
from scipy.io import loadmat

from hoopla.config import Config
from hoopla.data import validation
from hoopla.models.pet_model import BasePETModel
from hoopla.sar_models import SARModel


def load_observations(path: str, file_format: str, config: Config, pet_model: BasePETModel, sar_model: SARModel) -> dict:
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
    validation.calibration_validation(config.operations.calibration, observation_dict)
    if config.general.compute_pet:
        validation.potential_evapotranspiration(observation_dict, pet_model)
    if config.general.compute_snowmelt:
        validation.snow_accounting_validation(observation_dict, sar_model)

    return observation_dict


def load_forecast_data(filepath: str, file_format: str, config: Config, sar_model: SARModel):
    if file_format == 'mat':
        forecast_data = loadmat(file_name=filepath, simplify_cells=True)

    else:
        raise ValueError(f'"{file_format}" file_format not supported/not found.')

    validation.meteorological_forecast_validation(config, forecast_data, sar_model)

    return forecast_data
