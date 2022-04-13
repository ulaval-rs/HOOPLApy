from datetime import datetime
from typing import Dict

import numpy as np

from hoopla.pet_models import PETModel
from hoopla.pet_models.util import find_day_of_year

GSC = 0.082  # (MJ / m2 / min)
RHO = 1000  # (kg / L)


class Oudin(PETModel):

    def prepare(self, time_step: str, data: Dict):
        """Prepare the PET simulation

        Parameters
        ----------
        time_step
            The time step (3h or 24h).
        data
            Dict with the following keys:
            date: Date.
            T: Daily mean temperature (Celsius).
            Lat: Station latitude.

        Attributes
        ----------
        Re
            Extraterrestrial radiation (MJ/m2/time_step(ex. 3h))
        lambda_constant
            Latent vaporization energy (MJ/kg)
        rho
            Water volumetric mass (= 1000 kg/L)
        mean_air_temperature
            Mean air temperature
        DL
            Maximum day light (h)
        """
        days_of_year = np.array([find_day_of_year(date) for date in data['Date']])

        self.mean_air_temperature = data['T']
        self.lambda_constant = 2.501 - 0.002361 * self.mean_air_temperature  # (MJ / kg)

        # Computation
        Lrad = (np.pi * data['Lat']) / 180  # (rad)
        ds = 0.409 * np.sin((2 * np.pi / 365) * days_of_year - 1.39)  # (rad)
        dr = 1 + 0.033 * np.cos(days_of_year * 2 * np.pi / 365)  # no unit
        omega = np.arccos(-np.tan(Lrad) * np.tan(ds))  # (rad)

        if time_step == '3h':
            b = 2. * np.pi * (days_of_year - 81) / 364  # component of the seasonal correction.
            Sc = 0.1645 * np.sin(2 * b) - 0.1255 * np.cos(b) - 0.025 * np.sin(b)  # seasonal correction
            t = data['date'][:, 4] + 0.5  # standard clock time at the midpoint of the period[hour]
            Lz = 75  # longitude of the centre of the local time zone[degrees west of Greenwich]
            Lm = 72.0  # longitude of the measurement site[degrees west of Greenwich]
            omega0 = np.pi / 12. * (t + 0.06667 * (Lz - Lm) + Sc - 12)  # solar time angle at midpoint of the period
            t1 = 3  # time step( in hours)
            omega1 = omega0 - (np.pi * t1) / 24  # solar time angles at the beginning of the period
            omega2 = omega0 + (np.pi * t1) / 24  # solar time angles at the end of the period
            self.Re = (12 * 60 / np.pi) * GSC * dr * (
                    (omega2 - omega1) * np.sin(Lrad) * np.sin(ds) + np.cos(Lrad) * np.cos(ds) *
                    (np.sin(omega2) - np.sin(omega1))
            )  # ( 3 - hour) solar radiation formula from Allen et al.(1998) corrected by A.Thiboult

        elif time_step == '24h':
            self.Re = (24 * 60 / np.pi) * GSC * dr * (
                    omega * np.sin(Lrad) * np.sin(ds) + np.cos(Lrad) * np.cos(ds) * np.sin(omega)
            )  # in MJ / m2 / day

        else:
            raise ValueError('Bad time step.')

    def run(self):
        """Computation of the potential evapotranspiration according to the Oudin formula

        Returns
        -------
        float
            Potential Evapotranspiration (mm/3h)

        Notes
        -----
        Reference : Which potential evapotranspiration input for a lumped
            rainfall-runoff model? Part 2 - Towards a simple and efficient
            potential evapotranspiration model for rainfall-runoff modelling,
            Oudin et al., Journal of Hydrology, 2005, 290-306, 303

        Coded by G. Seiller
        Modified by A. Thiboult (2017)
        Translated to Python by Gabriel Couture (2022)
        """
        E = self.Re / (self.lambda_constant * RHO) * (self.mean_air_temperature + 5) / 100  # [m/j]
        E = E * 1000  # [mm/j]
        E = np.clip(E, 0, None)  # Clip the value below 0 and set them to 0

        return E
