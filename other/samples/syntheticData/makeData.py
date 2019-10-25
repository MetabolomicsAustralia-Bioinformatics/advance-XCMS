import os, sys, itertools, random

'''
MSSimulator can accept a fasta file with multiple peptides specified
# rt and int of peptides can be explicitely specified
# HOWEVER, seems that the same peptide cannot be assigned two unique RTs
# Workaround:
--> create sequence isomers for the same peptide (same m/z) which can
--> then be given unique RTs
'''

# of1 = open('peptides.fasta','wt')

# Create peptide of defined length
residues = ['A','C','D','E','F','G']

numPeptides = 5
numReplicates = 5
centralRT = 1000
step = 50
outLierOffset = 100
seqCounter = 1

class Peptide (object):

    def __init__(self, sequence, rt, intensity, fileID, featureID):
        self.sequence = sequence
        self.rt = rt
        self.intensity = intensity
        self.fileID = fileID
        self.featureID = featureID
        return


def generateIsomers(residues, reps):
    peptides = []
    while len(peptides) < reps:
        newPeptide = random.sample(residues, len(residues))
        if newPeptide not in peptides:
            peptides.append(newPeptide)
    assert len(peptides) == reps
    return peptides

def writePeptide(index, rt, sequence, of1):
    of1.write('>seq %s [# intensity= %s, RT=%s #]\n' % (index, 100000, rt))
    of1.write('%s\n'%(sequence))
    return

outPeptides = []

for p in range(numPeptides):
    multiplier = p + 1
    newResidues = residues * multiplier
    isomers = generateIsomers(newResidues, numReplicates)

    groupFraction = len(isomers) - 2
    for i in range(groupFraction):
        isomer = isomers[i]
        rt = centralRT + step * i
        isomer = ''.join(isomer)

        outPeptides.append(Peptide(isomer, rt, 100000, i, p))
        #writePeptide(seqCounter, rt, isomer, of1)
        seqCounter += 1

    lowerGroupRT = centralRT - (p + 1) * outLierOffset
    upperGroupRT = centralRT + (groupFraction-1) * step + (p + 1) * outLierOffset
   # print p, lowerGroupRT
   # print p, upperGroupRT


    i1 = ''.join(isomers[3])
    i2 = ''.join(isomers[4])

    outPeptides.append(Peptide(i1, lowerGroupRT, 100000, 3, p))
    outPeptides.append(Peptide(i2, upperGroupRT, 100000, 4, p))
#
#    writePeptide(seqCounter, lowerGroupRT, i1, of1)
#    seqCounter += 1
#    writePeptide(seqCounter, upperGroupRT, i2, of1)
#

files = []

for i in range(numReplicates):
    fi = 'peptides_%s.fasta' %i
    files.append(fi)
    of1 = open(fi, 'wt')
    for p in outPeptides:
        if p.fileID == i:
            writePeptide(i*p.fileID, p.rt, p.sequence, of1)
    of1.close()

for filei in files:
    iniFile = 'dataGen.ini'
    mzml = filei.replace('.fasta','.mzML')
    os.system('MSSimulator' + ' -ini %s' %iniFile + ' -in %s' %filei + ' -out %s' % mzml)


# of1.close()

