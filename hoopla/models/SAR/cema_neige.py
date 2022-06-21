import calendar

import numpy as np
from spotpy.parameter import ParameterSet

from hoopla.models.sar_model import BaseSARModel


class SARModel(BaseSARModel):
    """CemaNeige model"""

    def name(self) -> str:
        return 'CemaNeige'

    def inputs(self) -> list:
        return ['P', 'T', 'Tmin', 'Tmax']

    def hyper_parameters(self) -> list:
        return ['Beta', 'gradT', 'T, Zz5']

    def prepare(self, params: ParameterSet, hyper_parameters: dict) -> dict:
        """Setup state variables

        Parameters
        ----------
        params
            Useless in the CemaNeige model. This parameter exists in the BaseSARModel
            in case a Snow model needs the parameters for the initialization.
        hyper_parameters

        Returns
        -------
        SAR state variables
        """
        return {
            'G': np.zeros(5),
            'eTg': np.zeros(5),
            'Zz': hyper_parameters['Zz5'],
            'ZmedBV': hyper_parameters['Zz5'][2],
            'Beta': hyper_parameters['Beta'],
            'gradT': hyper_parameters['gradT'],
            'Tf': 0,
            'QNBV': hyper_parameters['QNBV'],
            'Vmin': hyper_parameters['Vmin'],
        }

    def run(self, model_inputs: dict, params: ParameterSet, state_variables: dict):
        """Snow accounting routine. Compute accumulation and snow melt.

        Parameters
        ----------
        model_inputs
            Dict of the model inputs
            P (float): total precipitation (solid + liquid)
            T (float): mean temperature (°C)
            Tmax (float) = max temperature (°C)
            Tmin (float) = min temperature (°C)
            Date (datetime): (1x6 matrix)
        params
            Set of the model parameters. The SAR model uses the last parameters
            0. CTg: snow cover thermal coefficient (calibrated paramter)
            1. Kf: snowmelt factor (mm/°C) (calibrated paramter)
        state_variables
            Dictionary of the following state variables:
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
        # Inputs
        date = model_inputs['Date']
        P = model_inputs['P']
        T = model_inputs['T']
        Tmin = model_inputs['Tmin']
        Tmax = model_inputs['Tmax']

        # Parameters
        CTg, Kf = params[-2], params[-1]

        # Variables
        G = state_variables['G']
        eTg = state_variables['eTg']
        Zz = state_variables['Zz']
        ZmedBV = state_variables['ZmedBV']
        Beta = state_variables['Beta']
        gradT = state_variables['gradT']
        Tf = state_variables['Tf']
        QNBV = state_variables['QNBV']
        Vmin = state_variables['Vmin']

        # Number of elevation bands
        nbzalt = 5

        # If it is a leap year, julian days after the 29/02 are shifted by one day for gradT
        day_of_year = date.timetuple().tm_yday
        if calendar.isleap(date.year) and day_of_year > 59:
            day_of_year -= 1
        theta = gradT[day_of_year-1]

        # Effective temperature
        Tz = T + theta * (Zz - ZmedBV) / 100
        Tzmax = Tmax + theta * (Zz - ZmedBV) / 100
        Tzmin = Tmin + theta * (Zz - ZmedBV) / 100
        Pdis = P / nbzalt  # Distribution of precipitation over the nbzalt bands
        modc = np.exp(Beta * (Zz - ZmedBV))
        c = np.sum(modc) / nbzalt
        Pz = (1 / c) * Pdis * np.exp(Beta * (Zz - ZmedBV))

        # Snow fraction
        fracneige = np.zeros(nbzalt)
        for i in range(nbzalt):
            if Zz[i] < 1500 and not (np.isnan(Tzmin).any() or np.isnan(Tzmax).any()):
                if Tzmax[i] <= 0:
                    fracneige[i] = 1
                elif Tzmin[i] >= 0:
                    fracneige[i] = 0
                else:
                    fracneige[i] = 1 - Tzmax[i] / (Tzmax[i] - Tzmin[i])
            else:  # USGS function (USGS is chosen if Tmax and Tmin are not defined)
                if Tz[i] > 3:
                    fracneige[i] = 0
                elif Tz[i] < -1:
                    fracneige[i] = 1
                else:
                    fracneige[i] = 1 - (Tz[i] + 1) / (3 + 1)

        fracneige = np.clip(fracneige, a_min=0.0, a_max=1.0)

        # Dispatching according to precipitation type
        Pg = Pz * fracneige
        Pl = Pz - Pg

        # Snow pack updating
        G = G + Pg

        # Snow pack thermal state
        eTg = CTg * eTg + (1 - CTg) * Tz
        eTg = np.clip(eTg, a_max=0.0, a_min=None)

        # Melting factor according to snowpack thermal state
        fTg = eTg >= Tf

        # Potential of the area covered in snow
        Fpot = (Tz > 0) * np.minimum(G, Kf * (Tz - Tf) * fTg)
        
        # Ratio of the area covered by snow
        Gthreshold = QNBV * 0.9
        fnts = np.clip(G / Gthreshold, a_max=1, a_min=None)

        # Effective melting
        snow_melt = Fpot * ((1 - Vmin) * fnts + Vmin)

        # Update of snow stock
        G = G - snow_melt

        # Depth total of runoff (sent to the hydrological model)
        runoff_d = np.sum(Pl) + np.sum(snow_melt)

        # Updating state variables
        state_variables['G'] = G
        state_variables['eTg'] = eTg

        return runoff_d, state_variables
