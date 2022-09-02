import abc

from spotpy.parameter import ParameterSet


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
    def prepare(self, params: ParameterSet, hyper_parameters: dict) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
    def run(self, model_inputs: dict, params: ParameterSet, state_variables: dict):
        raise NotImplementedError
