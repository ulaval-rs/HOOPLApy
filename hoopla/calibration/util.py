from datetime import datetime
from typing import List


def find_non_winter_indexes(dates: List[datetime]):
    return [i for i, d in enumerate(dates) if d.month not in (1, 2, 3)]
