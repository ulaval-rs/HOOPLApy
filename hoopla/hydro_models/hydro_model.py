import abc
from datetime import datetime
from typing import Callable, Dict, Iterable, List, Optional

import numpy as np
import spotpy
from spotpy.parameter import Uniform

from hoopla.calibration.util import find_non_winter_indexes
from hoopla.config import Config
from hoopla.pet_models import PETModel


class HydroModel:

    def __init__(self, name: str, inputs: List[str], config: Config):
        self.name = name
        self.inputs = inputs
        self.config = config

        self.objective_function = None
        self.pet_model: Optional[PETModel] = None
        self.params = []

    def setup(self,
              objective_function: Callable,
              P: np.array,
              dates: List[datetime],
              T: List[float],
              latitudes: List[float],
              observed_streamflow: List[float],
              pet_model: PETModel,
              initial_params: List[float],
              lower_boundaries_of_params: List[float],
              upper_boundaries_of_params: List[float]):
        self.objective_function = objective_function
        self.P = P
        self.dates = dates
        self.T = T
        self.latitudes = latitudes
        self.observed_streamflow = observed_streamflow
        self.pet_model = pet_model

        for i in range(len(initial_params)):
            self.params.append(
                Uniform(
                    optguess=initial_params[i],
                    low=lower_boundaries_of_params[i],
                    high=upper_boundaries_of_params[i],
                )
            )

    @abc.abstractmethod
    def prepare(self, params: List[float]):
        raise NotImplementedError

    @abc.abstractmethod
    def run(self, model_inputs: Dict, params: Iterable, state_variables: Dict):
        raise NotImplementedError

    def parameters(self):
        return spotpy.parameter.generate(self.params)

    def evaluation(self):
        return self.observed_streamflow

    def simulation(self, params: List[float]):
        if self.config.general.compute_warm_up:
            raise NotImplementedError

        state_variables = self.prepare(params)

        if self.config.general.compute_pet:
            pet_data = self.pet_model.prepare(
                time_step=self.config.general.time_step,
                dates=self.dates,
                T=self.T,
                latitudes=self.latitudes
            )
            E = self.pet_model.run(pet_data)

        # Container for results
        simulated_streamflow = []

        # Running simulation
        if self.config.general.compute_snowmelt:
            raise NotImplementedError
        else:
            for i, _ in enumerate(self.dates):
                Qsim, state_variables = self.run(
                    model_inputs={'P': self.P[i], 'E': E[i]},
                    params=params,
                    state_variables=state_variables
                )
                simulated_streamflow.append(Qsim)

        return np.array(simulated_streamflow)

    def objectivefunction(self, simulation: np.array, evaluation: np.array):
        if self.config.calibration.remove_winter:
            non_winter_indexes = find_non_winter_indexes(dates=self.dates)

            evaluation = evaluation.take(non_winter_indexes)
            simulation = simulation.take(non_winter_indexes)

        return self.objective_function(evaluation, simulation)
