import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# filename for point observations
pointfn = "E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/obs/csv/points17a_month_year_id.csv"

# directory for monthly wet/dry estimates from MWBM
mwbmdir = "E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/runoff/nhd17a_accumulated"

# output filename
outfn = "E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/obs/csv/points17a_runoff.csv"

# read point data to pandas
pointdf = pd.read_csv(pointfn)
# remove points after 2015
pointdf = pointdf.loc[pointdf.Year < 2016]

# sort by year and month
pointdf = pointdf.sort_values(by=['Year', 'Month'])

# add new columns for runoff values and agreement
pointdf = pointdf.assign(runoff_m=np.nan, disagree=np.nan)

# directory with runoff data for each reach
runoff_dir = "E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/runoff/nhd17a_accumulated/projected5070/"
year = pointdf.iloc[0, 9]
month = pointdf.iloc[0, 10]
runoff_df = pd.read_csv(runoff_dir + "accumrun_" + str(year) + ".csv")
colbase = "sum" + str(year)
colname = colbase + str(month).zfill(2)

cell_area = 900.0  # area of grid cell (m^2)
days_in_month = 30.0
ft3_to_m3 = 0.0283168
min_cfs = 0.5  # minimum cfs to be considered 'Wet'
min_ft3 = days_in_month*3600*min_cfs
min_m = (min_ft3*ft3_to_m3)/cell_area
print("min thresholds", min_m, min_m*1000)

for i in range(0, len(pointdf.index)):
    # read year and month from entry, if different from current filename and column name, update and read
    testyear = pointdf.iloc[i, 9]
    testmonth = pointdf.iloc[i, 10]
    if testyear < 2016:
        if testyear != year:
            year = testyear
            colbase = "sum" + str(year)
            runoff_df = pd.read_csv(runoff_dir + "accumrun_" + str(year) + ".csv")
        if testmonth != month:
            month = testmonth
            colname = colbase + str(month).zfill(2)
        # get runoff row that matches the feature
        row = runoff_df.loc[runoff_df.FEATUREID == pointdf.iloc[i, -5]]

        # assign runoff value to column in point df
        runoff_depth = row[colname].values[0] * cell_area  # convert from mm/m^2 to mm
        pointdf.iloc[i, -2] = runoff_depth
        # determine if runoff value agrees or disagrees with NHD class (agree=0, disagree=1)
        if pointdf.iloc[i, 4] == 'Wet' and runoff_depth < min_m*1000:
            pointdf.iloc[i, -1] = 1
        elif pointdf.iloc[i, 4] == 'Dry' and runoff_depth >= min_m*1000:
            pointdf.iloc[i, -1] = 1
            # print(runoff_depth, pointdf.iloc[i, 20],  pointdf.iloc[i, 9], pointdf.iloc[i, 10])
        elif pointdf.iloc[i, 4] == 'Dry' and runoff_depth < min_m*1000:
            pointdf.iloc[i, -1] = 0
        elif pointdf.iloc[i, 4] == 'Wet' and runoff_depth >= min_m*1000:
            pointdf.iloc[i, -1] = 0
        else:
            pointdf.iloc[i, -1] = -9999

print("disagree =", pointdf.disagree.sum(skipna=True), "total =", len(pointdf.index), "percent =", 1.0-pointdf.disagree.sum(skipna=True)/float(len(pointdf.index)))
outdf = pointdf[['OBJECTID', 'FEATUREID', 'Category', 'Year', 'Month', 'runoff_m', 'disagree']].copy()
outdf.to_csv(outfn, index=False)
plotdat = outdf.groupby(['Month', 'Category'])['disagree'].sum()
print(plotdat)

# print(outdf.groupby(['Month', 'Category'])['Month'].count())
print("All done!")
# outdf.boxplot(column=['runoff_m'], by=['Category'])
# plt.show()

# # loop through years with point data coverage
# for year in pointdf.Year.unique():
#     # read monthly runoff estimates for each reach
#     runoffdf = pd.read_csv(runoff_dir + "accumrun_" + str(year) + ".csv")
#     # base name for column
#     colbase = "sum" + str(year)
#     # subset point data to current(in loop) year
#     pointdf_year = pointdf.loc[pointdf.year == year]
#     # loop through months of year with point coverage
#     for month in pointdf_year.Month.unique():
#         # name of column with runoff estimate from MWBM
#         colname = colbase + str(month)
