import abc
from typing import Callable, List

import spotpy
from spotpy.parameter import Uniform


class HydroModel:

    def __init__(self, name: str, parameters: List[str]):
        self.name = name
        self.config_parameters = parameters

        self.objective_function = None
        self.params = []

    def setup(self,
              objective_function: Callable,
              initial_x: List[float],
              lower_boundaries_of_x: List[float],
              upper_boundaries_of_x: List[float]):
        self.objective_function = objective_function

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
        pass

    def objectivefunction(self, simulation, evaluation):
        return self.objective_function(evaluation, simulation)
