from Function import read_peaks, calc_score_matrix, write_matrix, align_with_trace
from DP import dp
from DP_Function import merge_alignments

if __name__=="__main__":
    
    print "reading Peaks"
    peaks1 = read_peaks('Pks_An_b3.tsv')
    peaks2 = read_peaks('Pks_An_b4.tsv')
    print "calc score matrix"
    score_matrix = calc_score_matrix(peaks1, peaks2)
    print "done"

    result = dp(score_matrix, 0.4)
    #write_matrix(result['trace'], 'trace.csv')

    #op = open('trace.csv', 'w')
    #for trace in result['trace']:
    #    op.write(str(trace) + '\n')
    #op.close()
    #print result['trace']
    #print len(result['trace'])

    align_with_trace(peaks1, peaks2, result['trace'])
