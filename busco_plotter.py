#!/usr/bin/python

'''

busco_plotter.py

Plots BUSCO short summary output as a horizontal stacked bar plot

'''

# ###load packages
from csv import reader
from os.path import join
import pandas as pd
import matplotlib.pyplot as plt
import argparse


def main(SHORT_SUMMARY, OUT_DIR):
    '''
    Parse the short summary and plot using pandas 
    '''
    # ###create blank storage containers
    busco_results = {}
    busco_line    = []

    # ###iterate through the busco short summary input
    with open(SHORT_SUMMARY) as in_file:
        for line in reader(in_file, delimiter = '\t'):

            # ###filter out lines without useful data
            if len(line) > 2:
                # print(line)

                # ###extract proportion Complete 
                if 'C:' in line[1]:
                    plot_label = line[1]

                # ###extract proportion Complete single copy                     
                if '(S)' in line[2]:
                    busco_line.append(int(line[1]))
                    
                # ###extract proportion Complete dulicapted
                if '(D)' in line[2]:
                    busco_line.append(int(line[1]))
                
                # ###extract proportion Fragmented
                if '(F)' in line[2]:
                    busco_line.append(int(line[1]))

                # ###extract proportion Missing
                if '(M)' in line[2]:
                    busco_line.append(int(line[1]))

                # ###extract Total number in BUSCO odb used
                if 'Total BUSCO groups' in line[2]:
                    busco_line.append(int(line[1]))
                    
        # ###compute percentages and get into plottable format
        busco_props = [100 * round(x/busco_line[-1], 4) for x in busco_line]
        busco_results[SHORT_SUMMARY.split('.')[-2]] = busco_props[0:-1]

    # ###create pandas dataframe
    busco_df = pd.DataFrame.from_dict(busco_results, orient='index', columns=['Complete', 'Duplicated', 'Fragmented', 'Missing'])

    # ###Write summary to standard out
    print(busco_df.to_string())

    # ###create plot and modify appearance
    ax = busco_df.plot(kind="barh", stacked=True, figsize=(8,2.2), color=['deepskyblue', 'royalblue', 'gold', 'orangered'])
    ax.set_xlabel("% BUSCOs")
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    plt.tick_params(axis='y', which='both', left=False, labelleft=False)
    plt.legend(loc="lower left", ncol=len(busco_df.columns))
    plt.annotate(plot_label, (2,-0.05), fontsize=16)
    plt.tight_layout()

    # ###Print output location to standard out and save figure
    print(join(OUT_DIR,SHORT_SUMMARY.split('/')[-1].split('.')[-2]+'.pdf'))
    plt.savefig(join(OUT_DIR,SHORT_SUMMARY.split('/')[-1].split('.')[-2]+'.pdf'))
    plt.close()

# ###Define and parse command line arguments 
parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('in_short_summary', type=str, help='path to busco short summary file to be plotted')
parser.add_argument('-o', '--out_dir', dest='out_dir', type=str, help='path where figure should be written', default='./')

if __name__ == '__main__':

    args = parser.parse_args()

    main(args.in_short_summary, args.out_dir)

__author__ = "Will Nash"
__copyright__ = "Copyright 2021, The Earlham Institute"
__credits__ = ["Will Nash", "Wilfried Haerty"]
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Will Nash"
__email__ = "will.nash@earlham.ac.uk"
__status__ = "Testing"
