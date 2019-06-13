import pandas as pd
import os
import numpy as np

scfn = "E:/konrad/Projects/usgs/baseflow-pnw/data/outputs/csv/StreamCat_17.csv"  # streamcat data
outsc = "E:/konrad/Projects/usgs/baseflow-pnw/data/outputs/csv/StreamCat_17_subset.csv"
joinfn = "E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/analysis/validation/min_cfs_threshold_5070_streamcat.csv"
permfn = "E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/analysis/validation/min_cfs_threshold_5070.csv"  # for projected data
# colnames = ['FEATUREID', 'Category', 'Year', 'Month', 'disagree024']

colnames_perm = ['FEATUREID', 'Category', 'Year', 'Month', 'disagree024']  # for projected data
colnames_sc = ['FEATUREID', 'ElevCat', 'BFICat', 'BFIWs', 'CatAreaSqKm', 'WsAreaSqKm', 'WtDepCat', 'WtDepWs', 'PermCat', 'PermWs',
               'RckDepCat', 'RckDepWs', 'Precip8110Cat', 'Precip8110Ws', 'PctEolFineWs', 'PctEolCrsWs', 'PctHydricWs',
               'PctGlacLakeFineWs', 'PctGlacLakeCrsWs', 'PctGlacTilCrsWs', 'PctGlacTilLoamWs', 'PctGlacTilClayWs',
               'PctColluvSedWs', 'PctExtruVolWs', 'PctSilicicWs', 'PctAlkIntruVolWs', 'PctNonCarbResidWs',
               'PctCarbResidWs', 'HydrlCondWs']

if os.path.exists(joinfn) and os.path.isfile(joinfn):
    join_df = pd.read_csv(joinfn)
else:
    if os.path.exists(outsc) and os.path.isfile(outsc):
        sc_df = pd.read_csv(outsc)
    else:
        sc_df = pd.read_csv(scfn)  # read streamcat data (This may take a minute, 1GB file for NHD region 17)
        sc_df = sc_df[colnames_sc]  # subset to only necessary columns
        sc_df.to_csv(outsc, index=False)
    perm_df = pd.read_csv(permfn)
    perm_df = perm_df[colnames_perm]  # subset to only necessary columns
    perm_df.rename(columns={colnames_perm[-1]: 'disagree'}, inplace=True)

    join_df = perm_df.set_index(colnames_perm[0]).join(sc_df.set_index(colnames_sc[0]))
    join_df.to_csv(joinfn)
print("DONE")
