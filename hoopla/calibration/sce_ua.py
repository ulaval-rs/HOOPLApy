from typing import Callable, Dict

import numpy as np
import spotpy

from hoopla.hydro_models.hydro_model import HydroModel
from hoopla.pet_models import PETModel


def shuffled_complex_evolution(
        hydro_model: HydroModel,
        data_for_calibration: Dict,
        pet_model: PETModel,
        objective_function: Callable,
        initial_parameters: np.array,
        lower_boundaries_of_parameters: np.array,
        upper_boundaries_of_parameters: np.array,
        ngs: int):
    hydro_model.setup(
        objective_function=objective_function,
        pet_model=pet_model,
        data_for_calibration=data_for_calibration,
        initial_x=initial_parameters,
        lower_boundaries_of_x=lower_boundaries_of_parameters,
        upper_boundaries_of_x=upper_boundaries_of_parameters
    )

    sampler = spotpy.algorithms.sceua(hydro_model, dbformat='ram')
    sampler.sample(repetitions=1000, ngs=ngs)
