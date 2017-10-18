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
import os

def parsefile(args):
    """
    Parse the excel spreadsheet, assuming it is a standard output from the calcium imager,
    Take relevant columns and create trace objects

    Usage:  'old/12-01-16 A slide.xlsx'
    :param path:
    :return:
    """



    path = args.path


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
            x_tolerance = 7

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
            tracelet_intervals = [(rise_end[i], rise_start[i + 1]) for i in range(len(rise_end) - 1)]

            for (start, end) in tracelet_intervals:
                print(trce.smooth[range(start, end)])
                trcelt = tracelet.Tracelet(tm=trce.median_time[start:end],
                                    dt=trce.ratio[start:end])
                trcelt.optimize()

                splt.plot(trcelt.x, trcelt.y, color='purple')
                splt.plot(trcelt.x,
                          [models.model(x - trcelt.x[0], trcelt.opt_k, trcelt.y[0], trcelt.y[-1]) for x in trcelt.x],
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
    import argparse

    parser = argparse.ArgumentParser(description='calctau reads in calcium trace data and performs curvefitting')


    parser.add_argument('path', help='path to calcium imaging spreadsheed')
    parser.add_argument('-o', '--out', help='path to output files',
                              default='out')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose error messages.')

    parser.set_defaults(func=parsefile)

    # Print help message if no arguments are given
    import sys
    if len(sys.argv[1:]) == 0:
        parser.print_help()
        parser.exit()

    # Parse all the arguments
    args = parser.parse_args()

    # Run the function in the argument
    args.func(args)
