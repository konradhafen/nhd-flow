import pandas as pd
import numpy as np
import os


YEAR_DAYS = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31], dtype=np.float)
LEAP_YEAR_DAYS = np.array([31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31], dtype=np.float)
CFS_TO_CMS = 0.0283168
CMS_TO_CFS = 35.3147


def leap_year(y):
    """
    Determines if a year is a leap year
    Args:
        y: year

    Returns: True for leap year, False otherwise

    """
    if y % 400 == 0:
        return True
    if y % 100 == 0:
        return False
    if y % 4 == 0:
        return True
    else:
        return False


def annualCompareToPoints(points_fn, mod_perm_base, out_fn, year_col='Year', obs_col='Category',
                          id_col_points='COMID', id_col_perm='catch_id', perm_col='perm'):
    result_col = 'disagree'  # name of result column
    points_df = pd.read_csv(points_fn)  # open observations data as data frame
    # get only first order streams and dry observations
    points_df = points_df[(points_df['StreamOrde'] == 1) & (points_df[obs_col] == 'Dry')]
    # create results data frame
    result_df = pd.DataFrame({id_col_points: points_df[id_col_points], year_col: points_df[year_col],
                              obs_col: points_df[obs_col], perm_col: np.nan, result_col: 1})
    years = points_df[year_col].unique()  # get years with observations
    for year in years:
        mod_df = pd.read_csv(mod_perm_base.replace('%year%', str(year)))  # read modeled data
        # get catchments with observations in a given year
        ids = points_df[points_df[year_col] == year][id_col_points].values
        # copy permanence value from modeled data to result data
        result_df.loc[result_df[id_col_points].isin(ids), perm_col] = \
            mod_df[mod_df[id_col_perm].isin(ids)][perm_col].values.astype('int')
    # change result column where modeled and observed values agree (for dry and wet observations)
    result_df.loc[(result_df[obs_col] == 'Dry') & (result_df[perm_col] == 0), result_col] = 0
    result_df.loc[(result_df[obs_col] == 'Wet') & (result_df[perm_col] == 1), result_col] = 0
    # write result to csv
    result_df.to_csv(out_fn, index=False)
    print(result_df[result_col].sum()/len(result_df.index))


def monthlyCompareToPoints(points_fn, mod_perm_base, out_fn, year_col='Year', month_col='Month', obs_col='Category',
                          id_col_points='COMID', id_col_perm='catch_id', perm_col='perm'):
    result_col = 'disagree'  # name of result column
    points_df = pd.read_csv(points_fn)  # open observations data as data frame
    # get only first order streams with a valid month value
    points_df = points_df[(points_df['StreamOrde'] == 1) & (points_df[month_col] > 0)]
    # create results data frame
    result_df = pd.DataFrame({id_col_points: points_df[id_col_points], year_col: points_df[year_col],
                              month_col: points_df[month_col], obs_col: points_df[obs_col],
                              perm_col: np.nan, result_col: 1})
    years = points_df[year_col].unique()  # get years with observations
    for year in years:
        mod_df = pd.read_csv(mod_perm_base.replace('%year%', str(year)))  # read modeled data
        months = points_df[points_df[year_col] == year][month_col].unique()  # get months with observations
        for month in months:
            # get catchments with observations in a given year and month
            ids = points_df[(points_df[year_col] == year) & (points_df[month_col] == month)][id_col_points].values
            # copy permanence value from modeled data to result data
            result_df.loc[result_df[id_col_points].isin(ids), perm_col] = \
                mod_df[mod_df[id_col_perm].isin(ids)]['runoff' + str(month).zfill(2)].values.astype('int')
    # change result column where modeled and observed values agree (for dry and wet observations)
    result_df.loc[(result_df[obs_col] == 'Dry') & (result_df[perm_col] == 0), result_col] = 0
    result_df.loc[(result_df[obs_col] == 'Wet') & (result_df[perm_col] == 1), result_col] = 0
    # write result to csv
    result_df.to_csv(out_fn, index=False)
    print(result_df[result_col].sum() / len(result_df.index))


def annualPermanence(start_year, end_year, basepath, outdir, fnbase, threshold, conv = 1.0):
    """

    Args:
        start_year: year to start
        end_year: year to end
        basepath: base filename for input files with %year% indicating where year should be inserted
        outdir: directory to write outputs
        fnbase: base filename for outputs, the year and extension (.csv) will be added to this string
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


# mwbm_base = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/runoff/daymet_catchments_17/' \
#             'catchment_runoff_%year%.csv'
# outdir = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/permanence/daymet_catchments_17/annual/'
# fn_base = "annual_permanence_01cfs_"
# flow_thresh = 0.1  # cfs
#
# annualPermanence(1980, 2018, mwbm_base, outdir, fn_base, flow_thresh, CFS_TO_CMS)
#
# outdir = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/permanence/daymet_catchments_17/monthly/'
# fn_base = "monthly_permanence_01cfs_"
# monthlyPermanence(1980, 2018, mwbm_base, outdir, fn_base, flow_thresh, CFS_TO_CMS)

pointsfn = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/obs/csv/points17_strord.csv'
annual_perm_base = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/permanence/daymet_catchments_17/' \
                   'annual/annual_permanence_01cfs_%year%.csv'
out_fn = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/validation/daymet_catchments_17/' \
                   'annual_validation.csv'
annualCompareToPoints(pointsfn, annual_perm_base, out_fn)

month_perm_base = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/permanence/daymet_catchments_17/' \
                   'monthly/monthly_permanence_01cfs_%year%.csv'
out_fn = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/validation/daymet_catchments_17/' \
                   'monthly_validation.csv'
monthlyCompareToPoints(pointsfn, month_perm_base, out_fn)
