from typing import Callable, Dict

import numpy as np
import spotpy

from hoopla.config import Config
from hoopla.models.hydro_model import BaseHydroModel
from hoopla.models.pet_model import BasePETModel


def shuffled_complex_evolution(
        hydro_model: BaseHydroModel,
        data_for_calibration: Dict,
        pet_model: BasePETModel,
        objective_function: Callable,
        initial_parameters: np.array,
        lower_boundaries_of_parameters: np.array,
        upper_boundaries_of_parameters: np.array,
        ngs: int,
        max_iteration: int,
        config: Config):
    hydro_model.setup(
        config=config,
        objective_function=objective_function,
        pet_model=pet_model,
        P=data_for_calibration['P'],
        dates=data_for_calibration['dates'],
        T=data_for_calibration['T'],
        latitudes=data_for_calibration['latitude'],
        observed_streamflow=data_for_calibration['Q'],
        initial_params=initial_parameters,
        lower_boundaries_of_params=lower_boundaries_of_parameters,
        upper_boundaries_of_params=upper_boundaries_of_parameters
    )

    sampler = spotpy.algorithms.sceua(hydro_model, dbname='sceua-data', dbformat='csv')
    sampler.sample(repetitions=max_iteration, ngs=ngs)

    results = spotpy.analyser.load_csv_results('sceua-data')
    max_index = np.argmin(results['like1'])
    best_param = results['par'][max_index], results['par_1'][max_index], results['par_2'][max_index], results['par_3'][max_index], results['par_4'][max_index], results['par_5'][max_index]
    best_cost_function_value = results['like1'][max_index]

    # import matplotlib.pyplot as plt
    # plt.figure(1, figsize=(9, 5))
    # plt.plot(results['like1'])
    # plt.ylabel('RMSE')
    # plt.xlabel('Iteration')
    # plt.show()
    # exit('TODO: fix the convergence')

    return best_param, best_cost_function_value

