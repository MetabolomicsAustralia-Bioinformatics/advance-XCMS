import os, sys, pickle
from commonClasses import *

def strToBool(data):
    if data == 'True': return True
    if data == 'False': return False
    if data == 'None': return None

def getDataFromLine(l):
    return [d.strip('#').strip(',').strip() for d in l.split(',')]

def parseRoutputFeatureData(inFile):

    featureSet = FeatureSet()

    # if true, each feature from each sample is loaded independently
    # used for saving training data for models
    training = False
    trainingCounter = 1

    headers = None
    fileDict = {}

    with open(inFile,'r') as if1:
        for line in if1:
            if '$' in line:
                continue
            if 'FILELIST' in line:
                filenum, filepath = [l.strip(',').strip() for l in line.split(',')][1:]
                fileDict[filenum] = filepath
                continue

            if '#' in line:
                headers = getDataFromLine(line)
                continue

            data = getDataFromLine(line)

            assert len(data) == len(headers)

            dataDict = dict((headers[i],data[i]) for i in range(len(data)))
            dataDict['sampleName'] = fileDict[dataDict['sample']]

            if training:
                featureNum = trainingCounter
                trainingCounter += 1

            featureSet.addXCMSPeakData(dataDict)
    featureSet.getMetaData()

    return featureSet

if __name__ == '__main__':
    parseRoutputFeatureData('/home/mleeming/Code/maProjects/eicClassifier/eicClassifier/test_code/integrate_data_extractor_w_seans_script/peakGroupsLeishmania.dat')
