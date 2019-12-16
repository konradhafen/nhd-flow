import pandas as pd
import numpy as np
import gdal
import os

input_dir = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/prism_1704/outputs/runoff/'
output_dir = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/prism_1704/outputs/runoff/raster/'
base_raster = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/runoff/usa_grids/runoff_197701.tif'

ds = gdal.Open(base_raster)
driver = gdal.GetDriverByName('GTiff')
xsize = ds.RasterXSize
ysize = ds.RasterYSize

start_year = 1990
end_year = 1992

os.chdir(output_dir)

for year in range(start_year, end_year+1):
    df = pd.read_csv(input_dir + 'index_' + str(year) + '.csv')
    idx = df['id'].values.flatten()
    for month in range(1, 13):
        col_name = 'runoff' + str(month).zfill(2)
        vals = df[col_name].values
        vals = np.round(vals*1000)  # convert to mm
        ds_out = driver.CreateCopy('runoff' + str(year) + str(month).zfill(2) + '.tif', ds)
        ds_out.GetRasterBand(1).Fill(-9999.0)
        ds_out.GetRasterBand(1).SetNoDataValue(-9999.0)
        dat = ds_out.GetRasterBand(1).ReadAsArray()
        dat = dat.flatten()
        dat[idx] = vals
        ds_out.GetRasterBand(1).WriteArray(dat.reshape((ysize, xsize)))
        ds_out = None
