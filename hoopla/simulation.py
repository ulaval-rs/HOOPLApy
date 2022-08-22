import json
import os
import warnings

from hoopla.config import Config
from hoopla.models.hydro_model import BaseHydroModel
from hoopla.models.pet_model import BasePETModel
from hoopla.models.sar_model import BaseSARModel


def make_simulation(config: Config,
                    observations: dict,
                    observations_for_warm_up: dict,
                    hydro_model: BaseHydroModel,
                    pet_model: BasePETModel,
                    sar_model: BaseSARModel,
                    parameters: list[float],
                    forecast_data: dict,
                    filepath_results: str):
    # Reservoirs to update
    if config.data.do_data_assimilation:
        raise NotImplementedError

    # Run simulation
    simulated_streamflow = simulate(
        config=config,
        observations=observations,
        observations_for_warm_up=observations_for_warm_up,
        hydro_model=hydro_model,
        pet_model=pet_model,
        sar_model=sar_model,
        parameters=parameters,
        forecast_data=forecast_data
    )

    # Save results
    # ------------
    results = {
        'hydro_model': hydro_model.name(),
        'PET_model': pet_model.name(),
        'SAR_model': sar_model.name(),
        'Qsim': list(simulated_streamflow),
        # 'DateForecast': list(date_forecast),
    }

    with open(filepath_results, 'w') as file:
        warnings.warn('TODO: Add more information when saving the simulation results file.')
        json.dump(results, file, indent=4)


def simulate(config: Config,
             observations: dict,
             observations_for_warm_up: dict,
             hydro_model: BaseHydroModel,
             pet_model: BasePETModel,
             sar_model: BaseSARModel,
             parameters: list[float],
             forecast_data: dict):
    # Reservoirs to update
    if config.data.do_data_assimilation:
        raise NotImplementedError

    # Simulation
    if config.data.do_data_assimilation:
        raise NotImplementedError
    else:
        hydro_model.setup(
            config=config,
            observations=observations,
            observations_for_warmup=observations_for_warm_up,
            pet_model=pet_model,
            sar_model=sar_model,
        )
        simulated_streamflow = hydro_model.simulation(parameters)

    return simulated_streamflow
