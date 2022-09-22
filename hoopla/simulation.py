import json
import os

from scipy.io import loadmat

from hoopla import util
from hoopla.config import Config
from hoopla.models.da_model import BaseDAModel
from hoopla.models.hydro_model import BaseHydroModel
from hoopla.models.pet_model import BasePETModel
from hoopla.models.sar_model import BaseSARModel


def make_simulation(config: Config,
                    observations: dict,
                    observations_for_warm_up: dict,
                    hydro_model: BaseHydroModel,
                    pet_model: BasePETModel,
                    sar_model: BaseSARModel,
                    da_model: BaseDAModel,
                    parameters: list[float],
                    filepath_results: str):
    # Run simulation
    simulated_streamflow = simulate(
        config=config,
        observations=observations,
        observations_for_warm_up=observations_for_warm_up,
        hydro_model=hydro_model,
        pet_model=pet_model,
        sar_model=sar_model,
        da_model=da_model,
        parameters=parameters,
    )

    # Save results
    # ------------
    results = {
        'hydro_model': hydro_model.name(),
        'PET_model': pet_model.name(),
        'SAR_model': sar_model.name(),
        'Qsim': list(simulated_streamflow),
        'observations': util.serialize_data(observations)
    }

    if os.path.exists(filepath_results):
        if config.general.overwrite:
            print(f'{filepath_results} exists, overwriting ...')
            with open(filepath_results, 'w') as file:
                json.dump(results, file, indent=4, default=str)
        else:
            print(f'{filepath_results} exists, with "overwrite=false", not saving results.')
    else:
        with open(filepath_results, 'w') as file:
            json.dump(results, file, indent=4, default=str)


def simulate(config: Config,
             observations: dict,
             observations_for_warm_up: dict,
             hydro_model: BaseHydroModel,
             pet_model: BasePETModel,
             sar_model: BaseSARModel,
             da_model: BaseDAModel,
             parameters: list[float]):
    # Reservoirs to update
    if config.data.do_data_assimilation:
        all_model_updated_res = loadmat(
            file_name=f'./data/{config.general.time_step}/Misc/reservoir_to_update.mat',
            simplify_cells=True
        )
        config.data.updated_res = all_model_updated_res[hydro_model.name()]

    # Simulation
    hydro_model.setup(
        config=config,
        operation='simulation',
        observations=observations,
        observations_for_warmup=observations_for_warm_up,
        pet_model=pet_model,
        sar_model=sar_model,
        da_model=da_model
    )
    return hydro_model.simulation(parameters)
