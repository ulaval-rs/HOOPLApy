import abc


class BasePETModel:

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
    def prepare(self, time_step: str, model_inputs: dict, hyper_parameters: dict) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
    def run(self, params: dict):
        raise NotImplementedError
