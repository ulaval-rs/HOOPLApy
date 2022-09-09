import abc
from typing import Callable, Optional, Sequence, Union

import numpy as np
import spotpy
from spotpy.parameter import ParameterSet

from hoopla.models.da_model import BaseDAModel
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
        self.da_model: Optional[BaseDAModel] = None

        self.model_params: Sequence[spotpy.parameter.Base] = []

        self.operation = None

    def setup(self,
              config: Config,
              operation: str,
              observations: dict,
              observations_for_warmup: dict,
              pet_model: BasePETModel,
              sar_model: BaseSARModel,
              da_model: BaseDAModel):
        self.config = config

        if operation not in ('calibration', 'simulation', 'forecast'):
            raise ValueError('Wrong operation. Can be "calibration", "simulation" or "forecast"')

        self.operation = operation

        self.observations = observations
        self.observations_for_warmup = observations_for_warmup
        self.pet_model = pet_model
        self.sar_model = sar_model
        self.da_model = da_model

    def setup_for_calibration(
            self,
            config: Config,
            operation: str,
            objective_function: Callable,
            observations: dict,
            observations_for_warmup: dict,
            observed_streamflow: Sequence[float],
            pet_model: BasePETModel,
            sar_model: BaseSARModel,
            da_model: BaseDAModel,
            model_parameters: Sequence[spotpy.parameter.Base]):
        self.setup(config, operation, observations, observations_for_warmup, pet_model, sar_model, da_model)

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

        if self.config.data.do_data_assimilation and self.operation == 'simulation':
            # Compute E or get the one from the observations data
            if self.config.general.compute_pet:
                ERP = np.empty(shape=(len(self.observations['dates']), self.config.data.N))
                ERP[:] = np.nan

                for t in range(self.config.data.N):
                    pet_params = self.pet_model.prepare(
                        time_step=self.config.general.time_step,
                        model_inputs={
                            'P': self.observations['P'][t],
                            'T': self.observations['TpetRP'][:, t],
                            'Tmin': self.observations['TminRP'][:, t],
                            'Tmax': self.observations['TmaxRP'][:, t],
                            'dates': self.observations['dates']
                        },
                        hyper_parameters={'latitude': self.observations['latitude']}
                    )
                    ERP[:, t] = self.pet_model.run(pet_params)

            # Init SAR model
            if self.config.general.compute_snowmelt:
                sar_state_variables = self.sar_model.prepare(params=params, hyper_parameters=self.observations)
            else:
                sar_state_variables = None

            # Init hydro model
            state_variables = self.prepare(params)

            # Initialization of states with WarmUp
            if self.config.general.compute_warm_up:
                for key, value in state_variables_warmup.items():
                    state_variables[key] = value

                if self.config.general.compute_snowmelt:
                    for key, value in sar_state_variables_warmup.items():
                        sar_state_variables[key] = value

            # Setting state variables for the data assimilation process
            state_variables = [state_variables for _ in range(self.config.data.N)]
            if self.config.general.compute_snowmelt:
                sar_state_variables = [sar_state_variables for _ in range(self.config.data.N)]

            # Run simulation
            simulated_streamflow = []

            if self.config.general.compute_snowmelt:
                for t, _ in enumerate(self.observations['dates']):
                    simulated_streamflow.append([])

                    for j in range(self.config.data.N):
                        runoff_d, sar_state_variables[j] = self.sar_model.run(
                            model_inputs={
                                'P': self.observations['PtRP'][t][j],
                                'T': self.observations['TsnowRP'][t][j],
                                'Tmin': self.observations['TminRP'][t][j],
                                'Tmax': self.observations['TmaxRP'][t][j],
                                'Date': self.observations['dates'][t]
                            },
                            params=params,
                            state_variables=sar_state_variables[j]
                        )
                        Qsim, state_variables[j] = self.run(
                            model_inputs={'P': self.observations['PtRP'][t][j], 'E': ERP[t][j]},
                            params=params,
                            state_variables=state_variables[j]
                        )
                        simulated_streamflow[-1].append(Qsim)

                    if np.remainder(t, self.config.data.dt) == 0:
                        if not np.any(np.isnan(self.observations['QRP'][t])):
                            state_variables = self.da_model.run(
                                state_variables=state_variables,
                                Qsim=np.array(simulated_streamflow[-1]),
                                Q=self.observations['Q'][t],
                                QRP=self.observations['QRP'][t],
                                eQ=self.observations['eQRP'][t],
                                DA_config=self.config.data
                            )

            else:
                for t, _ in enumerate(self.observations['dates']):
                    simulated_streamflow.append([])

                    for j in range(self.config.data.N):
                        Qsim, state_variables[j] = self.run(
                            model_inputs={'P': self.observations['PtRP'][t][j], 'E': ERP[t][j]},
                            params=params,
                            state_variables=state_variables[j]
                        )
                        simulated_streamflow[-1].append(Qsim)

                    if np.remainder(t, self.config.data.dt) == 0:
                        if not np.any(np.isnan(self.observations['QRP'][t])):
                            state_variables = self.da_model.run(
                                state_variables=state_variables,
                                Qsim=np.array(simulated_streamflow[-1]),
                                Q=self.observations['Q'][t],
                                QRP=self.observations['QRP'][t],
                                eQ=self.observations['eQRP'][t],
                                DA_config=self.config.data
                            )

            return np.array(simulated_streamflow)

        # Compute E or get the one from the observations data
        E = self._setup_pet_data() if self.config.general.compute_pet else self.observations['E']

        # Init SAR model
        if self.config.general.compute_snowmelt:
            sar_state_variables = self.sar_model.prepare(params=params, hyper_parameters=self.observations)
        else:
            sar_state_variables = None

        # Init hydro model
        state_variables = self.prepare(params)

        if self.config.general.compute_warm_up:
            for key, value in state_variables_warmup.items():
                state_variables[key] = value

            if self.config.general.compute_snowmelt:
                for key, value in sar_state_variables_warmup.items():
                    sar_state_variables[key] = value

        return self._run_model_simulation(params, E, state_variables, sar_state_variables)

    def objectivefunction(self, simulation: np.array, evaluation: np.array):
        if self.config.calibration.remove_winter:
            non_winter_indexes = find_non_winter_indexes(dates=self.observations['dates'])

            evaluation = evaluation.take(non_winter_indexes)
            simulation = simulation.take(non_winter_indexes)

        return abs(self.objective_function(evaluation, simulation))

    def _run_model_simulation(
            self,
            params: Union[ParameterSet, Sequence[float]],
            E: np.ndarray,
            state_variables: dict,
            sar_state_variables: dict) -> np.ndarray:
        simulated_streamflow = []  # Container for results

        if self.config.general.compute_snowmelt:
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

    def _warmup(self, params: Union[ParameterSet, Sequence[float]]):
        """Warm up

        The warm-up initialize the state variables of the Hydro and SAR models, if applicable.
        """
        # State variables to be return (initialized to None)
        sar_state_variables = None

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

    def _setup_pet_data(self):
        pet_params = self.pet_model.prepare(
            time_step=self.config.general.time_step,
            model_inputs={'dates': self.observations['dates'], 'T': self.observations['T']},
            hyper_parameters={'latitude': self.observations['latitude']}
        )

        return self.pet_model.run(pet_params)
