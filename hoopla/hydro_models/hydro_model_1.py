from typing import Callable, List

import numpy
import numpy as np
from spotpy.parameter import Uniform

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
        drftc = numpy.ceil(x[3])
        print(drftc)
        k = np.linspace(0, drftc)

        dl = numpy.zeros()

        # Initialization of the reservoir states
        S = x[0] * 0.5
        R = 10
        T = 5

    def simulation(self, parameters):
        data = hydro_model_1(
            P=NotImplemented,
            E=NotImplemented,
            x=parameters,
            S=NotImplemented,
            R=NotImplemented,
            T=NotImplemented
        )


def hydro_model_1(P: float, E: float, x: List[float], S: float, R: float, T: float):
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

    # # Total Flow calculation
    # Qsim =
