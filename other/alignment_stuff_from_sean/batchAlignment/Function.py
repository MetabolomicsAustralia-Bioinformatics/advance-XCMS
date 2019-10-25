import numpy as np
from Class import Peak, Score


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
            metNames[i]
        )
        peaks.append(peak)

    return peaks

def calc_similarity(peak1, peak2, max_rt=200, max_ppm=20):
    """ use a retention time window
    and an m/z and area similarity score"""


    if abs(peak1.get_rt() - peak2.get_rt()) > max_rt:
        score = 1.0
    else:

        rt_diff = abs(peak1.get_rt() - peak2.get_rt())
        rt_score = rt_diff/max_rt
        max_mz = abs(peak1.get_mz() - peak2.get_mz())
        max_mz_ppm = 1000000*max_mz/peak1.get_mz()
        areas1 = peak1.get_areas()
        areas2 = peak2.get_areas()
        area_dotp = np.dot(areas1, areas2)
        mag_dotp = np.sqrt(areas1.dot(areas1)) * np.sqrt(areas2.dot(areas2))

        area_score = area_dotp/mag_dotp

        if max_mz_ppm < max_ppm:
            # print peak1.get_mz(), peak2.get_mz()
            #print max_mz_ppm, max_ppm
            score = 1 - ((max_ppm-max_mz_ppm)/max_ppm)*area_score*rt_score
        else:
            score = 1.0

#        if peak1.get_index() in [3,4] and score < 1:
#            print 'ind1', peak1.get_index(), 'rt1', peak1.get_rt(), 'mz1', peak1.get_mz()
#
#            print 'ind2', peak2.get_index(), 'rt2', peak2.get_rt(), 'mz2', peak2.get_mz()
#
#
#            print "max_mz =", max_mz
#            print "max_mz_ppm", max_mz_ppm
#            print "area_score", area_score
#            print "rt_score=", rt_score
#            print "score = ", score
#            print
            #if (20-max_mz)>0:
        #    print (20-max_mz), 5/area_diff, score
    #if score < 0:
    #    score = 1.0
    return score # PyMS algorithm needs minimum for max similarity

def calc_score_matrix(peaklist1, peaklist2, write_op=True):

    score = Score(len(peaklist1), len(peaklist2))

    for peak1 in peaklist1:
        for peak2 in peaklist2:
            this_score = calc_similarity(peak1, peak2)


            # print peak1.get_index(), peak2.get_index(), this_score
            score.add_score(this_score, peak1.get_index()-1, peak2.get_index()-1)

    score_matrix = score.get_score_matrix()

    if write_op == True:
        op = open('score_matrix.csv', 'w')

        shape = score_matrix.shape
        op.write(',')
        for j in range(shape[1]):
            op.write(str(j+1)+',')
        op.write('\n')

        for i in range(shape[0]):
            op.write(str(i+1) + ',')
            for j in range(shape[1]):
                op.write(str(score_matrix[i,j]) + ',')
            op.write('\n')

    return score_matrix

def align_with_trace(peaklist1, peaklist2, trace, outfile="alignment.csv"):

    op = open(outfile, 'w')
    op.write('list1,,,list2\n')
    op.write('index,mz,rt,index,rt,mz\n')

    i=0
    j=0
    k=0

    common = []

    for direction in trace:

        if i<len(peaklist1):
            mz1 = str(peaklist1[i].get_mz())
            rt1 = str(peaklist1[i].get_rt())
            index1 = str(peaklist1[i].get_index())
            areas1 = peaklist1[i].get_areas()
        else:
            mz1 = ""
            rt1 = ""
            index1 = ""

        if j<len(peaklist2):
            mz2 = str(peaklist2[j].get_mz())
            rt2 = str(peaklist2[j].get_rt())
            index2 = str(peaklist2[j].get_index())
            areas2 = peaklist2[j].get_areas()
        else:
            mz2 = ""
            rt2 = ""
            index2 = ""

        if direction == 0:
            peaklist1[i].counter += 1
            peaklist2[j].counter += 1
            peaklist1[i].container.append(peaklist2[j])

            op.write(index1 + ',' +  mz1 + ',' + rt1 + ',')
            #for area in areas1:
            #    op.write(str(area) + ',')
            op.write(index2 + ',' + mz2 + ',' + rt2 + ',')
            #for area in areas1:
            #    op.write(str(area) + ',')
            op.write('\n')
            i = i+1
            j = j+1
            k = k+1

        if direction == 1:
            op.write(index1 + ',' + mz1 + ',' + rt1 + '\n')
            i = i+1

        if direction == 2:
            op.write(',,,' + index2 + ','  + mz2 + ',' + rt2 + '\n')
            j = j+1

    print "Num Common Peaks: ", k
    op.close()



def write_matrix(matrix, outfname):
    op = open(outfname, 'w')

    shape = matrix.shape
    op.write(',')
    for j in range(shape[1]):
        op.write(str(j+1)+',')
    op.write('\n')

    for i in range(shape[0]):
        op.write(str(i+1) + ',')
        for j in range(shape[1]):
            op.write(str(matrix[i,j]) + ',')
        op.write('\n')

