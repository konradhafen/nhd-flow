import pandas as pd
import numpy as np
import os

input_dir = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/runoff/nhd17a_accumulated/'
output_dir = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/runoff/nhd17a_permanent/'
outcsv = output_dir + 'obs_years.csv'
directory = os.fsencode(input_dir)

# determine minimum flow in meters
days_in_month = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
ft3_to_m3 = 0.0283168
min_cfs = 1.0
min_ft3 = days_in_month*3600*min_cfs
min_m = (min_ft3*ft3_to_m3)/(30*30)
min_m = min_m.reshape(1, 12)

out_df = pd.DataFrame()

for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith('.csv'):
        year = int(filename.split('_')[-1].split('.')[0])
        print(year, filename)
        df = pd.read_csv(input_dir + filename)
        npdf = df.values
        npdf = npdf[:, 1:]  # remove first column that contains FEATUREID
        result = npdf > min_m  # true where accumulated runoff is greater than threshold
        final = result.all(axis=1)*1  # 1d array true where every month is above threshold
        out_df.loc[:, str(year)] = pd.Series(final)

out_df.loc[:, 'FEATUREID'] = df.loc[:, 'FEATUREID'].values
out_df.to_csv(outcsv, index=False)


########################################################################################################################
# Testing code, leaving here until above code works
########################################################################################################################

# year = 1977
#
# csv_dir = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/runoff/nhd17a_accumulated/'
# incsv = csv_dir + 'accumrun_' + str(year) + '.csv'
#
# df = pd.read_csv(incsv)
#
# npdf = df.values
# npdf = npdf[:, 1:]
#
# days_in_month = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
# ft3_to_m3 = 0.0283168
# min_cfs = 1.0
# min_ft3 = days_in_month*3600*min_cfs
# min_m = (min_ft3*ft3_to_m3)/(30*30)
# min_m = min_m.reshape(1, 12)
#
# result = npdf > min_m
# final = result.all(axis=1)

# test = npdf[0:2, :]
# print(min_m)
# print(npdf.shape, min_m.shape)
# print('test', test)
# print('result', test>min_m)
#
# result = test>min_m
# print('final', result.all(axis=1))
# print('final number', 1*result.all(axis=1))
# final = result.all(axis=1)