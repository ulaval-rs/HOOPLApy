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
        """Setup state variables

        Parameters
        ----------
        dates
        params
        hyper_parameters

        Returns
        -------
        sar_parameters

        """
        # Cemaneige Parameters
        return {
            'CTg': params[-2],
            'Kf': params[-1],
            'G': np.zeros(1, 5),
            'eTg': np.zeros(1, 5),
            'Zz': hyper_parameters['Zz5'],
            'ZmedBV': hyper_parameters['Zz5'][2],
            'Beta': hyper_parameters['Beta'],
            'gradT': hyper_parameters['gradT'],
            'Tf': 0,
            'QNBV': hyper_parameters['QNVB'],
            'Vmin': hyper_parameters['Vmin'],
        }

    def run(self, inputs: dict, params: dict):
        """Snow accounting routine. Compute accumulation and snow melt.

        Parameters
        ----------
        inputs
            Dict of the model inputs
            P (float): total precipitation (solid + liquid)
            T (float): mean temperature (°C)
            Tmax (float) = max temperature (°C)
            Tmin (float) = min temperature (°C)
            Date (datetime): (1x6 matrix)
        params
            Dict of the SAR Parameters
            CTg: snow cover thermal coefficient (calibrated paramter)
            Kf: snowmelt factor (mm/°C) (calibrated paramter)
            G: snow stock
            eTg: snow cover thermal state
            Zz: catchment elevation quantiles (m)
            ZmedBV: median catchment elevation (m)
            Beta: correction of precipitation according to elevation (m-1)
            gradT: temperature gradient (°C/100 m)
            Tf: melting temperature (°C)
            QNBV: average annual snow accumulation (mm)
            Vmin: percentage of Kf that corresponds to the minimal melting rate (=0.1 if G = 0)

        Returns
        -------
        TODO
            runoffD = depth of runoff
            CemaParm = see input above
            Pg
            Pl = liquid precipitation
            snowMelt = snow melt


        Notes
        -----
        Default parameter values for daily time step (from A. Valery thesis)
          - CTg : values ranging from 0 to 1 , median = 0.25
          - Kf : values ranging from 0 to 20 , median = 3.74
        Default parameter values for 3h time step (from Hoopla testing)
          - CTg : values ranging from 0.75 to 1 , median = 0.93
          - Kf : values ranging from 0 to 1 , median = 0.40
        Misc:
          Gthreshold : quantity of snow above which all the catchment surface is supposed to be covered (mm)
                   Set to 9/10th of average annual snow accumulation = QNBV*0.9

        Following CEMAGREF - A. Valéry (2010)

        Coded by G. Seiller (2013)
        Slightly modified by A. Thiboult (2017)
        Converted to Python by Gabriel Couture (2022)

        """
        raise NotImplementedError
