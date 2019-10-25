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

alignments <- xset3@groupidx

gt <- groups(xset3)

print(paste('peaks array: rows',length(alignments)))
gtR <- length(gt[,1])
gtC <- length(gt[1,])
print(paste('gt array: rows', gtR, 'gtC',gtC))


print ('GT HEAD')
head(gt, 5)
print ('')
print ('GT TAIL')
tail(gt,5)
print('')
print('xsetPeaks head')
head(xset3@peaks,5)
print('')
print('xetPeaks tail')
tail(xset3@peaks,5)

