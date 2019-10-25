import os, sys
import numpy as np
from random import randint
import matplotlib.pyplot as plt
import pickle
from sklearn import cross_validation
from sklearn.linear_model import LogisticRegression as LR
import scipy.signal
import scipy.optimize as opt

try:
    import common
except:
    sys.path.append(os.path.join( os.path.dirname( __file__ ), '..' ))
    import common

def gauss(x, amp = 1, cent = 0, wid = 1, noise = 0, scale = 1):
    return (amp/ (np.sqrt(2*np.pi*(wid/scale)**2 )) * np.exp(-(x-(cent/scale))**2 / (2*(wid/scale)**2))) + noise

class CalculateMetrics(object):
    def __init__(self, ints):
        self.ints = ints
        self.maxInt = int(np.max(self.ints))
        self.intRange = np.max(self.ints) - np.min(self.ints)
        self.noiseLevel = int(self.getNoiseLevel())
        self.gaussSSE = self.gaussSSE()
        self.centroid = self.getCentroid()


        if self.noiseLevel == 0:
            self.noiseLevel = 1

        self.SNR = self.maxInt / self.noiseLevel
        self.localMax = self.countLocalMax()

        # self.metricsVector = np.asarray([self.maxInt, self.intRange, self.noiseLevel, self.gaussSSE, self.centroid])
        self.metricsVector = np.asarray([self.maxInt, self.SNR, self.gaussSSE, self.centroid, self.localMax])
        return

    def getNormalised(self):
        maxInt = int(np.max(self.ints))
        if maxInt == 0:
            maxInt = 1
        normalised = self.ints / maxInt

    def intensityOfThirds(self):
        normalisedInts = getNormalised()

        l = normalisedInts.shape[0]
        thirds = l // 3

        firstThird = np.sum(normalisedInts[0:thirds])
        middleThird = np.sum(normalisedInts[thirds:2*thirds])
        lastThird = np.sum(normalisedInts[2*thirds:l])
        print '%.2f, %.2f, %.2f' %(firstThird, middleThird, lastThird)
        return

    def gauss(x, amp, cent, wid, scale = 1):
        return(amp/ (np.sqrt(2*np.pi*(wid/scale)**2 )) * np.exp(-(x-(cent/scale))**2 / (2*(wid/scale)**2)))

    def smoothiSpectrum (self, p1 = 21, p2 = 5):
        return scipy.signal.savgol_filter(self.ints, p1, p2)

    def countLocalMax (self):
        sInts = self.smoothiSpectrum()

        sMax = np.max(sInts)
        localMax = 0

        width = 7

        xdata = []
        ydata = []

        for i in range(width, len(self.ints)-width):
            indexInt = sInts[i]
            before = sInts[i - width: i]
            after = sInts[i + 1 : i + 1 + width]

            # print before, after, indexInt
            lowerMask = np.where(indexInt > before)
            upperMask = np.where(indexInt > after)

            #print len(before[lowerMask]), len(after[upperMask])
            if len(before[lowerMask]) == width and len(after[upperMask]) == width:
                pc = (indexInt / sMax) * 100
                if pc > 10:
                    localMax += 1
                    xdata.append(range(i-width, i + 1 + width))
                    ydata.append(sInts[i -width: i + 1 + width])
        return localMax

    def getNoiseLevel(self):
        first = self.ints[:15]
        last = self.ints[len(self.ints)-10:]
        return (np.sum(first) + np.sum(last))/(len(first)+len(last))

    def gaussSSE(self):
        maxInt = int(np.max(self.ints))
        if maxInt == 0:
            maxInt = 1

        normalised = self.ints / maxInt

        assert len(normalised) > 30

        ll = int(len(normalised) // 2 - 15)
        hl = int(len(normalised) // 2 + 15)

        normalised = normalised[ll:hl]

        x = np.arange(30, dtype = 'float32') - 15

        y = gauss(x, wid = 3)
        y = y/np.max(y)

        assert len(normalised) == len(x)

        return np.sum((y-normalised)**2)

    def getCentroid(self):

        maxInt = int(np.max(self.ints))
        if maxInt == 0:
            maxInt = 1

        normalised = self.ints / maxInt

        #normalised = self.ints / np.max(self.ints)

        center = int(len(normalised)) // 2

        # print normalised
        weightedIntensities = 0
        weights = 0
        for i in range(len(normalised)):
            index = i - center
            if index == 0: index += 1
            weight = abs(index)
            weightedIntensities += weight * normalised[i]
            weights += weight

        #    print i, index, weightedIntensities, weights, weight, normalised[i]
        WI = weightedIntensities / weights
        return WI

def getClass(accepted):
    if accepted == True:
        return 1
    if accepted == False:
        return 0

def main():

    # read data
    allFeatures = common.parseRoutputFeatureData(sys.argv[1])

    of1 = open('metrics.dat','wt')

    for fn in allFeatures.featureNumbers:
        f = allFeatures.featureDict[fn]

        # remove unassigned features
        if f.accepted == None: continue

        for sn in range(len(f.sampleNumbers)):
            f.metrics = CalculateMetrics(f.ints[sn])

            dataClass = getClass(f.accepted)

           # print f.metrics.metricsVector
            data = ', '.join(str(_) for _ in f.metrics.metricsVector)
            of1.write('%s, %s\n'%(data, dataClass))
    of1.close()


if __name__ == '__main__':
    main()
