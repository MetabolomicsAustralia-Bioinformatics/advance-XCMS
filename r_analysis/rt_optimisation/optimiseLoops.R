library(xcms)
library(faahKO)



bw = 5
minsamp = 2
mzwid = 0.015
max_pks = 100

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


of1 <- paste('optTest.dat', sep = '')

getOptProgress <- function(xset, iter) {
    # print ('optProgress')
    # print (xset@groupidx)
    for (group in xset@groupidx) {
        #print (group)
        peakData <- xset@peaks[group,]
        rtData <- peakData[,'rt']
        mzData <- peakData[,'mz']
        rtDiff <- max(rtData) - min(rtData)
        numMissing <- numFiles - length(rtData)
        outStr <-  paste(
                    iter, mean(rtData), mean(mzData), rtDiff, numMissing
                    )
        cat(outStr, file = of1, append = TRUE, sep = '\n')

    }
}

doOpt <- function(xset, iters) {

    for (i in 1:iters) {
        xset <- retcor(xset)
	#xset <- retcor(xset, method = "loess", missing = 3)
        xset <- group(xset, method= "density", bw= bw, minfrac= 0.5,
                                      minsamp= minsamp, mzwid= mzwid, max=max_pks, sleep= 0
                                        )
        getOptProgress(xset, i)
    }
return (xset)

}


cdfpath <- system.file("cdf", package = "faahKO")
cdffiles <- list.files(cdfpath, recursive = TRUE, full.names = TRUE)

numFiles <- length(cdffiles)

xset <- xcmsSet(cdffiles)
xset <- group(xset, method= "density", bw= bw, minfrac= 0.5,
                              minsamp= minsamp, mzwid= mzwid, max=max_pks, sleep= 0
                                )

xset <- doOpt(xset, 20)



