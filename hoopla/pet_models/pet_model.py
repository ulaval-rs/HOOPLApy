import abc
from datetime import datetime
from typing import Dict, List


class PETModel:

    def __init__(self, name: str, inputs: List[str], hyper_parameters: List[str]):
        self.name = name
        self.inputs = inputs
        self.hyper_parameters = hyper_parameters

    @abc.abstractmethod
    def prepare(self, time_step: str, dates: List[datetime], T: List[float], latitudes: List[float]) -> Dict:
        raise NotImplementedError

    @abc.abstractmethod
    def run(self, pet_data: Dict):
        raise NotImplementedError
