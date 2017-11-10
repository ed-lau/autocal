"""
AutoCal
Automatic analysis of Calcium imaging data

Edward Lau 2017
lau1@stanford.edu

"""

def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    """

    Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    Modified from Scipy cookbook by Edward Lau

    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.


    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.


    :param y: array_like, shape (N,) the values of the time history of the signal.
    :param window_size: int, the length of the window. Must be an odd integer number.
    :param order: int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    :param deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    :param rate:
    :return: ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).


    >>> import numpy as np
    >>> savitzky_golay(np.array([1,2,3,4,5,4,3,2,1]), 3, 1)
    array([ 1.        ,  2.        ,  3.        ,  4.        ,  4.33333333,
        4.        ,  3.        ,  2.        ,  1.66666667])

    """


    import numpy as np
    import math

    assert type(window_size) == int and type(order) == int, 'Window size and order must be integers'
    assert window_size % 2 == 1 and window_size >= 1, 'Window size must be positive odd number'
    assert window_size >= order + 2, 'Window size is too small for polynomial order'

    order_range = range(order + 1)
    half_window = window_size // 2

    # Precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * math.factorial(deriv)

    # Fill back in the beginning and end signal points with values taken from the signal itself
    first_vals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    last_vals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((first_vals, y, last_vals))

    # Return the linear convolution
    return np.convolve(m[::-1], y, mode='valid')