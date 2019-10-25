# Load dependencies -------------------------------------------------------
library(xcms)
library(modeest)
library(CAMERA)
library(tools)

# Set working directory ---------------------------------------------------
getwd() # Show the current working directory
# Set the working directory (usually to ~/"project folder").
setwd("D:/MA/Monash/Beth McGraw/Mosquitos/Beth McGraw pilot 20160516/xcms/")
getwd()
dir()

# MS files should be grouped in folders below this directory.
datapath <- "./data/"
dir(datapath, recursive=TRUE)

# Load a "typical" MS file which can be considered a reference.
ref <- "./data/pbqc/pbqc_773-78731.mzdata.xml"

# Load all the MS files
rawfiles <- dir(datapath, full.names=TRUE,pattern="\\.mzdata*", recursive=TRUE)
rawfiles

##########################################################################
#
#  Set some parameters
#
##########################################################################

err_ppm = 20
PeakWidth = 25
# IntThresh used for noise in centwave
IntThresh = 100
mzdiff = 0.01
SNThresh = 5

rtStart <- 30
rtEnd <- 1440

# for graphics set width of window
width <- 25
###########################################################################
#
#   Deal with reference file
#
###########################################################################

# Load a reference file & define the scan range START----------------------
refRaw <- xcmsRaw(ref, profstep= 0.1, includeMSn= FALSE, mslevel= NULL, 
                  scanrange= NULL)
refRaw

scanStart <- head(which(refRaw@scantime > rtStart & refRaw@scantime < rtEnd),
                  n= 1)
scanEnd <- tail(which(refRaw@scantime > rtStart & refRaw@scantime < rtEnd),
                n= 1)
scanRange <- c(scanStart,scanEnd)

# Find Peaks in Ref -------------------------------------------------------
refRaw <- xcmsRaw(ref, profstep= 0.1, includeMSn= FALSE, mslevel= NULL,
                  scanrange= scanRange)
refRaw

refPks <- findPeaks(refRaw, method= 'centWave', ppm= err_ppm, 
                    peakwidth= PeakWidth, snthresh= SNThresh, 
                    prefilter= c(3,IntThresh), mzCenterFun= "mean",  
                    integrate= 1, mzdiff= mzdiff, verbose.columns= TRUE, 
                    fitgauss= FALSE, noise=IntThresh)
refPks

dir.create("./QC")
png("./QC/Ref_TIC.png", width = 1024, height = 768, units = "px")
plotTIC(refRaw, ident= FALSE, msident= FALSE)
dev.off()

png("./QC/Ref_EICs_100.png", width = 1024, height = 768, units = "px")
plotPeaks(refRaw, refPks,  c(10,10), width = width)
dev.off()

###########################################################################
#
#  Deal with all other LC/MS files
#
###########################################################################

# Create xset -------------------------------------------------------------
xset <- xcmsSet(rawfiles, method='centWave', ppm= err_ppm, 
                peakwidth= PeakWidth, snthresh= SNThresh, 
                prefilter= c(3,IntThresh), mzCenterFun= "mean",
                integrate= 1, mzdiff= mzdiff, verbose.columns= FALSE, 
                fitgauss= FALSE, nSlaves= 1)

xset

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


xset <- group(
  xset, method= "density", bw= bw, minfrac= 0.5, minsamp=minsamp,
  mzwid= mzwid, max= max_pks, sleep= 0)
xset

xsTable <- peakTable(xset, filebase= "./QC/xsTable", method= "medret",
                     value= "maxo")

write.table(xsTable[with(xsTable, order(rt, mz)), ], file= "./QC/grouped.tsv",
            sep= "\t", quote= FALSE, col.names= NA)


###############################################################################
#
#  Draw all .png files here: Individual EICs, Overlayed TICs etc etc
#
###############################################################################

# Plot TIC and EICs -------------------------------------------------------

getTIC <- function(file,rtcor=NULL) {
  object <- xcmsRaw(file)
  cbind(if (is.null(rtcor)) object@scantime else rtcor, 
        rawEIC(object,mzrange=range(object@env$mz))$intensity)
}

