import hoopla
from hoopla.config import DATA_PATH
from hoopla.data import load_observations
from hoopla.data.loader import load_forecast_data

from hoopla.initialization import list_catchments
from hoopla.models import load_hydro_model, list_hydro_models
from hoopla.sar_models import load_snow_models
from hoopla.pet_models import load_pet_models
from hoopla.calibration.calibration import make_calibration

config = hoopla.load_config('./config.toml')

catchment_names = list_catchments(config.general.time_step)
hydro_models = list_hydro_models()
pet_models = load_pet_models(config.general.time_step) if config.general.compute_pet else []
sar_models = load_snow_models(config.general.time_step) if config.general.compute_snowmelt else []

# Listing models
# ---------------------------------
print('catchments', catchment_names)
print('hydro_models', hydro_models)
print('evapotranspiration_models', pet_models)
print('snow_models', sar_models)
# ---------------------------------

# Load models
catchment_name = catchment_names[0]
hydro_model = load_hydro_model('hydro_model_1')
pet_model = pet_models[0] if len(pet_models) != 0 else None
sar_model = sar_models[0] if len(sar_models) != 0 else None

# Load data
observations = load_observations(
    path=f'{DATA_PATH}/{config.general.time_step}/Hydromet_obs/Hydromet_obs_{catchment_name}.mat',
    file_format='mat',
    config=config,
    pet_model=pet_model,
    sar_model=sar_model
)

# Data specification for catchment / parameters
data_meteo_forecast = load_forecast_data(
    filepath=f'{DATA_PATH}/{config.general.time_step}/Det_met_fcast/Met_fcast_{catchment_name}.mat',
    file_format='mat',
    config=config,
    sar_model=sar_model
)

# Crop observed data according to specified dates and warm up
crop_data(config, data_obs, hydro_model, pet_model, sar_model, ini='ini_calibration')
exit()

# Validate Data

make_calibration(
    config=config,
    catchment_name=catchment_name,
    hydro_model=hydro_model,
    pet_model=pet_model,
    sar_model=sar_model,
)
