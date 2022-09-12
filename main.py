import hoopla
from hoopla import data, models
from hoopla.calibration.calibration import make_calibration
from hoopla.config import DATA_PATH
from hoopla.initialization import list_catchments
from hoopla.simulation import make_simulation
from hoopla.forecast import make_forecast

config = hoopla.load_config('./config.toml')

catchment_names = list_catchments(config.general.time_step)
hydro_models = models.list_hydro_models()
pet_models = models.list_pet_models()
sar_models = models.list_sar_models()
da_models = models.list_da_models()

# Listing models
print('Available models\n----------------')
print('catchments', catchment_names)
print('hydro_models', hydro_models)
print('evapotranspiration_models', pet_models)
print('snow_models', sar_models)
print('da_models', da_models)

# Load models
print('Loading models ...')
catchment_name = catchment_names[0]
hydro_model = models.load_hydro_model('HydroMod1')
pet_model = models.load_pet_model('Oudin')
sar_model = models.load_sar_model('CemaNeige')
da_model = models.load_da_model('EnsembleKalmanFilter')

# Load observations
print('Loading data ...')
observations = data.load_observations(
    path=f'{DATA_PATH}/{config.general.time_step}/Hydromet_obs/Hydromet_obs_{catchment_name}.mat',
    file_format='mat',
    config=config,
    pet_model=pet_model,
    sar_model=sar_model
)

# Load meteo forecast data
forecast_data = data.load_forecast_data(
    filepath=f'{DATA_PATH}/{config.general.time_step}/Det_met_fcast/Met_fcast_{catchment_name}.mat',
    file_format='mat',
    config=config,
    sar_model=sar_model
)

calibration_file_results = f'./results/calibration-C={catchment_name}-H={hydro_model.name()}-E={pet_model.name()}-S={sar_model.name()}.json'
simulation_file_results = f'./results/simulation-C={catchment_name}-H={hydro_model.name()}-E={pet_model.name()}-S={sar_model.name()}.json'

# Calibration
# -----------
if config.operations.calibration:
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
        # Add the SAR model's parameters at the end of the parameters to calibrate
        model_parameters += sar_model_parameters

    # Crop observed data according to specified dates and warm up
    print('Removing unused data ...')
    observations, _, observations_for_warm_up = data.crop_data(
        config=config,
        observations=observations,
        hydro_model=hydro_model,
        pet_model=pet_model,
        sar_model=sar_model,
        ini_type='ini_calibration'
    )

    print('Starting calibration ...')
    make_calibration(
        observations=observations,
        observations_for_warm_up=observations_for_warm_up,
        config=config,
        hydro_model=hydro_model,
        pet_model=pet_model,
        sar_model=sar_model,
        model_parameters=model_parameters,
        filepath_results=calibration_file_results
    )

# Simulation
# ----------
if config.operations.simulation:
    calibrated_params = data.load_calibrated_model_parameters(
        filepath=calibration_file_results
    )

    # Crop data for the simulation
    print('Removing unused data ...')
    observations, _, observations_for_warm_up = data.crop_data(
        config=config,
        observations=observations,
        hydro_model=hydro_model,
        pet_model=pet_model,
        sar_model=sar_model,
        ini_type='ini_simulation'
    )

    print('Starting simulation ...')
    make_simulation(
        observations=observations,
        observations_for_warm_up=observations_for_warm_up,
        config=config,
        hydro_model=hydro_model,
        pet_model=pet_model,
        sar_model=sar_model,
        da_model=da_model,
        parameters=calibrated_params,
        filepath_results=simulation_file_results
    )

# Forecast
if config.operations.forecast:
    calibrated_params = data.load_calibrated_model_parameters(
        filepath=calibration_file_results
    )

    # Crop data for the simulation
    print('Removing unused data ...')
    observations, observations_for_forecast, observations_for_warm_up = data.crop_data(
        config=config,
        observations=observations,
        hydro_model=hydro_model,
        pet_model=pet_model,
        sar_model=sar_model,
        ini_type='ini_forecast',
        forecast_data=forecast_data
    )

    raise NotImplementedError('Ajout forecast data')
    print('Starting forecast')
    make_forecast(
        observations=observations,
        observations_for_warm_up=observations_for_warm_up,
        config=config,
        hydro_model=hydro_model,
        pet_model=pet_model,
        sar_model=sar_model,
        da_model=da_model,
        parameters=calibrated_params,
        filepath_results=simulation_file_results
    )
