import numpy as np

from hoopla import config
from hoopla.models.da_model import BaseDAModel


class DAModel(BaseDAModel):

    def __init__(self):
        super().__init__()

    def name(self) -> str:
        return 'EnsembleKalmanFilter'

    def run(self,
            state_variables: list,
            Qsim: np.ndarray,
            Q: np.ndarray,
            QRP: np.ndarray,
            eQ: np.ndarray,
            DA_config: config.Data) -> list:
        # Number members
        N = DA_config.N

        # Reshaping to get appropriate shape for the following matrix operations
        Qsim = Qsim.reshape(1, N)
        QRP = QRP.reshape(1, N)
        eQ = eQ.reshape(1, N)

        # Initialization of states matrix
        X = np.empty(shape=(len(DA_config.updated_res), N))
        X[:] = np.nan

        # Assignment of states
        for i, res in enumerate(DA_config.updated_res):
            X[i, :] = np.array([j[res] for j in state_variables])

        # Observation matrix
        z = np.dot(Qsim, np.ones(shape=(N, 1)))

        # EnKF computation
        HA = Qsim - np.dot(z, np.ones(shape=(1, N))) / N
        Y = QRP - Qsim
        L = np.dot(eQ, eQ.T) / N
        P = L + np.dot(HA, HA.T) / (N - 1)
        M = np.dot(np.linalg.inv(P), Y)
        Z = np.dot(HA.T, M)
        A = X - 1 / N * X
        Xa = X + np.dot(A, Z) / (N - 1)

        # Correction of nonsense state values
        Xa = np.clip(Xa, 0, np.inf)

        for i in range(N):
            for j, res in enumerate(DA_config.updated_res):
                state_variables[i][res] = Xa[j][i]

        return state_variables
