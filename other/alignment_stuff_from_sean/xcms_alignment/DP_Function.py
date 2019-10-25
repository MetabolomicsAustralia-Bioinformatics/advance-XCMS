def merge_alignments(peaklist1, peaklist2, traces):

    """
    @summary: Merges two alignments with gaps added in from DP traceback
    @param A1: First alignment
    @param A2: Second alignment
    @param traces: DP traceback
    @return: A single alignment from A1 and A2
    @author: Woon Wai Keen
    @author: Vladimir Likic
    @author: Qiao Wang
    """

    # create empty lists of dimension |A1| + |A2|
    dimension = len(peaklist1) + len(peaklist2)
    merged = [ [] for _ in range(dimension) ]

    idx1 = idx2 = 0

    indices1 = [peak.get_index() for peak in peaklist1]
    indices2 = [peak.get_index() for peak in peaklist2]
    # trace can either be 0, 1, or 2
    # if it is 0, there are no gaps. otherwise, if it is 1 or 2,
    # there is a gap in A2 or A1 respectively.

    for trace in traces:

        if trace == 0:
            for i in range(len(indices1)):
                merged[i].append(indices1[i][idx1])

            for j in range(len(indices2)):
                merged[1+i+j].append(indices2[j][idx2])

            idx1 = idx1 + 1
            idx2 = idx2 + 1

        elif trace == 1:
            for i in range(len(indices1)):
                merged[i].append(indices1[i][idx1])

            for j in range(len(indices2)):
                merged[1+i+j].append(None)

            idx1 = idx1 + 1

        elif trace == 2:
            for i in range(len(indices1)):
                merged[i].append(None)

            for j in range(len(indices2)):
                merged[1+i+j].append(indices2[j][idx2])

            idx2 = idx2 + 1

    return merged
