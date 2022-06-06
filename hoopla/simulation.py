from hoopla.config import Config
from hoopla.models.hydro_model import BaseHydroModel
from hoopla.models.pet_model import BasePETModel
from hoopla.models.sar_model import BaseSARModel


def make_simulation(observations: dict, config: Config,
                    hydro_model: BaseHydroModel, pet_model: BasePETModel, sar_model: BaseSARModel,
                    parameters: list[float], forecast_data: dict):
    if config.general.compute_snowmelt:
        if config.general.compute_warm_up:
            raise NotImplementedError
        else:
            TODO = simulate()
    else:
        if config.general.compute_warm_up:
            raise NotImplementedError
        else:
            TODO = simulate()


def simulate():
    raise NotImplementedError
