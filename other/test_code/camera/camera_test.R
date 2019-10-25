library(xcms)
library(CAMERA)
options(width = 160)
datapath <- system.file("cdf", package = "faahKO")

dir(datapath, recursive=TRUE)

rawfiles <- dir(datapath, full.names=TRUE, recursive=TRUE)
rawfiles

xset <- xcmsSet(rawfiles)
xset <- group(xset)
#
#xset2 <- retcor(xset, family = 'symmetric')
#xset2 <- group(xset2, bw = 10)
#
#xset3 <- fillPeaks(xset2)
#
print (xset@groupidx)
#
xs <- xset

pol <- 'negative'
ppm <- 20
mzabs <- 0.01
#
## Using CAMERA:
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

PksAn$pcgroup <- as.numeric(as.character(PksAn$pcgroup))
PksAn <- PksAn[order(PksAn['pcgroup']),]



for (i in 1:length(PksAn[['pcgroup']]) ) {
  print( PksAn[ i,c('rt', 'mz', 'pcgroup', 'isotopes', 'adduct')])
  }
