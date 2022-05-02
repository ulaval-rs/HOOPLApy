import abc
from datetime import datetime
from typing import Callable, Iterable, Optional, Sequence

import numpy as np
import spotpy
from spotpy.parameter import Uniform

from hoopla.calibration.util import find_non_winter_indexes
from hoopla.config import Config
from hoopla.models.pet_model import BasePETModel


class BaseHydroModel:

    def __init__(self):
        self.ready = False  # Indicate if the model is ready to use (need to setup first)

        # Defining variables to be set
        self.config: Optional[Config] = None
        self.objective_function: Optional[Callable] = None
        self.pet_model: Optional[BasePETModel] = None
        self.params: list[Uniform] = []
        self.dates: Optional[Sequence] = None
        self.P: Optional[Sequence] = None
        self.T: Optional[Sequence] = None
        self.latitude: Optional[Sequence] = None
        self.observed_streamflow: Optional[Sequence] = None

    def setup(self,
              config: Config,
              objective_function: Callable,
              P: np.array,
              dates: Sequence[datetime],
              T: Sequence[float],
              latitudes: float,
              observed_streamflow: Sequence[float],
              pet_model: BasePETModel,
              initial_params: list[float],
              lower_boundaries_of_params: list[float],
              upper_boundaries_of_params: list[float]):
        self.config = config
        self.objective_function = objective_function
        self.P = P
        self.dates = dates
        self.T = T
        self.latitude = latitudes
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

        self.ready = True

    @abc.abstractmethod
    def prepare(self, params: list[float]):
        raise NotImplementedError

    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def inputs(self) -> list[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def run(self, model_inputs: dict, params: Iterable, state_variables: dict):
        raise NotImplementedError

    def parameters(self):
        return spotpy.parameter.generate(self.params)

    def evaluation(self):
        return self.observed_streamflow

    def simulation(self, params: list[float]):
        if not self.ready:
            raise Exception('Model should be "setup()" to be used.')

        if self.config.general.compute_warm_up:
            raise NotImplementedError

        state_variables = self.prepare(params)

        if self.config.general.compute_pet:
            pet_params = self.pet_model.prepare(
                time_step=self.config.general.time_step,
                model_inputs={'dates': self.dates, 'T': self.T, 'latitude': self.latitude}
            )
            E = self.pet_model.run(pet_params)

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
