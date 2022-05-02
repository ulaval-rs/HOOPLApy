import hoopla
from hoopla.config import DATA_PATH
from hoopla.data import load_observations
from hoopla.data.loader import load_forecast_data

from hoopla.initialization import list_catchments
from hoopla.models import load_hydro_model, list_hydro_models, load_pet_model, list_pet_models, list_sar_models, load_sar_model
from hoopla.sar_models import load_snow_models
from hoopla.calibration.calibration import make_calibration
from hoopla.util.croping import crop_data

config = hoopla.load_config('./config.toml')

catchment_names = list_catchments(config.general.time_step)
hydro_models = list_hydro_models()
pet_models = list_pet_models()
sar_models = list_sar_models()

# Listing models
# ---------------------------------
print('catchments', catchment_names)
print('hydro_models', hydro_models)
print('evapotranspiration_models', pet_models)
print('snow_models', sar_models)
# ---------------------------------

# Load models
catchment_name = catchment_names[0]
hydro_model = load_hydro_model('HydroMod1')
pet_model = load_pet_model('Oudin')
sar_model = load_sar_model('CemaNeige')

# Load data
observations = load_observations(
    path=f'{DATA_PATH}/{config.general.time_step}/Hydromet_obs/Hydromet_obs_{catchment_name}.mat',
    file_format='mat',
    config=config,
    pet_model=pet_model,
    sar_model=sar_model
)

# Load meteo forecast data
data_meteo_forecast = load_forecast_data(
    filepath=f'{DATA_PATH}/{config.general.time_step}/Det_met_fcast/Met_fcast_{catchment_name}.mat',
    file_format='mat',
    config=config,
    sar_model=sar_model
)

# Crop observed data according to specified dates and warm up
crop_data(config, observations, hydro_model, pet_model, sar_model, ini='ini_calibration')

# Calibration
make_calibration(
    observations=observations,
    config=config,
    hydro_model=hydro_model,
    pet_model=pet_model,
    sar_model=sar_model,
)
