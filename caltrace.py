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
        self.sheetname = re.sub(r'[^\w\P]', '', sheetname)
        self.colname = re.sub(r'[^\w\P]', '', colname)
        self.tm = tm
        self.dt = dt
        self.bg = bg
        self.ratio = []
        self.median_time = []
        self.smooth = []
        self.deriv = []

    def __str__(self):
        """
        Printing class information.

        :return:
        """
        return ('Trace object with ' + str(len(self.tm)) + ' rows.')

    def make_ratio(self):
        """
        Divide 340 nm and 380 trace to make ratio trace and take median time of successive measurements

        :return:
        """

        # Taking ratio of every other reading (340 nm) over the immediate following reading (280 nm)
        self.ratio = [self.dt[0::2][i] / self.dt[1::2][i] for i in range(len(self.dt[0::2]))]

        # Taking the mean time between each 340 nm and 380 nm reading as the assumed time of the reading.
        self.median_time = [(self.tm[0::2][i] + self.tm[1::2][i]) / 2 for i in range(len(self.tm[0::2]))]

    def smoothen(self, size=15, order=3):
        """
        Wrapper to first run the savitzky-golay helper in sg.py then take derivative of the smoothened trace

        :param size: int, pass through for size
        :param order: int, pass through for order
        :return:
        """
        import sg
        import numpy as np

        assert self.ratio != [], 'Ratios not yet calculated!!'

        self.smooth = sg.savitzky_golay(np.array(self.ratio), size, order)

        # Take derivative
        self.deriv = np.diff(self.smooth)
