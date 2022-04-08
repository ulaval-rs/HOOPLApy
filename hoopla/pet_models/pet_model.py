from typing import List

import scipy.io

from hoopla.config import DATA_PATH

PET_MODELS = {
    'Oudin': None,
    'Kharrufa': None,
    'Penman': None
}


class PETModel:

    def __init__(self, name: str, inputs: List[str], hyper_parameters: List[str]):
        self.name = name
        self.inputs = inputs
        self.hyper_parameters = hyper_parameters
        self.model = PET_MODELS[name]


def load_pet_models(time_step: str) -> List[PETModel]:
    """Load the available evapotranspiration models (PET models).

    Parameters
    ----------
    time_step
        Time Step string ('24h' or '3h')

    Returns
    -------
    List[PETModel]
        List of the evapotranspiration models (PET Model)
    """
    models = scipy.io.loadmat(f'{DATA_PATH}/{time_step}/Misc/pet_model_names.mat')
    pet_models = []

    for model in models['nameE']:
        pet_models.append(
            PETModel(
                name=model[0][0],
                inputs=model[1][0].split('_'),
                hyper_parameters=model[2][0].split('_')
            )
        )

    return pet_models
