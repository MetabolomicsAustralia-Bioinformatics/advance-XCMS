library(BiocParallel)
register(bpstart(MulticoreParam(6)))
bpparam()

args <- commandArgs(TRUE)
print (args)
datapath <- as.character(args[1])
optimisationFileName <- as.character(args[2])
outputFileName <- as.character(args[3])

print(paste('datapath is:', datapath))
print(paste('optimisationFileName is:', optimisationFileName))
print(paste('outputFileName is:', outputFileName))

library(xcms)
library(faahKO)
options(width = 160)
testing <- TRUE

start_time <- Sys.time()

# MS files should be grouped in folders below this directory.
#datapath <- '/media/sf_VM_share/singapore_batch5_pbqd'
dir(datapath, recursive=TRUE)


# datapath <- system.file("cdf", package = "faahKO")
rawfiles <- list.files(datapath, recursive = TRUE, full.names = TRUE)
rawfiles

of1 <- paste(outputFileName, sep = '')
#of1 <- paste('gp5_pbqcs.dat', sep = '')
cat('$Parameters', file = of1, append = FALSE, sep = '\n')


for (i in 1:length(rawfiles)) {
    outStr <- paste('FILELIST', i, rawfiles[i], sep = ',')
    cat(outStr, file = of1, append = TRUE, sep = '\n')
}

#of2 <- paste('optTest.dat', sep = '')
of2 <- paste(optimisationFileName, sep = '')

getOptProgress <- function(xset, iter) {
    # print ('optProgress')
    # print (xset@groupidx)
    for (group in xset@groupidx) {
        #print (group)
        peakData <- xset@peaks[group,]
        rtData <- peakData[,'rt']
        mzData <- peakData[,'mz']
        rtDiff <- max(rtData) - min(rtData)

        outStr <-  paste(
                    iter, mean(rtData), mean(mzData), rtDiff
                    )
        cat(outStr, file = of2, append = TRUE, sep = '\n')

    }
}

##########################################################################
#
#  Set some parameters
#
##########################################################################

err_ppm = 20
PeakWidth = 25
# IntThresh used for noise in centwave
IntThresh = 100
mzdiff = 0.001
SNThresh = 10

rtStart <- 60
rtEnd <- 1860

# for graphics set width of window
width <- 25


###########################################################################
#
#  Deal with all other LC/MS files
#
###########################################################################
print ('Create xset')
# Create xset -------------------------------------------------------------
#xset <- xcmsSet(rawfiles, method='centWave', ppm= err_ppm,
#                peakwidth= PeakWidth, snthresh= SNThresh,
#                prefilter= c(3,IntThresh), mzCenterFun= "mean",
#                integrate= 1, mzdiff= mzdiff, verbose.columns= FALSE,
#                fitgauss= FALSE, BPPARAM = MulticoreParam(workers = 6))

xset <- xcmsSet(rawfiles)

############################################################################
#
#  Set Grouping & Alignment Parameters
#
##############################################################################

bw = 5
minsamp = 2
mzwid = 0.015
max_pks = 100

#############################################################################
#
# Grouping Happens here
#
#############################################################################
print ('grouping')
xset <- group(
  xset, method= "density", bw= bw, minfrac= 0.2, minsamp=minsamp,
  mzwid= mzwid, max= max_pks, sleep= 0)

###########################################################################
#
#  Retention Time Alignment
#
###########################################################################
print ('alignment')
# RT alignment ------------------------------------------------------------

numIter <- 5
for (i in 1:numIter) {
	print (paste('processing RTCORR loop',i))
	max_pks2 <- max_pks * i
	xset <- retcor(xset)
	# max is different when doing multiple retcor passes
	xset <- group(xset, method= "density", bw= bw, minfrac= 0.5,
		          minsamp= minsamp, mzwid= mzwid, max=max_pks2, sleep= 0
	)
	getOptProgress(xset, i)
}


##############################################################################
#
# Retrieve missing data
#
##############################################################################
print ('rt correction')
xset3 <- fillPeaks(xset, method="chrom", BPPARAM = MulticoreParam(workers = 6))


#//////////////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////////////


