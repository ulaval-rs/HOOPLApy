import abc
from typing import Callable, List

import numpy as np
import spotpy
from spotpy.parameter import Uniform

from hoopla.config import Config


class HydroModel:

    def __init__(self, name: str, inputs: List[str], config: Config):
        self.name = name
        self.inputs = inputs
        self.config = config

        self.objective_function = None
        self.dates = []
        self.params = []

    def setup(self,
              objective_function: Callable,
              dates: np.array,
              P: np.array,
              E: np.array,
              initial_x: List[float],
              lower_boundaries_of_x: List[float],
              upper_boundaries_of_x: List[float]):
        self.objective_function = objective_function
        self.dates = dates
        self.P = P
        self.E = E

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
        return None
        raise NotImplementedError

    @abc.abstractmethod
    def simulation(self, dates: np.array, x: List[float]):
        raise NotImplementedError

    def objectivefunction(self, simulation, evaluation):
        return self.objective_function(evaluation, simulation)
