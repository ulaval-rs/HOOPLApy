import hoopla

from hoopla.initialization import list_evaporation_models, list_models, list_snow_models, list_catchments
from hoopla.calibration import make_calibration

config = hoopla.load_config('./config.toml')

catchment_names = list_catchments(config)
models = list_models(config)
pet_models = list_evaporation_models(config)
sar_models = list_snow_models(config)

# Remove this after exploration
# ---------------------------------
print('catchments', catchment_names)
print('models', models)
print('evapotranspiration_models', pet_models)
print('snow_models', sar_models)
# ---------------------------------

# You may want to select this models that you want here
catchment_name = catchment_names[0]
model = models[0]
pet_model = pet_models[0]
sar_model = sar_models[0]

# Making calibration
make_calibration(
    config=config,
    catchment_name=catchment_name,
    model=model,
    pet_model=pet_model,
    sar_model=sar_model,
)
