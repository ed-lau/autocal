def model(x, k, y0, y1):
    """
    One-compartment exponential decay model

    :return:
    """
    import math
    return y0 + (y1 - y0) * (1 - math.exp(-1 * x * k))

