import os
import zipfile

dirname = "E:/konrad/Projects/usgs/nhd-flow-estimates/raw_data/miller2018-monthlyRF/"
indir = os.fsencode(dirname)
os.chdir(dirname)
for file in os.listdir(indir):
    fn = os.fsdecode(file)
    if fn.endswith('.zip'):
        print(fn)
        zfile = zipfile.ZipFile(dirname + fn)
        zfile.extractall()
        print(fn, 'extracted')
        zfile.close()
    else:
        continue
