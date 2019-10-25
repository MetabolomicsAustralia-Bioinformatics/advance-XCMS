library(multtest)
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


###################################################
### code chunk number 3: PeakIdentification
###################################################
cdffiles <- list.files(filepath, recursive = TRUE, full.names = TRUE)

xset <- xcmsSet(cdffiles)

xset <- group(xset)

xset2 <- retcor(xset, family = 'symmetric')

xset2 <- group(xset2, bw = 10)

xset3 <- fillPeaks(xset2)
xset3 <- group(xset3)

rows <- length(xset3@peaks[,1])
cols <- length(xset3@peaks[1,])

alignments <- xset3@groupidx

groupEntries <- unlist(xset3@groupidx, recursive = TRUE)

of1 <- paste('peakGroup.dat', sep = '')
headers = 'mz, mzmin, mzmax, rt, rtmin, rtmax, into, intf, maxo, maxf, i, sn, sample, group, index, filled'
cat(headers, file = of1, append = FALSE, sep = '\n')

getMissedPeaks <- function(mz, sample, index, xset, tol = 0.1) {i

    # Don't want to select other filled peaks so need to get matrix of only directly detected peaks
    firstFilled <- head(xset@filled,1)
    lastReal <- firstFilled - 1
    xReal <- xset@peaks[0:lastReal,]

    # search for alternative peaks in the same data file within mz tols
    indices <- which(xReal[,'sample'] == sample & xReal[,1] > mz - tol & xReal[,1] < mz + tol)
    return (indices)
}

# each group contains the peak indices that have been aligned into a single feature
for (group in 1:length(alignments)) {

    groupLen <- length(alignments[[group]])

    # loop through all peaks in the feature group
    for (i in 1:groupLen) {
        # get index of peak - indices correspond to entries in peaks array
        index <- alignments[[group]][i]

        # check if peak in filled
        filledPeak <- index %in% xset3@filled

        if (filledPeak == TRUE) {
            filled <- 1
            targetMZ <- xset3@peaks[index,1]
            sample <- xset3@peaks[index, 'sample']
            recoveredIndices <- getMissedPeaks(targetMZ, sample, index, xset3)
        } else {
            filled <- 0
        }

        # filled = 0 > directly detected peak
        # filled = 1 > filled peak
        # filled = 2 > potential direct candidate for a filled peak

        # write data to file, this could be a regular or filled peak
        data <- unlist(do.call(paste, as.data.frame(xset3@peaks[index,])))
        outStr <- paste(paste(data,collapse = ' '), group, index, filled, collapse = ' ')
        cat(outStr, file = of1, append = TRUE, sep = '\n')

        # if filled, write any other candidate peaks to file as well
        if (exists('recoveredIndices')) {
            if ( length(recoveredIndices) > 0) {
                for (recoveredIndex in recoveredIndices) {
                    if (recoveredIndex %in% groupEntries == FALSE) {
                        print (paste('writing data for recovered index',recoveredIndex))
                        data <- unlist(do.call(paste, as.data.frame(xset3@peaks[recoveredIndex,])))
                        outStr <- paste(paste(data, collapse = ' '), group, index, 2, collapse = ' ')
                        cat(outStr, file = of1, append = TRUE, sep = '\n')
                    }
                }
            }
        }
    }
}


