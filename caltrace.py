"""
calctau
Calculates Tau from Ca++ imaging data

Edward Lau 2017
lau1@stanford.edu

"""

class CalciumTrace(object):
    """
    Object to hold one single calcium trace.

    """

    def __init__(self, sheetname, colname, tm, dt, bg):
        """

        :param sheetname:
        :param colname:
        :param tm:  a list holding time information
        :param dt:  a list holding calcium data (both 340 and 380 nm)
        :param bg:  a list holding background

        """

        assert len(dt) == len(tm) and len(dt) == len(bg), 'Dimension mismatch in data/background/time!!'
        assert len(dt) % 2 == 0, 'Number of rows not even - check data file!!'

        import re

        # Hold the sheet and column data after sanitizing
        self.sheetname = re.sub(r'[^\w\\P]', '', sheetname)
        self.colname = re.sub(r'[^\w\\P]', '', colname)
        self.tm = tm
        self.dt = dt
        self.bg = bg

        # Private
        self.ratio = []
        self.median_time = []
        self.smooth = []
        self.deriv = []
        self.ratio_verified = False
        self.ratio_has_been_flipped = False

    def __str__(self):
        """
        Printing class information.

        :return: Printed class information
        """
        return ('Trace object with ' + str(len(self.tm)) + ' rows.')

    def make_ratio(self):
        """
        Divide 340 nm and 380 trace to make ratio trace and take median time of successive measurements

        :return: True
        """

        # Taking ratio of every other reading (340 nm) over the immediate following reading (280 nm)
        self.ratio = [self.dt[0::2][i] / self.dt[1::2][i] for i in range(len(self.dt[0::2]))]

        # Taking the mean time between each 340 nm and 380 nm reading as the assumed time of the reading.
        self.median_time = [(self.tm[0::2][i] + self.tm[1::2][i]) / 2 for i in range(len(self.tm[0::2]))]

        return True

    def smoothen(self, size=15, order=3, derivatize=True):
        """
        Wrapper to first run the savitzky-golay helper in sg.py then take derivative of the smoothened trace

        :param size: int, pass through for size
        :param order: int, pass through for order
        :param derivatize: logical, whether to get first derivative of the trace

        :return: True
        """
        import sg
        import numpy as np

        assert self.ratio != [], 'Ratios not yet calculated!!'

        self.smooth = sg.savitzky_golay(np.array(self.ratio), size, order)

        if derivatize:
            # Take derivative
            self.deriv = np.diff(self.smooth)

        return True

    def correct_ratio(self, deriv_median_tol=0):
        """
        On the TI50 scope, either 340 or 380 nm emission may be recorded first depending on initial mirror position.
        Getting the correct 340/380 ratio requires knowing which emission wavelength was recorded first.
        Here we will guess the initial position from the calculated ratiometric values.
        We assume that in correct ratios, the calcium imaging trace of the cells will have sharper rises than falls.
        So here we check whether the median of the derivative of the trace is above 0.
        If it is above 0, we will recalculate the trace ratio using the flipped ratios and smoothen.

        :param deriv_median_tol: Tolerance of derivative median above or below 0 (not fully implemented yet)

        :return: True
        """

        import numpy as np

        assert self.deriv != [], 'Derivative of the calcium trace has not been calculated!!'

        # Check if the median of the derivative is above the tolerance (default 0)
        if np.median(self.deriv) > deriv_median_tol and not self.ratio_verified:
            # Get reciprocal of every element via list comprehension
            self.ratio = [1./r for r in self.ratio]
            self.ratio_has_been_flipped = True

        # If the median is not above the threshold, then verify the ratio is correct.
        else:
            self.ratio_verified = True



        return True



