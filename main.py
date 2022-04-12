import hoopla

from hoopla.initialization import list_catchments
from hoopla.sar_models import load_snow_models
from hoopla.pet_models import load_pet_models
from hoopla.hydro_models import load_hydrological_models
from hoopla.calibration.calibration import make_calibration

config = hoopla.load_config('./config.toml')

catchment_names = list_catchments(config.general.time_step)
hydro_models = load_hydrological_models(config)
pet_models = load_pet_models(config.general.time_step) if config.general.compute_pet else []
sar_models = load_snow_models(config.general.time_step) if config.general.compute_snowmelt else []


# Remove this after exploration
# ---------------------------------
print('catchments', catchment_names)
print('hydro_models', hydro_models)
print('evapotranspiration_models', pet_models)
print('snow_models', sar_models)
# ---------------------------------

# You may want to select this models that you want here
catchment_name = catchment_names[0]
hydro_model = hydro_models[0]
pet_model = pet_models[0] if len(pet_models) != 0 else None
sar_model = sar_models[0] if len(sar_models) != 0 else None

make_calibration(
    config=config,
    catchment_name=catchment_name,
    hydro_model=hydro_model,
    pet_model=pet_model,
    sar_model=sar_model,
)