#cdffiles <- list.files(filepath, recursive = TRUE, full.names = TRUE)
#print(cdffiles)

#xset <- xcmsSet(cdffiles)
#xset <- group(xset)

#xset2 <- retcor(xset, family = 'symmetric')
#xset2 <- group(xset2, bw = 10)

#xset3 <- fillPeaks(xset2)
#xset3 <- group(xset3)

groupIndices <- which(groups(xset3)[,1] > 1)

EICs <- getEIC(xset3, groupidx = groupIndices, rt = 'corrected')

allGroups <- xset3@groupidx

groupEntries <- unlist(xset3@groupidx, recursive = TRUE)



# careful
# seems that the exact cols present in the xcmsSet@Peaks array depend on the method used to generate it

# these cols present in every case according to https://rdrr.io/bioc/xcms/man/findPeaks-methods.html
# mz, mzmin, mzmax, rt, rtmin, rtmax, into, maxo


#           0    1       2     3    4       5     6     7     8     9   10  11   12     13      14     15       16        17    18  19
#headers <- '#mz, mzmin, mzmax, rt, rtmin, rtmax, into, intf, maxo, maxf, i, sn, sample, group, index, filled, accepted, score, rts, ints'

#                     1    2      3    4     5       6     7     8     9      10      11     12       13       14    15   16
standardHeaders <- '#mz, mzmin, mzmax, rt, rtmin, rtmax, into, maxo, sample, group, index, filled, accepted, score, eicRTs, eicINTs, specMZs, specINTs'

cat(standardHeaders, file = of1, append = TRUE, sep = '\n')

getMissedPeaks <- function(mz, sample, index, xset, tol = 0.1) {
    # Don't want to select other filled peaks so need to get matrix of only directly detected peaks
    firstFilled <- head(xset@filled,1)
    lastReal <- firstFilled - 1
    xReal <- xset@peaks[0:lastReal,]

    # search for alternative peaks in the same data file within mz tols
    indices <- which(xReal[,'sample'] == sample & xReal[,1] > mz - tol & xReal[,1] < mz + tol)
    return (indices)
}

getEICdataForPeak <- function(groupNumber, sampleNumber, EICs) {
    dataFrame <- as.data.frame(do.call(rbind, EICs@eic[[sampleNumber]][groupNumber]))
    rts <- paste(unlist(dataFrame['rt']), sep = '', collapse = ' ')
    ints <- paste(unlist(round(dataFrame['intensity'])), sep = '', collapse = ' ')
    eicData <- list('rts' = rts, 'ints' = ints)
    return(eicData)
}

getStandardPeakColumns <- function(xset, row) {

    # some peak edetection algos in xcms add extra columns to the xset@peaks matrix
    # don't want this to muck around with the output formatting
    # extract data from only the columns that are present in all groups

    result <- unlist(
                do.call(paste,
                        as.data.frame(
                            xset@peaks[row, c("mz", "mzmin", "mzmax", "rt", "rtmin", "rtmax", "into", "maxo")]
                            )
                        )
                    )
    return (result)
}


getGroupNumberFromName <- function(name, xset) {
    return (which(groupnames(xset) == name))
}
getGroupNameFromNumber <- function(number, xset) {
    return(groupnames(xset)[number])
}
getSampleNumberFromPeakIndex <- function(peakIndex, xset) {
    return(xset@peaks[peakIndex, 'sample'])
}
getPeakMZFromIndex <- function(peakIndex, xset) {
    return(xset@peaks[peakIndex, 1])
}

