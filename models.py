"""
AutoCal
Automatic analysis of Calcium imaging data

Edward Lau 2017
lau1@stanford.edu

"""

def model_first(x, k, y0, y1):
    """
    One-compartment first-order exponential decay model
    :param x:   float time
    :param k:   float rate constant
    :param y0:  float initial value
    :param y1:  float plateau value
    :return:    value at time point
    """

    import math
    return y0 + (y1 - y0) * (1 - math.exp(-1 * x * k))

def model_zero(x, k, y0, y1):
    """
    One-compartment first-order exponential decay model
    :param x:   float time
    :param k:   float rate constant
    :param y0:  float initial value
    :param y1:  float plateau value
    :return:    value at time point
    """

    import math
    return y0 - (k * x)

