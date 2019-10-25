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

xset <- xcmsSet(cdffiles[1])
xset <- group(xset)
eicraw <- getEIC(xset, rt = "raw", mzrange = matrix(c(100,300)))
