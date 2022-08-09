from hoopla.config import Config
from hoopla.models.hydro_model import BaseHydroModel
from hoopla.models.pet_model import BasePETModel
from hoopla.models.sar_model import BaseSARModel


def make_simulation(observations: dict, config: Config,
                    hydro_model: BaseHydroModel, pet_model: BasePETModel, sar_model: BaseSARModel,
                    parameters: list[float], forecast_data: dict):
    # Reservoirs to update
    if config.data.do_data_assimilation:
        raise NotImplementedError

    # Run simulation
    TODO_result, best_params, sar_results = simulate(
        config=config,
        hydro_model=hydro_model,
        pet_model=pet_model,
        sar_model=sar_model,
        parameters=parameters,
        forecast_data=forecast_data
    )


def simulate(config: Config,
             hydro_model: BaseHydroModel, pet_model: BasePETModel, sar_model: BaseSARModel,
             parameters: list[float], forecast_data: dict):
    # Load calibrated parameters

    # Function handles

    # Reservoirs to update
    if config.data.do_data_assimilation:
        raise NotImplementedError

    # Simulation
    if config.data.do_data_assimilation:
        raise NotImplementedError
    else:
        hydro_model.setup_for_calibration()

    raise NotImplementedError
