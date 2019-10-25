import sys

from xlsxwriter.workbook import Workbook
import numpy as np
import matplotlib.pyplot as plt
np.set_printoptions(precision = 3)
np.set_printoptions(edgeitems=10)
np.core.arrayprint._line_width = 200

def read_peaks(infile):

    fp = open(infile, 'r').readlines()
    peaks = []
    index = 0
    fnames = []
    ints = []
    for i, l in enumerate(fp):
        l = l.strip().split(',')
        if i == 0:
            metNames = [str(x) for x in l[1:]]
        if i == 1:
            mzs = [float(x) for x in l[1:]]
        if i == 2:
            rts = [float(x) for x in l[1:]]
        if i > 4:
            fnames.append(str(l[0]))
            ints.append([float(x) for x in l[1:]])

    # transpose ints
    ints = map(list, zip(*ints))

    for i in range(len(mzs)):
        peak = Peak(
            i,
            mzs[i],
            rts[i],
            fnames,
            ints[i],
            metNames[i],
            infile
        )
        peaks.append(peak)

    return peaks

class Peak(object):
    def __init__(self, index, mz, rt, fname, areas, metName, dataFileName):
        self.index = index
        self.mz = mz
        self.rt = rt
        self.fnames = fname
        self.areas = areas
        self.metName = metName
        self.container = []
        self.counter = 0
        self.dataFileName = dataFileName
        return

def getPairs(ref, test):
    ppmTol = 50
    for rp in ref:
        matches = []
        for tp in test:
            if abs(rp.mz - tp.mz) / rp.mz * 1000000 < ppmTol:
                matches.append(tp)
        if len(matches) == 1:
            rp.container.append(matches[0])
        if len(matches) > 1:
            print 'Warning - ambiguous matches found'
            print matches
    return

class ConsensusGroup(object):

    def __init__(self):

        return


def main():
    files = [
        'batch_2.csv',
        'batch_3.csv',
        'batch_4.csv',
        'batch_5.csv',
        'batch_6.csv'
    ]
    ref = 0
    peakLists = []
    for f in files:
        pl = read_peaks(f)
        peakLists.append(pl)

    for f in range(len(files)):
        if f == ref: continue
        print 'Processing file',f

        test = peakLists[f]
        reference = peakLists[ref]

        getPairs(reference, test)

    # get peaks that have matches in all files
    matched = []
    for p in peakLists[ref]:
        if len(p.container) == len(files) - 1:
            matched.append(p)

    WB = Workbook('output.xlsx')
    WS = WB.add_worksheet()

    WS.set_column('A:ZZ', 15)
    # add first columns
    col, row = 0,0
    headerLabels = ['# dataFileName','# Name','# m/z','# RT (s)','#']
    for i in range(len(files)):
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

    col += 1

    # write results
    for p in matched:
        col += 1
        row = 0
        for datum in [p.dataFileName, p.metName, p.mz, p.rt, '' ]:
            WS.write(row, col, datum)
            row += 1
        for c in p.container:
            for datum in [c.dataFileName, c.metName, c.mz, c.rt, '']:
                WS.write(row, col, datum)
                row += 1

        for intensity in p.areas:
            WS.write(row, col, intensity)
            row += 1
        for c in p.container:
            for intensity in c.areas:
                WS.write(row, col, intensity)
                row += 1

    WB.close()


if __name__=="__main__":
    main()

