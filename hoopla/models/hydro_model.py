import abc
from typing import Callable, Optional, Sequence, Union

import numpy as np
import spotpy
from spotpy.parameter import ParameterSet

from hoopla.models.sar_model import BaseSARModel
from hoopla.models.util import find_non_winter_indexes
from hoopla.config import Config
from hoopla.models.pet_model import BasePETModel


class BaseHydroModel:

    def __init__(self):
        self.config: Optional[Config] = None
        self.objective_function: Optional[Callable] = None

        self.observations: Optional[dict] = None
        self.observations_for_warmup: Optional[dict] = None
        self.observed_streamflow: Optional[Sequence] = None

        self.pet_model: Optional[BasePETModel] = None
        self.sar_model: Optional[BaseSARModel] = None

        self.model_params: Sequence[spotpy.parameter.Base] = []

    def setup(self,
              config: Config,
              observations: dict,
              observations_for_warmup: dict,
              pet_model: BasePETModel,
              sar_model: BaseSARModel):
        self.config = config
        self.observations = observations
        self.observations_for_warmup = observations_for_warmup
        self.pet_model = pet_model
        self.sar_model = sar_model

    def setup_for_calibration(
            self,
            config: Config,
            objective_function: Callable,
            observations: dict,
            observations_for_warmup: dict,
            observed_streamflow: Sequence[float],
            pet_model: BasePETModel,
            sar_model: BaseSARModel,
            model_parameters: Sequence[spotpy.parameter.Base]):
        self.setup(config, observations, observations_for_warmup, pet_model, sar_model)

        self.objective_function = objective_function
        self.observed_streamflow = observed_streamflow

        self.model_params = model_parameters

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

    def simulation(self, params: Union[ParameterSet, Sequence[float]]) -> np.ndarray:
        if self.config.general.compute_warm_up:
            state_variables_warmup, sar_state_variables_warmup = self._warmup(params)

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
        if self.config.general.compute_warm_up:
            state_variables = state_variables_warmup
        else:
            state_variables = self.prepare(params)

        simulated_streamflow = []  # Container for results

        # Running the model while considering the SAR model or not.
        if self.config.general.compute_snowmelt:
            if self.config.general.compute_warm_up:
                sar_state_variables = sar_state_variables_warmup
            else:
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
                    model_inputs={'P': runoff_d, 'E': E[i]},
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

    def _warmup(self, params: Union[ParameterSet, Sequence[float]]):
        """Warm up

        The warm-up initialize the state variables of the Hydro and SAR models, if applicable.
        """
        # State variables to be return
        sar_state_variables = {}

        # Init hydro model
        state_variables = self.prepare(params)

        # Compute E or get the one from the observations data
        if self.config.general.compute_pet:
            pet_params = self.pet_model.prepare(
                time_step=self.config.general.time_step,
                model_inputs={'dates': self.observations_for_warmup['dates'], 'T': self.observations_for_warmup['T']},
                hyper_parameters={'latitude': self.observations_for_warmup['latitude']}
            )

            E = self.pet_model.run(pet_params)
        else:
            E = self.observations_for_warmup['E']

        # Running the model while considering the SAR model or not.
        if self.config.general.compute_snowmelt:
            sar_state_variables = self.sar_model.prepare(params=params, hyper_parameters=self.observations_for_warmup)

            # Running simulation
            for i, _ in enumerate(self.observations_for_warmup['dates']):
                runoff_d, sar_state_variables = self.sar_model.run(
                    model_inputs={
                        'P': self.observations_for_warmup['P'][i],
                        'T': self.observations_for_warmup['T'][i],
                        'Tmin': self.observations_for_warmup['Tmin'][i],
                        'Tmax': self.observations_for_warmup['Tmax'][i],
                        'Date': self.observations_for_warmup['dates'][i]
                    },
                    params=params,
                    state_variables=sar_state_variables
                )
                _, state_variables = self.run(
                    model_inputs={'P': runoff_d, 'E': E[i]},
                    params=params,
                    state_variables=state_variables
                )

        else:
            for i, _ in enumerate(self.observations_for_warmup['dates']):
                _, state_variables = self.run(
                    model_inputs={'P': self.observations_for_warmup['P'][i], 'E': E[i]},
                    params=params,
                    state_variables=state_variables
                )

        return state_variables, sar_state_variables
