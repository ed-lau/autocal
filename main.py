"""
calctau
Calculates Tau from Ca++ imaging data

Edward Lau 2017
lau1@stanford.edu

"""


import matplotlib.pyplot as plt
import matplotlib.patches as pch
import openpyxl as xl
import caltrace, tracecol, tracelet, models
import os, sys, argparse

def parsefile(args):
    """
    Parse the excel spreadsheet, assuming it is a standard output from the calcium imager,
    Take relevant columns and create trace objects

    Usage:  'data/12-01-16 A slide.xlsx'
    :param path:
    :return:
    """



    path = args.path

    # Read the Excel file
    xl0 = xl.load_workbook(filename=path)

    # Get all the sheets, for each sheet
    for sheetname in xl0.get_sheet_names():

        # Read the sheet
        sheet = xl0.get_sheet_by_name(sheetname)

        # Start a new trace collection
        trcecl = tracecol.TraceCollection()

        # Within each sheet, get all the columns via the generator
        cols = []
        for col in sheet.columns:
            cols.append(col)

        # Specify which columns contain data on the time, background, and data?
        b_cols = 15
        t_cols = 1
        d_cols = range(5, 15)

        # Get background and time data in the form of lists via list comprehension
        bck = [cell.value for cell in cols[b_cols]]
        t = [cell.value for cell in cols[t_cols]]

        # Loop through the data columns and for each column make a Trace object
        for d_col in d_cols:
            d = [cell.value for cell in cols[d_col]]

            # Create trace object.
            trce = caltrace.CalciumTrace(sheetname=sheetname,
                                         colname=d[0],
                                         tm=t[1:],
                                         dt=d[1:],
                                         bg=bck[1:])

            # Print the trace via the pretty print function defined in class (not fully implemented).
            print(trce)

            # For the newly created Trace object, create the 340/380 ratio from raw trace data
            trce.make_ratio()

            # Smoothen, get derivative, check whether derivative is below 0, if not, flip then smoothen again
            while not trce.ratio_verified:
                # Run a low pass filter to smoothen the raw trace, then get the first derivative
                trce.smoothen(size=15,
                              order=3,
                              derivatize=True)

                # If the median of the derivative is above 0 it should mean the trace is rising more often
                # than it is falling. In which case we will think the 340/380 ratios are flipped.
                # If the trace initially needs flipping, then correct_ratio()  verifies the trace is good
                # when run the second time with the flipped trace, this ensures the flipped trace is smoothened
                # With the same parameters (size, order, etc.)
                trce.correct_ratio(deriv_median_tol=0)


            #
            # Detect peak in each pulse
            #

            # Peak detection tolerance parameters (these will be specifiable in argparse later).
            y_tolerance = 0.0005
            x_tolerance = 7

            # List of times when the traces begin to rise, and stops rising
            rise_starts = []
            rise_ends = []
            rise_intervals = []

            for i in range(len(trce.deriv)):

                # Mark the interval where the differential is above the y-tolerance
                if trce.deriv[i] > y_tolerance:
                    rise_interval.append(i)

                # Once the differential drops below the y_tolerance value,
                # Check if the interval is long enough (> x_tolerance)
                # If it is, mark the beginning and the end of the interval
                else:
                    if len(rise_interval) > x_tolerance:
                        rise_starts.append(rise_interval[0])
                        rise_ends.append(rise_interval[-1])
                    rise_interval = []

            # Rise times are calculated as the time interval between the start and end of each rise cycles
            assert len(rise_starts) == len(rise_ends), 'Check this trace - incorrect number of cycles detected.'

            rise_t = [trce.median_time[rise_starts[i]] - trce.median_time[rise_ends[i]] for i in
                      range(len(rise_starts))]



            # Plot out the figures
            fig = plt.figure()
            fig.suptitle(trce.sheetname + trce.colname, fontsize=14)

            splt = fig.add_subplot(511)
            splt.plot(trce.median_time, trce.ratio)
            ttl = pch.Patch(color='red', label='1: raw trace')
            splt.legend(handles=[ttl], fontsize=6)
            splt.set_xlabel('t')
            splt.set_ylabel('ratio')

            # Plot out the smoothened trace
            splt = fig.add_subplot(512)
            splt.plot(trce.median_time, trce.smooth)
            ttl = pch.Patch(color='red', label='2: low pass polynomial filter')
            splt.legend(handles=[ttl], fontsize=6)
            # plt.plot([median_time[i] for i in rise_start],
            #          [smooth[i] for i in rise_start], 'ro')
            # plt.plot([median_time[i] for i in rise_end],
            #          [smooth[i] for i in rise_end], 'ro')

            splt = fig.add_subplot(513)
            # Plot out the differential
            splt.plot(trce.median_time[1:], trce.deriv)
            splt.plot([trce.median_time[i] for i in rise_start],
                     [trce.deriv[i] for i in rise_start], 'ro')
            splt.plot([trce.median_time[i] for i in rise_end],
                     [trce.deriv[i] for i in rise_end], 'ro')
            ttl = pch.Patch(color='red', label='3: peak detection in derivative')
            splt.legend(handles=[ttl], fontsize=6)

            splt = fig.add_subplot(514)
            splt.plot(trce.median_time, trce.ratio)
            splt.plot([trce.median_time[i] for i in rise_start],
                     [trce.ratio[i] for i in rise_start], 'ro')
            splt.plot([trce.median_time[i] for i in rise_end],
                     [trce.ratio[i] for i in rise_end], 'ro')
            ttl = pch.Patch(color='red', label='4: apply peaks to raw')
            splt.legend(handles=[ttl], fontsize=6)

            splt = fig.add_subplot(515)
            splt.plot(trce.median_time, trce.ratio)
            splt.plot([trce.median_time[i] for i in rise_start],
                     [trce.ratio[i] for i in rise_start], 'ro')
            splt.plot([trce.median_time[i] for i in rise_end],
                     [trce.ratio[i] for i in rise_end], 'ro')
            ttl = pch.Patch(color='red', label='5: fit kinetic curve')
            splt.legend(handles=[ttl], fontsize=6)

            # From the first peak (rise_end) to the next trough (rise_start),
            # Define an interval of the calcium trace and make that into a tracelet object
            # for curve-fitting
            tracelet_intervals = [(rise_ends[i], rise_starts[i + 1]) for i in range(len(rise_ends) - 1)]

            for (start, end) in tracelet_intervals:
                print(trce.smooth[range(start, end)])
                trcelt = tracelet.Tracelet(tm=trce.median_time[start:end],
                                           dt=trce.ratio[start:end])
                trcelt.optimize()

                splt.plot(trcelt.x, trcelt.y, color='purple')
                splt.plot(trcelt.x,
                          [models.model_zero(x - trcelt.x[0], trcelt.opt_k, trcelt.y[0], trcelt.y[-1]) for x in trcelt.x],
                          color='green')
                splt.text(trcelt.x[0], trcelt.y[0], 'tau:' + str(1/trcelt.opt_k), color='red', fontsize=3)


            # Save the picutre and then close the plot.

            # Create directory if not exists
            os.makedirs(args.out, exist_ok=True)
            save_path = os.path.join(args.out, trce.sheetname + trce.colname + '.png')
            fig.savefig(save_path, dpi=300)
            plt.close()




#
# Code for running main with parsed arguments from command line
#

if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description='''\
    CalcTau v.0.0.2
    Edward Lau 2017 - lau1@stanford.edu
    Reads calcium trace data and fits kinetic curves.''')

    parser.add_argument('path', help='path to calcium imaging spreadsheet')
    parser.add_argument('-o', '--out', help='path to output files',
                              default='out')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose error messages.')

    parser.set_defaults(func=parsefile)

    # Print help message if no arguments are given
    if len(sys.argv[1:]) == 0:
        parser.print_help()
        parser.exit()

    # Parse all the arguments
    args = parser.parse_args()

    # Run the function in the argument
    args.func(args)
