#!/usr/bin/python

'''

map_from_gbif.py

parse a csv downloaded from GBIF, plot it to european map

'''
# ###Load packages
import h3pandas
import argparse

import numpy as np
import pandas as pd
import seaborn as sns
import geopandas as gpd
import matplotlib.pyplot as plt

from os.path import join
from shapely.geometry import Point
from collections import OrderedDict
from dwca.read import DwCAReader
from dwca.darwincore.utils import qualname as qn

def main(RECORDS, MAP, OUT_DIR):

    print(RECORDS)
    print(MAP)
    print(OUT_DIR)

    ### from https://python-dwca-reader.readthedocs.io/en/latest/pandas_tutorial.html
    with DwCAReader(RECORDS) as dwca:
        print("Core data file is: {}".format(dwca.descriptor.core.file_location)) # => 'occurrence.txt'

        core_df = dwca.pd_read('occurrence.txt', parse_dates=True, low_memory=False)
    ###
    
    #issues manually checked before filtering
    fields=['year','decimalLatitude','decimalLongitude']

    filtered_df = core_df[core_df.columns.intersection(fields)]

    # ### This section is to generate a cumulative count of years per site
    # grouped_filtered_df = filtered_df.groupby(['year'])

    # print(grouped_filtered_df.head())

    # group_count = filtered_df.groupby(['decimalLatitude', 'decimalLongitude', 'year']).size().reset_index(name='counts')
    # group_count = group_count.rename({'decimalLongitude': 'lng', 'decimalLatitude': 'lat'}, axis=1)[['lng', 'lat', 'year', 'counts']]
    
    # print(group_count.head())
    # ###

    # ### Here, grouping by site and then extracting the earliest year an individual is recorded in that sight 
    print('Counting records...') 
    earliest_year_per_site_df = filtered_df.groupby(['decimalLatitude', 'decimalLongitude'], as_index=False)['year'].min()
    earliest_year_per_site_df = earliest_year_per_site_df.rename({'decimalLongitude': 'lng', 'decimalLatitude': 'lat', 'year': 'first_year'}, axis=1)[['lng', 'lat', 'first_year']]
    # print(earliest_year_per_site_df.head())


    # ### Here loading the map, changing the projection and creating the base plot for the background of the hexes    
    print('Plotting map...')
    europe_map = gpd.read_file(MAP)

    europe_map = europe_map.to_crs("EPSG:3395")
    # europe_map = europe_map.to_crs("EPSG:4326")

    resolution = 3
    hexagons = europe_map.h3.polyfill_resample(resolution)
    print('hexes made')

    # ###Here setting the plot dimensions up and plotting the base map
    fig, ax = plt.subplots(figsize=(14,6))
    hexagons_plot = europe_map.plot(color="lightgrey", ax = ax)
    
    # ### Here mixing the counts with the hexes 
    # ### For cumulative records
    # gch3 = group_count.h3.geo_to_h3(4)
    
    # ### For earliest year recorded 
    gch3 = earliest_year_per_site_df.h3.geo_to_h3(6)
    
    # ### Here, selecting unique year counts per hex for the cumulative count map
    # gch3 = gch3.drop(columns=['lng', 'lat']).groupby('h3_04')['year'].agg(['unique'])
    
    # ### Here, selecting the ealiest year recorded per hex
    gch3 = gch3.drop(columns=['lng', 'lat']).groupby('h3_06')['first_year'].agg(['min'])
    
    #project to hex boundries 
    ggch3 = gch3.h3.h3_to_geo_boundary()

    # ### Create cumulative counts for the count map
    # ggch3['n_years'] = ggch3['unique'].str.len()

    # ### Here, changing the projection of the hexes 
    ggch3 = ggch3.to_crs(epsg=3395)
    
    # ###Here, plotting the cumulative years plot
    # ggch3.plot(column='n_years', figsize=(10, 10), ax = ax)

    # ###Here, plotting the ealiest year recorded
    ggch3.plot(column='min', figsize=(10, 10), legend=True, legend_kwds={
        "location":"bottom",
        "shrink":.5
    }, ax = ax)

    # ###Saving the figure to .pdf
    plt.savefig('gbif_occurences_plot.pdf')
    
      
parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('records', type=str, help='path to .zip downloaded GBIF')
parser.add_argument('map', type=str, help='path to europe shape file from https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units/countries')
parser.add_argument('out_dir', type=str, help='path where output files should be written')

if __name__ == '__main__':

    args = parser.parse_args()

    main(args.records, args.map, args.out_dir)


__author__ = "Will Nash"
__copyright__ = "Copyright 2023, The Earlham Institute"
__credits__ = ["Will Nash", "Wilfried Haerty"]
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Will Nash"
__email__ = "will.nash@earlham.ac.uk"
__status__ = "Testing"
