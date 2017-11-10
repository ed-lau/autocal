"""
calctau
Calculates Tau from Ca++ imaging data

Edward Lau 2017
lau1@stanford.edu

"""


class TraceCollection(object):
    """
    Object to hold a collection of traces, which corresponds to one tab in the Excel sheet, for summary statistics

    """

    def __init__(self):
        self.rise_ts = []        # Collection of rise times
        self.t10s = []           # Collection of t10 values
        self.t50s = []           # Collection of t50 values
        self.t90s = []           # Collection of t90 values
        self.t100s = []          # Collection of fall interval (t100) values
        self.amplitudes = []     # Collection of amplitude values
        self.taus = []           # Collection of tau values
