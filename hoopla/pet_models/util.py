from datetime import datetime


def find_day_of_year(date: datetime) -> int:
    """Compute day of the year (1st jan = 1, 31 dec = 365)"""
    date_interval = date - datetime(year=date.year, month=1, day=1)

    return date_interval.days + 1
