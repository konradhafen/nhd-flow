import pandas as pd
import numpy as np

input_dir = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/runoff/nhd17a_permanent/'
incsv = input_dir + 'obs_years.csv'

indf = pd.read_csv(incsv)

pointfn = "E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/obs/csv/points17a_month_year_id.csv"

# read point data to numpy
pointdf = pd.read_csv(pointfn)
# remove points after 2015 and wet points
pointdf = pointdf.loc[pointdf.Year < 2016]
pointdf = pointdf.loc[pointdf.Category == 'Dry']

# sort by year and month
pointdf = pointdf.sort_values(by=['Year', 'Month'])

# add new column for agreement
pointdf = pointdf.assign(disagree=np.nan)

for i in range(0, len(pointdf.index)):
    year = str(pointdf.iloc[i, 9])
    row = indf.loc[indf.FEATUREID == pointdf.iloc[0, -4]]
    perm = row[year].values[0]
    if perm == 0:
        pointdf.iloc[i, -1] = 0
    elif perm == 1:
        pointdf.iloc[i, -1] = 1

print("disagree =", pointdf.disagree.sum(skipna=True), "total =", len(pointdf.index), "percent =", 1.0-pointdf.disagree.sum(skipna=True)/float(len(pointdf.index)))
