from datetime import datetime

import numpy as np

from hoopla.models.sar_model import BaseSARModel


class SARModel(BaseSARModel):
    """CemaNeige model"""

    def name(self) -> str:
        return 'CemaNeige'

    def inputs(self) -> list:
        return ['P', 'T', 'Tmin', 'Tmax']

    def hyper_parameters(self) -> list:
        return ['Beta', 'gradT', 'T, Zz5']

    def prepare(self, dates: list[datetime], params: list, hyper_parameters: dict) -> dict:
        # Cemaneige Parameters
        CTg = params[-2]
        Kf = params[-1]

        G = np.zeros(1, 5)
        eTg = np.zeros(1, 5)

        Zz = hyper_parameters['Zz5']
        ZmedBV = Zz[2]
        Beta = hyper_parameters['Beta']
        gradT = hyper_parameters['gradT']
        Tf = 0
        QNBV = hyper_parameters['QNVB']
        Vmin = hyper_parameters['Vmin']

        raise NotImplementedError

    def run(self, inputs: dict, params: dict):
        raise NotImplementedError