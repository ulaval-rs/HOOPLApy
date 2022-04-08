from dataclasses import dataclass
from datetime import datetime
from typing import Dict

import toml

DATA_PATH = './data'


@dataclass
class Operations:
    calibration: bool
    simulation: bool
    forecast: bool


@dataclass
class TimeInterval:
    begin: datetime
    end: datetime


@dataclass
class Dates:
    calibration: TimeInterval
    simulation: TimeInterval
    forecast: TimeInterval

    def __post_init__(self):
        self.calibration = TimeInterval(**self.calibration)
        self.simulation = TimeInterval(**self.simulation)
        self.forecast = TimeInterval(**self.forecast)


@dataclass
class General:
    verbose: bool
    time_step: str
    compute_pet: bool
    compute_snowmelt: bool
    compute_warm_up: bool
    export_light: bool
    overwrite: bool
    parallel_compute: bool


@dataclass
class Calibration:
    export: bool
    calibrate_snow: bool
    method: str
    remove_winter: bool
    score: str
    maxiter: int
    SCE: Dict[str, int]


@dataclass
class Forecast:
    issue_time: int
    perfect_forecast: bool
    horizon: int
    meteo_ens: bool


@dataclass
class Data:
    do_data_assimilation: bool
    tech: str
    Uc_Q: float
    Uc_Pt: float
    Uc_temp_pet: float
    Uc_temp_snow_melt: float
    Uc_temp_min: float
    Uc_temp_max: float
    Uc_E: float
    dt: float
    N: int
    PF: Dict


@dataclass
class Config:
    operations: Operations
    dates: Dates
    general: General
    calibration: Calibration
    forecast: Forecast
    data: Data

    def __post_init__(self):
        self.operations = Operations(**self.operations)
        self.dates = Dates(**self.dates)
        self.general = General(**self.general)
        self.calibration = Calibration(**self.calibration)
        self.forecast = Forecast(**self.forecast)
        self.data = Data(**self.data)


def load_config(path: str) -> Config:
    configurations = toml.load(path)

    return Config(**configurations)
