import os
import numpy as np
import sys
import matplotlib.pyplot as plt

def readData (files):

    data = []

    for filei in files:
        xs,ys = [],[]
        with open(filei,'r') as if1:
            for l in if1:
                l = [x.strip(',').strip() for x in l.split(',')]
                xs.append(float(l[0]))
                ys.append(float(l[1]))

        data.append(
            [np.asarray(xs), np.asarray(ys)]
        )

    return data

import copy

def alignChrom(data, ref, width, roi):

    alignedData = []

    refChrom = data[ref]
    mask = np.where((refChrom[0] > roi[0]) & (refChrom[0] < roi[1]))
    refInts = refChrom[1][mask]
    refRTs = refChrom[0][mask]

    plt.plot(refRTs, refInts)
    for i, d in enumerate(data):
        if i == 0: continue
        #if i > 5: break

        x = d[0]
        y = d[1]

        minError = None
        minErrorInts = None

        for i in range(-1*width, width + 1):
            try:
                subMask = mask[0] + i
                subY = y[subMask]
                cut = 1

                error = ((subY-refInts)**2).sum()

                if minErrorInts == None:
                    minError = error
                    minErrorInts = copy.deepcopy(subY)
                else:
                    if error < minError:
                        minError = error
                        minErrorInts = copy.deepcopy(subY)

            except Exception, e:
                pass
        try:
            #plt.plot(refRTs, y[mask])# minErrorInts)
            plt.plot(refRTs, minErrorInts)
        except:
            pass
    plt.show()


    return

wd = os.getcwd()
files = [ f for f in os.listdir(wd) if '.peak' in f ]

data = readData(files)

#print data[1]

#for i, d in enumerate(data):
#    if i == 0: continue
#    plt.plot(data[i][0],data[i][1])
#plt.show()

roi = (1150, 1275)

ref = 0
width = 20

alignChrom(data, ref, width, roi)


