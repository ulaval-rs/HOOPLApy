import json
import warnings

from scipy.io import loadmat

from hoopla.config import Config
from hoopla.models.da_model import BaseDAModel
from hoopla.models.hydro_model import BaseHydroModel
from hoopla.models.pet_model import BasePETModel
from hoopla.models.sar_model import BaseSARModel


def make_forecast(
        config: Config,
        observations: dict,
        observations_for_warm_up: dict,
        observations_for_forecast: dict,
        hydro_model: BaseHydroModel,
        pet_model: BasePETModel,
        sar_model: BaseSARModel,
        da_model: BaseDAModel,
        parameters: list[float],
        filepath_results: str):
    # Run forecast
    if config.forecast.meteo_ens:
        raise NotImplementedError
        TODO = forecast(
            config=config,
            observations=observations,
            observations_for_warm_up=observations_for_warm_up,
            observations_for_forecast=observations_for_forecast,
            hydro_model=hydro_model,
            pet_model=pet_model,
            sar_model=sar_model,
            da_model=da_model,
            parameters=parameters
        )
    else:
        simulated_streamflow = forecast(
            config=config,
            observations=observations,
            observations_for_warm_up=observations_for_warm_up,
            observations_for_forecast=observations_for_forecast,
            hydro_model=hydro_model,
            pet_model=pet_model,
            sar_model=sar_model,
            da_model=da_model,
            parameters=parameters
        )

    # Save Results
    results = {
        'hydro_model': hydro_model.name(),
        'PET_model': pet_model.name(),
        'SAR_model': sar_model.name(),
        'Qsim': list(simulated_streamflow),
    }

    with open(filepath_results, 'w') as file:
        warnings.warn('TODO: Add more information when saving the forecast results file.')
        json.dump(results, file, indent=4)


def forecast(
        config: Config,
        observations: dict,
        observations_for_warm_up: dict,
        observations_for_forecast: dict,
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
        operation='forecast',
        observations=observations,
        observations_for_warmup=observations_for_warm_up,
        observations_for_forecast=observations_for_forecast,
        pet_model=pet_model,
        sar_model=sar_model,
        da_model=da_model
    )

    return hydro_model.simulation(parameters)



