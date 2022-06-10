import json
import os
import warnings
from typing import Sequence

import numpy as np
import spotpy.parameter
from spotpy import objectivefunctions

from hoopla.calibration.sce_ua import shuffled_complex_evolution
from hoopla.config import Config
from hoopla.models.hydro_model import BaseHydroModel
from hoopla.models.pet_model import BasePETModel
from hoopla.models.sar_model import BaseSARModel

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


def make_calibration(observations: dict, config: Config,
                     catchment: str, hydro_model: BaseHydroModel, pet_model: BasePETModel, sar_model: BaseSARModel,
                     model_parameters: Sequence[spotpy.parameter.Base],
                     sar_model_parameters: Sequence[spotpy.parameter.Base]) -> None:

    if config.general.compute_warm_up:
        raise NotImplementedError
    else:
        simulated_streamflow, best_params, sar_results = calibrate(
            config=config,
            observations=observations,
            hydro_model=hydro_model,
            pet_model=pet_model,
            sar_model=sar_model,
            model_parameters=model_parameters,
            sar_model_parameters=sar_model_parameters,
        )

    # Save results
    # ------------
    results = {
        'hydro_model': hydro_model.name(),
        'PET_model': pet_model.name(),
        'SAR_model': sar_model.name(),
        'Qsim': list(simulated_streamflow),
        'best_parameters': best_params,
    }
    if not os.path.exists('./results'):
        os.makedirs('./results')

    with open(f'./results/C={catchment}-H={hydro_model.name()}-E={pet_model.name()}-S={sar_model.name()}.json', 'w') as file:
        warnings.warn('Add more information when saving the calibration results file.')
        json.dump(results, file, indent=4)


def calibrate(config: Config,
              observations: dict,
              hydro_model: BaseHydroModel,
              pet_model: BasePETModel,
              sar_model: BaseSARModel,
              model_parameters: Sequence[spotpy.parameter.Base],
              sar_model_parameters: Sequence[spotpy.parameter.Base]) -> tuple[np.ndarray, Sequence[float], dict]:
    # Scores for the objective function
    # ---------------------------------
    if config.calibration.score not in SCORES:
        raise ValueError(f'Score must be one of: {SCORES}')
    if SCORES[config.calibration.score] == NotImplemented:
        raise ValueError(f'Score function ({config.calibration.score}) is not implemented')

    objective_function = SCORES[config.calibration.score]

    # Calibration
    # This aims to find the best parameters
    # ---------------------
    if config.calibration.method == 'DDS':
        raise NotImplementedError
    elif config.calibration.method == 'SCE':
        best_parameters, best_f = shuffled_complex_evolution(
            hydro_model=hydro_model,
            data_for_calibration=observations,
            pet_model=pet_model,
            objective_function=objective_function,
            model_parameters=model_parameters,
            ngs=config.calibration.SCE['ngs'],
            max_iteration=config.calibration.maxiter,
            config=config
        )
    else:
        raise ValueError(f'Calibration method "{config.calibration.method}" not known. '
                         'Calibration method should be "DDS" or "SCE"')

    # ReRun simulation with best parameters
    if config.general.compute_snowmelt:
        raise NotImplementedError
    else:
        simulated_streamflow = hydro_model.simulation(best_parameters)

        return simulated_streamflow, best_parameters, {}
