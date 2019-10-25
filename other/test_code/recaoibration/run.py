import os

batches = [
    [
        '/media/sf_VM_share/S_aureus_LC-MS_raw_data/QTOF/mzXML', # data path
        'sAureus_HILIC_features_QTOF_recal.dat', # output file
    ]
]

'''
Error in seq.default(object@scanindex[scan] + 1, min(object@scanindex[scan +  :
  'from' must be of length 1
Calls: getRawData ... getMSData -> getScan -> getScan -> .local -> seq -> seq.default
In addition: Warning message:
In if (scan < 0) scan <- length(object@scantime) + 1 + scan :
  the condition has length > 1 and only the first element will be used

'''

for i, batch in enumerate(batches):
    path, out = batch
    os.system('Rscript dataExtractor.R %s %s > log.dat' % (
        path, out)
    )

