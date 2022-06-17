import abc
from datetime import datetime
from typing import Callable, Iterable, Optional, Sequence

import numpy as np
import spotpy
from spotpy.parameter import ParameterSet, Uniform

from hoopla.models.sar_model import BaseSARModel
from hoopla.models.util import find_non_winter_indexes
from hoopla.config import Config
from hoopla.models.pet_model import BasePETModel


class BaseHydroModel:

    def __init__(self):
        self.ready = False  # Indicate if the model is ready to use (need to setup first)

        self.config: Optional[Config] = None
        self.objective_function: Optional[Callable] = None

        self.observations: Optional[dict] = None
        self.observed_streamflow: Optional[Sequence] = None

        self.pet_model: Optional[BasePETModel] = None
        self.sar_model: Optional[BaseSARModel] = None

        self.model_params: Sequence[spotpy.parameter.Base] = []

    def setup(self,
              config: Config,
              objective_function: Callable,
              observations: dict,
              observed_streamflow: Sequence[float],
              pet_model: BasePETModel,
              sar_model: BaseSARModel,
              model_parameters: Sequence[spotpy.parameter.Base]):
        self.config = config
        self.objective_function = objective_function
        self.observations = observations
        self.observed_streamflow = observed_streamflow
        self.pet_model = pet_model
        self.sar_model = sar_model
        self.model_params = model_parameters
        self.ready = True

    @abc.abstractmethod
    def prepare(self, params: ParameterSet):
        raise NotImplementedError

    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def inputs(self) -> list[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def run(self, model_inputs: dict, params: ParameterSet, state_variables: dict):
        raise NotImplementedError

    def parameters(self):
        return spotpy.parameter.generate(self.model_params)

    def evaluation(self):
        return self.observed_streamflow

    def simulation(self, params: ParameterSet) -> np.ndarray:
        if not self.ready:
            raise Exception('Model should be "setup()" to be used.')

        if self.config.general.compute_warm_up:
            raise NotImplementedError

        # Compute E or get the one from the observations data
        if self.config.general.compute_pet:
            pet_params = self.pet_model.prepare(
                time_step=self.config.general.time_step,
                model_inputs={'dates': self.observations['dates'], 'T': self.observations['T']},
                hyper_parameters={'latitude': self.observations['latitude']}
            )
            E = self.pet_model.run(pet_params)
        else:
            E = self.observations['E']

        # Init hydro model
        state_variables = self.prepare(params)
        simulated_streamflow = []  # Container for results

        # Running the model while considering the SAR model or not.
        if self.config.general.compute_snowmelt:
            sar_state_variables = self.sar_model.prepare(params=params, hyper_parameters=self.observations)

            # Running simulation
            for i, _ in enumerate(self.observations['dates']):
                runoff_d, sar_state_variables = self.sar_model.run(
                    model_inputs={
                        'P': self.observations['P'][i],
                        'T': self.observations['T'][i],
                        'Tmin': self.observations['Tmin'][i],
                        'Tmax': self.observations['Tmax'][i],
                        'Date': self.observations['dates'][i]
                    },
                    params=params,
                    state_variables=sar_state_variables
                )
                Qsim, state_variables = self.run(
                    model_inputs={'P': runoff_d[i], 'E': E[i]},
                    params=params,
                    state_variables=state_variables
                )
                simulated_streamflow.append(Qsim)

        else:
            for i, _ in enumerate(self.observations['dates']):
                Qsim, state_variables = self.run(
                    model_inputs={'P': self.observations['P'][i], 'E': E[i]},
                    params=params,
                    state_variables=state_variables
                )
                simulated_streamflow.append(Qsim)

        return np.array(simulated_streamflow)

    def objectivefunction(self, simulation: np.array, evaluation: np.array):
        if self.config.calibration.remove_winter:
            non_winter_indexes = find_non_winter_indexes(dates=self.observations['dates'])

            evaluation = evaluation.take(non_winter_indexes)
            simulation = simulation.take(non_winter_indexes)

        return abs(self.objective_function(evaluation, simulation))
