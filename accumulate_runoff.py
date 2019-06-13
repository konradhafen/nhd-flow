import numpy as np
import pandas as pd
import gispy as gis
import os
import time
from collections import defaultdict, OrderedDict


def accumulationRank(flow_df):
    """

    Args:
        flow_df: Pandas data frame from PlusFlow.dbf table

    Returns:
        flow_df with RANK column added

    """
    # determine accumulation rank
    flow_df['RANK'] = 0
    flow_df.RANK[flow_df.FROMCOMID == 0] = 1
    rank = 1
    nextcoms = [1]
    while (not all(x == 0 for x in nextcoms)) and (rank < len(flow_df)):
        nextcoms = flow_df.TOCOMID[flow_df.RANK == rank].values
        rank += 1
        flow_df.RANK[flow_df.FROMCOMID.isin(nextcoms)] = rank
    return flow_df

def upstreamCOMIDs(fcom, tcom, rank):
    """

    Args:
        fcom: FROMCOMIDs from PlusFlow table
        tcom: TOCOMIDs from PlusFlow table
        rank: RANK from flow_df

    Returns:
        rank dictionary for each comid, dictionary of upstream comids for each comid

    """
    upcoms = defaultdict(list)
    ranks = defaultdict(list)
    for i in range(0, len(flow_df), 1):
        FROMCOMID = fcom[i]
        RANK = rank[i]
        if FROMCOMID == 0:
            upcoms[tcom[i]] = []
            ranks[tcom[i]] = RANK
        else:
            upcoms[tcom[i]].append(FROMCOMID)
            ranks[tcom[i]].append(RANK)
    ranks = {k: np.max([ranks[k]]) for k in ranks}
    return ranks, upcoms

def dictSwapper(d):
    swapped = defaultdict(list)
    for k, v in d.items():
        swapped[v].append(k)
    return swapped

def accumulate(df, ranks, upcoms, outfn, year):
    colnames = ['FEATUREID']
    for i in range(1, 13):
        colnames.append('sum' + str(year) + str(i).zfill(2))
    accum_df = pd.DataFrame(columns=colnames)
    for i in colnames:
        accum_df[[i]] = df[[i]]
    colnames.remove('FEATUREID')

    count = 0
    for k, v in ranks.items():
        if k > 1:
            comids = ranks[k]
            for comid in comids:
                if comid in accum_df.FEATUREID.values:
                    to_process = upcoms[comid]
                    to_process.append(comid)
                    for month in range(1, 2):
                        row = accum_df.loc[accum_df.FEATUREID.isin(to_process), colnames]
                        rowdf = pd.DataFrame(row.sum()).transpose()
                        accum_df.loc[accum_df.FEATUREID == comid, colnames] = rowdf[colnames].values[0]

        count += 1
        #print('year', year, 'finished', count)
    accum_df.to_csv(outfn, index=False)

tStart = time.time()
catchdbf = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/Catchments/Catchment17a.dbf'
flowdbf = 'E:/konrad/Projects/usgs/prosper-nhd/data/nhd/MR/NHDPlusV21_PN_17_NHDPlusAttributes_08/NHDPlusPN/NHDPlus17/NHDPlusAttributes/PlusFlow.dbf'
catch_df = gis.vector.dbf2DF(catchdbf)
flow_df = gis.vector.dbf2DF(flowdbf)
flow_df = flow_df[flow_df.TOCOMID != 0]

runoff_dir = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/runoff/nhd17a_catchments_30m/projected5070/'
output_dir = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/runoff/nhd17a_accumulated/projected5070/'
fnend = '_mm.csv'
directory = os.fsencode(runoff_dir)

flow_df = accumulationRank(flow_df)
ranks, upcoms = upstreamCOMIDs(flow_df.FROMCOMID.values, flow_df.TOCOMID.values, flow_df.RANK.values)

ranks = dictSwapper(ranks)
ranks = OrderedDict(sorted(ranks.items()))

tSetup = time.time()
print('setup time', tSetup-tStart)

for file in os.listdir(directory):
    t0 = time.time()
    filename = os.fsdecode(file)
    if filename.endswith(fnend):
        year = int(filename.split('_')[-2].split('.')[0])
        print(year)
        outcsv = output_dir + 'accumrun_' + str(year) + '.csv'
        runoff_df = pd.read_csv(runoff_dir + filename)

        runoff_comid = runoff_df.FEATUREID
        flow_comid = flow_df.FROMCOMID[flow_df.TOCOMID.isin(runoff_comid)]
        flow_comid = flow_comid[flow_comid != 0]
        add_comid = flow_comid[~flow_comid.isin(runoff_comid)]
        temp_df = pd.DataFrame(np.zeros((len(add_comid), len(runoff_df.columns.values))),
                               columns=runoff_df.columns.values)
        temp_df.FEATUREID = add_comid.values
        runoff_df = runoff_df.append(temp_df, ignore_index=True)
        del (temp_df)

        tAcc = time.time()
        accumulate(runoff_df, ranks, upcoms, outcsv, year)
        tIter = time.time()

        print(year, 'done', 'run', tIter-t0, '', 'accumulation', tIter-tAcc, 'elapsed time', tIter-tStart)
tEnd = time.time()
print('done Total time:', tEnd-tStart)


# runoffcsv = 'E:/konrad/Projects/usgs/nhd-flow-estimates/wrk_data/WaterBalance/runoff/nhd17a_catchments_30m/catrun_1977.csv'
#
# runoff_df = pd.read_csv(runoffcsv)
#
#
# # Make sure there is an entry in the variable table for all COMIDs in FROMCOMIDs
# runoff_comid = runoff_df.FEATUREID
# flow_comid = flow_df.FROMCOMID[flow_df.TOCOMID.isin(runoff_comid)]
# flow_comid = flow_comid[flow_comid != 0]
# add_comid = flow_comid[~flow_comid.isin(runoff_comid)]
# temp_df = pd.DataFrame(np.zeros((len(add_comid), len(runoff_df.columns.values))), columns=runoff_df.columns.values)
# temp_df.FEATUREID = add_comid.values
# runoff_df = runoff_df.append(temp_df, ignore_index=True)
# del(temp_df)
#
#
# flow_df = accumulationRank(flow_df)
# ranks, upcoms = upstreamCOMIDs(flow_df.FROMCOMID.values, flow_df.TOCOMID.values, flow_df.RANK.values)
#
# ranks = dictSwapper(ranks)
# ranks = OrderedDict(sorted(ranks.items()))
#
# accumulate(runoff_df, ranks, upcoms, outcsv, year)
