from typing import List

import scipy.io

from hoopla.config import Config, DATA_PATH
from hoopla.pet_models import PETModel
from hoopla.pet_models.oudin import Oudin

PET_MODELS = {
    'Oudin': Oudin,
    'Kharrufa': PETModel,
    'Penman': PETModel
}


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
    models = scipy.io.loadmat(f'{DATA_PATH}/{time_step}/Misc/pet_model_names.mat', simplify_cells=True)
    pet_models = []

    for model in models['nameE']:
        name = model[0]
        pet_model = PET_MODELS[name](name=name, inputs=model[1].split('_'), hyper_parameters=model[2].split('_'))
        pet_models.append(pet_model)

    return pet_models
