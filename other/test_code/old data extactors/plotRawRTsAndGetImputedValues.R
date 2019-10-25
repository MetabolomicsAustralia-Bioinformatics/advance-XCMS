library(multtest)
library(xcms)
library(faahKO)

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

headers = 'mz, mzmin, mzmax, rt, rtmin, rtmax, into, intf, maxo, maxf, i, sn, sample, group, index, filled'

# cat(headers, file = of1, append = FALSE, sep = '\n')
of1 <- paste('peakGroup.dat', sep = '')

for (group in 1:length(alignments)) {

    groupLen <- length(alignments[[group]])

    for (i in 1:groupLen) {
        index <- alignments[[group]][i]
        filledPeak <- index %in% xset3@filled

        if (filledPeak == TRUE) {
            filled <- 1
            indices <- getMissedPeaks(xset3@peaks[index,1])
        } else {
            filled <- 0
        }

        data <- unlist(do.call(paste, as.data.frame(xset3@peaks[index,])))
        #print (data)
        outStr <- paste(paste(data,collapse = ' '), group, index, filled, collapse = ' ')
        cat(outStr, file = of1, append = TRUE, sep = '\n')
    }
}

getMissedPeaks <- function(mz, xset, tol = 0.1) {
    indices <- which(xset@peaks[,1] > mz - tol & xset@peaks[,1] < mz + tol)
    return (indices)
}


