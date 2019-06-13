import gispy as gis
import pandas as pd
from osgeo import osr
import numpy as np

def roundDown(number, multiple):
    """
    Round a number down to a multiple
    Args:
        number: number to round
        multiple: multiple of rounded number

    Returns:
        the rounded number

    """
    return number - (number % multiple)

basedir = 'E:/konrad/Projects/usgs/nhd-flow-estimates/'
idfile = 'raw_data/WolockMcCabe-WaterBalance/prismid.asc'  # prism id .asc from data source below
datadir = 'raw_data/WolockMcCabe-WaterBalance/runoff/'  # directory containing csv files from https://www.sciencebase.gov/catalog/item/59c2b980e4b091459a61d425

#######################################################################################################################
# Data Citation
# Wolock, D.M., and McCabe, G.J., 2018, Water Balance Model Inputs and Outputs for the Conterminous United States,
# 1900-2015: U.S. Geological Survey data release, https://doi.org/10.5066/F71V5CWN.
#######################################################################################################################

# Get years where there are observations
obsdbf = 'E:/konrad/Projects/usgs/prosper-nhd/data/obs/DataRelease_filter_NA83.dbf'  # path to dbf of observation shapefile
df = gis.vector.dbf2DF(obsdbf)

years = df.iloc[:]['Year'].values
years = np.unique(years)

outdir = 'wrk_data/WaterBalance/runoff/'  # directory for output rasters
srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)  # WGS84
start_year = 1977
end_year = 2015  # max of 2015
for decade in range(roundDown(start_year, 10), roundDown(end_year, 10)+1, 10):  # data organized by decade
    fn = 'run' + str(decade) + 's.csv'  # file name for decade of data
    df = pd.read_csv(basedir + datadir + fn)  # read as pandas dataframe
    prismid = df.iloc[:]['prismid'].values  # prism id values that correspond to runoff values (consistent for a decade)
    for year in range(decade, decade+10):  # iterate through each year in a decade
        if (year >= start_year) and (year <= end_year) and (year in years):
            for month in range(1, 13):  # iterate through each year in a month
                cn = 'run_' + str(year) + str(month).zfill(2)  # column name containing runoff values for month of year
                ofn = 'runoff_' + str(year) + str(month).zfill(2) + '.tif'  # output raster (.tif) name
                new_values = df.iloc[:][cn].values  # runoff values to replace prism ids (from month-year column)
                gis.raster.remapValues(basedir + idfile, basedir + outdir + ofn, prismid, new_values,
                                       proj=srs.ExportToWkt())  # replace ids with runoff values
                print(ofn, 'written')
