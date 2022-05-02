from typing import Dict

from scipy.io import loadmat
from spotpy import objectivefunctions

from hoopla.calibration.sce_ua import shuffled_complex_evolution
from hoopla.config import Config, DATA_PATH
from hoopla.data import validation
from hoopla.models.hydro_model import BaseHydroModel
from hoopla.models.pet_model import BasePETModel
from hoopla.sar_models.sar_model import SARModel
from hoopla.util.croping import crop_data

SCORES = {
    'RMSE': objectivefunctions.rmse,
    'RMSEsqrt': NotImplemented,
    'RMSElog': NotImplemented,
    'MSE': objectivefunctions.mse,
    'MSEsqrt': NotImplemented,
    'MSElog': NotImplemented,
    'MAE': objectivefunctions.mae,
    'NSE': objectivefunctions.nashsutcliffe,
    'NSEsqrt': NotImplemented,
    'NSEinv': NotImplemented,
    'PVE': NotImplemented,
    'PVEabs': NotImplemented,
    'Balance': NotImplemented,
    'r': objectivefunctions.correlationcoefficient,
    'bKGE': NotImplemented,
    'gKGE': NotImplemented,
    'KGEm': NotImplemented
}
ORIENT_SCORES = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1]


def make_calibration(observations: dict, config: Config,
                     hydro_model: BaseHydroModel, pet_model: BasePETModel, sar_model: SARModel):
    # Launch calibration
    if config.general.compute_snowmelt:
        if config.general.compute_warm_up:
            raise NotImplementedError
        else:
            calibrate(config, observations, hydro_model, pet_model, sar_model)
    else:
        if config.general.compute_warm_up:
            raise NotImplementedError
        else:
            calibrate(config, observations, hydro_model, pet_model, sar_model)

    raise NotImplementedError


def calibrate(config: Config, data_for_calibration: Dict,
              hydro_model: BaseHydroModel, pet_model: BasePETModel, sar_model: SARModel):
    # Parameters boundaries
    # Notes: The parameters are cast in an array.
    # Each hydrological model has its own number of parameters, thus the array.
    # ---------------------
    model_param_boundaries = loadmat(
        file_name=f'{DATA_PATH}/{config.general.time_step}/Model_parameters/model_param_boundaries.mat',
        simplify_cells=True
    )
    snow_model_param_boundaries = loadmat(
        file_name=f'{DATA_PATH}/{config.general.time_step}/Model_parameters/snow_model_param_boundaries.mat',
        simplify_cells=True
    )

    if config.general.compute_snowmelt:
        if config.calibration.calibrate_snow:
            initial_parameters = [
                model_param_boundaries[hydro_model.name]['sIni'],
                snow_model_param_boundaries[sar_model.name]['sIni']
            ]
            lower_boundaries_of_parameters = [
                model_param_boundaries[hydro_model.name]['sMin'],
                snow_model_param_boundaries[sar_model.name]['sMin']
            ]
            upper_boundaries_of_parameters = [
                model_param_boundaries[hydro_model.name]['sMax'],
                snow_model_param_boundaries[sar_model.name]['sMax']
            ]
        else:
            initial_parameters = [
                model_param_boundaries[hydro_model.name]['sIni'],
                snow_model_param_boundaries[sar_model.name]['default']
            ]
            lower_boundaries_of_parameters = [
                model_param_boundaries[hydro_model.name]['sMin'],
                snow_model_param_boundaries[sar_model.name]['default']
            ]
            upper_boundaries_of_parameters = [
                model_param_boundaries[hydro_model.name]['sMax'],
                snow_model_param_boundaries[sar_model.name]['default']
            ]

    else:
        initial_parameters = model_param_boundaries[hydro_model.name()]['sIni']
        lower_boundaries_of_parameters = model_param_boundaries[hydro_model.name()]['sMin']
        upper_boundaries_of_parameters = model_param_boundaries[hydro_model.name()]['sMax']

    # Scores for the objective function
    # ---------------------------------
    if config.calibration.score not in SCORES:
        raise ValueError(f'Score must be one of: {SCORES}')
    if SCORES[config.calibration.score] == NotImplemented:
        raise ValueError(f'Score function ({config.calibration.score}) is not implemented')

    objective_function = SCORES[config.calibration.score]

    # Calibration
    # This aims to find the best parameters
    # ---------------------
    if config.calibration.method == 'DDS':
        raise NotImplementedError
    elif config.calibration.method == 'SCE':
        best_parameters, best_f = shuffled_complex_evolution(
            hydro_model=hydro_model,
            data_for_calibration=data_for_calibration,
            pet_model=pet_model,
            objective_function=objective_function,
            initial_parameters=initial_parameters,
            lower_boundaries_of_parameters=lower_boundaries_of_parameters,
            upper_boundaries_of_parameters=upper_boundaries_of_parameters,
            ngs=config.calibration.SCE['ngs'],
            max_iteration=config.calibration.maxiter
        )
    else:
        raise ValueError(f'Calibration method "{config.calibration.method}" not known. '
                         'Calibration method should be "DDS" or "SCE"')

    # ReRun simulation with best parameters
    # -------------------------------------
    if config.general.compute_warm_up:
        if config.general.compute_snowmelt:
            raise NotImplementedError
        else:
            raise NotImplementedError

    # Compute potential evapotranspiration
    if config.general.compute_pet:
        pet_data = pet_model.prepare(
            time_step=config.general.time_step,
            dates=data_for_calibration['Date'],
            T=data_for_calibration['T'],
            latitudes=data_for_calibration['Lat']
        )
        E = pet_model.run(pet_data)

    # Snow accounting model initialization
    if config.general.compute_snowmelt:
        raise NotImplementedError

    # Hydrological model initialization
    state_variables = hydro_model.prepare(best_parameters)

    # Initialization of states with WarmUp
    if config.general.compute_warm_up:
        raise NotImplementedError

    # Simulation with best param
    simulated_streamflow = []

    if config.general.compute_snowmelt:
        raise NotImplementedError
    else:
        for i, _ in enumerate(data_for_calibration['Date']):
            model_inputs = {'P': data_for_calibration['Pt'][i], 'E': E[i]}
            Qsim, state_variables = hydro_model.run(model_inputs, best_parameters, state_variables)

            simulated_streamflow.append(Qsim)

    return simulated_streamflow
