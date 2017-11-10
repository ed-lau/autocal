"""
calctau - sarcomere custom file
Calculates Tau from Ca++ imaging data

Edward Lau 2017
lau1@stanford.edu

"""



import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.patches as pch
import openpyxl as xl
import os, sys, argparse
import numpy as np
import sg


def sarcomere(args):
    """
    Measure sarcomere length

    Usage: python sarcomere_custom.py 'data/sarcomere/Expn24 sarcomer length 204 copy.xlsx' '204' -o sarcomere_out

    path =
    workbook_name = '204'
    out = 'sarcomere_out'


    :param args:
    :return:
    """

    path = args.path
    workbook_name = args.workbook_name
    out = args.out

    # Read the Excel file
    xl0 = xl.load_workbook(filename=path)


    # Get all the sheets, for each sheet
    for sheetname in xl0.get_sheet_names():

        # Read the sheet
        sheet = xl0.get_sheet_by_name(sheetname)


        # Within each sheet, get all the columns via the generator
        cols = []

        for col in sheet.columns:
            cols.append(col)


        # Manually take only the first eight columns

        # Specify which columns contain data on the distance, and which one the intensity
        d_cols = list(range(0,8,2))
        i_cols = [d_col + 1 for d_col in d_cols]


        # Initiate column names
        colname = 0

        # Initiate the storage for all the distance reads within this particular sheet (read)
        sarcomere_dists = []

        # Loop through the data columns and for each column make a Trace object
        for d_col in d_cols:

            colname += 1
            print(colname)

            dist = [cell.value for cell in cols[d_col]]
            read = [cell.value for cell in cols[d_col+1]]

            # Take out first value (column header)
            dist = dist[1:]
            read = read[1:]

            # Remove empty cells - assuming right now that every dist (X) column has corresponding read (Y)
            dist = [x for x in dist if x is not None]
            read = [y for y in read if y is not None]

            assert len(dist) == len(read), "Length of X and Y are not the same in this column."

            read_smooth = sg.savitzky_golay(np.array(read), 13, 3)

            read_deriv = np.diff(read_smooth)
            read_deriv2 = np.diff(read_deriv)


            #
            # Detect peak in each pulse
            #

            # Peak detection tolerance parameters (these will be specifiable in argparse later).
            y_tolerance = 0.1
            x_tolerance = 5

            # List of times when the traces begin to rise, and stops rising
            rise_starts = []
            rise_ends = []
            rise_interval = []

            for i in range(len(read_deriv)):

                # Mark the interval where the differential is above the y-tolerance
                if read_deriv[i] > y_tolerance:
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




            # From the first peak (rise_end) to the next, define an interval of the sarcomere intensity
            # and print out distances
            sarcomere_intervals = [(rise_ends[i], rise_ends[i+1]) for i in range(len(rise_ends)-1)]
            sarcomere_dist = [dist[rise_ends[i + 1] + 1] - dist[rise_ends[i] + 1] for i in range(len(rise_ends) - 1)]
            sarcomere_dists += sarcomere_dist

            # Plot out the figures
            fig = plt.figure()
            fig.suptitle('workbook' + workbook_name + 'sheet ' + sheetname + ' column ' + str(colname), fontsize=14)

            # Plot out raw traces
            splt = fig.add_subplot(311)
            splt.plot(dist, read)
            ttl = pch.Patch(color='red', label='1: raw trace')
            splt.legend(handles=[ttl], fontsize=6)
            splt.plot([dist[i+1] for i in rise_ends],
                      [read[i+1] for i in rise_ends], 'ro')
            splt.set_xlabel('distance')
            splt.set_ylabel('intensity')

            # Plot out smoothened traces
            splt = fig.add_subplot(312)
            splt.plot(dist, read_smooth)
            ttl = pch.Patch(color='red', label='2: low pass polynomial filter')
            splt.legend(handles=[ttl], fontsize=6)
            splt.set_xlabel('distance')
            splt.set_ylabel('intensity')
            splt.plot([dist[i+1] for i in rise_ends],
                      [read_smooth[i+1] for i in rise_ends], 'ro')


            for (start, end) in sarcomere_intervals:
                splt.text(np.mean((dist[end], dist[start])),
                          read_smooth[end]/2,
                          str(round(dist[end+1] - dist[start+1],2)),
                          color='red',
                          fontsize=5)

            # Plot out derivatives
            splt = fig.add_subplot(313)
            ttl = pch.Patch(color='red', label='3: peak detection in derivative')
            splt.legend(handles=[ttl], fontsize=6)
            # Plot out the differential
            splt.plot(dist[1:], read_deriv)
            # splt.plot([dist[i] for i in rise_starts],
            #          [dist[i] for i in rise_starts], 'ro')
            splt.plot([dist[i + 1] for i in rise_ends],
                      [read_deriv[i + 1] for i in rise_ends], 'ro')


            # Save the picutre and then close the plot.

            # Create directory if not exists
            os.makedirs(out, exist_ok=True)
            save_path = os.path.join(out, workbook_name + sheetname + str(colname) + '.png')
            fig.savefig(save_path, dpi=300)
            plt.close()

        #
        # For each sheet, plot out histogram of all measured distances
        #
        num_bins = 15
        n, bins, patches = plt.hist(sarcomere_dists, num_bins, normed=1, facecolor='blue', alpha=0.5)
        y = mlab.normpdf(bins, np.mean(sarcomere_dists), np.std(sarcomere_dists))
        plt.plot(bins, y, 'r--')

        label_text = 'workbook' + workbook_name + 'sheet ' + sheetname + '\n' +\
                     'n: ' + str(len(sarcomere_dists)) + \
                     ' mean: ' + str(round(np.mean(sarcomere_dists),3)) +\
                     ' sd: ' + str(round(np.std(sarcomere_dists),3))

        plt.title(label_text, fontsize=14)
        save_path = os.path.join(out, workbook_name + sheetname + '_histogram.png')
        plt.savefig(save_path, dpi=300)

        plt.close()

        #
        # Save all distances as CSV
        #
        csv_path = os.path.join(out, workbook_name + sheetname + '.csv')

        np.savetxt(csv_path, np.array(sarcomere_dists), fmt='%.3f', delimiter=",")

#
# Code for running main with parsed arguments from command line
#

if __name__ == "__main__":

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description='''\
    Sarcomeric Module v.0.0.5
    Edward Lau 2017 - lau1@stanford.edu
    Reads sarcomere trace data and outputs spacing statistics.''')

    parser.add_argument('path', help='path to sarcomere imaging spreadsheet')
    parser.add_argument('workbook_name', help='name of workbook')
    parser.add_argument('-o', '--out', help='path to output files',
                              default='out')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose error messages.')

    parser.set_defaults(func=sarcomere)

    # Print help message if no arguments are given
    if len(sys.argv[1:]) == 0:
        parser.print_help()
        parser.exit()

    # Parse all the arguments
    args = parser.parse_args()

    # Run the function in the argument
    args.func(args)
