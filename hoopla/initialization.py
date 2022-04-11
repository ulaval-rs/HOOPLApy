from typing import List

import scipy.io

from hoopla.config import DATA_PATH


def list_catchments(time_step: str) -> List[str]:
    """Load catchment names and returns list of names.

    Parameters
    ----------
    time_step
        Time Step string ('24h' or '3h')

    Returns
    -------
    List[str]
        List of catchment names.
    """
    catchments = scipy.io.loadmat(f"{DATA_PATH}/{time_step}/Misc/catchment_names.mat")

    return [i[0][0] for i in catchments["nameC"]]
