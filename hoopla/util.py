from datetime import datetime
from typing import Sequence

import numpy as np

from hoopla.config import Config


def find_day_of_year(date: datetime) -> float:
    """Compute day of the year (1st jan = 1, 31 dec = 365)"""
    date_interval = date - datetime(year=date.year, month=1, day=1)

    # In the original HOOPLA implementation, it returns fractional days
    # 1 day = 24h = 24 * 60 minutes = 24 * 60 * 60 seconds
    return date_interval.days + date_interval.seconds / (60*60*24)


def find_non_winter_indexes(dates: Sequence[datetime]):
    JAN, FEB, MARS, DEC = 1, 2, 3, 12

    return [i for i, date in enumerate(dates) if date.month not in (JAN, FEB, MARS, DEC)]


def serialize_data(data: dict) -> dict:
    """Transform data to built-in Python objects (ex. int, float, str, list, dict)"""
    result = {}

    for k, v in data.items():
        if isinstance(v, np.ndarray):
            result[k] = v.tolist()
        elif isinstance(v, datetime):
            result[k] = v.strftime('%Y-%m-%d %H:%M:%S')

        else:
            result[k] = v

    return result


def make_combinations(config: Config) -> list[dict]:
    models_combination = []

    for hydro_model_name in config.models.hydro_models:
        for pet_model_name in config.models.pet_models:
            for sar_model_name in config.models.sar_models:
                for da_model_name in config.models.da_models:
                    models_combination.append({
                        'config': config,
                        'hydro_model_name': hydro_model_name,
                        'pet_model_name': pet_model_name,
                        'sar_model_name': sar_model_name,
                        'da_model_name': da_model_name
                    })

    return models_combination
