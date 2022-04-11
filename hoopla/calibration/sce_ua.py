from typing import Callable

import numpy as np
import spotpy

from hoopla.hydro_models.hydro_model import HydroModel
from hoopla.pet_models import PETModel


def shuffled_complex_evolution(
        hydro_model: HydroModel,
        dates: np.array,
        P: np.array,
        E: np.array,
        pet_model: PETModel,
        objective_function: Callable,
        initial_parameters: np.array,
        lower_boundaries_of_parameters: np.array,
        upper_boundaries_of_parameters: np.array,
        ngs: int):
    hydro_model.setup(
        objective_function=objective_function,
        pet_model=pet_model,
        dates=dates,
        P=P,
        E=E,
        initial_x=initial_parameters,
        lower_boundaries_of_x=lower_boundaries_of_parameters,
        upper_boundaries_of_x=upper_boundaries_of_parameters
    )

    sampler = spotpy.algorithms.sceua(hydro_model, dbformat='ram')
    sampler.sample(repetitions=1000, ngs=ngs)
