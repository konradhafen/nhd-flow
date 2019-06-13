import os
from osgeo import ogr
import numpy as np
import csv

def flowValues(shpfn, fnids, indir, ofn):
    ds = ogr.Open(shpfn)
    lyr = ds.GetLayer()
    ofile = open(ofn, 'w', newline='')
    writer = csv.writer(ofile)
    row = ['comid', 'nhd_year', 'nq1', 'oq1', 'nq2', 'oq2', 'nq3', 'oq3', 'nq4', 'oq4', 'nq5', 'oq5', 'nq6', 'oq6',
           'nq7', 'oq7', 'nq8', 'oq8', 'nq9', 'oq9', 'nq10', 'oq10', 'nq11', 'oq11', 'nq12', 'oq12', 'nhd_perm',
           'obs_perm']
    writer.writerow(row)
    for i in range(0, lyr.GetFeatureCount()):
        feat = lyr.GetFeature(i)
        row = flowValuesForFeature(feat, fnids, indir, ofn)
        if row is not None:
            writer.writerow(row)
        print('row', i, 'of', lyr.GetFeatureCount())
    ofile.close()

def flowValuesForFeature(feature, fnids, indir, ofn, field = 'COMID'):
    comid = feature.GetFieldAsInteger(field)
    if np.in1d(comid, fnids):
        nhdyr = nhdYear(feature.GetFieldAsInteger('Survey_Yea'), feature.GetFieldAsInteger('Field_Chec'))
        obsyr = feature.GetFieldAsInteger('Year')
        fn = indir + str(comid) + '.csv'
        row = getFlowRow(comid, nhdyr, obsyr, fn)
        return row

def getFieldAsArray(shpfn, field):
    ds = ogr.Open(shpfn)
    lyr = ds.GetLayer()
    values = []
    for i in range(0, lyr.GetFeatureCount()):
        feat = lyr.GetFeature(i)
        values.append(feat.GetFieldAsInteger(field))
    return np.asarray(values)

def getFileName(indir):
    values = []
    for file in os.listdir(indir):
        fn = os.fsdecode(file)
        if fn.endswith('.csv'):
            values.append(int(os.path.splitext(fn)[0]))
    return np.asarray(values)

def getFlowRow(comid, nhdyr, obsyr, fn, thresh=0.1):
    obsperm = 1
    nhdperm = 1
    row = []
    row.append(comid)
    row.append(nhdyr)
    dat = np.genfromtxt(fn, delimiter=',', skip_header=1)
    obsdat = dat[np.where(dat[:, 2] == obsyr), 10]
    nhddat = dat[np.where(dat[:, 2] == nhdyr), 10]
    for i in range(0, 12):
        if obsdat.shape[1] < 12:
            omd = 0.0
        else:
            omd = obsdat[0, i]
        if nhddat.shape[1] < 12:
            nmd = 0.0
        else:
            nmd = nhddat[0, i]
        if omd <= thresh:
            obsperm = 0
        if nmd <= thresh:
            nhdperm = 0
        row.append(nmd)
        row.append(omd)

    row.append(nhdperm)
    row.append(obsperm)
    return row

def nhdYear(surveyyear, checkyear):
    if surveyyear < 1950 and checkyear < 1950:
        return 0
    elif surveyyear > checkyear:
        return surveyyear
    elif checkyear > surveyyear:
        return checkyear
    else:
        return 0


shpdir = "E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/obs/"
csvdir = "E:/konrad/Projects/usgs/nhd-flow-estimates/raw_data/miller2018-monthlyRF/"
shpfn = "obs_quads_nhd_join.shp"
ofn = "E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/obs/csv/obs_nhd_quads_flowestimatesRF.csv"

comids = getFieldAsArray(shpdir + shpfn, 'COMID')
print(comids.shape, np.min(comids), np.max(comids))
fns = getFileName(csvdir)
print(fns.shape)
mask = np.in1d(fns, comids)
mask2 = np.in1d(comids, fns)
print(fns[mask].shape)
print(comids[mask2].shape)
print(np.unique(fns[mask]).shape)
print(np.unique(comids[mask2]).shape)
flowValues(shpdir + shpfn, fns, csvdir, ofn)

