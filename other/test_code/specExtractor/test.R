library(xcms)
library(faahKO)
cdfpath <- system.file("cdf", package = "faahKO")
cdffiles <- list.files(cdfpath, recursive = TRUE, full.names = TRUE)

xset1 <- xcmsSet(cdffiles[1:2])


head(xset1@peaks, 5)
tail(xset1@peaks, 5)

length(xset1@peaks[,'mz'])
#dxraw1<-xcmsRaw(cdffiles[1])
#
#
## get rt of desired spec
#rts <- xset1@peaks[,'rt']
#mzs <- xset1@peaks[,'mz']
#
#rt50 <- rts[50]
#mz50 <- mzs[50]
#
#mzH <- mz50 + 10
#mzL <- mz50 - 10
#
#print (paste(rt50, mz50))
#
#scanTimes <- xraw1@scantime
#scanIndex <- match(rt50, scanTimes)
#
#spec <- getScan(xraw1, scanIndex)
#
#avgSpec <- getScan(xraw1, scanIndex-3, scanIndex+3)
#
#print ('')
#spec
#
#mask <- which(spec[,'mz'] > mzL & spec[,'mz'] < mzH)
#
#mask
#
#of1 <- paste('test.dat', sep = '')
#of2 <- paste('avgtest.dat', sep = '')
#
#print ('')
#subset <- spec[mask,]
#avgsubset <- avgSpec[mask,]
#
getMSData <- function(xraw, rt, mz) {

    mzH <- mz + 10
    mzL <- mz - 10

    scanTimes <- xraw@scantime
    scanIndex <- match(rt, scanTimes)

    spec <- getScan(xraw, scanIndex)
    mask <- which(spec[,'mz'] > mzL & spec[,'mz'] < mzH)

    subset <- spec[mask,]
#    print (subset)
    mzs <- subset[,'mz']
    ints <- subset[,'intensity']
    msdata <- list('mz' = mzs, 'int' = ints)
    return (msdata)
}

getRawData <- function(xset, files) {

    totalPeaks <- length(xset@peaks[,'mz'])
    allData <- vector('list', totalPeaks)

    dataCounter <- 1

    for (filenum in 1:length(files)) {
        # get peaks from file
        mask <- which(xset@peaks[,'sample'] == filenum)

        if (length(mask) == 0) { next }

        samplePeaks <- xset@peaks[mask,]

        # get raw data for file
        xraw <- xcmsRaw(files[filenum])

        for (samplePeak in 1:length(samplePeaks[,'mz'])) {
            mz <- samplePeaks[samplePeak,'mz']
            rt <- samplePeaks[samplePeak,'rt']
            peakMSData <- getMSData(xraw, rt, mz)
            allData[dataCounter] <- list(peakMSData)
            dataCounter <- dataCounter + 1
        }
        print (paste('file', filenum, 'length of subset', length(samplePeaks[,'mz'])))
    }
    return(allData)
}

data <- getRawData(xset1, cdffiles)

for (d in seq(data)) {
    print(paste('data entry', d))
    elementData <- data[[d]]
    print(paste('mz', elementData['mz']))
    print(paste('int', elementData['int']))
    print('')
}


# warnings()
#
#
#
#for (i in 1:length(mask)) {
#
#    outStr <- paste(subset[i,] ,collapse = ', ', sep = ', ')
#    cat(outStr, file = of1, append = TRUE, sep = '\n')
#
#    outStr2 <- paste(avgsubset[i,], collapse = ', ', sep = ', ')
#    cat(outStr2, file = of2, append = TRUE, sep = '\n')
#}
#
#plotScan(xraw1, scanIndex)
