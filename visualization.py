import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

########################################################################################################################
## Use data obtained from the compare_mwbm_to_points.py functions
########################################################################################################################


def monthlyWetDry(fn, obs_col='Category', perm_col='perm', res_col='disagree', month_col='Month', nhd_col='NHD'):
    df = pd.read_csv(fn)
    print(df.groupby([obs_col, month_col])[res_col].value_counts())
    # Do logisitic regression for prob of disagreement with month as independent variable
    res_df = df.groupby([obs_col, month_col])[res_col].value_counts().to_frame().unstack()
    res_df.plot.bar()
    plt.show()


def annualDry(fn, obs_col='Category', perm_col='perm', res_col='disagree', nhd_col='NHD'):
    df = pd.read_csv(fn)
    nhd_rcol = 'nhd_da'  # NHD result column (does NHD disagree with observation
    df[nhd_rcol] = 1
    df.loc[(df[obs_col] == 'Dry') & (df[nhd_col] == 'Nonpermanent'), nhd_rcol] = 0
    df.loc[(df[obs_col] == 'Wet') & (df[nhd_col] == 'Permanent'), nhd_rcol] = 0
    print(df.groupby(obs_col)[res_col].value_counts())


fn = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/validation/daymet_catchments_17/' \
     'monthly_validation_01cfs.csv'

monthlyWetDry(fn)



# fn = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/validation/daymet_catchments_17/' \
#      'annual_validation_01cfs.csv'
# annualDry(fn)
