from typing import Sequence

import numpy as np
import spotpy.parameter

from hoopla.models.hydro_model import BaseHydroModel


def shuffled_complex_evolution(hydro_model: BaseHydroModel, ngs: int, max_iteration: int) -> tuple[Sequence[float], float]:
    sampler = spotpy.algorithms.sceua(hydro_model, dbname='sceua-data', dbformat='csv')
    sampler.sample(
        repetitions=max_iteration,  # maximum number of function evaluations allowed during optimization
        ngs=ngs,
        kstop=10,
        peps=1e-4,
        max_loop_inc=max_iteration * 10
    )

    return _load_results('sceua-data')


def dds(hydro_model: BaseHydroModel, max_iteration: int) -> tuple[Sequence[float], float]:
    sampler = spotpy.algorithms.dds(hydro_model, dbname='dds-data', dbformat='csv')
    sampler.sample(repetitions=max_iteration)

    return _load_results('dds-data')


def _load_results(filename: str) -> tuple[Sequence[float], float]:
    results = spotpy.analyser.load_csv_results(filename)

    max_index = np.argmin(results['like1'])
    best_param = results['par'][max_index], results['par_1'][max_index], results['par_2'][max_index], results['par_3'][max_index], results['par_4'][max_index], results['par_5'][max_index]
    best_cost_function_value = results['like1'][max_index]

    return best_param, best_cost_function_value