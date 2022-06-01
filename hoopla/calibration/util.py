from datetime import datetime
from typing import Sequence


def find_non_winter_indexes(dates: Sequence[datetime]):
    JAN, FEB, MARS = 1, 2, 3

    return [i for i, date in enumerate(dates) if date.month not in (JAN, FEB, MARS)]
