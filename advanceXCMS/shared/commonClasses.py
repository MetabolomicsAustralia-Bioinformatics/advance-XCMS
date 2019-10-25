import numpy as np
import copy
import sys
class FeatureSet(object):
    '''
    All feature groups detected in processing
    a batch of LCMS data files through XCMS
    '''
    def __init__(self):
        self.featureDict = {}
        return

    def addXCMSPeakData(self, dataDict):

        if int(dataDict['group']) not in self.featureDict.keys():
            self.featureDict[int(dataDict['group'])] = Feature()
        self.featureDict[int(dataDict['group'])].addNewSampleData(dataDict)
        return

    def getMetaData(self):
        self.featureNums = sorted(self.featureDict.keys())
        self.numSamples = len(self.featureDict[self.featureNums[0]].samples.keys())
        for f in self.featureDict.values():
            f.getMetaData()
        # self.getGroupData()
        return

    def getFeatureByIndex(self, indices, annotatedOnly):
        counter = 0
        selectedFeatures = []

        for f in self.featureNums:
            feature = self.featureDict[f]
            if annotatedOnly:
                if feature.acceptedAssignment is not None:
                    if  counter in indices:
                        selectedFeatures.append([f, self.dataFileID])
                    counter += 1
                continue
            else:
                if counter in indices:
                    selectedFeatures.append([f, self.dataFileID])
                counter += 1
                continue
        return selectedFeatures

    def getFeatureMapAndSummaryData(self, attrs, annotatedOnly = True):
        data = []
        for f in self.featureNums:
            feature = self.featureDict[f]
            if annotatedOnly == True:
                if feature.acceptedAssignment:
                    data.append([getattr(feature, attr) for attr in attrs])
                else:
                    continue
            else:
                data.append([getattr(feature, attr) for attr in attrs])
        return zip(*data)

    def getDataForFeature(self, fn, attrs):
        f = self.featureDict[fn]
        return [getattr(f, attr) for attr in attrs]

    def addAttrToFeatures(self, attr, val):
        for f in self.featureDict.values():
            setattr(f, attr, val)
        return

    def __getitem__(self, i):
        return self.featureDict[i]

class Feature(object):
    '''
    All Data for a single peak accross
    all samples
    '''
    def __init__(self):
        self.assignments = []
        self.samples = {}
        self.eicPlot = None

        self.acceptedAssignment = None
        self.assignmentCandidates = []
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

    def addAssignmentCandidate(self, data):
        self.assignmentCandidates.append(
            AssignmentCandidate(data)
        )
        return

    def addNewSampleData(self, dataDict):
        if int(dataDict['sample']) not in self.samples.keys():
            self.samples[int(dataDict['sample'])] = Sample()
        self.samples[int(dataDict['sample'])].addNewSampleCandidate(dataDict)
        self.acceptedFeature = True #strToBool(dataDict['accepted'])

        ''' Set self.acceptedFeature to True to make all features accepted by default
        '''
        return

    def registerPlot(self, item):
        self.eicPlot = item
        return

    def getMZ(self):
        return self.avgmz
    def avgRT(self):
        return self.avgrt

    def unregisterPlot(self):
        self.eicPlot = None
        return

    def getMetaData(self):
        filled, group, rtmin, rtmax = self.getAcceptedCandidateData(
            ['filled', 'group', 'rtmin', 'rtmax']
        )

        # avg mz and rt valus calculated from direct peaks only
        mz, rt, into, maxo = self.getAcceptedCandidateDataByFilledStatus(
            ['mz','rt', 'into', 'maxo'], [0]
        )

        self.minRTMin = min(rtmin)
        self.maxRTMax = max(rtmax)

        self.maxRTMin = min(rtmax)
        self.minRTMax = max(rtmin)

        self.avgmz = sum(mz) / len(mz)
        self.avgrt = sum(rt) / len(rt)
        self.avginto = sum(into) / len(into)
        self.avgmaxo = sum(maxo) / len(maxo)

        self.featureMzAccuracy = (max(mz) - min(mz)) * 1000000 / self.avgmz
        self.featureRtAccuracy = max(rt) - min(rt)
        self.numFilled = len([x for x in filled if x == 1])
        assert len(set(group)) == 1
        self.featureNumber = group[0]
        self.sampleNums = [x.sample for x in [s.accepted for s in self.samples.values()]]
        return


    def getEICs(self):
        return
    def getMSs(self):
        return
    def getAssignments(self):
        return
    def getRT(self):
        return self.avgrt
    def getMZ(self):
        return self.avgmz

    def getAcceptedCandidateData(self, attrs):
        data = [[getattr(s.accepted, attr) for attr in attrs] for s in self.samples.values()]
        return zip(*data)

    def getAcceptedCandidateDataByFilledStatus(self, attrs, filled):
        data = []
        for attr in attrs:
            attrData = []
            for s in self.samples.values():
                if s.accepted.filled in filled:
                    attrData.append(getattr(s.accepted, attr))
            if len(attrs) == 1:
                return attrData
            else:
                data.append(attrData)
        return data

    def getSampleDataByFilledStatus(self, attrs, filled, sample = None):
        data = []
        for attr in attrs:
            attrData = []
            for s in self.samples.values():

                # used to select data from only a given sample
                if sample:
                    if s.sample != sample: continue

                for c in s.candidates:
                    if c.filled == filled:
                        attrData.append(getattr(c,attr))

            if len(attrs) == 1:
                return attrData
            else:
                data.append(attrData)
        return data


    def getAvgEICData(self):

        eicData = []

        minX = -9999999999
        maxX = 9999999999
        for s in self.samples.values():
            sa = s.accepted

            # these will bexome the new 'x-values'
            indices = np.arange(len(sa.eicRTs))

            rtPeakIndex = np.argmin(
                np.abs(sa.eicRTs - sa.rt)
            )

            xIndex = indices - rtPeakIndex
            eicData.append( [xIndex, sa.eicINTs] )

            thisMin = min(xIndex)
            thisMax = max(xIndex)

            if thisMin > minX:
                minX = thisMin
            if thisMax < maxX:
                maxX = thisMax

        yStack = []
        xStack = None
        for i in eicData:
            xs, ys = i
            mask = np.where( ( xs >= minX ) & ( xs <= maxX))

            subx = xs[mask]
            xStack = subx
            ys = np.nan_to_num(ys)
            suby = ys[mask]/np.max(ys[mask])*100
            yStack.append(suby)

        yStack = np.array(yStack)
        yMean = yStack.mean(axis = 0)

        return xStack, yMean

