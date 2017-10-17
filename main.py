"""
calctau
Calculates Tau from Ca++ imaging data

Edward Lau 2017
lau1@stanford.edu

"""



import matplotlib.pyplot as plt
import openpyxl as xl
import caltrace
import models

def parsefile(path):
    """
    Parse the excel spreadsheet, assuming it is a standard output from the calcium imager,
    Take relevant columns and create trace objects

    :param path:
    :return:
    """



    path = 'old/12-01-16 A slide.xlsx'


    xl0 = xl.load_workbook(filename=path)

    # Get all the sheets, for each sheet
    for sheetname in xl0.get_sheet_names():
        sheet = xl0.get_sheet_by_name(sheetname)

        # Within each sheet, get column by the generator
        cols = []
        for col in sheet.columns:
            cols.append(col)

        # Which columns are the time, background, and data?
        b_cols = 15
        t_cols = 1
        d_cols = range(5, 15)

        # Get background and time data in lists
        bck = [cell.value for cell in cols[b_cols]]
        t = [cell.value for cell in cols[t_cols]]

        # Loop through the data columns and make Trace objects
        for d_col in d_cols:
            d = [cell.value for cell in cols[d_col]]

            # Create trace object.
            trce = caltrace.CalciumTrace(sheetname=sheetname,
                                         colname=d[0],
                                         tm=t[1:],
                                         dt=d[1:],
                                         bg=bck[1:])
            print(trce)

            # Create ratio from raw trace data
            trce.make_ratio()

            # Run low pass filter
            trce.smoothen(size=15,
                           order=3)


            y_tolerance = 0.0005
            x_tolerance = 3

            rise_start = []
            rise_end = []

            rise_interval = []
            for i in range(len(trce.deriv)):

                # Mark the interval where the differential is above the y-tolerance
                if trce.deriv[i] > y_tolerance:
                    rise_interval.append(i)


                # Once the differential is below the y_tolerance value,
                # Check if the interval is long enough (> x_tolerance)
                # If it is, mark the beginning and the end of the interval
                else:
                    if len(rise_interval) > x_tolerance:
                        rise_start.append(rise_interval[0])
                        rise_end.append(rise_interval[-1])
                    rise_interval = []



            # Plot out the figures
            plt.figure(1)
            plt.subplot(611)
            plt.plot(trce.median_time, trce.ratio)
            plt.title('Step 1: load raw trace')
            # plt.plot([median_time[i] for i in rise_start],
            #          [ratio[i] for i in rise_start], 'ro')
            # plt.plot([median_time[i] for i in rise_end],
            #          [ratio[i] for i in rise_end], 'ro')

            # Plot out the smoothened trace
            plt.subplot(612)
            plt.plot(trce.median_time, trce.smooth)
            plt.title('Step 2: apply low pass polynomial filter')
            # plt.plot([median_time[i] for i in rise_start],
            #          [smooth[i] for i in rise_start], 'ro')
            # plt.plot([median_time[i] for i in rise_end],
            #          [smooth[i] for i in rise_end], 'ro')

            plt.subplot(615)
            # Plot out the differential
            plt.plot(trce.median_time[1:], trce.deriv)
            plt.title('Step 3: take first derivative for peak detection')
            plt.plot([trce.median_time[i] for i in rise_start],
                     [trce.deriv[i] for i in rise_start], 'ro')
            plt.plot([trce.median_time[i] for i in rise_end],
                     [trce.deriv[i] for i in rise_end], 'ro')

            plt.subplot(616)
            plt.plot(trce.median_time, trce.ratio)
            plt.title('Step 1: apply maxima and minima to raw traces')
            plt.plot([trce.median_time[i] for i in rise_start],
                     [trce.ratio[i] for i in rise_start], 'ro')
            plt.plot([trce.median_time[i] for i in rise_end],
                     [trce.ratio[i] for i in rise_end], 'ro')

            # From the first peak (rise_end) to the next trough (rise_start),
            # Define an interval of the calcium trace and make that into a tracelet object
            # for curve-fitting
            tracelet_intervals = [(rise_end[i], rise_start[i + 1]) for i in range(len(rise_end) - 1)]

            for (start, end) in tracelet_intervals:
                print(trce.smooth[range(start, end)])
                tracelet = Tracelet(tm=trce.median_time[start:end],
                                    dt=trce.ratio[start:end])
                tracelet.optimize()

                plt.plot(tracelet.x, tracelet.y)
                plt.plot(tracelet.x, [models.model(x - tracelet.x[0], tracelet.opt_k, tracelet.y[0], tracelet.y[-1]) for x in tracelet.x])


            plt.savefig(trce.sheetname + trce.colname + '.png')

        print(sheet)



class TraceCollection(object):
    """
    Object to hold all traces of the Excel file for summary statistics

    """

    def __init__(self):
        pass


class Tracelet(object):
    """
    Object to hold each downward slope of a trace for optimization.

    """

    def __init__(self, tm, dt):
        """
        Initialize, using time as x axis and data as y axis.
        :param tm:
        :param dt:
        """
        self.x = tm
        self.y = dt
        self.opt_k = 1
        self.tau = 1
        self.R2 = 0


    def objective_function(self, k):
        """
        This is the cost function we want to minimize
        :return:
        """
        import models
        y0 = self.y[0]
        y1 = self.y[-1]
        y = self.y

        ypred = [models.model(x-self.x[0], k, y0, y1) for x in self.x]

        return sum([(y[i] - ypred[i])**2 for i in range(len(y))])


    def optimize(self):
        """
        Perform optimization to yield best-fitted k (x), tau, SE, and R2, etc.

        :return:
        """
        import scipy.optimize
        res = scipy.optimize.minimize(self.objective_function, 1)

        self.opt_k = res.x
        self.tau = 1/res.x
        print(res.x)


