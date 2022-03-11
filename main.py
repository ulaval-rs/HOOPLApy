import hoopla

from hoopla.initialization import list_evaporation_models, list_models, list_snow_models, list_catchments
from hoopla.calibration import make_calibration

config = hoopla.load_config('./config.toml')

catchments = list_catchments(config)
models = list_models(config)
evapotranspiration_models = list_evaporation_models(config)
snow_models = list_snow_models(config)

# Remove this after exploration
# ---------------------------------
print('catchments', catchments)
print('models', models)
print('evapotranspiration_models', evapotranspiration_models)
print('snow_models', snow_models)
# ---------------------------------

# You may want to remove (PET/SAR) models that you don't want
models.pop('HydroMod3')

# Making calibration
make_calibration(
    config=config,
    catchment_name=catchments[0],
    models=models,
    pet_models=evapotranspiration_models,
    sar_models=snow_models,
)
