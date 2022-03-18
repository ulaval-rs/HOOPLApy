import hoopla

from hoopla.initialization import list_catchments
from hoopla.sar_models.sar_model import load_snow_models
from hoopla.pet_models.pet_model import load_pet_models
from hoopla.hydro_models.hydro_model import load_models
from hoopla.calibration import make_calibration

config = hoopla.load_config('./config.toml')

catchment_names = list_catchments(config)
models = load_models(config)
pet_models = load_pet_models(config) if config.general.compute_pet else []
sar_models = load_snow_models(config) if config.general.compute_snowmelt else []


# Remove this after exploration
# ---------------------------------
print('catchments', catchment_names)
print('hydro_models', models)
print('evapotranspiration_models', pet_models)
print('snow_models', sar_models)
# ---------------------------------

# You may want to select this models that you want here
catchment_name = catchment_names[0]
model = models[0]
pet_model = pet_models[0] if len(pet_models) != 0 else None
sar_model = sar_models[0] if len(sar_models) != 0 else None

# Making calibration
make_calibration(
    config=config,
    catchment_name=catchment_name,
    model=model,
    pet_model=pet_model,
    sar_model=sar_model,
)
