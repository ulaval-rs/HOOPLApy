from typing import Dict, List, Sequence, Tuple

import numpy as np

from hoopla.models.hydro_model import BaseHydroModel


class HydroModel(BaseHydroModel):

    def inputs(self):
        return ['P', 'E']

    def prepare(self, params: List[float]) -> Dict:
        """Setup state variables

        Parameters
        ----------
        params
            List of the model parameters, in that order:
            0. Soil reservoir capacity
            1. Soil reservoir overflow dissociation constant R
            2. Routing reservoir emptying constant
            3. Delay
            4. Rainfall partitioning coefficient
            5. Routing reservoir emptying constant R T

        Returns
        -------
        State variables
            Dictionary of the state variables

        """
        # Routing delay consideration
        drftc = np.ceil(params[3])
        k = np.linspace(0, drftc).T

        DL = np.zeros(k.shape)  # A zeros matrix of the size of k
        DL[-2] = 1 / (params[3] - k[-2] + 1)
        DL[-1] = 1 - DL[-2]
        HY = 0 * DL  # A zeros matrix of the size of DL

        # Initialization of the reservoir states
        S, R, T = params[0] * 0.5, 10, 5

        return {'S': S, 'R': R, 'T': T, 'DL': DL, 'HY': HY}

    def run(self, model_inputs: Dict, params: Sequence, state_variables: Dict) -> Tuple[np.array, Dict]:
        """The model logic

        Parameters
        ----------
        model_inputs
            Dict of the model inputs
            P (float): Mean areal rainfall (mm)
            E (float): Mean areal evapotranspiration (mm)
        params
            List of the model parameters, in that order:
            0. Soil reservoir capacity
            1. Soil reservoir overflow dissociation constant R
            2. Routing reservoir emptying constant
            3. Delay
            4. Rainfall partitioning coefficient
            5. Routing reservoir emptying constant R T
        state_variables
            Dict of the state variables
            S: Soil reservoir state
            R: Root layer reservoir state
            T: Direct routing reservoir state

        Returns
        -------
        Simulated streamflow, State variables

        Notes
        -----
        - Thornthwaite, C.W., Mather, J.R., 1955. The water balance. Report.
          (Drexel Institute of Climatology. United States)
        - Perrin, C. (2000). Vers une amélioration d'un modèle global pluie-débit,
          PhD Thesis, Appendix 1, p. 313-316. Retrieved from
          https://tel.archives-ouvertes.fr/tel-00006216
        """
        P, E = model_inputs['P'], model_inputs['E']
        S, R, T = state_variables['S'], state_variables['R'], state_variables['T']
        DL, HY = state_variables['DL'], state_variables['HY']

        Ps = (1 - params[5]) * P
        Pr = P - Ps

        # Soil moisture accounting(S)
        if Ps >= E:
            S = S + Ps - E
            Is = max(0.0, S - params[0])
            S = S - Is
        else:
            S = S * np.exp((Ps - E) / params[0])
            Is = 0

        # Routing part
        # ------------
        # # Slow Routing (R)
        R = R + Is * (1 - params[1])
        Qr = R / (params[2] * params[5])
        R = R - Qr

        # # Fast routing (T)
        T = T + Pr + Is * params[1]
        Qt = T / params[5]
        T = T - Qt

        # Shift HY values of one step (losing the first one) and set last value to 0
        HY[:-1] = HY[1:]
        HY[-1] = 0

        # Total Flow calculation
        HY = HY + DL * (Qt + Qr)
        Qsim = max(0, HY[0])  # Simulated streamflow (Q is observed streamflow, Qsim is simulated streamflow)

        updated_state_variables = {'S': S, 'R': R, 'T': T, 'DL': DL, 'HY': HY}

        return Qsim, updated_state_variables