getMSData <- function(xraw, rt, mz) {

    mzH <- mz + 10
    mzL <- mz - 10

    scanTimes <- xraw@scantime
    scanIndex <- match(rt, scanTimes)
    #print (scanIndex)
    #print(scanIndex)

    result <- tryCatch (
        {
        spec <- getScan(xraw, scanIndex)
        mask <- which(spec[,'mz'] > mzL & spec[,'mz'] < mzH)
        #print(spec)
        subset <- spec[mask,]

        # NB: subset class = matrix if more than 1 entry
        # if # entries == 1, class = numeric

        if (class(subset) == 'matrix') {
            mzs <- subset[,'mz']
            ints <- subset[,'intensity']
        } else {
            mzs <- subset[1]
            ints <- subset[2]
        }
        #mzs <- paste(unlist(subset[,'mz']), sep = '', collapse = ' ')
        #ints <- paste(unlist(subset[,'intensity']), sep = '', collapse = ' ')
        msdata <- list('mz' = mzs, 'int' = ints, 'mzTarget' = mz, 'rtTarget' = rt)
        },

        error = function(cond)
        {
        msdata <- list('mz' = c(0), 'int' = c(0), 'mzTarget' = mz, 'rtTarget' = rt)
        return (msdata)
        }
    )
    return (result)
}

getRawData <- function(xset, files) {

    totalPeaks <- length(xset@peaks[,'mz'])
    allData <- vector('list', totalPeaks)

    for (filenum in 1:length(files)) {
        print (paste('processing filenum', filenum))
        # get peaks from file
        mask <- which(xset@peaks[,'sample'] == filenum)

        if (length(mask) == 0) { next }

        # get raw data for file
        xraw <- xcmsRaw(files[filenum])
        rawRTs <- xset@rt[['raw']][[filenum]]
        correctedRTs <- xset@rt[['corrected']][[filenum]]
#        if (filenum == 2) {
#        print('raw')
#        print(length(rawRTs))
#        print(rawRTs)
#        print('corrected')
#        print(length(correctedRTs))
#        print(correctedRTs)
#        }
        for (samplePeak in mask) {
            mz <- xset@peaks[samplePeak,'mz']
            # careful here, rt corrections changes the rt in xset@peaks
            # this RT is the CORRECTED value
            rtCorr <- xset@peaks[samplePeak,'rt']

            # need to get corresponding raw RT
            # seem that the number of decimal can differ b/w raw and
            # corrected RT lists for cerain rtcorr algos
            # ---> need to minimise difference

            #rtIndex <- match(rtCorr, correctedRTs)

            rtIndex <- which(abs(correctedRTs - rtCorr) == min(abs(correctedRTs - rtCorr)))
#            print(paste(rtCorr, correctedRTs[rtIndex]))
            rtRaw <- rawRTs[rtIndex]
#
#            if (filenum == 2) {
#                print (correctedRTs)
#                print (rtIndex)
#                print(paste(filenum, samplePeak, rtCorr, rtRaw))
#                q()
#            }
            peakMSData <- getMSData(xraw, rtRaw, mz)
            #print('')
            allData[samplePeak] <- list(peakMSData)
        }
    }
    return(allData)
}

#
#mask <- which(xset3@peaks[,'sample'] == 1)
#
#head (xset3@peaks[mask,],10)
#
#mask <- which(xset3@peaks[,'sample'] == 2)
#
#head (xset3@peaks[mask,],10)
#
#print('2 raw')
#print(xset3@rt[['raw']][[2]])
#print('2 corrected')
#print(xset3@rt[['corrected']][[2]])
#
print ('getting ms data')

# print (xset3@peaks)
rawData <- getRawData(xset3, rawfiles)

print ('writing results')

# each group contains the peak indices that have been aligned into a single feature
for (groupNumber in groupIndices) {

    group <- allGroups[[groupNumber]]
    groupLen <- length(group)

    # loop through all peaks in the feature group
    for (peak in group) {
        sampleNumber <- getSampleNumberFromPeakIndex(peak, xset3)
        targetMZ <- getPeakMZFromIndex(peak, xset3)

        # check if peak in filled
        filledPeak <- peak %in% xset3@filled

        if (filledPeak == TRUE) {
            filled <- 1
            #targetMZ <- xset3@peaks[peak,1]
            #sample <- xset3@peaks[peak, 'sample']
            recoveredIndices <- getMissedPeaks(targetMZ, sampleNumber, peak, xset3)
        } else {
            filled <- 0
            recoveredIndices <- NULL
        }

        # filled = 0 > directly detected peak
        # filled = 1 > filled peak
        # filled = 2 > potential direct candidate for a filled peak

        eicData <- getEICdataForPeak(groupNumber, sampleNumber, EICs)

        # write data to file, this could be a regular or filled peak
        #data <- unlist(do.call(paste, as.data.frame(xset3@peaks[peak,])))
        data <- getStandardPeakColumns(xset3, peak)
        peakMassSpec <- rawData[[peak]]

        x <- peakMassSpec[['mz']]
        #print(x)
        #print(typeof(x))
        #print(max(x))

#        if (targetMZ < min(peakMassSpec[['mz']]) | targetMZ > max(peakMassSpec[['mz']])) {
#            print('')
#            print (paste(sampleNumber, targetMZ, peakMassSpec['mzTarget']))
#            print (peakMassSpec['mz'])
#        }

        mzs <- paste(unlist(peakMassSpec[['mz']]), sep = '', collapse = ' ')
        ints <- paste(unlist(peakMassSpec[['int']]), sep = '', collapse = ' ')


#        print('')
#        print('')
        outStr <- paste(paste(data,collapse = ', ', sep = ', '), sampleNumber, groupNumber, peak, filled, 'None', 0, eicData['rts'], eicData['ints'], mzs, ints, collapse = ', ', sep = ', ')
#        outStr <- paste(paste(data,collapse = ', ', sep = ', '), sampleNumber, groupNumber, peak, filled, 0, 0, 0, 0, collapse = ', ', sep = ', ')
        cat(outStr, file = of1, append = TRUE, sep = '\n')

        # if filled, write any other candidate peaks to file as well
        if (!is.null(recoveredIndices)) {
            if ( length(recoveredIndices) > 0) {
                for (recoveredIndex in recoveredIndices) {
                    if (recoveredIndex %in% groupEntries == FALSE) {
                        # special case, need to get EICs for ungrouped peaks separately
                        # data <- unlist(do.call(paste, as.data.frame(xset3@peaks[recoveredIndex,])))
                        data <- getStandardPeakColumns(xset3, recoveredIndex)
                        outStr <- paste(paste(data, collapse = ', ', sep = ', '), sampleNumber, groupNumber, peak, 2, 'None', 0, 0, 0, mzs, ints, collapse = ', ', sep = ', ')

                        cat(outStr, file = of1, append = TRUE, sep = '\n')
                    }
                }
            }
        }
    }
}


warnings()



