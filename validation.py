import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from calendar import monthrange

########################################################################################################################
#
########################################################################################################################


def compareToPoints(pointfn, runoff_dir, min_cfs=[0.1], new_colnames=["disagree"], fbase="accumrun_", fext=".csv",
                    cell_area=900.0, lconv=1.0):
    pointdf = pd.read_csv(pointfn)  # read point data to pandas
    pointdf = pointdf.loc[pointdf.Year < 2016]  # remove points after 2015
    pointdf = pointdf.sort_values(by=['Year', 'Month'])  # sort by year and month
    pointdf = pointdf.assign(runoff=np.nan)  # add new column for runoff values
    out_colnames = ['OBJECTID', 'FEATUREID', 'Category', 'Year', 'Month', 'runoff']  # column names to return

    for i in range(0, len(new_colnames)):  # add columns for each cfs threshold
        pointdf[new_colnames[i]] = np.nan
        out_colnames.append(new_colnames[i])

    year = pointdf.iloc[0, 9]  # year of earliest observation
    month = pointdf.iloc[0, 10]  # month of earliest observation
    runoff_df = pd.read_csv(runoff_dir + fbase + str(year) + fext)  # read modeled runoff values for earliest year
    colbase = "sum" + str(year)  # column name to get runoff for first month
    colname = colbase + str(month).zfill(2)
    ft3_to_m3 = 0.0283168  # conversion from ft^3 to m^3

    for i in range(0, len(pointdf.index)):
        print(i+1, "of", len(pointdf.index))
        testyear = pointdf.iloc[i, 9]
        testmonth = pointdf.iloc[i, 10]
        if testyear != year:
            year = testyear
            colbase = "sum" + str(year)
            runoff_df = pd.read_csv(runoff_dir + fbase + str(year) + fext)
            colname = colbase + str(month).zfill(2)
        if testmonth != month:
            month = testmonth
            colname = colbase + str(month).zfill(2)
        # calculate the minimum threshold for wet/dry classification
        min_ft3 = monthrange(year, month)[1] * 3600 * min_cfs
        min_m = (min_ft3 * ft3_to_m3) / cell_area
        row = runoff_df.loc[runoff_df.FEATUREID == pointdf['FEATUREID'].iloc[i]]  # get runoff row that matches the feature
        runoff_depth = row[colname].values[0] * 1.0 # cell_area  # convert from mm/m^2 to mm
        # print(runoff_depth)
        # print(min_m)
        pointdf.iloc[i, -2] = runoff_depth  # set runoff depth
        # determine if runoff value agrees or disagrees with NHD class (agree=0, disagree=1)
        # print(runoff_depth, min_m * lconv)
        for k in range(0, len(min_m)):
            if pointdf.iloc[i, 4] == 'Wet' and runoff_depth < min_m[k] * lconv:
                pointdf[new_colnames[k]].iloc[i] = 1  # disagree
            elif pointdf.iloc[i, 4] == 'Dry' and runoff_depth >= min_m[k] * lconv:
                pointdf[new_colnames[k]].iloc[i] = 1  # disagree
            elif pointdf.iloc[i, 4] == 'Dry' and runoff_depth < min_m[k] * lconv:
                pointdf[new_colnames[k]].iloc[i] = 0  # agree
            elif pointdf.iloc[i, 4] == 'Wet' and runoff_depth >= min_m[k] * lconv:
                pointdf[new_colnames[k]].iloc[i] = 0  # agree
            else:
                pointdf.iloc[i, -1] = -9999  # no data
    return pointdf[out_colnames].copy()


def summarizeAgreement_sample(fn, nsample, nrep, min_cfs, cat_col='Category', dis_col='disagree'):
    nrows = nrep * len(min_cfs)
    df = pd.read_csv(fn)
    result_df = pd.DataFrame(index=np.arange(0, nrows), columns=['min_cfs', 'Overall', 'Wet', 'Dry'], dtype=float)
    count = 0

    for k in range(0, len(min_cfs)):
        colname = dis_col+str(int(min_cfs[k]*100)).zfill(3)
        for l in range(0, nrep):
            wetdf = df.loc[df[cat_col] == 'Wet'][colname].sample(n=nsample)  # get random selection of wet points
            drydf = df.loc[df[cat_col] == 'Dry'][colname].sample(n=nsample)  # get random selection of dry points
            wa = 1.0 - np.sum(wetdf.values)/nsample
            da = 1.0 - np.sum(drydf.values)/nsample
            oa = 1.0 - (np.sum(wetdf.values) + np.sum(drydf.values))/(nsample*2.0)
            result_df.loc[count] = [min_cfs[k], oa, wa, da]
            count += 1
    return result_df

########################################################################################################################
# RUN HERE
########################################################################################################################

# filename for point observations
pointfn = "E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/obs/csv/points17a_month_year_id.csv"
# directory for monthly wet/dry estimates from MWBM, when using reprojected values need to update code to multiply by cell area
# mwbmdir = "E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/runoff/nhd17a_accumulated/"
mwbmdir = "E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/runoff/nhd17a_accumulated/projected5070/"
# output csv filename
# outfn = "E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/analysis/validation/min_cfs_threshold.csv"  # for original data
outfn = "E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/analysis/validation/min_cfs_threshold_5070.csv"  # for projected data
fig_dir = "C:/Users/khafe/Downloads/"  # directory to save figures

########################################################################################################################
# Determine if points are wet or dry for given minimum cfs, save to file
########################################################################################################################

# min_cfs = np.arange(50, 71, 1)  # for original data
min_cfs = np.arange(0.01, 1.01, 0.01)  # for projected data
# colnames = []
# for i in range(0, len(min_cfs)):
#     colnames.append("disagree"+str(int(min_cfs[i]*100)).zfill(3))
# result_df = compareToPoints(pointfn, mwbmdir, min_cfs, colnames, lconv=1.0)  # use lconv to convert from m to other units, when using reprojected values need to update code to multiply by cell area
# result_df.to_csv(outfn, index=False)

########################################################################################################################
# Summarize and plot results by sampling an even number of wet/dry points
########################################################################################################################

# Plot agreement
summary_df = summarizeAgreement_sample(outfn, 93, 100, min_cfs)
value_cols = ["Overall", "Wet", "Dry"]
summary_df.plot(x="min_cfs", y=value_cols, style=['ko', 'bx', 'rx'])
plt.xlabel("Wet/Dry Threshold (cfs)")
plt.ylabel("Agreement with Observations")
fig = plt.gcf()
plt.show()
fig.savefig(fig_dir + "agreement.png")

# Average agreement by minimum cfs threshold
avg_df = summary_df.groupby(['min_cfs']).mean()
splot = avg_df.plot(y=value_cols, style=['ko', 'bx', 'rx'])
splot.set_xlabel("Wet/Dry Threshold (cfs)")
splot.set_ylabel("Average Agreement with Observations")
fig = plt.gcf()
plt.show()
fig.savefig(fig_dir + "agreement_average.png")

# Make adjustments to visual overall accuracy accounting for differences in wet/dry accuracy
avg_df['wd_dif'] = abs(avg_df['Wet'] - avg_df['Dry'])
avg_df['adjusted'] = avg_df['Overall'] - avg_df['wd_dif']
splot = avg_df.plot(y='adjusted')
splot.set_xlabel("Wet/Dry Threshold (cfs)")
splot.set_ylabel("Adjusted Agreement")
fig = plt.gcf()
plt.show()
fig.savefig(fig_dir + "agreement_adjusted.png")
print(avg_df.loc[avg_df.adjusted == avg_df.adjusted.max()])
