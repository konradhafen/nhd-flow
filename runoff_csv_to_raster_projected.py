import gispy as gis
import pandas as pd
from osgeo import osr
import numpy as np

#######################################################################################################################
# This does the same thing as runoff_csv_to_raster.py, except it uses a layer that has been converted to a projected
# coordinate system (EPSG 5070). This will result in some discrepancies between the original data and data
# calculated from these results. Results from this script should only be use for proof of concept. To get the best
# results, the MWBM model should be run on the actual input data.
#######################################################################################################################

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
idfile = 'raw_data/WolockMcCabe-WaterBalance/prismid_5070.tif'  # prism id .asc from data source below
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

outdir = 'wrk_data/WaterBalance/runoff/usa_grids/projected5070/'  # directory for output rasters
srs = osr.SpatialReference()
srs.ImportFromEPSG(5070)  # NAD83 CONUS Albers
xres, yres = gis.raster.getXYResolution(basedir + idfile)
area = abs(xres*yres)
# print("cell size", xres, yres, area)
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
                new_values = new_values/area  # convert from mm*100 to mm*100/m^2 (normalize by area)
                gis.raster.remapValues(basedir + idfile, basedir + outdir + ofn, prismid, new_values,
                                       proj=srs.ExportToWkt())  # replace ids with runoff values
                print(ofn, 'written')
