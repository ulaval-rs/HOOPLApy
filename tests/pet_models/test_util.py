from datetime import datetime

import pytest

from hoopla.models.util import find_day_of_year


@pytest.mark.parametrize('date, expected_day_number', [
    (datetime(year=2000, month=12, day=31), 366),
    (datetime(year=2000, month=1, day=1), 1),
    (datetime(year=2001, month=12, day=31), 365),
    (datetime(year=2001, month=3, day=21), 80),
])
def test_find_day_of_year(date, expected_day_number):
    result = find_day_of_year(date)

    assert result == expected_day_number
