import abc
from datetime import datetime


class BaseSARModel:

    def __init__(self):
        pass

    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def inputs(self) -> list:
        raise NotImplementedError

    @abc.abstractmethod
    def hyper_parameters(self) -> list:
        raise NotImplementedError

    @abc.abstractmethod
    def prepare(self, time_step: str, dates: list[datetime], T: list[float], latitude: float) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
    def run(self, pet_data: dict):
        raise NotImplementedError
