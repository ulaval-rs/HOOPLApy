from typing import List

import numpy
import numpy as np

from hoopla.hydro_models.hydro_model import HydroModel


class HydroModel1(HydroModel):

    def prepare(self, x: List[float]):
        """Initialization

        Parameters
        ----------
        x
            List of the model parameters, in that order:
            0. Soil reservoir capacity
            1. Soil reservoir overflow dissociation constant R
            2. Routing reservoir emptying constant
            3. Delay
            4. Rainfall partitioning coefficient
            5. Routing reservoir emptying constant R T
        """
        self.P = self.data_for_calibration['Pt']  # Precipitation

        # Routing delay consideration
        drftc = numpy.ceil(x[3])
        k = np.linspace(0, drftc).T

        self.DL = np.zeros(k.shape)  # A zeros matrix of the size of k
        self.DL[-2] = 1 / (x[3] - k[-2] + 1)
        self.DL[-1] = 1 - self.DL[-2]
        self.HY = 0 * self.DL  # A zeros matrix of the size of DL

        # Initialization of the reservoir states
        self.S = x[0] * 0.5
        self.R = 10
        self.T = 5

        # Initialize HydroModel1 for all time steps
        lP = len(self.data_for_calibration['Date'])
        Qs = np.zeros((lP, 1))

        return {'Qs': Qs}

    def simulation(self, x: List[float]):
        if self.config.general.compute_warm_up:
            raise NotImplementedError

        self.prepare(x=x)

        if self.config.general.compute_pet:
            self.pet_model.prepare(time_step=self.config.general.time_step, data=self.data_for_calibration)
            self.E = self.pet_model.run()

        # Container for results
        self.results = {'Qsim': []}

        # Running simulation
        if self.config.general.compute_snowmelt:
            raise NotImplementedError
        else:
            for i, _ in enumerate(self.data_for_calibration['Date']):
                result = hydro_model_1(
                    P=self.P[i], E=self.E[i], x=x,
                    S=self.S, R=self.R, T=self.T, DL=self.DL, HY=self.HY)
                self.results['Qsim'].append(result['Qsim'])

                # Resetting state variables
                self.S = result['S']
                self.R = result['R']
                self.T = result['T']
                self.HY = result['HY']

        # Evaluation of the calibration
        if self.config.calibration.remove_winter:
            raise NotImplementedError

        else:
            Qsim = np.array(self.results['Qsim'])

            return Qsim


def hydro_model_1(P: float, E: float, x: List[float], S: float, R: float, T: float, DL: np.array, HY: np.array):
    """Hydro Model 1
    
    Parameters
    ----------
    P
        Mean areal rainfall (mm)
    E
        Mean areal evapotranspiration (mm)
    x
        List of the model parameters, in that order:
        0. Soil reservoir capacity
        1. Soil reservoir overflow dissociation constant R
        2. Routing reservoir emptying constant
        3. Delay
        4. Rainfall partitioning coefficient
        5. Routing reservoir emptying constant R T
    S
        Soil reservoir state
    R
        Root layer reservoir state
    T
        Direct routing reservoir state

    Returns
    -------

    Notes
    -----
    - Thornthwaite, C.W., Mather, J.R., 1955. The water balance. Report.
      (Drexel Institute of Climatology. United States)
    - Perrin, C. (2000). Vers une amélioration d'un modèle global pluie-débit,
      PhD Thesis, Appendix 1, p. 313-316. Retrieved from
      https://tel.archives-ouvertes.fr/tel-00006216
    """
    Ps = (1 - x[5]) * P
    Pr = P - Ps

    # Soil moisture accounting(S)
    if Ps >= E:
        S = S + Ps - E
        Is = max(0.0, S - x[0])
        S = S - Is
    else:
        S = S * np.exp((Ps - E) / x[0])
        Is = 0

    # Routing part
    # ------------
    # # Slow Routing (R)
    R = R + Is * (1 - x[1])
    Qr = R / (x[2] * x[5])
    R = R - Qr

    # # Fast routing (T)
    T = T + Pr + Is * x[1]
    Qt = T / x[5]
    T = T - Qt

    # Shift HY values of one step (losing the first one) and set last value to 0
    HY[:-1] = HY[1:]
    HY[-1] = 0

    # Total Flow calculation
    HY = HY + DL * (Qt + Qr)
    Qsim = max(0, HY[0])  # Simulated streamflow (Q is observed streamflow)

    return {'Qsim': Qsim, 'S': S, 'R': R, 'T': T, 'HY': HY}
