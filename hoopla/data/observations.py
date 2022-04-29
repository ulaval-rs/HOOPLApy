from dataclasses import dataclass
from datetime import datetime

import numpy as np


@dataclass
class Observations:
    dates: np.ndarray[1, datetime]
    P: np.ndarray[1, float]
    latitude: float
    Q: np.ndarray[1, float]  # Streamflow
    beta: float

    def __post_init__(self):
        self.P = np.array(self.P)
        self.Q = np.array(self.Q)