class Sample(object):
    '''
    Data for all peaks related to a single feature for a single
    sample

    '''
    def __init__(self):
        self.accepted = None
        self.candidates = []
        return
    def addNewSampleCandidate(self, dataDict):
        candidate = Candidate(dataDict)
        self.candidates.append(candidate)
        if candidate.filled == 0 or candidate.filled == 1:
            self.accepted = candidate
            self.sample = candidate.sample
        return
    def isAcceptedFilled(self):
        if self.accepted.filled == 1:
            return True
        else:
            return False
    def getNumRecoveryCandidates(self):
        count = 0
        for c in self.candidates:
            if c.filled == 2:
                count += 1
        return count

    def acceptSampleRecoveryCandidate(self, index):
        '''
        Need to ensure that change of recovery samples is preserved
        upon re-loading the results file after a save

        For newly accepted candidate:
            set candidate.filled to 0
            set self.ccepted to candidates

        for old accepted candidate:
            set candidate.filled to 2
        '''
        # index number is the list index of the recovery candidate
        # once all others are excluded

        recoveryCandidates = [i for i in self.candidates if i.filled == 2]

        for c in self.candidates:
            if c == self.accepted:
                c.filled = 2

        recoveryCandidates[index].filled = 0
        self.accepted = recoveryCandidates[index]
        return

    def loadPickle(self):
        return
    def dumpPickle(self):
        return

class Candidate(object):
    '''
    All possible peak candidates (direct, filled
    or recovery) from a single sample

    mz, mzmin, mzmax, rt, rtmin, rtmax,
    into, maxo, sample, group, index,
    filled, accepted, score, eicRTs,
    eicINTs, specMZs, specINTs'
    '''
    def __init__(self, dataDict):
        for k, v in dataDict.iteritems():
            setattr(self, k, v)
        self.typeData()
        return

    def typeData(self):
        self.mz = float(self.mz)
        self.rt = float(self.rt)
        self.rtmin = float(self.rtmin)
        self.rtmax = float(self.rtmax)
        self.sample = int(self.sample)
        self.group = int(self.group)
        self.score = int(self.score)
        try:
            self.into = int(float(self.into))
        except:
            self.into = 0
        self.maxo = int(float(self.maxo))
        self.eicRTs = np.array(self.getVals(self.eicRTs), dtype = 'float32')
        self.eicINTs = np.array(self.getVals(self.eicINTs), dtype = 'float32')
        self.specMZs = np.array(self.getVals(self.specMZs), dtype = 'float32')
        self.specINTs = np.array(self.getVals(self.specINTs), dtype = 'float32')
        self.filled = int(self.filled)

        ''' Default integration reset attributes
        '''
        self.originalIntO = copy.deepcopy(self.into)
        self.originalMaxO = copy.deepcopy(self.maxo)
        self.originalrtmin = copy.deepcopy(self.rtmin)
        self.originalrtmax = copy.deepcopy(self.rtmax)

        return

    def getVals(self, valArray):
        if valArray == '':
            return [0]
        else:
            try:
                return [v.strip() for v in valArray.split(' ')]
            except AttributeError:
                return valArray # used when accepting targetExplorer peaks
    def isFilled(self):
        if self.filled == 1:
            return True
        else:
            return False

class AssignmentCandidate(object):
    def __init__(self, data):
        for k,v in data.iteritems():
            setattr(self, k, v)
        return
    ''' eq and hash methods are to allow for creating sets of objects '''
    def __eq__(self, other):
        if self.name == other.name:
            return True
        else:
            return False
    def __hash__(self):
        return hash(self.name)

def strToBool(data):
    if data == 'True': return True
    if data == 'False': return False
    if data == 'None': return None
