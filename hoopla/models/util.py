from datetime import datetime
from typing import Sequence


def find_day_of_year(date: datetime) -> int:
    """Compute day of the year (1st jan = 1, 31 dec = 365)"""
    date_interval = date - datetime(year=date.year, month=1, day=1)

    return date_interval.days + 1


def find_non_winter_indexes(dates: Sequence[datetime]):
    JAN, FEB, MARS, DEC = 1, 2, 3, 12

    return [i for i, date in enumerate(dates) if date.month not in (JAN, FEB, MARS, DEC)]