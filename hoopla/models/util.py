from datetime import datetime
from typing import Sequence

import numpy as np


def find_day_of_year(date: datetime) -> int:
    """Compute day of the year (1st jan = 1, 31 dec = 365)"""
    date_interval = date - datetime(year=date.year, month=1, day=1)

    return date_interval.days + 1


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
