import abc


class BaseDAModel:

    def __init__(self):
        pass

    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError
