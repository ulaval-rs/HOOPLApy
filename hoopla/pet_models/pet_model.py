from typing import List

import scipy.io

from hoopla.config import Config
from hoopla.initialization import DATA_PATH

PET_MODELS = {
    'Oudin': None,
    'Kharrufa': None,
    'Penman': None
}


class PETModel:

    def __init__(self, name: str, parameter_group_1: List[str], parameter_group_2: List[str]):
        self.name = name
        self.parameter_group_1 = parameter_group_1
        self.parameter_group_2 = parameter_group_2
        self.model = PET_MODELS[name]


def load_pet_models(config: Config) -> List[PETModel]:
    """Load PET models"""
    models = scipy.io.loadmat(f'{DATA_PATH}/{config.general.time_step}/Misc/pet_model_names.mat')
    pet_models = []

    for model in models['nameE']:
        pet_models.append(
            PETModel(
                name=model[0][0],
                parameter_group_1=model[1][0].split('_'),
                parameter_group_2=model[2][0].split('_')
            )
        )

    return pet_models
