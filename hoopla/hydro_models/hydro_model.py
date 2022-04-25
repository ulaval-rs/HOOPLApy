import abc
from typing import Callable, Dict, List, Optional

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
        self.data_for_calibration = {}
        self.params = []

    def setup(self,
              objective_function: Callable,
              data_for_calibration: Dict,
              pet_model: PETModel,
              initial_x: List[float],
              lower_boundaries_of_x: List[float],
              upper_boundaries_of_x: List[float]):
        self.objective_function = objective_function
        self.pet_model = pet_model
        self.data_for_calibration = data_for_calibration

        for i in range(len(initial_x)):
            self.params.append(
                Uniform(
                    optguess=initial_x[i],
                    low=lower_boundaries_of_x[i],
                    high=upper_boundaries_of_x[i],
                )
            )

    @abc.abstractmethod
    def prepare(self, x: List[float]):
        raise NotImplementedError

    def parameters(self):
        return spotpy.parameter.generate(self.params)

    def evaluation(self):
        observed_stream_flow = self.data_for_calibration['Q']
        return observed_stream_flow

    @abc.abstractmethod
    def simulation(self, x: List[float]):
        raise NotImplementedError

    def objectivefunction(self, simulation: np.array, evaluation: np.array):
        if self.config.calibration.remove_winter:
            non_winter_indexes = find_non_winter_indexes(self.data_for_calibration['Date'])

            evaluation = evaluation.take(non_winter_indexes)
            simulation = simulation.take(non_winter_indexes)

        return self.objective_function(evaluation, simulation)
