import json
from datetime import datetime

import numpy as np
import spotpy.parameter
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
    observation_dict = validation.general_validation(observation_dict)
    observation_dict = validation.validate_calibration(config.operations.calibration, observation_dict)
    if config.general.compute_pet:
        observation_dict = validation.validate_potential_evapotranspiration(observation_dict, pet_model)
    if config.general.compute_snowmelt:
        observation_dict = validation.validate_snow_accounting(observation_dict, sar_model)

    return observation_dict


def load_forecast_data(filepath: str, file_format: str, config: Config, sar_model: BaseSARModel) -> dict:
    if file_format == 'mat':
        forecast_data = loadmat(file_name=filepath, simplify_cells=True)

    else:
        raise ValueError(f'"{file_format}" file_format not supported/not found.')

    forecast_data = validation.validate_meteorological_forecast(config, forecast_data, sar_model)

    return forecast_data


def load_model_parameters(filepath: str, model_name: str, file_format: str) -> list[spotpy.parameter.Base]:
    """The models boundaries correspond to the initial value and the min and max values of each model parameters."""
    if file_format == 'mat':
        param_boundaries = loadmat(file_name=filepath, simplify_cells=True)

        try:
            param_boundaries = param_boundaries[model_name]
        except KeyError:
            raise ValueError(f'Model {model_name} not found in data')

        if 'sIni' not in param_boundaries and 'sMin' not in param_boundaries and 'sMax' not in param_boundaries:
            raise ValueError('params_boundaries should contain the following keys ("sIni", "sMin", "sMax")')

        parameters = []
        for i in range(len(param_boundaries['sIni'])):
            parameters.append(
                # Write now the default distribution is the Uniform one. Could be changed.
                spotpy.parameter.Uniform(
                    optguess=param_boundaries['sIni'][i],
                    low=param_boundaries['sMin'][i],
                    high=param_boundaries['sMax'][i]
                )
            )

    else:
        raise ValueError(f'"{file_format}" file_format not supported/not found.')

    return parameters


def load_sar_model_parameters(
        filepath: str, model_name: str, file_format: str,
        calibrate_snow: bool) -> list[spotpy.parameter.Base]:
    if file_format == 'mat':
        param_boundaries = loadmat(file_name=filepath, simplify_cells=True)

        try:
            param_boundaries = param_boundaries[model_name]
        except KeyError:
            raise ValueError(f'Model {model_name} not found in data')

        if ('sIni' not in param_boundaries and 'sMin' not in param_boundaries and 'sMax' not in param_boundaries) or\
                'default' not in param_boundaries:
            raise ValueError('params_boundaries should contain the following keys ("sIni", "sMin", "sMax") or "default"')

        parameters = []
        for i in range(len(param_boundaries['sIni'])):
            if calibrate_snow:
                parameters.append(
                    # Write now the default distribution is the Uniform one. Could be changed.
                    spotpy.parameter.Uniform(
                        optguess=param_boundaries['sIni'][i],
                        low=param_boundaries['sMin'][i],
                        high=param_boundaries['sMax'][i]
                    )
                )
            else:
                parameters.append(
                    spotpy.parameter.Constant(param_boundaries['default'][i])
                )

    else:
        raise ValueError(f'"{file_format}" file_format not supported/not found.')

    return parameters


def load_calibrated_model_parameters(filepath: str, file_format: str = 'json') -> list[float]:
    """The calibrated models parameters."""
    if file_format == 'json':
        with open(filepath) as file:
            calibrated_params = json.load(file)['best_parameters']

    else:
        raise ValueError(f'"{file_format}" file_format not supported/not found.')

    return calibrated_params