##
##  overlay TIC from all files in current folder or from xcmsSet, create pdf
##
getTICs <- function(xcmsSet=NULL,files=NULL, pdfname="TICs.pdf", 
                    rt=c("raw","corrected")) {
  if (is.null(xcmsSet)) {
    filepattern <- c("[Cc][Dd][Ff]", "[Nn][Cc]", "([Mm][Zz])?[Xx][Mm][Ll]",
                     "[Mm][Zz][Dd][Aa][Tt][Aa]", "[Mm][Zz][Mm][Ll]")
    filepattern <- paste(paste("\\.", filepattern, "$", sep = ""),
                         collapse = "|")
    if (is.null(files))
      files <- getwd()
    info <- file.info(files)
    listed <- list.files(files[info$isdir], pattern = filepattern,
                         recursive = TRUE, full.names = TRUE)
    files <- c(files[!info$isdir], listed)
  } 
  else {
    files <- filepaths(xcmsSet)
  }
  
  N <- length(files)
  TIC <- vector("list",N)
  
  for (i in 1:N) {
    cat(files[i],"\n")
    if (!is.null(xcmsSet) && rt == "corrected")
      rtcor <- xcmsSet@rt$corrected[[i]] else
        rtcor <- NULL
      TIC[[i]] <- getTIC(files[i],rtcor=rtcor)
  }
  
  pdf(pdfname,w=16,h=10)
  cols <- rainbow(N)
  lty = 1:N
  pch = 1:N
  xlim = range(sapply(TIC, function(x) range(x[,1])))
  ylim = range(sapply(TIC, function(x) range(x[,2])))
  plot(0, 0, type="n", xlim = xlim, ylim = ylim, 
       main = "Total Ion Chromatograms", xlab = "Retention Time (s)",
       ylab = "TIC")
  for (i in 1:N) {
    tic <- TIC[[i]]
    points(tic[,1], tic[,2], col = cols[i], pch = pch[i], type="l")
  }
  legend("topright",paste(basename(files)), col = cols, lty = lty, pch = pch)
  dev.off()
  
  invisible(TIC)
}
####

##
##  overlay TIC from all files in current folder or from xcmsSet, create PNG
##
getTICs <- function(xcmsSet=NULL,files=NULL, pngName="TICs.png",
                    rt=c("raw","corrected")) {
  if (is.null(xcmsSet)) {
    filepattern <- c("[Cc][Dd][Ff]", "[Nn][Cc]", "([Mm][Zz])?[Xx][Mm][Ll]",
                     "[Mm][Zz][Dd][Aa][Tt][Aa]", "[Mm][Zz][Mm][Ll]")
    filepattern <- paste(paste("\\.", filepattern, "$", sep = ""), 
                         collapse = "|")
    if (is.null(files))
      files <- getwd()
    info <- file.info(files)
    listed <- list.files(files[info$isdir], pattern = filepattern,
                         recursive = TRUE, full.names = TRUE)
    files <- c(files[!info$isdir], listed)
  } 
  else {
    files <- filepaths(xcmsSet)
  }
  
  N <- length(files)
  TIC <- vector("list",N)
  
  for (i in 1:N) {
    cat(files[i],"\n")
    if (!is.null(xcmsSet) && rt == "corrected")
      rtcor <- xcmsSet@rt$corrected[[i]] else
        rtcor <- NULL
      TIC[[i]] <- getTIC(files[i],rtcor=rtcor)
  }
  
  png(pngName,h=768, w=1024)
  cols <- rainbow(N)
  lty = 1:N
  pch = 1:N
  xlim = range(sapply(TIC, function(x) range(x[,1])))
  ylim = range(sapply(TIC, function(x) range(x[,2])))
  plot(0, 0, type="n", xlim = xlim, ylim = ylim, 
       main = "Total Ion Chromatograms", xlab = "Retention Time (s)",
       ylab = "TIC")
  for (i in 1:N) {
    tic <- TIC[[i]]
    points(tic[,1], tic[,2], col = cols[i], pch = pch[i], type="l")
  }
  legend("topright",paste(basename(files)), col = cols, lty = lty, pch = pch)
  dev.off()
  
  invisible(TIC)
}

