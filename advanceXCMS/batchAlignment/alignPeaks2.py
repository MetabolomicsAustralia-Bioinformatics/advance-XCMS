import numpy as np
import os, sys

sys.path.append(
    os.path.join(
        os.getcwd(), '..'
    )
)

from advanceXCMS.shared.commonClasses import *

from scipy import spatial

def doCosineSimilarityScoring ( refPeak, matchFeaturesObjects):

    refX, refY = refPeak.getAvgEICData()

    minX, maxX = min(refX), max(refX)

    matchEICData = []

    for m in matchFeaturesObjects:
        mX, mY = m.getAvgEICData()
        matchEICData.append([mX,mY])
        if min(mX) > minX: minX = min(mX)
        if max(mX) < maxX: maxX = max(mX)

    refMask = np.where( (refX >= minX) & (refX <= maxX))
    subRefX = refX[refMask]
    subRefY = refY[refMask]

    results = []

    for i, m in enumerate(matchEICData):

        xs, ys = m

        mask = np.where( ( xs >= minX ) & ( xs <= maxX))

        subx = xs[mask]
        suby = ys[mask]
        try:
            coSimilary = 1 - spatial.distance.cosine(suby, subRefY)
        except:
            coSimilary = 0
            print 'Warning >>> NAN encountered in cosine similarity calculation. Adding 0 by default'

        results.append(coSimilary)

    return matchFeaturesObjects[results.index(max(results))]

def getPairs(peakLists, refBatchIndex, ppmTol, refTol):

    refBatch = peakLists[refBatchIndex]

    consensusResults = []
    cCounter = 1
    for rfn in refBatch.featureNums:
        refPeak = refBatch.featureDict[rfn]

        consensus = Consensus(cCounter)

        # add entries for ref peak
        consensus.consensusMap[refBatch.batchCounter] = [rfn]
        consensus.acceptedFeatures[refBatch.batchCounter] = refPeak

        for testBatch in peakLists:
            if testBatch.batchCounter == refBatch.batchCounter: continue

            matches = []
            matchFeaturesObjects = []

            for tfn in testBatch.featureNums:
                testPeak = testBatch.featureDict[tfn]

                if abs(refPeak.avgmz - testPeak.avgmz) / refPeak.avgmz * 1000000 < ppmTol:
                    matches.append(tfn)
                    matchFeaturesObjects.append(testPeak)

            consensus.consensusMap[testBatch.batchCounter] = matches
            if len(matches) > 0:
                #consensus.acceptedFeatures.append(testBatch.featureDict[matches[0]])


                #consensus.acceptedFeatures[testBatch.batchCounter] = testBatch.featureDict[matches[0]]

                # to cosine similarity scoring to find groupings
                consensus.acceptedFeatures[testBatch.batchCounter] = doCosineSimilarityScoring(refPeak, matchFeaturesObjects)

            else:
                consensus.acceptedFeatures[testBatch.batchCounter] = None

        cCounter += 1
        consensus.getMetaData()
        consensusResults.append(consensus)
    return consensusResults

class Consensus (object):
    def __init__(self, counter):
        self.consensusID = counter
        self.consensusMap = {} # keys = batchCounter number, values = list of featureNumbers
        self.acceptedFeatures = {} # feature objects for the accepted hits.

        self.assignmentCandidates = []
        self.acceptedAssignment = None
        return

    def areTheereBatchGaps(self):
        noneValues = []
        for k, v in self.acceptedFeatures.iteritems():
            if v == None:
                noneValues.append(k)
        return noneValues


    def getMetaData(self, doannotation = True):

        mzs = [f.avgmz for f in self.acceptedFeatures.values() if f is not None]
        rts = [f.avgrt for f in self.acceptedFeatures.values() if f is not None]
        ints = [f.avginto for f in self.acceptedFeatures.values() if f is not None]
        numFilled = [f.numFilled for f in self.acceptedFeatures.values() if f is not None]

        self.consensusintSTDEV = int(np.std(np.asarray(ints)))
        self.consensusnumfilled = sum(numFilled)
        self.consensusavgmz = sum(mzs)/len(mzs)
        self.consensusavgrt = sum(rts)/len(rts)
        self.consensusavgints = sum(ints)/len(ints)
        #if doannotation:
        #    self.getAnnotations()
        return

    def getAnnotations(self):
        assignmentCandidates = []
        acceptedAssignments = []

        for acceptedFeatureBatch in sorted(self.acceptedFeatures.keys()):
            acceptedFeature = self.acceptedFeatures[acceptedFeatureBatch]
            acceptedAssignments.append(acceptedFeature.acceptedAssignment)
            for ac in acceptedFeature.assignmentCandidates:
                assignmentCandidates.append(ac)

        self.assignmentCandidates = list(set(assignmentCandidates))
        if len(list(set(acceptedAssignments))) == 1:
            self.acceptedAssignment = acceptedAssignments[0]
        else:
            self.acceptedAssignment = None
        return

    def getRT(self):
        return self.consensusavgrt
    def getMZ(self):
        return self.consensusavgmz

    def addAssignmentCandidate(self, data):
        self.assignmentCandidates.append(
            AssignmentCandidate(data)
        )
        return

    def getNearestRTAssignment(self):
        if len(self.assignmentCandidates) == 0:
            return

        if len(self.assignmentCandidates) == 1:
            self.acceptedAssignment = self.assignmentCandidates[0]
            return

        # if > 1 candidata, minimise RT difference
        # init min to first candidate
        minRTDiff = self.assignmentCandidates[0].rtError
        minRTDiffCandidate = self.assignmentCandidates[0]
        for c in self.assignmentCandidates:
            if c.rtError < minRTDiff:
                minRTDiff = c.rtError
                minRTDiffCandidate = c
        self.acceptedAssignment = minRTDiffCandidate
        return

def getReference(peakLists):
    '''
    decide which batch to use as reference
    - for now, pick batch with most features
    '''
    numFeaturesInBatches = [len(pl.featureNums) for pl in peakLists]
    maxFeatures = max(numFeaturesInBatches)
    refBatch = numFeaturesInBatches.index(maxFeatures)
    return refBatch

def doInitialAlignment(peakLists, ppmTol, refTol):
    refBatchIndex = getReference(peakLists)
    consensus = getPairs(peakLists, refBatchIndex, ppmTol, refTol)
    return consensus




