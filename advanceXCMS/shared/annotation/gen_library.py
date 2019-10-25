import argparse
from Function import read_library_peaks, read_xcms_peaks, get_adduct_peaks, \
    add_isotope,write_library, get_matches, write_matches, get_decoy_peaks, \
    rt_filter_matches, copy_annotated_pics, get_matches_consensus

help_msg = "Matches XCMS output to library"
parser = argparse.ArgumentParser(description=help_msg)
parser.add_argument('--ppm', default=5.0, help='allowed ppm error')
parser.add_argument('--seconds', default=10, help='retention time drift')
parser.add_argument('--matchfile', default='filtered_matches.csv')
parser.add_argument('--infile', default='Pks_An.tsv')


def get_real_library(peaks, polarity):
    adducts = []
    for peak in peaks:
        these_adducts = get_adduct_peaks(peak, polarity)
        for adduct in these_adducts:
            adducts.append(adduct)

    Mplus1_ions = []
    for peak in peaks:
        Mplus1_ions.append(add_isotope(peak, 1))

    Mplus2_ions = []
    for peak in peaks:
        Mplus2_ions.append(add_isotope(peak, 2))

    full_library = peaks + adducts + Mplus1_ions + Mplus2_ions

    return full_library

def get_decoy_library(peaks):
    decoy_peaks = []
    for peak in peaks:
        these_adducts = get_decoy_peaks(peak, 'neg')
        for adduct in these_adducts:
            decoy_peaks.append(adduct)
    return decoy_peaks


def doAnnotation(data, libraryFile, ppmError, rtError, polarity, dataType = 'batch'):
    #print 'running annotation'
    # read library file
    # format is: Name, mz, rt, index/groupNumber
    libPeaks = read_library_peaks(libraryFile)

    # add adducts for each library peak
    # full_library = get_real_library(libPeaks, polarity)

    # Get matches to real library and write out
    # featureSet = get_matches(full_library, featureSet, ppm=float(ppmError))

    if dataType == 'batch':
        # Get matches to real library and write out
        data = get_matches(
            libPeaks,
            data,
            ppm = float(ppmError),
            seconds = float(rtError)
        )

        useRTFiltering = False
        if useRTFiltering:
            matches = rt_filter_matches(data, seconds = float(rtError))

        # pick closest rt assignment
        for fn in data.featureNums:
            f = data[fn]
            f.getNearestRTAssignment()

    else:
        print 'Running consensus feature annotation'
        data = get_matches_consensus(
            libPeaks,
            data,
            ppm = float(ppmError),
            seconds = float(rtError)
        )
        for c in data:
            c.getNearestRTAssignment()


    return libPeaks

if __name__=="__main__":
    args = parser.parse_args()
    peaks = read_library_peaks('lib_peaks.csv')

    #############################################
    #
    # Create the real library
    #
    ############################################
    full_library = get_real_library(peaks)
    write_library(full_library, 'full_library.csv')

    # Read XCMS file
    xcms_peaks = read_xcms_peaks(args.infile)
    #print xcms_peaks[10].get_mass()

    # Get matches to real library and write out
    matches = get_matches(full_library, xcms_peaks, ppm=float(args.ppm))
    write_matches(matches, 'matches.csv')
    rt_filtered_matches = rt_filter_matches(matches, seconds = float(args.seconds))
    write_matches(rt_filtered_matches, args.matchfile)

    ################################################
    #
    # Create decoy library
    #
    ###############################################
    decoy_peaks = get_decoy_library(peaks)

    write_library(decoy_peaks, 'decoy_library.csv')
    decoy_matches = get_matches(decoy_peaks, xcms_peaks, ppm=float(args.ppm))
    write_matches(decoy_matches, 'decoy_matches.csv')

    fdr = float(len(decoy_matches))/float(len(matches))
    #print "FDR = ", fdr
    #print "num matches =", len(rt_filtered_matches)

    copy_annotated_pics(rt_filtered_matches, '/home/socall/projects/singapore2017/final/EICs_Aligned/reduced')

