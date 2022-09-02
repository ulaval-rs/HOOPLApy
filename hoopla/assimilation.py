import numpy as np

from hoopla.config import Config


def initialize(observation: dict, config: Config) -> tuple[dict, np.ndarray]:
    """Append initialized values to observation dictionary"""
    # Temperatures
    T_pet_RP = np.random.normal(np.array([observation['T'] for _ in range(config.data.N)]).T, config.data.Uc_T_pet)
    T_snow_RP = np.random.normal(np.array([observation['T'] for _ in range(config.data.N)]).T, config.data.Uc_T_snow_melt)
    T_max_RP = np.random.normal(np.array([observation['Tmax'] for _ in range(config.data.N)]).T, config.data.Uc_T_max)
    T_min_RP = np.random.normal(np.array([observation['T'] for _ in range(config.data.N)]).T, config.data.Uc_T_min)

    # Streamflow
    QRP = np.random.normal(
        loc=np.array([observation['Q'] for _ in range(config.data.N)]).T,
        scale=np.array([observation['Q'] for _ in range(config.data.N)]).T * config.data.Uc_Q
    )
    eQRP = np.array([observation['Q'] for _ in range(config.data.N)]).T - QRP

    # Rainfall
    k = observation['P'] ** 2 / (config.data.Uc_Pt * observation['P']) ** 2
    theta = (config.data.Uc_Pt * observation['P']) ** 2 / observation['P']

    PtRP = np.random.gamma(
        np.array([k for _ in range(config.data.N)]).T,
        np.array([theta for _ in range(config.data.N)]).T,
    )
    PtRP[np.where(np.isnan(PtRP))] = 0

    # Initialize weights for the particle filter
    weights = np.ones(shape=(1, config.data.N)) / config.data.N

    # Potential evapotranspiration
    if not config.general.compute_pet:
        observation['ERP'] = np.random.normal([observation['E'] for _ in range(config.data.N)], config.data.Uc_E)

    # Assigning the values to observation
    observation['TpetRP'] = T_pet_RP
    observation['TsnowRP'] = T_snow_RP
    observation['TmaxRP'] = T_max_RP
    observation['TminRP'] = T_min_RP
    observation['QRP'] = QRP
    observation['eQRP'] = eQRP
    observation['PtRP'] = PtRP

    return observation, weights
