from typing import List

import scipy.io

from hoopla.config import Config, DATA_PATH

SAR_MODELS = {
    "CemaNeige": None,
}


class SARModel:
    def __init__(self, name: str, inputs: List[str], hyper_parameters: List[str]):
        self.name = name
        self.inputs = inputs
        self.hyper_parameters = hyper_parameters
        self.model = SAR_MODELS[name]


def load_snow_models(time_step: str) -> List[SARModel]:
    """Load the available snow accounting models (SAR models).

    Parameters
    ----------
    time_step
        Time Step string ('24h' or '3h')

    Returns
    -------
    List[SARModel]
        List of available snow accounting models (SAR models).
    """
    models = scipy.io.loadmat(f"{DATA_PATH}/{time_step}/Misc/snow_model_names.mat")
    sar_models = []

    for model in models["nameS"]:
        sar_models.append(
            SARModel(
                name=model[0][0],
                inputs=model[1][0].split("_"),
                hyper_parameters=model[2][0].split("_"),
            )
        )

    return sar_models
