import sys
from Function import read_peaks, calc_score_matrix, write_matrix, align_with_trace
from DP import dp
from DP_Function import merge_alignments

from xlsxwriter.workbook import Workbook

import numpy as np
np.set_printoptions(precision = 3)
np.set_printoptions(edgeitems=10)
np.core.arrayprint._line_width = 200

if __name__=="__main__":

    files = [
        #'batch_2.csv',
        #'batch_3.csv',
        'batch_4.csv',
        'batch_5.csv',
        #'batch_6.csv'
    ]

    ref = 0

    peakLists = []
    for f in files:
        pl = read_peaks(f)
#        pl.sort(key=lambda x: x.rt, reverse=False)
#        index = 0
#        for p in pl:
#            p.index = index
#            index += 1
        peakLists.append(pl)

    for f in range(len(files)):
        if f == ref: continue
        print 'Processing file',f

        test = peakLists[f]
        reference = peakLists[ref]

        score_matrix = calc_score_matrix(
            reference,
            test
        )

        print score_matrix

        result = dp(score_matrix, 0.3)

        print result['phi']
        print result['matches']
        print result['trace']

        align_with_trace(
            reference,
            test,
            result['trace']
        )

    # get peaks that have matches in all files
    matched = []
    for p in peakLists[ref]:
        if len(p.container) == len(files) - 1:
            matched.append(p)

    WB = Workbook('output.xlsx')
    WS = WB.add_worksheet()

    # add first columns
    col, row = 0,0
    headerLabels = ['Name','m/z','RT (s)']
    for header in headerLabels:
        WS.write(row,col,header)
        row += 1

    # write filenames to first col
    for fn in matched[0].fnames:
        WS.write(row,col,fn)
        row += 1
    for item in matched[0].container:
        for fn in item.fnames:
            WS.write(row, col, fn)
            row += 1

    # write results
    for p in matched:
        col += 1
        row = 0
        WS.write(row, col, p.metName)
        row += 1
        WS.write(row, col, p.mz)
        row += 1
        WS.write(row, col, p.rt)
        row += 1

        for intensity in p.allAreas:
            WS.write(row, col, intensity)
            row += 1
        for c in p.container:
            for intensity in c.allAreas:
                WS.write(row, col, intensity)
                row += 1

    WB.close()

