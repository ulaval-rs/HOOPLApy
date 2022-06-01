import hoopla
from hoopla import data, models
from hoopla.calibration.calibration import make_calibration
from hoopla.config import DATA_PATH
from hoopla.initialization import list_catchments
from hoopla.util.croping import crop_data

config = hoopla.load_config('./config.toml')

catchment_names = list_catchments(config.general.time_step)
hydro_models = models.list_hydro_models()
pet_models = models.list_pet_models()
sar_models = models.list_sar_models()

# Listing models
# ---------------------------------
print('catchments', catchment_names)
print('hydro_models', hydro_models)
print('evapotranspiration_models', pet_models)
print('snow_models', sar_models)
# ---------------------------------

# Load models
catchment_name = catchment_names[0]
hydro_model = models.load_hydro_model('HydroMod1')
pet_model = models.load_pet_model('Oudin')
sar_model = models.load_sar_model('CemaNeige')

# Load data
observations = data.load_observations(
    path=f'{DATA_PATH}/{config.general.time_step}/Hydromet_obs/Hydromet_obs_{catchment_name}.mat',
    file_format='mat',
    config=config,
    pet_model=pet_model,
    sar_model=sar_model
)

# Load meteo forecast data
data_meteo_forecast = data.load_forecast_data(
    filepath=f'{DATA_PATH}/{config.general.time_step}/Det_met_fcast/Met_fcast_{catchment_name}.mat',
    file_format='mat',
    config=config,
    sar_model=sar_model
)

model_parameters = data.load_model_parameters(
    filepath=f'{DATA_PATH}/{config.general.time_step}/Model_parameters/model_param_boundaries.mat',
    model_name=hydro_model.name(),
    file_format='mat',
)
if config.general.compute_snowmelt:
    sar_model_parameters = data.load_sar_model_parameters(
        filepath=f'{DATA_PATH}/{config.general.time_step}/Model_parameters/snow_model_param_boundaries.mat',
        model_name=sar_model.name(),
        file_format='mat',
        calibrate_snow=config.calibration.calibrate_snow
    )
else:
    sar_model_parameters = []

# Crop observed data according to specified dates and warm up
crop_data(config, observations, hydro_model, pet_model, sar_model, ini='ini_calibration')

# Calibration
make_calibration(
    observations=observations,
    config=config,
    catchment=catchment_name,
    hydro_model=hydro_model,
    pet_model=pet_model,
    sar_model=sar_model,
    model_parameters=model_parameters,
    sar_model_parameters=sar_model_parameters
)
