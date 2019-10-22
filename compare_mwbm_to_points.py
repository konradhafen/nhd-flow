import pandas as pd
import numpy as np
import os


YEAR_DAYS = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31], dtype=np.float)
LEAP_YEAR_DAYS = np.array([31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31], dtype=np.float)
CFS_TO_CMS = 0.0283168
CMS_TO_CFS = 35.3147


def leap_year(y):
    if y % 400 == 0:
        return True
    if y % 100 == 0:
        return False
    if y % 4 == 0:
        return True
    else:
        return False


def annualPermanence(start_year, end_year, basepath, outdir, fnbase, threshold, conv = 1.0):
    """

    Args:
        start_year: year to start
        end_year: year to end
        basepath: base filename for input files with %year% indicating where year should be inserted
        outdir: directory to write outputs
        threshold: average monthly flow rate (e.g. cfs or cms) below which a stream is considered dry
        conv: unit conversion for threshold (default: 1.0)

    Returns:

    """
    os.chdir(outdir)
    for year in range(start_year, end_year+1):
        outfn = fnbase + str(year) + '.csv'
        ndays = YEAR_DAYS
        if leap_year(year): ndays = LEAP_YEAR_DAYS
        rdf = pd.read_csv(basepath.replace('%year%', str(year)))
        pdf = pd.DataFrame({'catch_id': rdf['catch_id'].values})
        temp = rdf.iloc[:, 1:] >= (ndays * 24.0 * 60.0 * 60.0 * threshold * conv)
        pdf['perm'] = temp.all(axis='columns').astype('int')
        pdf.to_csv(outfn, index=False)


def monthlyPermanence(start_year, end_year, basepath, outdir, fnbase, threshold, conv = 1.0):
    """

    Args:
        start_year: year to start
        end_year: year to end
        basepath: base filename for input files with %year% indicating where year should be inserted
        outdir: directory to write outputs
        threshold: average monthly flow rate (e.g. cfs or cms) below which a stream is considered dry
        conv: unit conversion for threshold (default: 1.0)

    Returns:

    """
    os.chdir(outdir)
    for year in range(start_year, end_year + 1):
        outfn = fnbase + str(year) + '.csv'
        ndays = YEAR_DAYS
        if leap_year(year): ndays = LEAP_YEAR_DAYS
        rdf = pd.read_csv(basepath.replace('%year%', str(year)))
        pdf = pd.DataFrame({'catch_id': rdf['catch_id'].values})
        temp = (rdf.iloc[:, 1:] >= (ndays * 24.0 * 60.0 * 60.0 * threshold * conv)).astype('int')
        pdf = pd.concat([pdf, temp], axis=1)
        pdf.to_csv(outfn, index=False)


mwbm_base = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/runoff/daymet_catchments_17/' \
            'catchment_runoff_%year%.csv'
outdir = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/permanence/daymet_catchments_17/annual/'
fn_base = "annual_permanence_01cfs_"
flow_thresh = 0.1  # cfs

annualPermanence(1980, 2018, mwbm_base, outdir, fn_base, flow_thresh, CFS_TO_CMS)

outdir = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/permanence/daymet_catchments_17/monthly/'
fn_base = "monthly_permanence_01cfs_"
monthlyPermanence(1980, 2018, mwbm_base, outdir, fn_base, flow_thresh, CFS_TO_CMS)

pointsfn = ''
nhdfn = ''
