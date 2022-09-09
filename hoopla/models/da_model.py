import abc
from typing import Iterable

import numpy as np

from .. import config


class BaseDAModel:

    def __init__(self):
        pass

    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def run(self,
            state_variables: list,
            Qsim: np.ndarray,
            Q: np.ndarray,
            QRP: np.ndarray,
            eQ: np.ndarray,
            DA_config: config.Data) -> tuple[dict, dict]:
        raise NotImplementedError
