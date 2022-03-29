from typing import Dict

import numpy as np
from scipy.io import loadmat

from hoopla.calibration.sce_ua import shuffled_complex_evolution
from hoopla.config import Config, DATA_PATH
from hoopla.hydro_models.hydro_model import HydroModel
from hoopla.pet_models.pet_model import PETModel
from hoopla.sar_models.sar_model import SARModel
from hoopla.util import validation
from hoopla.util.croping import crop_data

SCORES = ['RMSE', 'RMSEsqrt', 'RMSElog', 'MSE', 'MSEsqrt', 'MSElog', 'MAE', 'NSE',
          'NSEsqrt', 'NSEinv', 'PVE', 'PVEabs', 'Balance', 'r', 'bKGE', 'gKGE', 'KGEm']
ORIENT_SCORES = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1]


def make_calibration(config: Config, catchment_name: str,
                     hydro_model: HydroModel, pet_model: PETModel,
                     sar_model: SARModel):
    # Data specification for catchment / parameters
    data_obs = loadmat(f'{DATA_PATH}/{config.general.time_step}/Hydromet_obs/Hydromet_obs_{catchment_name}.mat')
    data_meteo_forecast = loadmat(f'{DATA_PATH}/{config.general.time_step}/Det_met_fcast/Met_fcast_{catchment_name}.mat')

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


def calibrate(config: Config, data_obs: Dict, hydro_model: HydroModel, pet_model: PETModel, sar_model: SARModel):
    model_param_bound = loadmat(f'{DATA_PATH}/{config.general.time_step}/Model_parameters/model_param_boundaries.mat')
    snow_model_param_bound = loadmat(f'{DATA_PATH}/{config.general.time_step}/Model_parameters/snow_model_param_boundaries.mat')

    if config.general.compute_snowmelt:
        if config.calibration.calibrate_snow:
            raise NotImplementedError
        else:
            raise NotImplementedError

    else:
        s_min = model_param_bound[hydro_model.name]['sMin'][0][0][0]
        s_ini = model_param_bound[hydro_model.name]['sIni'][0][0][0]
        s_max = model_param_bound[hydro_model.name]['sMax'][0][0][0]

    score_matrix = [config.calibration.score == s for s in SCORES]

    # Calibration
    if config.calibration.method == 'DDS':
        best_parameters, best_f, all_best_f = dynamically_dimensioned_search(
            s_ini=s_ini,
            s_min=s_min,
            s_max=s_max,
            max_iter=config.calibration.maxiter
        )
    elif config.calibration.method == 'SCE':
        best_parameters, best_f, all_best_f = shuffled_complex_evolution(
            number_of_iterations=config.calibration.maxiter,
            nbr_of_complexes=config.calibration.SCE['ngs']
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
