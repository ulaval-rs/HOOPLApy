from typing import List

import scipy.io

from .config import Config

DATA_PATH = './data'


def list_catchments(config: Config) -> List:
    """Load catchment names and returns list of names"""
    catchments = scipy.io.loadmat(f'{DATA_PATH}/{config.general.time_step}/Misc/catchment_names.mat')

    return [i[0][0] for i in catchments['nameC']]
