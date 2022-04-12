from datetime import datetime
from typing import Dict

import numpy as np
from scipy.io import loadmat
from spotpy import objectivefunctions

from hoopla.calibration.sce_ua import shuffled_complex_evolution
from hoopla.config import Config, DATA_PATH
from hoopla.hydro_models.hydro_model import HydroModel
from hoopla.pet_models.pet_model import PETModel
from hoopla.sar_models.sar_model import SARModel
from hoopla.util import validation
from hoopla.util.croping import crop_data

SCORES = {
    'RMSE': objectivefunctions.rmse,
    'RMSEsqrt': NotImplemented,
    'RMSElog': NotImplemented,
    'MSE': objectivefunctions.mse,
    'MSEsqrt': NotImplemented,
    'MSElog': NotImplemented,
    'MAE': objectivefunctions.mae,
    'NSE': objectivefunctions.nashsutcliffe,
    'NSEsqrt': NotImplemented,
    'NSEinv': NotImplemented,
    'PVE': NotImplemented,
    'PVEabs': NotImplemented,
    'Balance': NotImplemented,
    'r': objectivefunctions.correlationcoefficient,
    'bKGE': NotImplemented,
    'gKGE': NotImplemented,
    'KGEm': NotImplemented
}
ORIENT_SCORES = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1]


def make_calibration(config: Config, catchment_name: str,
                     hydro_model: HydroModel, pet_model: PETModel,
                     sar_model: SARModel):
    # Data specification for catchment / parameters
    data_obs = loadmat(
        file_name=f'{DATA_PATH}/{config.general.time_step}/Hydromet_obs/Hydromet_obs_{catchment_name}.mat',
        simplify_cells=True
    )
    data_meteo_forecast = loadmat(
        file_name=f'{DATA_PATH}/{config.general.time_step}/Det_met_fcast/Met_fcast_{catchment_name}.mat',
        simplify_cells=True
    )

    # Serialized dates
    data_obs['Date'] = np.array(
        [datetime(year=d[0], month=d[1], day=d[2], hour=d[3], minute=d[4], second=d[5]) for d in data_obs['Date']]
    )

    # Validate that all necessary data are provided
    validation.check_data(config, pet_model, sar_model, data_obs, data_meteo_forecast)

    # Crop observed data according to specified dates and warm up
    crop_data(config, data_obs, hydro_model, pet_model, sar_model, ini='ini_calibration')

    # Launch calibration
    if config.general.compute_snowmelt:
        if config.general.compute_warm_up:
            raise NotImplementedError
        else:
            calibrate(config, data_obs, hydro_model, pet_model, sar_model)
    else:
        if config.general.compute_warm_up:
            raise NotImplementedError
        else:
            calibrate(config, data_obs, hydro_model, pet_model, sar_model)

    raise NotImplementedError


def calibrate(config: Config, data_for_calibration: Dict, hydro_model: HydroModel, pet_model: PETModel,
              sar_model: SARModel):
    # Parameters boundaries
    # Notes: The parameters are cast in an array.
    # Each hydrological model has its own number of parameters, thus the array.
    # ---------------------
    model_param_boundaries = loadmat(
        file_name=f'{DATA_PATH}/{config.general.time_step}/Model_parameters/model_param_boundaries.mat',
        simplify_cells=True
    )
    snow_model_param_boundaries = loadmat(
        file_name=f'{DATA_PATH}/{config.general.time_step}/Model_parameters/snow_model_param_boundaries.mat',
        simplify_cells=True
    )

    if config.general.compute_snowmelt:
        if config.calibration.calibrate_snow:
            initial_parameters = [
                model_param_boundaries[hydro_model.name]['sIni'],
                snow_model_param_boundaries[sar_model.name]['sIni']
            ]
            lower_boundaries_of_parameters = [
                model_param_boundaries[hydro_model.name]['sMin'],
                snow_model_param_boundaries[sar_model.name]['sMin']
            ]
            upper_boundaries_of_parameters = [
                model_param_boundaries[hydro_model.name]['sMax'],
                snow_model_param_boundaries[sar_model.name]['sMax']
            ]
        else:
            initial_parameters = [
                model_param_boundaries[hydro_model.name]['sIni'],
                snow_model_param_boundaries[sar_model.name]['default']
            ]
            lower_boundaries_of_parameters = [
                model_param_boundaries[hydro_model.name]['sMin'],
                snow_model_param_boundaries[sar_model.name]['default']
            ]
            upper_boundaries_of_parameters = [
                model_param_boundaries[hydro_model.name]['sMax'],
                snow_model_param_boundaries[sar_model.name]['default']
            ]

    else:
        initial_parameters = model_param_boundaries[hydro_model.name]['sIni']
        lower_boundaries_of_parameters = model_param_boundaries[hydro_model.name]['sMin']
        upper_boundaries_of_parameters = model_param_boundaries[hydro_model.name]['sMax']

    # Scores for the objective function
    # ---------------------------------
    if config.calibration.score not in SCORES:
        raise ValueError(f'Score must be one of: {SCORES}')
    if SCORES[config.calibration.score] == NotImplemented:
        raise ValueError(f'Score function ({config.calibration.score}) is not implemented')

    objective_function = SCORES[config.calibration.score]

    # Calibration
    # ---------------------
    if config.calibration.method == 'DDS':
        raise NotImplementedError
        best_parameters, best_f, all_best_f = dynamically_dimensioned_search()
    elif config.calibration.method == 'SCE':
        best_parameters, best_f, all_best_f = shuffled_complex_evolution(
            hydro_model=hydro_model,
            data_for_calibration=data_for_calibration,
            pet_model=pet_model,
            objective_function=objective_function,
            initial_parameters=initial_parameters,
            lower_boundaries_of_parameters=lower_boundaries_of_parameters,
            upper_boundaries_of_parameters=upper_boundaries_of_parameters,
            ngs=config.calibration.SCE['ngs']
        )
    else:
        raise ValueError(f'Calibration method "{config.calibration.method}" not known. '
                         'Calibration method should be "DDS" or "SCE"')

    # Run simulation with best parameters
    if config.general.compute_warm_up:
        if config.general.compute_snowmelt:
            raise NotImplementedError
        else:
            raise NotImplementedError


def dynamically_dimensioned_search(s_ini: np.array, s_min: np.array, s_max: np.array, max_iter: int):
    """Dynamically Dimensioned Search algorithm

    By Bryan Tolson.  Version 1.0.2  Oct 2005
    Slightly modified by A. Thiboult (2017)

    Parameters
    ----------
    s_ini
        Initial points to evaluate. Empty vector to force a random initial evaluation.
    s_min
        Vector of minimum values of parameters to optimise.
    s_max
        Vector of maximum values of parameters to optimise.
    max_iter
        Maximum number of iterations.

    Returns
    -------
    Tuple[List, List, np.array]
        best, all_best, solution
        
        best: decision variables found as the best set and its function value
        all_best: all best solutions over all iterations
        solution: Matrix with the following structure
            col 1: iteration number i
            col 2: best current solution at iteration i
            col 3: tested solution at iteration i
            col4 to col(3 + parameters to optimise): parameters tested
    """
    raise NotImplementedError