# TICs as PNG
getTICs(xcmsSet= xset, pngName= "./QC/TICs_Raw.png", rt= "raw")

# Get EICs
xset_grps <- groups(xset)
eicsRaw <- getEIC(xset, mzrange=xset_grps, rtrange = width , 
                  groupidx = 1:nrow(xset_grps), rt= "raw")

# As individual PNGs
dir.create("./QC/EICs_Raw/")
do.call(file.remove,list(list.files("./QC/EICs_Raw", full.names= TRUE)))
png(file.path("./QC/EICs_Raw/%003d.png"), h=768, w=1024)
plot(eicsRaw, xset)
dev.off()

###########################################################################
#
#  Retention Time Alignment
#
###########################################################################

# RT alignment ------------------------------------------------------------
align_ref <- match(basename(ref),basename(rawfiles[]))
align_ref

png(filename= "./QC/xs_align.png", w=1280, h=1024)
xs_align <- retcor(xset, method= "obiwarp", center= align_ref, 
                   plottype= "deviation", profStep= 0.1, distFunc= "cor_opt", 
                   response=2, gapInit=1, gapExtend=2.4
)
dev.off()
# max is different when doing multiple retcor passes
xs_align <- group(xs_align, method= "density", bw= bw, minfrac= 0.5, 
                  minsamp= minsamp, mzwid= mzwid, max=max_pks, sleep= 0
)
xs_align

# write table
Pks_aligned <- peakTable(xs_align, filebase = "./QC/peaks_align_W_missing",
                         method = "medret", value = "maxo")

##############################################################################
#
# Retrieve missing data
#
##############################################################################
xs_filled <- fillPeaks(xs_align, method="chrom", nSlaves=1)


Pks_filled <- peakTable(xs_filled, filebase = "./QC/pks_align_no_missing",
                        method="medret", value = "maxo")

###############################################################################
#
#  Write Graphics files after alignment
#
###############################################################################


# Plot TICs
getTICs(xcmsSet= xs_filled, pngName= "./QC/TICs_Aligned.png", rt= "corrected")

# Plot EICs ---------------------------------------------------------------
xsFillmeta <- groups(xs_filled)
eicsFilled <- getEIC(xs_filled, groupidx = 1:nrow(xsFillmeta), rt= "corrected")

dir.create("./QC/EICs_Aligned/")
do.call(file.remove,list(list.files("./QC/EICs_Aligned", full.names= TRUE)))
png(file.path("./QC/EICs_Aligned/%003d.png"), h=768, w=1024)
plot(eicsFilled, xs_align)
dev.off()

###############################################################################
#
# Set CAMERA parameters
#
################################################################################

ppm <- 20
mzabs <- 0.02
pol <- "positive"

################################################################################
#
# CAMERA  - Annotate Isotopes, adducts and group related peaks
#
#################################################################################


xs <- xs_filled # Choose an xcmxSet object

# Using CAMERA:
xs_an <- xsAnnotate(xs, polarity= pol)
xs_an   <- groupFWHM(xs_an, sigma= 6, intval= "maxo")
xs_an <- findIsotopes(xs_an, maxcharge=3, maxiso=4, ppm= ppm, 
                      mzabs= mzabs, intval="maxo", minfrac=0.5,
                      filter= TRUE)
xs_an <- groupCorr(xs_an, cor_eic_th=0.75, pval=0.05,
                   graphMethod="hcs", calcIso= TRUE, calcCiS = TRUE,
                   calcCaS= TRUE, cor_exp_th=0.75)
xs_an <- findAdducts(xs_an, ppm= ppm, mzabs= mzabs, multiplier= 3,
                     polarity= pol)
PksAn <- getPeaklist(xs_an, intval="maxo")

write.table(PksAn, file=paste("./QC/Pks_An", "tsv", sep="."), sep= "\t",
            col.names= NA, row.names= TRUE)


