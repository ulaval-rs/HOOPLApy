from dataclasses import dataclass
from typing import List


@dataclass
class HydroModel:
    name: str
    parameters: List


@dataclass
class PETModel:
    """Potential evapotranspiration model"""
    name: str
    parameters_group_1: List
    parameters_group_2: List


@dataclass
class SARModel:
    """Snow Melt Accounting model"""
    name: str
    parameters_group_1: List
    parameters_group_2: List

