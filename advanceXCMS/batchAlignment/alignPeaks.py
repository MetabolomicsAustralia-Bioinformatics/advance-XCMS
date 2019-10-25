import sys

import numpy as np
import matplotlib.pyplot as plt
np.set_printoptions(precision = 3)
np.set_printoptions(edgeitems=10)
np.core.arrayprint._line_width = 200

class ConsensusGroup(object):
    '''
    Consensus grouping of metabolites

    entries Dictionary
    ---------------------------------------------------------
    Contains all possible matches for a given peak with x ppm
    ---------------------------------------------------------
    keys: batch id numbers
    values: lists of feature id numbers for
    potentially matching features in that group

    acceptedEntries Dictionary
    ---------------------------------------------------------
    Contains accepted feature ids only. Initially these are
    the first elements of each value list in self.entries
    ---------------------------------------------------------
    '''
    def __init__(self):
        self.entries = {}
        self.acceptedEntries = {}
        return

    def getNumMissingVals(self):
        '''
        Get number of batches that don't have a corresponding feature
        '''
        self.numMissing = 0
        for k,v in self.entries.iteritems():
            if v == []: self.numMissing += 1
        return

    def getInitialAlignmentsDIct(self):
        for k,v in self.entries.iteritems():
            if len(v) > 0:
                for i, vi in enumerate(v):
                    if i == 0:
                        vi.usedInAlignmentGoup = 1
                    else:
                        vi.usedInAlignmentGoup = 2

                self.acceptedEntries[k] = [v[0]]
            elif len(v) == 0:
                self.acceptedEntries[k] = []

        print

        print 'Initial Alignment is:'
        for k, v in self.entries.iteritems():
            for i in v:
                print k, i.avgmz, i.avgrt
        print 'accepted Alignment is:'
        for k, v in self.acceptedEntries.iteritems():
            print k, v[0].avgmz, v[0].avgrt
        return

    def getMetaData(self):
        mzs, rts, intos = [], [], []
        for k,v in self.acceptedEntries.iteritems():
            if v == []: continue
            mzs.append(v.avgmz)
            rts.append(v.avgrt)
            intos.append(v.avginto)

        self.consensusAvgMz = sum(mzs)/len(mzs)
        self.consensusAvgRt = sum(rts)/len(rts)
        self.consensusAvgInt = sum(intos)/len(intos)

        self.getAnnotations()
        return

    def getAnnotations(self):
        print '-------------- getting annotations -------------'
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

def getPairs(peakLists, refBatchIndex, ppmTol, rtTol):

    referenceBatch = peakLists[refBatchIndex]

    # assign an empty consensusGroup object to each feature in reference
    for fn in referenceBatch.featureNums:
        f = referenceBatch.featureDict[fn]
        f.consensus = ConsensusGroup()

        # add an empty list for each batch
        for peakList in peakLists:
            f.consensus.entries[peakList.batchCounter] = []

    # be careful here:
    # Features that are grouped in the test samples will not be
    # grouped in the reference files

    # actually, thi is OK

    for rfn in referenceBatch.featureNums:
        rf = referenceBatch.featureDict[rfn]
        for peakList in peakLists:
            # actually don't want this, need to incorporate the internal feature
            # details so that referencing can be performed from other batches
            # if peakLists.batchCounter == referenceBatch.batchCounter:
            #    continue

            for tfn in peakList.featureNums:
                tf = peakList.featureDict[tfn]
                if abs(rf.avgmz - tf.avgmz) / rf.avgmz * 1000000 < ppmTol:
                    rf.consensus.entries[peakList.batchCounter].append(tf)

    consensusItems = []
    for fn in referenceBatch.featureNums:
        f = referenceBatch.featureDict[fn]
        f.consensus.getInitialAlignmentsDIct()
        consensusItems.append(f.consensus)

    print
    print 'CHECK PEAKLIST ENTRIES:'
    print '-----------------------------------------------------------'
    for pl in peakLists:
        for fn in pl.featureNums:
            f = pl.featureDict[fn]

            for k,v in f.consensus.entries.iteritems():
                for i in v:
                    print k,i.avgmz, i.avgrt


    return consensusItems

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

    print '================= running alignment ================='
    refBatchIndex = getReference(peakLists)
    consensus = getPairs(peakLists, refBatchIndex, ppmTol, refTol)
    return consensus
