import abc
from typing import Dict, List


class PETModel:

    def __init__(self, name: str, inputs: List[str], hyper_parameters: List[str]):
        self.name = name
        self.inputs = inputs
        self.hyper_parameters = hyper_parameters

    @abc.abstractmethod
    def prepare(self, time_step: str, data: Dict):
        raise NotImplementedError

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError
