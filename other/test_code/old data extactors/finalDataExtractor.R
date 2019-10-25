
#library(multtest)
library(xcms)
library(faahKO)
options(width = 160)
testing <- TRUE

# set path according to opsys
opSys <- Sys.info()[1]
isLinux <- grepl('Linux', opSys[1])

if ( testing == TRUE ) {
    filepath <- system.file("cdf", package = "faahKO")
} else {
    if (isLinux) {
        filepath <- '/home/mleeming/Code/maProjects/eicClassifier/sample_data2'
    } else {
        filepath <- '/Users/michaelleeming/Desktop/MA/projects/eicClassifier/sample_data2'
    }
}

# filepath <- '/media/sf_VM_share/leishmania'

cdffiles <- list.files(filepath, recursive = TRUE, full.names = TRUE)[1:2]
print(cdffiles)

xset <- xcmsSet(cdffiles)
xset <- group(xset)

xset2 <- retcor(xset, family = 'symmetric')
xset2 <- group(xset2, bw = 10)

xset3 <- fillPeaks(xset2)
#xset3 <- group(xset3)

head(xset@peaks,10)
print('')
head(xset3@peaks,10)

groupIndices <- which(groups(xset3)[,1] > 1)

EICs <- getEIC(xset3, groupidx = groupIndices, rt = 'corrected')

allGroups <- xset3@groupidx

groupEntries <- unlist(xset3@groupidx, recursive = TRUE)

of1 <- paste('peakGroupsLeishmania.dat', sep = '')

# careful
# seems that the exact cols present in the xcmsSet@Peaks array depend on the method used to generate it

# these cols present in every case according to https://rdrr.io/bioc/xcms/man/findPeaks-methods.html
# mz, mzmin, mzmax, rt, rtmin, rtmax, into, maxo


#           0    1       2     3    4       5     6     7     8     9   10  11   12     13      14     15       16        17    18  19
#headers <- '#mz, mzmin, mzmax, rt, rtmin, rtmax, into, intf, maxo, maxf, i, sn, sample, group, index, filled, accepted, score, rts, ints'

#                     1    2      3    4     5       6     7     8     9      10      11     12       13       14    15   16
standardHeaders <- '#mz, mzmin, mzmax, rt, rtmin, rtmax, into, maxo, sample, group, index, filled, accepted, score, eicRTs, eicINTs, specMZs, specINTs'

cat(standardHeaders, file = of1, append = FALSE, sep = '\n')

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
    spec <- getScan(xraw, scanIndex)
    mask <- which(spec[,'mz'] > mzL & spec[,'mz'] < mzH)

    subset <- spec[mask,]

    mzs <- subset[,'mz']
    ints <- subset[,'intensity']

    #mzs <- paste(unlist(subset[,'mz']), sep = '', collapse = ' ')
    #ints <- paste(unlist(subset[,'intensity']), sep = '', collapse = ' ')
    msdata <- list('mz' = mzs, 'int' = ints, 'mzTarget' = mz, 'rtTarget' = rt)
    return (msdata)
}

getRawData <- function(xset, files) {

    totalPeaks <- length(xset@peaks[,'mz'])
    allData <- vector('list', totalPeaks)

    for (filenum in 1:length(files)) {
        # get peaks from file
        mask <- which(xset@peaks[,'sample'] == filenum)

        if (length(mask) == 0) { next }

        # get raw data for file
        xraw <- xcmsRaw(files[filenum])
        rawRTs <- xset@rt[['raw']][[filenum]]
        correctedRTs <- xset@rt[['corrected']][[filenum]]

        for (samplePeak in mask) {
            mz <- xset@peaks[samplePeak,'mz']
            # careful here, rt corrections changes the rt in xset@peaks
            # this RT is the CORRECTED value
            rtCorr <- xset@peaks[samplePeak,'rt']

            # need to get corresponding raw RT
            rtIndex <- match(rtCorr, correctedRTs)
            rtRaw <- rawRTs[rtIndex]
            peakMSData <- getMSData(xraw, rtRaw, mz)
            allData[samplePeak] <- list(peakMSData)
        }
    }
    return(allData)
}

# print (xset3@peaks)
rawData <- getRawData(xset3, cdffiles)

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

        if (targetMZ < min(peakMassSpec[['mz']]) | targetMZ > max(peakMassSpec[['mz']])) {

            print('')

            print (paste(sampleNumber, targetMZ, peakMassSpec['mzTarget']))
            print (peakMassSpec['mz'])
        }

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
                        outStr <- paste(paste(data, collapse = ', ', sep = ', '), sampleNumber, groupNumber, peak, 2, 'None', 0, 0, 0, collapse = ', ', sep = ', ')

                        cat(outStr, file = of1, append = TRUE, sep = '\n')
                    }
                }
            }
        }
    }
}