#
#
#of1 <- paste('peakGroup.dat', sep = '')
#
## careful
## seems that the exact cols present in the xcmsSet@Peaks array depend on the method used to generate it
#
## these cols present in every case according to https://rdrr.io/bioc/xcms/man/findPeaks-methods.html
## mz, mzmin, mzmax, rt, rtmin, rtmax, into, maxo
#
#
##           0    1       2     3    4       5     6     7     8     9   10  11   12     13      14     15       16        17    18  19
##headers <- '#mz, mzmin, mzmax, rt, rtmin, rtmax, into, intf, maxo, maxf, i, sn, sample, group, index, filled, accepted, score, rts, ints'
#
##                     1    2      3    4     5       6     7     8     9      10      11     12       13       14    15   16
#standardHeaders <- '#mz, mzmin, mzmax, rt, rtmin, rtmax, into, maxo, sample, group, index, filled, accepted, score, eicRTs, eicINTs'
#
#cat(standardHeaders, file = of1, append = FALSE, sep = '\n')
#
#getMissedPeaks <- function(mz, sample, index, xset, tol = 0.1) {
#    # Don't want to select other filled peaks so need to get matrix of only directly detected peaks
#    firstFilled <- head(xset@filled,1)
#    lastReal <- firstFilled - 1
#    xReal <- xset@peaks[0:lastReal,]
#
#    # search for alternative peaks in the same data file within mz tols
#    indices <- which(xReal[,'sample'] == sample & xReal[,1] > mz - tol & xReal[,1] < mz + tol)
#    return (indices)
#}
#
#getEICdataForPeak <- function(groupNumber, sampleNumber, EICs) {
#    dataFrame <- as.data.frame(do.call(rbind, EICs@eic[[sampleNumber]][groupNumber]))
#    rts <- paste(unlist(dataFrame['rt']), sep = '', collapse = ' ')
#    ints <- paste(unlist(round(dataFrame['intensity'])), sep = '', collapse = ' ')
#    eicData <- list('rts' = rts, 'ints' = ints)
#    return(eicData)
#}
#
#getStandardPeakColumns <- function(xset, row) {
#
#    # some peak edetection algos in xcms add extra columns to the xset@peaks matrix
#    # don't want this to muck around with the output formatting
#    # extract data from only the columns that are present in all groups
#
#    result <- unlist(
#                do.call(paste,
#                        as.data.frame(
#                            xset@peaks[row, c("mz", "mzmin", "mzmax", "rt", "rtmin", "rtmax", "into", "maxo")]
#                            )
#                        )
#                    )
#    return (result)
#}
#
#
#getGroupNumberFromName <- function(name, xset) {
#    return (which(groupnames(xset) == name))
#}
#getGroupNameFromNumber <- function(number, xset) {
#    return(groupnames(xset)[number])
#}
#getSampleNumberFromPeakIndex <- function(peakIndex, xset) {
#    return(xset@peaks[peakIndex, 'sample'])
#}
#getPeakMZFromIndex <- function(peakIndex, xset) {
#    return(xset@peaks[peakIndex, 1])
#}
#
#
## each group contains the peak indices that have been aligned into a single feature
#for (groupNumber in groupIndices) {
#
#    group <- allGroups[[groupNumber]]
#    groupLen <- length(group)
#
#    # loop through all peaks in the feature group
#    for (peak in group) {
#
#        sampleNumber <- getSampleNumberFromPeakIndex(peak, xset3)
#        targetMZ <- getPeakMZFromIndex(peak, xset3)
#
#        # check if peak in filled
#        filledPeak <- peak %in% xset3@filled
##        print(paste('filledPeak?', filledPeak))
#
#        if (filledPeak == TRUE) {
#            filled <- 1
#            #targetMZ <- xset3@peaks[peak,1]
#            #sample <- xset3@peaks[peak, 'sample']
#            recoveredIndices <- getMissedPeaks(targetMZ, sampleNumber, peak, xset3)
#        } else {
#            filled <- 0
#            recoveredIndices <- NULL
#        }
#
#        # filled = 0 > directly detected peak
#        # filled = 1 > filled peak
#        # filled = 2 > potential direct candidate for a filled peak
#
#        eicData <- getEICdataForPeak(groupNumber, sampleNumber, EICs)
#
#        # write data to file, this could be a regular or filled peak
#        #data <- unlist(do.call(paste, as.data.frame(xset3@peaks[peak,])))
#        data <- getStandardPeakColumns(xset3, peak)
#
#        outStr <- paste(paste(data,collapse = ', ', sep = ', '), sampleNumber, groupNumber, peak, filled, 0, 0, eicData['rts'], eicData['ints'], collapse = ', ', sep = ', ')
##        outStr <- paste(paste(data,collapse = ', ', sep = ', '), sampleNumber, groupNumber, peak, filled, 0, 0, 0, 0, collapse = ', ', sep = ', ')
#        cat(outStr, file = of1, append = TRUE, sep = '\n')
#
#        # if filled, write any other candidate peaks to file as well
#        if (!is.null(recoveredIndices)) {
#            if ( length(recoveredIndices) > 0) {
#                for (recoveredIndex in recoveredIndices) {
#                    if (recoveredIndex %in% groupEntries == FALSE) {
#                        # special case, need to get EICs for ungrouped peaks separately
#                        # data <- unlist(do.call(paste, as.data.frame(xset3@peaks[recoveredIndex,])))
#                        data <- getStandardPeakColumns(xset3, recoveredIndex)
#                        outStr <- paste(paste(data, collapse = ', ', sep = ', '), sampleNumber, groupNumber, peak, 2, 0, 0, 0, 0, collapse = ', ', sep = ', ')
#
#                        cat(outStr, file = of1, append = TRUE, sep = '\n')
#                    }
#                }
#            }
#        }
#    }
#}



end_time <- Sys.time()

print( end_time - start_time )
