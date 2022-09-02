from hoopla.models.da_model import BaseDAModel

from filterpy.kalman import EnsembleKalmanFilter


class DAModel(BaseDAModel):

    def __init__(self):
        super()

    def name(self) -> str:
        return 'EnsembleKalmanFilter'

    def run(self):
        pass
