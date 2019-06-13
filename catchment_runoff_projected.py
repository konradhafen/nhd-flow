import gispy as gis
import numpy as np
import gdal
from osgeo import osr
import pandas as pd

# Get years where there are observations
obsdbf = 'E:/konrad/Projects/usgs/prosper-nhd/data/obs/DataRelease_filter_NA83.dbf'  # path to dbf of observation shapefile
df = gis.vector.dbf2DF(obsdbf)

years = df.iloc[:]['Year'].values
years = np.unique(years)
#years = years[np.where(years >= 2009)]

catchshp = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/Catchments/Catchment17a.shp'
idfield = 'FEATUREID'
tmplraster = 'E:/konrad/Projects/usgs/prosper-nhd/data/nhd/MR/CatSeed/NHDPlusV21_PN_17_17a_CatSeed_01/NHDPlusPN/' \
             'NHDPlus17/NHDPlusCatSeed17a/catseed.tif'  # path to template raster for NHD region/area
basedir = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/runoff/'
csvdir = 'nhd17a_catchments_30m/projected5070/'
outsrs = osr.SpatialReference()
outsrs.ImportFromEPSG(5070)
bbox = gis.raster.getBoundingBox(tmplraster)  # bounding box for 30 m NHD raster
tmplproj = gis.raster.getProjection(tmplraster)  # projection for 30 m NHD raster
xres, yres = gis.raster.getXYResolution(tmplraster)
yearct = 0

for year in years:
    df = pd.DataFrame()
    for month in range(1, 13):
        fn = 'usa_grids/projected5070/runoff_' + str(year) + str(month).zfill(2) + '.tif'  # file name to clip and save (in new dir)
        clipraster = basedir + fn  # path of raster to clip
        outraster = basedir + 'nhd17a_catchments_30m/projected5070/temp.tif'  # path of clipped output
        gis.raster.clipRasterBoundingBox(clipraster, outraster, bbox, tmplproj, dstSrs=tmplproj,
                                         xres=xres, yres=yres)  # clip raster
        print(fn, 'clipped')
        dict_names = ['min' + str(year) + str(month).zfill(2),
                      'mean' + str(year) + str(month).zfill(2),
                      'median' + str(year) + str(month).zfill(2),
                      'max' + str(year) + str(month).zfill(2),
                      'sd' + str(year) + str(month).zfill(2),
                      'sum' + str(year) + str(month).zfill(2),
                      'count' + str(year) + str(month).zfill(2),
                      'majority' + str(year) + str(month).zfill(2),
                      idfield,
                      'deltamed' + str(year) + str(month).zfill(2)]
        zstats = gis.raster_vector.zonalStatistics(catchshp, outraster, idxfield=idfield, names=dict_names)
        df_temp = pd.DataFrame.from_dict(zstats)

        df_int = df_temp[[idfield, 'mean'+str(year)+str(month).zfill(2), 'sum'+str(year)+str(month).zfill(2)]]
        if month == 1:
            df = df.append(df_int, ignore_index=True)
        else:
            df = df.join(df_int.set_index(idfield), on=idfield)

    df.to_csv(basedir + csvdir + 'catrun_' + str(year) + '_mm.csv', index=False)
    yearct += 1
    print('completed', yearct, 'of', years.shape)

