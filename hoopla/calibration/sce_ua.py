import numpy
import spotpy



def shuffled_complex_evolution(
        cost_function: callable,
        x: numpy.array,
        y: numpy.array,
        var_min,
        var_max,
        nbr_of_complexes: int) -> tuple:
    """shuffled complex evolution (sce-ua) method

    parameters
    ----------
    fctname
        character string of the function to optimize.
    x
        the initial parameter array at the start.
    y
        the optimized parameter array at the end.
    var_min
        the lower bound of the parameters.
    var_max
        the upper bound of the parameters.
    nbr_of_complexes
        number of complexes (sub-pop.)- between 2 and 20
    userdata (optional)
        for the function to optimize

    results
    -------
    tuple
        tuple of 3 elements:
            bestx: best parameters
            bestf: best value of the cost function
            allbest: best value of the cost function for each iteration

    notes
    -----
    copyright (c) 2015, yarpiz (www.yarpiz.com)
    all rights reserved. please read the "license_sce.txt" for license terms.
    project code: ypea110
    project title: implementation of shuffled complex evolution (sce-ua)
    publisher: yarpiz (www.yarpiz.com)

    developer: s. mostapha kalami heris (member of yarpiz team)
    contact info: sm.kalami@gmail.com, info@yarpiz.com

    modification: 20/09/2017 by antoine thiboult.
                  - modification of the file sce_ua for compatibility with ls
                    hoopla
                  - add a convergence criteria condition
                  29/03/2022 by gabriel couture
                  - traduction from matlab to python.
    """

