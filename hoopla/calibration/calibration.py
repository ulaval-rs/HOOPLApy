import json
import os
import warnings
from typing import Sequence

import numpy as np
import spotpy.parameter
from spotpy import objectivefunctions

from hoopla.calibration.optimization import shuffled_complex_evolution, dds
from hoopla.config import Config
from hoopla.models import util
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


def make_calibration(config: Config,
                     observations: dict,
                     observations_for_warm_up: dict,
                     hydro_model: BaseHydroModel,
                     pet_model: BasePETModel,
                     sar_model: BaseSARModel,
                     model_parameters: Sequence[spotpy.parameter.Base],
                     filepath_results: str) -> None:
    simulated_streamflow, best_params = calibrate(
            config=config,
            observations=observations,
            observations_for_warmup=observations_for_warm_up,
            hydro_model=hydro_model,
            pet_model=pet_model,
            sar_model=sar_model,
            model_parameters=model_parameters,
    )

    # Save results
    # ------------
    results = {
        'hydro_model': hydro_model.name(),
        'PET_model': pet_model.name(),
        'SAR_model': sar_model.name(),
        'Qsim': list(simulated_streamflow),
        'best_parameters': best_params,
        'observations': util.serialize_data(observations)
    }

    with open(filepath_results, 'w') as file:
        json.dump(results, file, indent=4, default=str)


def calibrate(config: Config,
              observations: dict,
              observations_for_warmup: dict,
              hydro_model: BaseHydroModel,
              pet_model: BasePETModel,
              sar_model: BaseSARModel,
              model_parameters: Sequence[spotpy.parameter.Base]) -> tuple[np.ndarray, Sequence[float]]:
    """Calibrate

    Parameters
    ----------
    config
        Configuration.
    observations
        Dictionary of the observed data (the needed data for the calibration).
    observations_for_warmup
        Dictionary of the observed data used by the warmup.
    hydro_model
    pet_model
    sar_model
    model_parameters

    Returns
    -------
    simulated_streamflow, best_params

    Notes
    -----
    Now, the SAR results are not exported.
    """
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
    # Setup the hydro model with the correct data
    hydro_model.setup_for_calibration(
        config=config,
        operation='calibration',
        objective_function=objective_function,
        observations=observations,
        observations_for_warmup=observations_for_warmup,
        observed_streamflow=observations['Q'],
        pet_model=pet_model,
        sar_model=sar_model,
        model_parameters=model_parameters,
    )
    if config.calibration.method == 'DDS':
        best_parameters, best_f = dds(
            hydro_model=hydro_model,
            max_iteration=config.calibration.maxiter
        )
    elif config.calibration.method == 'SCE':
        best_parameters, best_f = shuffled_complex_evolution(
            hydro_model=hydro_model,
            ngs=config.calibration.SCE['ngs'],
            max_iteration=config.calibration.maxiter
        )
    else:
        raise ValueError(f'Calibration method "{config.calibration.method}" not known. '
                         'Calibration method should be "DDS" or "SCE"')

    # ReRun simulation with best parameters
    simulated_streamflow = hydro_model.simulation(best_parameters)

    return simulated_streamflow, best_parameters
