from typing import Sequence

import numpy as np
import spotpy.parameter

from hoopla.models.hydro_model import BaseHydroModel


def shuffled_complex_evolution(hydro_model: BaseHydroModel, ngs: int, max_iteration: int) -> tuple[Sequence[float], float]:
    sampler = spotpy.algorithms.sceua(hydro_model, dbname='sceua-data', dbformat='csv')
    sampler.sample(
        # repetitions=max_iteration,
        repetitions=100,
        ngs=ngs,
        kstop=10,
        peps=1e-4,
        max_loop_inc=max_iteration
    )

    results = spotpy.analyser.load_csv_results('sceua-data')
    max_index = np.argmin(results['like1'])
    best_param = results['par'][max_index], results['par_1'][max_index], results['par_2'][max_index], results['par_3'][max_index], results['par_4'][max_index], results['par_5'][max_index]
    best_cost_function_value = results['like1'][max_index]

    return best_param, best_cost_function_value


def dds(hydro_model: BaseHydroModel, max_iteration: int) -> tuple[Sequence[float], float]:
    sampler = spotpy.algorithms.dds(hydro_model, dbname='dss-data', dbformat='csv')
    sampler.sample(repetitions=max_iteration)

    results = spotpy.analyser.load_csv_results('dds-data')
    max_index = np.argmin(results['like1'])
    best_param = results['par'][max_index], results['par_1'][max_index], results['par_2'][max_index], results['par_3'][max_index], results['par_4'][max_index], results['par_5'][max_index]
    best_cost_function_value = results['like1'][max_index]

    return best_param, best_cost_function_value
