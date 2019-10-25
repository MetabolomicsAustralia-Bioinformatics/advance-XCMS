import os, sys, re, time, copy

from PyQt4 import QtCore, QtGui
import pyqtgraph as pg

#import pickle
try:
    import cPickle as pickle
except:
    import pickle

import numpy as np

from advanceXCMS.gui.eicExplorerDock import Ui_DockWidget as Eed
from advanceXCMS.gui.featureMapDock import Ui_DockWidget as Fmd
from advanceXCMS.gui.peakRecoveryDock import Ui_DockWidget as Prd
from advanceXCMS.gui.filesAndFeaturesWidget2 import Ui_DockWidget as Ffw
from advanceXCMS.gui.summaryStats import Ui_DockWidget as Sst
from advanceXCMS.gui.targetedExplorerDock import Ui_TargetExplorer as Tep

from pyqtgraph.Point import Point
from pyqtgraph.graphicsItems.ItemGroup import ItemGroup
from pyqtgraph.Qt import QtGui, QtCore
from matplotlib.mlab import inside_poly
from pyqtgraph.graphicsItems import ScatterPlotItem
from xlsxwriter.workbook import Workbook

from advanceXCMS.shared import Common as common
from advanceXCMS.shared import commonClasses
from advanceXCMS.shared.annotation import gen_library as gl

from pyteomics import mzxml, auxiliary
import pymzml

try:
    import better_exceptions
    import inspect
except:
    pass


'''
Missing values in tablewidgets
Perhaps:
https://stackoverflow.com/questions/7960505/strange-qtablewidget-behavior-not-all-cells-populated-after-sorting-followed-b

May be due to a bug in pyqt when populating a table with column sorting enabled

Solution
-------------------
When updating table, set sorting to false before calling the add row methods....
Reset sorting to enabled afterwards...
'''

class EicExplorer(QtGui.QDockWidget, Eed):
    def __init__(self):
        pg.setConfigOption('background','w')
        pg.setConfigOption('foreground','k')
        QtGui.QWidget.__init__(self)
        self.widget = Eed()
        self.setupUi(self)
        return

class FeatureMap(QtGui.QDockWidget, Fmd):
    def __init__(self):
        pg.setConfigOption('background','w')
        pg.setConfigOption('foreground','k')
        QtGui.QWidget.__init__(self)
        self.widget = Fmd()
        self.setupUi(self)
        return

class PeakRecovery(QtGui.QDockWidget, Prd):
    def __init__(self):
        pg.setConfigOption('background','w')
        pg.setConfigOption('foreground','k')
        QtGui.QWidget.__init__(self)
        self.widget = Prd()
        self.setupUi(self)
        return

class SummaryStats(QtGui.QDockWidget, Sst):
    def __init__(self):
        pg.setConfigOption('background','w')
        pg.setConfigOption('foreground','k')
        QtGui.QWidget.__init__(self)
        self.widget = Sst()
        self.setupUi(self)
        return

class TargetExplorer(QtGui.QDockWidget, Tep):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.widget = Tep()
        self.setupUi(self)

        self.splitter_2.setSizes([400,100])
        return

class FilesAndFeatures(QtGui.QDockWidget, Ffw):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.widget = Ffw()
        self.setupUi(self)
        return

_DOCK_OPTS = QtGui.QMainWindow.AnimatedDocks
_DOCK_OPTS |= QtGui.QMainWindow.AllowNestedDocks
_DOCK_OPTS |= QtGui.QMainWindow.AllowTabbedDocks

class XCMSView(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('XCMSView')
        self.setTabPosition( QtCore.Qt.AllDockWidgetAreas, QtGui.QTabWidget.North )
        self.setDockOptions( _DOCK_OPTS )

        self.PRD = PeakRecovery()
        self.EED = EicExplorer()
        self.FMD = FeatureMap()
        self.SST = SummaryStats()
        self.TEP = TargetExplorer()
        self.FFW = FilesAndFeatures()

        self.dockList = [self.FMD, self.SST, self.TEP, self.PRD, self.EED]

        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.FFW)
        # self.splitDockWidget(self.FFW, self.FMD, QtCore.Qt.Vertical)

        for d in self.dockList:
            self.addDockWidget(QtCore.Qt.TopDockWidgetArea, d)

        if len(self.dockList) > 1:
            for index in range(len(self.dockList)-1):
                self.tabifyDockWidget(self.dockList[index], self.dockList[index + 1])

        self.eicExplorer = self.EED.eicExplorerLayout.addPlot()
        self.eicExplorer.vb.enableAutoRange(axis = self.eicExplorer.vb.XYAxes, enable = True)
        self.featureMap = self.FMD.featureMapLayout.addPlot(viewBox = FeatureMapViewBox())

        # min/max of largest integration
        self.PRD.iLineMaxWide = pg.InfiniteLine(angle = 90, movable = False, pen = 'b')
        self.PRD.iLineMinWide = pg.InfiniteLine(angle = 90, movable = False, pen = 'b')

        # min/max of narrowest integration
        self.PRD.iLineMaxNarrow = pg.InfiniteLine(angle = 90, movable = False, pen = 'r')
        self.PRD.iLineMinNarrow = pg.InfiniteLine(angle = 90, movable = False, pen = 'r')

        self.highlightedFeatureEICPlot = pg.PlotItem(viewBox = EICViewBox())
        self.highlightedFeatureEICPlot.addItem(self.PRD.iLineMaxWide)
        self.highlightedFeatureEICPlot.addItem(self.PRD.iLineMinWide)

        self.highlightedFeatureEICPlot.addItem(self.PRD.iLineMaxNarrow)
        self.highlightedFeatureEICPlot.addItem(self.PRD.iLineMinNarrow)

        self.highlightedFeatureEICPlot.setLimits(yMin=0)

        self.spectrumPlot = pg.PlotItem(viewBox = EICViewBox())
        self.spectrumPlot.setLimits(yMin=0)
        self.spectrumPlot.setLabel(axis = 'left', text = 'Intensity')
        self.spectrumPlot.setLabel(axis = 'bottom', text = 'm/z')
        self.msPlotText = pg.TextItem(text = '', color = 'k', anchor = (0.5,0))
        self.spectrumPlot.addItem(self.msPlotText)
        self.PRD.spectrumPlotFI.addItem(self.spectrumPlot)

        self.eicExplorer.setLabel(axis = 'left', text = 'Intensity')
        self.eicExplorer.setLabel(axis = 'bottom', text = 'm/z')

        self.massAccuracyPlot = self.SST.massAccuracyLayout.addPlot(viewBox = FeatureMapViewBox())
        self.rtAccuracyPlot = self.SST.rtDriftLayout.addPlot(viewBox = FeatureMapViewBox())
        self.PRD.eicPlotFI.addItem(self.highlightedFeatureEICPlot)

        self.massAccuracyPlot.setLabel(axis = 'left', text = 'ppm')
        self.massAccuracyPlot.setLabel(axis = 'bottom', text = 'm/z')

        self.rtAccuracyPlot.setLabel(axis = 'left', text = 'RT range (s)')
        self.rtAccuracyPlot.setLabel(axis = 'bottom', text = 'RT (s)')

        self.featureMap.setLabel(axis = 'left', text = 'RT (s)')
        self.featureMap.setLabel(axis = 'bottom', text = 'Feature')

        self.highlightedFeatureEICPlot.setLabel(axis = 'bottom', text = 'RT (sec)')
        self.highlightedFeatureEICPlot.setLabel(axis = 'left', text = 'Intensity')

        # linear region for feature inspector EIC pane
        self.linReg = pg.LinearRegionItem()
        self.highlightedFeatureEICPlot.addItem(self.linReg)

        self.TEPplot = pg.PlotItem(viewBox = EICViewBox())
        self.TEPplot.setLabel(axis = 'left', text = 'Intensity')
        self.TEPplot.setLabel(axis = 'bottom', text = 'Retention Time (s)')
        self.TEP.eicPlot.addItem(self.TEPplot)

        # add iLine to EIC
        self.TEP.iLine = pg.InfiniteLine(angle = 90, movable = True, pen = 'b')
        self.TEP.linReg = pg.LinearRegionItem()

        self.TEP.mzTolEntry.setText('0.03')
        self.TEP.rtDisplayEntry.setText('100')

        self.TEPactiveSamples = []
        self.TEPmsActive = False
        self.outputfile = None

        ''' set resize models for table contents '''
        # https://stackoverflow.com/questions/38098763/pyside-pyqt-how-to-make-set-qtablewidget-column-width-as-proportion-of-the-a
        featureTableHeaders = self.FFW.xcmsFeatures.horizontalHeader()
        featureTableHeaders.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        featureTableHeaders.setResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        featureTableHeaders.setResizeMode(2, QtGui.QHeaderView.Stretch)
        featureTableHeaders.setResizeMode(3, QtGui.QHeaderView.Stretch)
        featureTableHeaders.setResizeMode(4, QtGui.QHeaderView.Stretch)

        fileTableHeaders = self.FFW.openDataFilesTable.horizontalHeader()
        fileTableHeaders.setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        fileTableHeaders.setResizeMode(1, QtGui.QHeaderView.Stretch)

        tables = [
            [ self.PRD.assignmentCandidateTable, [] ],
            [ self.TEP.standardTable, [0,2,3,4,5,6] ],
            [ self.PRD.filledPeaksTable, [] ],
            [ self.TEP.refStandardsTable, [0, 2, 3] ],
            [ self.TEP.samplesTable, [0] ]
        ]

        for t in tables:
            self.setTableHeaderPolicy(t[0], t[1])

        ''' enable sorting '''
        self.FFW.xcmsFeatures.setSortingEnabled(True)
        self.PRD.filledPeaksTable.setSortingEnabled(True)
        self.TEP.standardTable.setSortingEnabled(True)

        ''' set selection models '''
        self.FFW.xcmsFeatures.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.FFW.openDataFilesTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.PRD.filledPeaksTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.PRD.assignmentCandidateTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.TEP.standardTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.TEP.refStandardsTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.TEP.samplesTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        ''' containers and variables '''
        self.allDataFiles = []
        self.featureSetsList = []
        self.dataFileIdCounter = 1
        self.activeFeatures = []
        self.eicExplorerPlots = []
        self.numTraces = 0
        self.standards = []

        ''' colors and symbols for plot '''

        self.colorSet = [
            (17, 49, 99),
            (99, 17, 94),
            (209, 180, 39),
            (0,0,0),
            (28, 135, 96)
        ]

        #self.colorSet = ['b', 'm', 'y', 'k', 'c'] # k = black
        self.symbolSet = ['o', 't', 's', 'd', 'p']

        ''' QColors for feature table backgrounds '''
        self.green = QtGui.QColor(200,255,200)
        self.red = QtGui.QColor(255,200,200)
        self.white = QtGui.QColor(255,255,255)
        self.black = QtGui.QColor(0,0,0)
        self.orange = QtGui.QColor(255, 225, 200)
        self.plotGreen = QtGui.QColor(12,127,50)

        ''' set up feature map plot '''
        self.FMD.featureMapLayout.clear()
        self.featureMap = self.FMD.featureMapLayout.addPlot(viewBox = FeatureMapViewBox())

        ''' gui connections '''
        self.createConnections()

        self.libraryFile = None

        screenShape = QtGui.QDesktopWidget().screenGeometry()
        self.resize(screenShape.width()*0.8, screenShape.height()*0.8)
        #self.PRD.widget.setMinimumSize(screenShape.width()*0.55,0)
        self.redrawEICPlotLayout()

        #self.loadData(inFile = '/home/mleeming/Code/TestCode/test_data/s_pneumo_subset/sPneumo_HILIC_features_QTOF_SN_2_7-2-18.dat')
        #self.selectLibraryFile()
        #self.annotatePeaks()
        return

    def setTableHeaderPolicy(self, table, restrict):
        tableHeader = table.horizontalHeader()
        cc = table.columnCount()
        for c in range(cc):
            if c in restrict:
                mode = QtGui.QHeaderView.ResizeToContents
            else:
                mode = QtGui.QHeaderView.Stretch
            tableHeader.setResizeMode(c, mode)

        table.verticalHeader().setVisible(False)
        return

    def createConnections(self):
        self.FFW.loadResults.clicked.connect(self.loadData)

        self.FFW.allFeaturesRB.toggled.connect(lambda: self.radiobuttonToggled(self.FFW.allFeaturesRB))
        self.FFW.acceptedFeaturesRB.toggled.connect(lambda: self.radiobuttonToggled(self.FFW.acceptedFeaturesRB))
        self.FFW.rejectedFeaturesRB.toggled.connect(lambda: self.radiobuttonToggled(self.FFW.rejectedFeaturesRB))
        self.FFW.unassignedFeaturesRB.toggled.connect(lambda: self.radiobuttonToggled(self.FFW.unassignedFeaturesRB))

        self.FFW.limitToAnnotatedCB.toggled.connect(self.limitToAnnotated)

        self.EED.prevButton.clicked.connect(lambda: self.getNextBatch('prev'))
        self.EED.nextButton.clicked.connect(lambda: self.getNextBatch('next'))

        self.PRD.filledOnlyCB.toggled.connect(self.updatePeakRecovery)

        self.FFW.xcmsFeatures.itemSelectionChanged.connect(self.updateSelection)

        self.PRD.filledPeaksTable.itemSelectionChanged.connect(self.updateFilledPeakCandidateTable)
        self.EED.eicExplorerLayout.scene().sigMouseClicked.connect(self.onClick)

        self.featureMap.vb.mapSelectionChanged.connect(
            lambda data, pointIndices: self.featurePointHighlighted(
                data, pointIndices, callBack = self.highlightPointsInRectangle
            )
        )

        self.FFW.selectLibFile.clicked.connect(self.selectLibraryFile)
        self.FFW.annotateFromLib.clicked.connect(self.annotatePeaks)

        self.massAccuracyPlot.vb.mapSelectionChanged.connect(
            lambda data, pointIndices: self.featurePointHighlighted(
                data, pointIndices, callBack = self.highlightPointsInRectangle
            )
        )

        self.rtAccuracyPlot.vb.mapSelectionChanged.connect(
            lambda data, pointIndices: self.featurePointHighlighted(
                data, pointIndices, callBack = self.highlightPointsInRectangle
            )
        )

        self.FFW.saveResults.clicked.connect(self.writeResultsFile)

        self.EED.numCols.valueChanged.connect(self.redrawEICPlotLayout)
        self.EED.numRows.valueChanged.connect(self.redrawEICPlotLayout)
        self.PRD.acceptAssignment.clicked.connect(self.acceptSelectedAssignmentCandidate)
        # self.PRD.recoverSelected.clicked.connect(self.acceptRecoveryCandidate)
        # self.PRD.autoRecovery.clicked.connect(self.doAutoRecovery)
        self.PRD.setIntegrationBoundaries.clicked.connect(self.doManualIntegration)
        self.PRD.selectedSampleOnly.toggled.connect(self.showSelectedEICOnly)
        self.PRD.clearAssignment.clicked.connect(self.clearAcceptedAssignment)
        self.PRD.restoreDefaultIntegrationButton.clicked.connect(self.restoreDefaultIntegration)
       # self.TEP.searchMissingButton.clicked.connect(self.searchMissingEICs)


        # target explorer connections
        self.TEP.extractEICsButton.clicked.connect(self.TEPextractEICs)
        self.TEP.iLine.sigDragged.connect(self.updateTEPMS)
        self.TEP.iLine.sigPositionChangeFinished.connect(self.updateTEPMS)

        self.TEP.refStandardsTable.itemSelectionChanged.connect(self.updateTEPPlot)
        self.TEP.selectedOnlyCB.toggled.connect(self.updateTEPPlot)
        self.TEP.samplesTable.itemSelectionChanged.connect(self.getSelectedTEPSamples)
        self.TEP.showIntegrationCB.toggled.connect(self.addRemoveTEPIntegration)
        self.TEP.showSpectrumCB.toggled.connect(self.addRemoveTEPMS)

#        self.TEP.refStandardsTable.itemSelectionChanged.connect(self.TEPselectionChanged)
#        self.TEP.samplesTable.itemSelectionChanged.connect(self.TEPselectionChanged)

        self.TEP.integrateRegionButton.clicked.connect(self.integrateTEPRegion)
        self.TEP.clearIntegrationButton.clicked.connect(self.clearTEPIntegration)
        self.TEP.acceptPeakButton.clicked.connect(self.acceptTEPPeak)

        self.FFW.outputFileBrowseButton.clicked.connect(self.outputFileBrowse)
        return

    def integrateTEPRegion(self):

        low, high = self.TEP.linReg.getRegion()

        def getBaseLineSubtract(m, b, x):
            return m*x + b

        highlightedRow = int(str(self.TEP.refStandardsTable.selectionModel().selectedRows()[0].row()))

        # careful, row indices no longer correlate with order of standards list once table is sorted by user
        standardIndex = int(self.TEP.refStandardsTable.item(highlightedRow,0).text())
        standard = self.standards[standardIndex]

        for k, v in standard.eicTraces.iteritems():
            rts = v.rts
            ints = v.ints

            if k in self.TEPactiveSamples:

                mask = np.where(
                    (rts > low) & (rts < high)
                )

                eicRTsub = rts[mask]
                eicINTsub = ints[mask]

                lowRT, highRT = eicRTsub[0], eicRTsub[-1]
                lowInt, highInt = eicINTsub[0], eicINTsub[-1]

                m = (highInt - lowInt) / (highRT - lowRT)
                b = lowInt - m*lowRT

                newArea = 0
                for p in range(eicRTsub.shape[0]):
                    rt, intensity = eicRTsub[p], eicINTsub[p]
                    base = getBaseLineSubtract(m,b,rt)
                    new = intensity - base
                    newArea += new

                if newArea < 0:
                    newArea = 0

                v.into = int(newArea)
                v.rtmin = low
                v.rtmax = high

        self.updateTEPPlot()
        return

    def clearTEPIntegration(self):
        highlightedRow = int(str(self.TEP.refStandardsTable.selectionModel().selectedRows()[0].row()))

        # careful, row indices no longer correlate with order of standards list once table is sorted by user
        standardIndex = int(self.TEP.refStandardsTable.item(highlightedRow,0).text())
        standard = self.standards[standardIndex]

        for k, v in standard.eicTraces.iteritems():
            rts = v.rts
            ints = v.ints
            if k in self.TEPactiveSamples:
                v.into = None
                v.rtmin = None
                v.rtmax = None

        self.updateTEPPlot()
        return

    def acceptTEPPeak(self):

        highlightedRow = int(str(self.TEP.refStandardsTable.selectionModel().selectedRows()[0].row()))

        # careful, row indices no longer correlate with order of standards list once table is sorted by user
        standardIndex = int(self.TEP.refStandardsTable.item(highlightedRow,0).text())
        standard = self.standards[standardIndex]

        assert len(self.featureSetsList) < 2

        featureSet = self.featureSetsList[0]

        groupID = max(featureSet.featureNums) + 1 # feature ID
        print 'num groups before; ', len(featureSet.featureNums)
        for i, df in enumerate(self.MSdataFiles):
            v = standard.eicTraces[df.name]
            # need to make one data item per sample
            print groupID, df.sampleID
            # check integration has been done
            if not hasattr(v, 'rtmax'):
                print 'Need to integrate peak first'
                return
            dataDict = {
            'sample' : df.sampleID,
            'group' : groupID,
            'sampleName' : df.absName,
            'score' : 0,
            'index' : 0,

            'rt' : sum([v.rtmax, v.rtmin])/2,
            'rtmax' : v.rtmax,
            'rtmin' : v.rtmin,

            'into' : v.into,
            'maxo' : 0,

            'mz' : standard.mz,
            'mzmin' : standard.mz,
            'mzmax' : standard.mz,

            'eicRTs' : v.rts,
            'eicINTs' : v.ints,

            'specMZs' : [0],
            'specINTs' : [0],

            'filled' : 0,
            'accepted' : 1,
            }
            featureSet.addXCMSPeakData(dataDict)
        featureSet.getMetaData()

        dfID = None
        for fn in featureSet.featureNums:
            f = featureSet[fn]
            try:
                dfID = f.dataFileID
                break
            except:
                pass

        # set up assignment Candidate and add to newly created feature
        data = {
            'name': standard.name,
            'mz': standard.mz,
            'massError': 0,
            'rt': dataDict['rt'],
            'rtError': 0
            }
        featureSet[groupID].addAssignmentCandidate(data)
        featureSet[groupID].getNearestRTAssignment()

        featureSet.addAttrToFeatures('dataFileID', dfID)
        featureSet[groupID].acceptedFeature = True
        self.rewriteFeatureTable()

        highlightedRow = int(str(self.TEP.refStandardsTable.selectionModel().selectedRows()[0].row()))
        self.TEP.refStandardsTable.itemSelectionChanged.disconnect()
        self.fillStandardsTable()
        self.TEP.refStandardsTable.selectRow(highlightedRow)
        self.TEP.refStandardsTable.itemSelectionChanged.connect(self.updateTEPPlot)
        return

    def TEPextractEICs(self):
        mztol = float(str(self.TEP.mzTolEntry.text()))
        for s in self.standards:
            s.ll = s.mz - mztol
            s.hl = s.mz + mztol
            s.eicTraces = {}
            for f in self.MSdataFiles:
                s.eicTraces[f.name] = EICTrace()

        for f in self.MSdataFiles:
            print 'extracting eic for', f.name
            name = f.name

            f.scanTimes = []
            f.scanIndices = []

            if '.mzml' in f.absName.lower():
                spectra = readMzML(f.absName)
            elif '.mzxml' in f.absName.lower():
                spectra = readMzXML(f.absName)
            else:
                print 'Unrecognised file type'
                return

            for spec in spectra:
                time, mzs, ints, lvl, n = spec
                f.scanTimes.append(time)
                f.scanIndices.append(n)
                for s in self.standards:
                    # add time value
                    s.eicTraces[name].rts.append(time)

                    eicInt = 0
                    mzsubset = np.where((mzs > s.ll) & (mzs < s.hl))
                    if mzsubset[0].shape[0] > 0: eicInt += np.sum(ints[mzsubset])
                    s.eicTraces[name].ints.append(eicInt)

            f.scanTimes = np.asarray(f.scanTimes)
            f.scanIndices = np.asarray(f.scanIndices)

        for s in self.standards:
            for k, v in s.eicTraces.iteritems():
                v.rts = np.asarray(v.rts)
                v.ints = np.asarray(v.ints)

        self.TEP.refStandardsTable.selectRow(0)
        return

    def updateTEPPlot(self):

        highlightedRow = int(str(self.TEP.refStandardsTable.selectionModel().selectedRows()[0].row()))

        # careful, row indices no longer correlate with order of standards list once table is sorted by user
        standardIndex = int(self.TEP.refStandardsTable.item(highlightedRow,0).text())
        standard = self.standards[standardIndex]

        if len(self.TEPplot.listDataItems()) == len(self.MSdataFiles):
            pass
        else:
            self.TEPplot.clear()
            for d in self.MSdataFiles:
                self.TEPplot.plot()

        selectedOnly = self.TEP.selectedOnlyCB.isChecked()

        counter = 0
        globalmax = 0
        dataItems = self.TEPplot.listDataItems()
        try:
            for k, v in standard.eicTraces.iteritems():
                rts = v.rts
                ints = v.ints
                if k in self.TEPactiveSamples:
                    pen = 'r'
                else:
                    pen = 'k'
                if selectedOnly and k not in self.TEPactiveSamples:
                    rts, ints = [],[]
                else:
                    try:
                        rangemax = np.max(ints[np.where((rts > standard.rt - 100) & (rts < standard.rt + 100))])
                        if rangemax > globalmax:
                            globalmax = rangemax
                    except:
                        #print ints
                        pass
                dataItems[counter].setData(rts, ints, pen = pen)
                counter += 1
        except AttributeError:
            print 'Extract EICs first'
            return
        if self.TEP.showSpectrumCB.isChecked():
            self.TEP.iLine.setValue(standard.rt)

        rtTol = int(self.TEP.rtDisplayEntry.text())
        self.TEPplot.setXRange(standard.rt - rtTol, standard.rt + rtTol)
        self.TEPplot.setYRange(0, globalmax)
        self.updateTEPLinReg()
        self.updateTEPSampleTable()
        return

    def updateTEPSampleTable(self):

        self.TEP.samplesTable.itemSelectionChanged.disconnect()

        highlightedRow = int(str(self.TEP.refStandardsTable.selectionModel().selectedRows()[0].row()))

        # careful, row indices no longer correlate with order of standards list once table is sorted by user
        standardIndex = int(self.TEP.refStandardsTable.item(highlightedRow,0).text())
        standard = self.standards[standardIndex]

        table = self.TEP.samplesTable
        self.clearTable(table)
        for i, df in enumerate(self.MSdataFiles):
            eic = standard.eicTraces[df.name]
            rc = table.rowCount()

            if eic.into:
                intensity = eic.into
            else:
                intensity = '-'
            table.insertRow(rc)
            table.setItem(rc, 0, self.addData(i))
            table.setItem(rc, 1, self.addData(df.name))
            table.setItem(rc, 2, self.addData(intensity))

        self.TEP.samplesTable.itemSelectionChanged.connect(self.getSelectedTEPSamples)
        #self.TEP.samplesTable.itemSelectionChanged.connect(self.TEPselectionChanged)
#        self.TEP.samplesTable.selectRow(0)
        return

    def getSelectedTEPSamples(self):
        highlightedRows = self.TEP.samplesTable.selectionModel().selectedRows()
        self.TEPactiveSamples = []
        for row in highlightedRows:
            highlightedRow = row.row()
            self.TEPactiveSamples.append( str(self.TEP.samplesTable.item(highlightedRow, 1).text()) )
        self.updateTEPPlot()
        return

    def TEPselectionChanged(self):
        self.getSelectedTEPSamples()
        self.updateTEPPlot()
        return

    def updateTEPMS(self):
        selectedSample = self.TEPactiveSamples[0]
        activeFile = None

        for f in self.MSdataFiles:
            if f.name == selectedSample:
                activeFile = f

        activeFile = self.MSdataFiles[0]

        iLineVal = float(self.TEP.iLine.value())
        scanNumber = np.argmin(np.absolute(activeFile.scanTimes - iLineVal))
        specIndex = activeFile.scanIndices[scanNumber]

        spec = activeFile.spec[specIndex]

        mz, i = self.zeroFill(np.array(spec.mz), np.array(spec.i))
        self.TEPMSDataItem.setData(x = mz, y = i)
        return

    def addRemoveTEPMS(self):
        showMS = self.TEP.showSpectrumCB.isChecked()
        if not showMS:
            self.TEP.eicPlot.removeItem(self.TEPMS)
            self.TEPplot.removeItem(self.TEP.iLine)
            self.TEPmsActive = False
        else:
            self.TEPMS = self.TEP.eicPlot.addPlot(row = 1, col = 0, viewBox = EICViewBox())
            # self.MS = self.eicPlot.addPlot(row = 1, col = 0)
            self.TEPMS.setLabel(axis = 'left', text = 'Intensity')
            self.TEPMS.setLabel(axis = 'bottom', text = 'm/z')
            self.TEPMSDataItem = self.TEPMS.plot(x = [], y = [], pen = 'k')
            self.TEPplot.addItem(self.TEP.iLine)
            self.TEPmsActive = True
            try:
                self.TEPactiveSamples = self.TEPactiveSamples[0]
                self.updateTEPPlot()
            except IndexError:
                pass
        return

    def addRemoveTEPIntegration(self):
        showInt = self.TEP.showIntegrationCB.isChecked()
        if not showInt:
            self.TEPplot.removeItem(self.TEP.linReg)
        else:
            self.TEPplot.addItem(self.TEP.linReg)
            self.updateTEPLinReg()
        return

    def updateTEPLinReg(self):
        highlightedRow = int(str(self.TEP.refStandardsTable.selectionModel().selectedRows()[0].row()))

        # careful, row indices no longer correlate with order of standards list once table is sorted by user
        standardIndex = int(self.TEP.refStandardsTable.item(highlightedRow,0).text())
        standard = self.standards[standardIndex]

        self.TEP.linReg.setRegion([standard.rt-20, standard.rt+20])
        return

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self,
                                           'Confirm',
                                           'Are you sure you want to quit?\nUnsaved changes will be lost.',
                                            QtGui.QMessageBox.Yes,
                                            QtGui.QMessageBox.No
                                           )
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
        return

    def limitToAnnotated(self):
        self.rewriteFeatureTable()
        self.drawFeatureMap()
        return

    def outputFileBrowse(self):
        self.outputfile = str(QtGui.QFileDialog.getSaveFileName(self, 'Write Results File', selectedFilter='*.xvf'))
        # self.FFW.outputFileNameField.setText(self.outputfile)
        return

    def writeResultsFile(self):
        try:
            highlightedRow = self.FFW.openDataFilesTable.selectionModel().selectedRows()[0].row()
            dataFileID = int(str(self.FFW.openDataFilesTable.item(highlightedRow, 0).text()))
        except IndexError:
            print 'No results file selected'
            return

        if not self.outputfile:
            return

        fileName = self.outputfile

        if '.xlsx' not in fileName:
            fileName += '.xlsx'

        #fileName = "TEST.xlsx"
        WB = Workbook(fileName)
        WS = WB.add_worksheet()

        featureSet= None
        for featureSeti in self.featureSetsList:
            if featureSeti.dataFileID == dataFileID:
                featureSet = featureSeti
                break

        if featureSet == None:
            print 'No feature set'
            return

        if self.FFW.writePickleFileCB.isChecked():
            # save pickled object
            pickle.dump([self.standards, featureSet], open( fileName.replace('.xlsx', '') + '.pickle', "wb" ) )

        # add first columns
        col, row = 0,0
        headerLabels = ['Name','m/z','RT (s)', 'ppm Error', 'RT Error (s)']
        for header in headerLabels:
            WS.write(row,col,header)
            row += 1

        f = featureSet.featureDict[1]

        assert len(featureSet.featureNums) == len(featureSet.featureDict.keys())

        for sn in f.sampleNums:
            name = os.path.basename(f.samples[sn].accepted.sampleName)
            name = name.split('.')[0].strip('.')
            WS.write(row,col,name)
            row += 1

        annotatedOnly = self.FFW.writeAnnotedOnlyCB.isChecked()

        col = 1
        for fn in featureSet.featureNums:
            row = 0
            f = featureSet.featureDict[fn]
            if f.acceptedFeature != True: continue
            if annotatedOnly:
                if not f.acceptedAssignment: continue
            print 'Printing feature', fn
            annotation = f.acceptedAssignment
            try:
                # write feature headers, name, mz, rt
                headers = [''.join([i if ord(i) < 128 else '' for i in annotation.name]), f.avgmz, f.avgrt, annotation.massError, annotation.rtError]
                print 'headers:', headers
            except AttributeError:
                headers = ['-', f.avgmz, f.avgrt, '-', '-']
            except UnicodeError:
                print '\nUnicode Exception:'
                print '-------------------------------------'
                print annotation.name
                print
                headers = ['-', f.avgmz, f.avgrt, '-', '-']

            for h in headers:
                WS.write(row,col,h)
                row += 1

            for sn in f.sampleNums:
                sample = f.samples[sn]
                accepted = sample.accepted
                WS.write(row,col,accepted.into)
                row += 1
            col += 1

        WB.close()
        return

    def pointsClicked(self, plot, points):
        returnPoints = []
        for i, plotPoint in enumerate(self.massAccuracyPlot.points()):
            for clickedPoint in points:
                if plotPoint.__dict__ == clickedPoint.__dict__:
                    print "found selected point", i
                    returnPoints.append(i+1)
        return returnPoints

    def selectLibraryFile(self):
        inFile = QtGui.QFileDialog.getOpenFileName(self, "Load metabolite library file")
        # inFile = '/home/mleeming/project_data/LCMS_data_analysis/BPA_sepsis/metabolite_standards.csv'

        print 'library file is:', inFile
        if str(inFile):
            self.FFW.libFileText.setText(os.path.basename(str(inFile)))
            self.libraryFile = str(inFile)
        return

    def annotatePeaks(self):

        if not self.libraryFile:
            print 'Please select library file'
            return
        try:
            # get input data
            ppmTol = float(self.FFW.libMatchPPMError.text())
            rtTol = float(self.FFW.libMatchRTError.text())
        except:
            print 'Error in ppm or rt tolerance specification'
            return

        if self.FFW.posIonCB.isChecked():
            polarity = 'pos'
        elif self.FFW.negIonCB.isChecked():
            polarity = 'neg'
        else:
            print 'Error in ion mode selection'
            return

        # get highlighted data file
        highlightedRow = self.FFW.openDataFilesTable.selectionModel().selectedRows()[0].row()
        dataFileID = int(str(self.FFW.openDataFilesTable.item(highlightedRow, 0).text()))

        dataFile = None
        for featureSet in self.featureSetsList:
            if featureSet.dataFileID == dataFileID:
                dataFile = featureSet

        if not dataFile:
            print 'No data file selected'
            return

        self.standards = gl.doAnnotation(dataFile, self.libraryFile, ppmTol, rtTol, polarity)
        self.fillStandardsTable()

        # accept annotated features by default
        for featureSet in self.featureSetsList:
            for fn in featureSet.featureNums:
                f = featureSet[fn]
                if f.acceptedAssignment:
                    f.acceptedFeature = True
        return

    def addDataFilesToExplorerTable(self):
        table = self.TEP.samplesTable
        self.clearTable(table)
        self.MSdataFiles = []
        for featureSet in self.featureSetsList:
            for fn in featureSet.featureNums:
                f = featureSet[fn]
                for sn in f.sampleNums:
                    self.MSdataFiles.append(DataFile(f.samples[sn].accepted.sampleName, f.samples[sn].accepted.sample))
                    name = os.path.basename(f.samples[sn].accepted.sampleName)
                    name = name.split('.')[0].strip('.')
                    rc = table.rowCount()
                    table.insertRow(rc)
                    table.setItem(rc, 0, self.addData(sn))
                    table.setItem(rc, 1, self.addData(name))
                break

        return

    def getAcceptedStandards(self):
        for s in self.standards:
            s.matchedFeatures = []
            for featureSet in self.featureSetsList:
                for fn in featureSet.featureNums:
                    f = featureSet[fn]
                    if not f.acceptedAssignment: continue
                    a = f.acceptedAssignment
                    if a.name == s.name and a.mz == s.mz:
                        s.matchedFeatures.append(fn)
        return

    def fillStandardsTable(self):

        self.TEP.standardTable.setSortingEnabled(False)
        table = self.TEP.standardTable
        explorerTable = self.TEP.refStandardsTable

        self.clearTable(table)
        self.clearTable(explorerTable)

        self.getAcceptedStandards()

        for i, standard in enumerate(self.standards):
            table.insertRow(i)
            table.setItem(i, 0, self.addData(i))
            table.setItem(i, 1, self.addData(standard.name))
            table.setItem(i, 2, self.addData(len(standard.matchedFeatures)))

            explorerTable.insertRow(i)
            explorerTable.setItem(i, 0, self.addData(i))
            explorerTable.setItem(i, 1, self.addData(standard.name))
            explorerTable.setItem(i, 2, self.addData(standard.rt))
            explorerTable.setItem(i, 3, self.addData(standard.mz))

            if len(standard.matchedFeatures) == 1:
                rtError = abs(standard.rt - self.featureSetsList[0][standard.matchedFeatures[0]].avgrt)
                rtError = '%.2f' %rtError
            elif len(standard.matchedFeatures) > 1:
                rts = [self.featureSetsList[0][x].avgrt for x in standard.matchedFeatures]
                minrt = min(rts)

                rtError = abs(standard.rt - minrt)
                rtError = '%.2f' %rtError
            else:
                rtError= ''

            table.setItem(i, 3, self.addData(standard.rt))
            table.setItem(i, 4, self.addData(rtError))

            if len(standard.matchedFeatures) == 1:
                mzError = abs(standard.mz - self.featureSetsList[0][standard.matchedFeatures[0]].avgmz)/standard.mz * 1000000
                mzError = '%.1f' %mzError
            elif len(standard.matchedFeatures) > 1:
                mzs = [self.featureSetsList[0][x].avgmz for x in standard.matchedFeatures]
                minmz = min(mzs)

                mzError = abs(standard.mz - minmz)/standard.mz * 1000000
                mzError = '%.1f' %mzError
            else:
                mzError= ''

            table.setItem(i, 5, self.addData(standard.mz))
            table.setItem(i, 6, self.addData(mzError))

            numMatched = len(standard.matchedFeatures)
            if numMatched == 0: color = self.red
            elif numMatched == 1: color = self.green
            else: color = self.orange

            for c in range(table.columnCount()):
                table.item(i, c).setBackground(color)

            for c in range(explorerTable.columnCount()):
                explorerTable.item(i, c).setBackground(color)

        self.TEP.standardTable.setSortingEnabled(True)
#        table.resizeRowsToContents()
#        table.selectRow(0)
        return

    def loadData(self, inFile = None):
        if not inFile:
            inFile = str(QtGui.QFileDialog.getOpenFileName(self, "Load XCMS feature file"))

        if str(inFile) == '': return

        if '.pickle' in inFile or '.p' in inFile:
            try:
                self.standards, featureSet = pickle.load(open(inFile,'rb'))
                featureSet.getMetaData() # recalculate meta data if integration bounday extrema not present

            except KeyError: # compatibility
                featureSet = pickle.load(open(inFile,'rb'))
        else:
            featureSet = common.parseRoutputFeatureData(inFile)
            featureSet.dataFileName = str(inFile)

        featureSet.symbol = self.symbolSet[self.dataFileIdCounter - 1 % len(self.symbolSet)]
        featureSet.color = self.colorSet[self.dataFileIdCounter - 1 % len(self.colorSet)]

        #featureSet.brush = pg.mkBrush(featureSet.color)
        #featureSet.pen = pg.mkPen(featureSet.color)
        featureSet.dataFileID = self.dataFileIdCounter
        featureSet.addAttrToFeatures('dataFileID', featureSet.dataFileID)
        self.dataFileIdCounter += 1

        self.featureSetsList.append(featureSet)

        if len(self.standards) > 0:
            self.fillStandardsTable()

        # numtraces used to preDraw plotDataItems when EIC explorer grid is redrawn
        for featureSet in self.featureSetsList:
            num = 1
            while True:
                try:
                    nsamples = len(featureSet[num].samples.values())
                    if nsamples > self.numTraces:
                        self.numTraces = nsamples
                    break
                except:
                    num += 1

        # add file to data file table
        rc = self.FFW.openDataFilesTable.rowCount()
        self.FFW.openDataFilesTable.insertRow(rc)
        self.FFW.openDataFilesTable.setItem(rc, 0, self.addData(featureSet.dataFileID))
        self.FFW.openDataFilesTable.setItem(rc, 1, QtGui.QTableWidgetItem(os.path.basename(inFile)))

        doScoring = False
        if doScoring:
                allFeatures.applyEICScoring(self.model)

        self.FFW.openDataFilesTable.resizeRowsToContents()
        self.FFW.openDataFilesTable.selectRow(0)

        self.rewriteFeatureTable()
        self.drawFeatureMap()

        self.addDataFilesToExplorerTable()

        return

    def radiobuttonToggled(self, button):
        if button.isChecked():
            self.rewriteFeatureTable()
        return

    def rewriteFeatureTable(self):
        # clear all data from table
        self.clearTable(self.FFW.xcmsFeatures)

        # disable table sorting
        self.FFW.xcmsFeatures.setSortingEnabled(False)

        allFeatures = self.FFW.allFeaturesRB.isChecked()
        acceptedOnly = self.FFW.acceptedFeaturesRB.isChecked()
        rejectedOnly = self.FFW.rejectedFeaturesRB.isChecked()
        unassignedOnly = self.FFW.unassignedFeaturesRB.isChecked()

        annotatedOnly = self.FFW.limitToAnnotatedCB.isChecked()

        if acceptedOnly: condition = True
        elif rejectedOnly: condition = False
        elif unassignedOnly: condition = None

        for featureSet in self.featureSetsList:
            for fn in featureSet.featureNums:
                f = featureSet[fn]
                if not allFeatures:
                    if f.acceptedFeature != condition:
                        continue
                if annotatedOnly:
                    if not f.acceptedAssignment:
                        continue

                rc = self.FFW.xcmsFeatures.rowCount()
                self.FFW.xcmsFeatures.insertRow(rc)

                newTableColour, newPlotColor = self.getColor(f)

                '''
                QTableWidget accepts only strings by default
                - creates problems when sorting columns of number via gui
                - sorting occurs lexically rather than numerically
                To workaround this:
                - change editrole of QtableWidget
                See this SO question:
                    https://stackoverflow.com/questions/13074035/qtablewidget-integer
                '''
                self.FFW.xcmsFeatures.setItem(rc, 0, self.addData(featureSet.dataFileID))
                self.FFW.xcmsFeatures.setItem(rc, 1, self.addData(f.featureNumber))
                self.FFW.xcmsFeatures.setItem(rc, 2, self.addData(f.avgrt))
                self.FFW.xcmsFeatures.setItem(rc, 3, self.addData(f.avgmz))
                self.FFW.xcmsFeatures.setItem(rc, 4, self.addData(f.numFilled))

                self.changeRowColor(rc, newTableColour)

        self.FFW.xcmsFeatures.resizeColumnsToContents()
        self.FFW.xcmsFeatures.resizeRowsToContents()

        # re-enable sorting
        self.FFW.xcmsFeatures.setSortingEnabled(True)

        # highlight first row
        # selectRow triggers itemSelectionChanged slot which calls updatePlots
        # self.FFW.xcmsFeatures.itemSelectionChanged.disconnect()

        self.FFW.xcmsFeatures.selectRow(0)
        self.alignText(self.FFW.xcmsFeatures)

        # self.FFW.xcmsFeatures.itemSelectionChanged.connect(self.updateSelection)
        return

    def getTableWidth(self, table):
        w = 0
        for c in range(table.columnCount()):
            w += table.columnWidth(c)
        return w

    def getNextBatch(self, direction):
        highlightedRows = self.FFW.xcmsFeatures.selectionModel().selectedRows()

        if direction == 'prev': i = -1
        else: i = 1

        newRows = [x.row() + i * len(highlightedRows) for x in highlightedRows]

        # disconnect xcmsFeatures itemselectionchanged signal temporarily
        # --> prevents itemselection change slots firing when each new selection is added
        self.FFW.xcmsFeatures.itemSelectionChanged.disconnect()
        self.FFW.xcmsFeatures.clearSelection()

        if len(highlightedRows) > 1:
            self.FFW.xcmsFeatures.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)

        for i in newRows:
            self.FFW.xcmsFeatures.selectRow(i)

        if len(highlightedRows) > 1:
            self.FFW.xcmsFeatures.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        # reconnect signal
        self.FFW.xcmsFeatures.itemSelectionChanged.connect(self.updateSelection)
        self.updateSelection()
        return

    def updateSelection(self):

        rows,cols,total = self.getDimensions()

        r,c = 0,0

        highlightedRows = self.FFW.xcmsFeatures.selectionModel().selectedRows()

        if len(highlightedRows) > total:
            highlightedRows = highlightedRows[0:total]

        '''
        note:
        If more features are selected than plots allowed, excess features are not
        plotted but this is not reflected in the selection tables
        '''

        self.activeFeatures = []

        for row in highlightedRows:
            highlightedRow = row.row()
            dataFileID = int(str(self.FFW.xcmsFeatures.item(highlightedRow, 0).text()))
            hitFeatureID = int(str(self.FFW.xcmsFeatures.item(highlightedRow, 1).text()))

            # get matching feature
            feature = self.getFeature(dataFileID, hitFeatureID)

            self.activeFeatures.append(feature)

        self.redrawLayout()

        '''
        Call updatePeakRecovery here
        This could be added as a slot for xcmsFeatures.itemselectionchanged.
        However, would need to handle the effects of signal .disconnect() seperately
        '''
        self.updatePeakRecovery()
        return

    def redrawLayout(self):

        '''
        Updates data shown in EIC explorer
        '''
        if len(self.activeFeatures) < 1: return
        pltacq =0
        update = 0
        for i, f in enumerate(self.activeFeatures):

            plt = self.eicExplorerPlots[i]
            dataItems = plt.listDataItems()

            plt.setTitle(
                'RT = %.2f,  m/z = %.3f, DF = %s, FI = %s' %(
                    f.avgrt, f.avgmz, f.dataFileID, f.featureNumber
                )
            )

            newTableColour, newPlotColor= self.getColor(f)
            self.setPlotAxisColor(plt, newPlotColor)

            if len(dataItems) == len(f.sampleNums):
                for j, s in enumerate(f.samples.values()):
                    x = s.accepted.eicRTs
                    y = s.accepted.eicINTs
                    if len(x) < 2 or len(y) < 2:
                        x, y = [],[]
                    dataItems[j].setData(x = x, y = y, pen = 'k')
            else:
                for item in dataItems:
                    plt.removeItem(item)

                for s in f.samples.values():
                    x = s.accepted.eicRTs
                    y = s.accepted.eicINTs
                    if len(x) < 2 or len(y) < 2:
                        x, y = [],[]
                    plt.plot(x = x, y = y, pen = 'k')
        for p in self.eicExplorerPlots:
            p.autoRange()
        self.updateActivePointsInFM()
        self.updateActivePointsInSummaryMaps()
        return

    def redrawEICPlotLayout(self):
        '''
        Redraws subplots in EIC explorer
        - called when ncols or nrows is changed
        '''
        self.clearPlots()
        self.eicExplorerPlots = []
        rows, cols, total = self.getDimensions()

        for r in range(rows):
            for c in range(cols):
                plt = pg.PlotItem(viewBox = EICViewBox())
                if self.numTraces:
                    for nt in range(self.numTraces):
                        plt.plot()
                self.EED.eicExplorerLayout.addItem(
                    plt,
                    row = r,
                    col = c,
                )
                self.eicExplorerPlots.append(plt)
        return

    def clearPlots(self):

        rows, cols, total = self.getDimensions()

        for r in range(rows):
            for c in range(cols):
                item = self.EED.eicExplorerLayout.getItem(r,c)
                if item:
                    self.EED.eicExplorerLayout.removeItem(item)
        self.EED.eicExplorerLayout.clear()
        return

    def onClick(self, event):
        '''
        https://stackoverflow.com/questions/27222016/pyqt-mousepressevent-get-object-that-was-clicked-on
        '''
        # disable changes from right clicks
        if event.button() == QtCore.Qt.RightButton:
            return

        # get clicked plot
        items = self.EED.eicExplorerLayout.scene().items(event.scenePos())
        items = [x for x in items if isinstance(x, pg.PlotItem)]
        plot = items[0]

        plotTitle = plot.titleLabel.text

        # get feature corresponding to plot
        DF, FI = self.getFeatureFromPlotTitle(plotTitle)
        feature = self.getFeature(DF, FI)
        featureRow = self.highlightFeature(FI, DF, returnRow = True)
        feature = self.changeAssignmentOnClick(feature)
        newTableColour, newPlotColor= self.getColor(feature)

        self.setPlotAxisColor(plot, newPlotColor)
        self.changeRowColor(featureRow, newTableColour)
        return

    def drawFeatureMap(self):

        annotatedOnly = self.FFW.limitToAnnotatedCB.isChecked()
        self.featureMap.clear()
        self.massAccuracyPlot.clear()
        self.rtAccuracyPlot.clear()

        self.featureMap.setLabel(axis = 'left', text = 'RT (s)')
        self.featureMap.setLabel(axis = 'bottom', text = 'm/z')

        for featureSet in self.featureSetsList:
            c = featureSet.color
            s = featureSet.symbol
            name = featureSet.dataFileName

            if annotatedOnly:
                mz, rt, mzacc, rtacc = featureSet.getFeatureMapAndSummaryData(
                    ['avgmz','avgrt','featureMzAccuracy','featureRtAccuracy'],
                    annotatedOnly = True
                )
            else:

                mz, rt, mzacc, rtacc = featureSet.getFeatureMapAndSummaryData(
                    ['avgmz','avgrt','featureMzAccuracy','featureRtAccuracy'],
                    annotatedOnly = False
                )

            self.featureMap.plot(
                         x = np.asarray(mz),
                         y = np.asarray(rt),
                         symbol = 'o',
                         pen = None,
                         )

            # add summary plots
            self.massAccuracyPlot.plot(
                x = np.asarray(mz),
                y = np.asarray(mzacc),
                symbol = 'o',
                pen = None
            )

            self.rtAccuracyPlot.plot(
                x = np.asarray(rt),
                y = np.asarray(rtacc),
                symbol = 'o',
                pen = None
            )

        self.updateActivePointsInFM()
        self.updateActivePointsInSummaryMaps()
        return

    def featurePointHighlighted(self, data, pointIndices, callBack = None):
        '''
        slot that catches the data emitted when rectangle is selected in featureMap or summary plots
        '''
#        print 'featurePointHighlighted'
#        for d in dataItems:
#            d.autoRange()
        '''
        Need to implement a method to get the selected data file if there are multiple
        '''
        if len(self.featureSetsList) == 1:
            featureSet = self.featureSetsList[0]
        else:
            print 'Need to handle dataFile selection in featuremap rectangle highlighting'
            return


        # get features corresponding to selected points

        '''
        Be careful here:
            - pointIndices refer to the index of the dataPoint IN THE PLOT
            - if acceptedAnnotatedONly is checked, indices do not correspond to feature indices
        '''

        selectedFeatures = featureSet.getFeatureByIndex(pointIndices, self.FFW.limitToAnnotatedCB.isChecked())

        #for i in pointIndices:
            # index = i + 1 # features in featureSets are 1 indexed

            #feature = featureSet.getFeatureByIndex(i, self.limitToAnnotatedCB.isChecked())

            # if index in featureSet.featureNums: # why would this not be the case?
            #    selectedFeatures.append([index, featureSet.dataFileID])

        # whats this about?
        #f = self.featureSetsList[0].featureDict[pointIndices[0] + 1]

        if callBack:
            return callBack(selectedFeatures)

        #self.highlightPointsInRectangle(selectedFeatures)
        return


    def highlightPointsInRectangle(self, points):

        self.FFW.xcmsFeatures.itemSelectionChanged.disconnect()
        self.FFW.xcmsFeatures.clearSelection()

        self.activeFeatures = []

        if len(points) > 1:
            self.FFW.xcmsFeatures.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)

        rc = self.FFW.xcmsFeatures.rowCount()
        for r in range(rc):
            dataFileID = int(str(self.FFW.xcmsFeatures.item(r, 0).text()))
            hitFeatureID = int(str(self.FFW.xcmsFeatures.item(r, 1).text()))

            if [hitFeatureID, dataFileID] in points:
                self.FFW.xcmsFeatures.selectRow(r)
                feature = self.getFeature(dataFileID, hitFeatureID)
                self.activeFeatures.append(feature)

        if len(points) > 1:
            self.FFW.xcmsFeatures.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        # reconnect signal
        self.FFW.xcmsFeatures.itemSelectionChanged.connect(self.updateSelection)

        assert len(self.activeFeatures) == len(points)

        self.updateActivePointsInFM()
        self.updateActivePointsInSummaryMaps()
        self.redrawLayout()
        return

    def updateActivePointsInSummaryMaps(self):
        try:
            self.massAccuracyPlot.removeItem(self.activeMzAccuracySpots)
            self.rtAccuracyPlot.removeItem(self.activeRtAccuracySpots)
        except:
            pass

        # get x, y data from active features
        mzx = [f.avgmz for f in self.activeFeatures]
        mzy = [f.featureMzAccuracy for f in self.activeFeatures]

        rtx = [f.avgrt for f in self.activeFeatures]
        rty = [f.featureRtAccuracy for f in self.activeFeatures]

        self.activeMzAccuracySpots = self.massAccuracyPlot.plot(x = mzx,
                                                                y = mzy,
                                                                pen = None,
                                                                brush = None,
                                                                symbolPen = 'r',
                                                                symbolBrush = 'r',
                                                                symbol = 'o')

        self.activeRtAccuracySpots = self.rtAccuracyPlot.plot(x = rtx,
                                                              y = rty,
                                                              pen = None,
                                                              brush = None,
                                                              symbolPen = 'r',
                                                              symbolBrush = 'r',
                                                              symbol = 'o')

        return

    def updateActivePointsInFM(self):
        # clear previous
        try:
            self.featureMap.removeItem(self.activePointSpots)
        except:
            pass

        # get x, y data from active features
        x = [f.avgmz for f in self.activeFeatures]
        y = [f.avgrt for f in self.activeFeatures]

        self.activePointSpots = self.featureMap.plot(x = x,
                                                     y = y,
                                                     pen = None,
                                                     brush = None,
                                                     symbolPen = 'r',
                                                     symbolBrush = 'r',
                                                     symbol = 'o')
        return

    def updatePeakRecovery(self):
        earlyReturn = False
        if earlyReturn:
            print 'DEBUG --> return from updatePeakRecovery'
            print 'returning'
            return

        self.PRD.filledPeaksTable.itemSelectionChanged.disconnect()

        self.clearTable(self.PRD.filledPeaksTable)
        #self.clearTable(self.PRD.peakCandidatesTable)

        # disable table sorting
        self.PRD.filledPeaksTable.setSortingEnabled(False)
        #self.PRD.peakCandidatesTable.setSortingEnabled(False)

        self.PRD.filledPeaksTable.itemSelectionChanged.connect(self.updateFilledPeakCandidateTable)

        if len(self.activeFeatures) != 1:
            # clear screen to avoid confusion
            self.PRD.intensityDistribution.clear()
            self.PRD.peakDistributionLayout.clear()
            self.PRD.putativeAnnotationLabel.setText(str(''))
            self.PRD.annotationCandidates.setText(str(''))
            while self.PRD.assignmentCandidateTable.rowCount() > 0:
                self.PRD.assignmentCandidateTable.removeRow(0)

            self.clearTable(self.PRD.filledPeaksTable)
            self.clearFeatureInspectorPlots()
            return

        f = self.activeFeatures[0]

        # plot map of sample points
        self.PRD.peakDistributionLayout.clear()
        self.peakDistributionPlot = pg.PlotItem(viewBox = EICViewBox())

        self.peakDistributionPlot.plot(
            x = f.getSampleDataByFilledStatus(['mz'], 0),
            y = f.getSampleDataByFilledStatus(['rt'], 0),
            pen = None,
            brush = None,
            symbolPen = 'r',
            symbolBrush = None,
            symbol = 'o'
        )

        self.peakDistributionPlot.plot(
            x = f.getSampleDataByFilledStatus(['mz'], 1),
            y = f.getSampleDataByFilledStatus(['rt'], 1),
            pen = None,
            brush = None,
            symbolPen = 'k',
            symbolBrush = None,
            symbol = 'o'
        )

        self.peakDistributionPlot.setLabel(axis = 'left', text = 'RT (s)')
        self.peakDistributionPlot.setLabel(axis = 'bottom', text = 'm/z')

        mz, rt = f.getAcceptedCandidateData(['mz','rt'])

        self.peakDistributionPlot.setXRange(min(mz) - 0.5 , max(mz) + 0.5)
        self.peakDistributionPlot.setYRange(min(rt) - 20, max(rt) + 20)

        self.PRD.peakDistributionLayout.addItem(self.peakDistributionPlot)

        '''
        Plot intensity distribution
        '''

        self.PRD.intensityDistribution.clear()
        self.intensityDistributionPlot = pg.PlotItem(viewBox = EICViewBox())

        self.intensityDistributionPlot.plot(
            x = f.getSampleDataByFilledStatus(['sample'], 0),
            y = f.getSampleDataByFilledStatus(['into'], 0),
            pen = None,
            brush = None,
            symbolPen = 'r',
            symbolBrush = None,
            symbol = 'o'
        )

        self.intensityDistributionPlot.plot(
            x = f.getSampleDataByFilledStatus(['sample'], 1),
            y = f.getSampleDataByFilledStatus(['into'], 1),
            pen = None,
            brush = None,
            symbolPen = 'k',
            symbolBrush = None,
            symbol = 'o'
        )

        self.intensityDistributionPlot.setLabel(axis = 'bottom', text = 'Sample')
        self.intensityDistributionPlot.setLabel(axis = 'left', text = 'Peak Area')
        self.PRD.intensityDistribution.addItem(self.intensityDistributionPlot)

        self.intensityDistributionAcceptedPoints = pg.PlotDataItem()
        self.peakDistributionAcceptedPoints = pg.PlotDataItem()

        self.intensityDistributionPlot.addItem(self.intensityDistributionAcceptedPoints)
        self.peakDistributionPlot.addItem(self.peakDistributionAcceptedPoints)

        rowCounter = 0

        for r in f.sampleNums:

            sample = f.samples[r]
            acceptedCandidate = sample.accepted

            if self.PRD.filledOnlyCB.isChecked():
                if not acceptedCandidate.isFilled():
                    continue

            #if self.PRD.candidateOnlyCB.isChecked():
            #    if sample.getNumRecoveryCandidates() < 1: continue

            self.PRD.filledPeaksTable.insertRow(rowCounter)
            self.PRD.filledPeaksTable.setItem(rowCounter, 0, self.addData(acceptedCandidate.sample))
            self.PRD.filledPeaksTable.setItem(rowCounter, 1, self.addData(acceptedCandidate.rt))
            self.PRD.filledPeaksTable.setItem(rowCounter, 2, self.addData(acceptedCandidate.mz))
            self.PRD.filledPeaksTable.setItem(rowCounter, 3, self.addData(acceptedCandidate.into))
            self.PRD.filledPeaksTable.setItem(rowCounter, 4, self.addData(acceptedCandidate.maxo))
            self.PRD.filledPeaksTable.setItem(rowCounter, 5, self.addData(acceptedCandidate.isFilled()))
#            self.PRD.filledPeaksTable.setItem(rowCounter, 6, self.addData(sample.getNumRecoveryCandidates()))
            rowCounter += 1

        self.PRD.filledPeaksTable.selectRow(0)
        self.PRD.filledPeaksTable.resizeRowsToContents()

        candidates = f.getSampleDataByFilledStatus(['filled'], 2)
        del candidates

        if f.acceptedAssignment:
            self.PRD.putativeAnnotationLabel.setText(str(f.acceptedAssignment.name))
            # self.PRD.annotationPPMErrorLabel.setText(str('%.2f' %f.acceptedAssignment.massError))
            self.PRD.annotationCandidates.setText(str(len(f.assignmentCandidates)))
            self.updateAssignmentCandidateTable()
        else:
            self.PRD.putativeAnnotationLabel.setText(str(''))
            #self.PRD.annotationPPMErrorLabel.setText(str(''))
            self.PRD.annotationCandidates.setText(str(len(f.assignmentCandidates)))
            while self.PRD.assignmentCandidateTable.rowCount() > 0:
                self.PRD.assignmentCandidateTable.removeRow(0)


        self.alignText(self.PRD.filledPeaksTable)
        self.PRD.filledPeaksTable.setSortingEnabled(True)
        # self.PRD.peakCandidatesTable.setSortingEnabled(True)
        return

    def clearFeatureInspectorPlots(self):
        # clear EIC traces
        EICdataItems = self.highlightedFeatureEICPlot.listDataItems()
        for d in EICdataItems:
            d.setData(x = [], y = [])
        # clear MS traces
        MSdataItems = self.spectrumPlot.listDataItems()
        for d in MSdataItems:
            d.setData(x = [], y = [])
        return

    def updateAssignmentCandidateTable(self):

        while self.PRD.assignmentCandidateTable.rowCount() > 0:
            self.PRD.assignmentCandidateTable.removeRow(0)

        f = self.activeFeatures[0]

        if not f.acceptedAssignment: return

        for i, a in enumerate(f.assignmentCandidates):
            self.PRD.assignmentCandidateTable.insertRow(i)
            self.PRD.assignmentCandidateTable.setItem(i, 0, self.addData(a.name))
            self.PRD.assignmentCandidateTable.setItem(i, 1, self.addData(a.massError))
            self.PRD.assignmentCandidateTable.setItem(i, 2, self.addData(a.rtError))

        self.alignText(self.PRD.assignmentCandidateTable)
        return

    def clearAcceptedAssignment(self):

        if len(self.activeFeatures) != 1: return

        f = self.activeFeatures[0]
        f.acceptedAssignment = False

        self.PRD.putativeAnnotationLabel.setText(str(''))
        self.PRD.annotationCandidates.setText(str(len(f.assignmentCandidates)))

        self.fillStandardsTable()
        return

    def acceptSelectedAssignmentCandidate(self):

        highlightedRow = self.PRD.assignmentCandidateTable.selectionModel().selectedRows()[0].row()
        f = self.activeFeatures[0]
        f.acceptedAssignment = f.assignmentCandidates[highlightedRow]

        self.PRD.putativeAnnotationLabel.setText(str(f.acceptedAssignment.name))
        self.PRD.annotationCandidates.setText(str(len(f.assignmentCandidates)))

        self.fillStandardsTable()
        return

    def updateFilledPeakCandidateTable(self):
        self.highlightChromatogramForSelectedSample(caller = 'updatefilledpeakcandidateTable')
        return

    def acceptRecoveryCandidate(self):
        highlightedRow = self.PRD.peakCandidatesTable.selectionModel().selectedRows()[0].row()
        sample = int(str(self.PRD.peakCandidatesTable.item(highlightedRow, 0).text()))
        f = self.activeFeatures[0]
        s = f.samples[sample]
        s.acceptSampleRecoveryCandidate(highlightedRow)
        self.updateFilledPeakCandidateTable()
        self.updatePeakRecovery()
        return

    def doManualIntegration(self):
        # get ROI boundaries
        low,high = self.linReg.getRegion()

        # get selected features
        highlightedRows = self.PRD.filledPeaksTable.selectionModel().selectedRows()
        selectedSamples = [int(str(self.PRD.filledPeaksTable.item(i.row(), 0).text())) for i in highlightedRows]

        f = self.activeFeatures[0]

        def getBaseLineSubtract(m, b, x):
            return m*x + b

        for i, s in enumerate(f.samples.values()):

            accepted = s.accepted

            if accepted.sample in selectedSamples:

                accepted = s.accepted

                mask = np.where(
                    (accepted.eicRTs > low) & (accepted.eicRTs < high)
                )

                eicRTsub = accepted.eicRTs[mask]
                eicINTsub = accepted.eicINTs[mask]

                lowRT, highRT = eicRTsub[0], eicRTsub[-1]
                lowInt, highInt = eicINTsub[0], eicINTsub[-1]

                m = (highInt - lowInt) / (highRT - lowRT)
                b = lowInt - m*lowRT

                newArea = 0
                for p in range(eicRTsub.shape[0]):
                    rt, intensity = eicRTsub[p], eicINTsub[p]
                    base = getBaseLineSubtract(m,b,rt)
                    new = intensity - base
                    newArea += new

                if newArea < 0:
                    newArea = 0

                accepted.into = int(newArea)
                accepted.rtmin = low
                accepted.rtmax = high

        # recalculate metaData after integration
        f.getMetaData()
        self.updatePeakRecovery()
        return

    def restoreDefaultIntegration(self):
        # get selected features
        highlightedRows = self.PRD.filledPeaksTable.selectionModel().selectedRows()
        selectedSamples = [int(str(self.PRD.filledPeaksTable.item(i.row(), 0).text())) for i in highlightedRows]

        feature = self.activeFeatures[0]
        for sn in feature.sampleNums:
            f = feature.samples[sn].accepted

            # account for samples that have not yet been reIntegrated
            if not hasattr(f, 'originalrtmax'): continue

            f.into = copy.deepcopy(f.originalIntO)
            f.maxo = copy.deepcopy(f.originalMaxO)
            f.rtmin = copy.deepcopy(f.originalrtmin)
            f.rtmax = copy.deepcopy(f.originalrtmax)

        # recalculate batch metadata
        feature.getMetaData()
        self.updatePeakRecovery()
        return

    def showSelectedEICOnly(self):
        self.highlightChromatogramForSelectedSample()
        return

    def highlightChromatogramForSelectedSample(self, caller = 'None'):

        highlightedRows = self.PRD.filledPeaksTable.selectionModel().selectedRows()
        selectedSamples = [int(str(self.PRD.filledPeaksTable.item(i.row(), 0).text())) for i in highlightedRows]

        f = self.activeFeatures[0]
        ''' Add EIC plot to feature inspector pane '''
        dataItems = self.highlightedFeatureEICPlot.listDataItems()

        if len(self.activeFeatures) > 1: return

        try:
            assert len(dataItems) == len(f.samples.values())
        except AssertionError:
            while len(self.highlightedFeatureEICPlot.listDataItems()) < len(f.samples.values()):
                self.highlightedFeatureEICPlot.plot()
            dataItems = self.highlightedFeatureEICPlot.listDataItems()

        samplesToHighlight = []
        highlightedRTmin, highlightedRTmax = [],[]
        highlightedPeakData = []
        counter = 0
        for i, s in enumerate(f.samples.values()):
            accepted = s.accepted
            x = accepted.eicRTs
            y = accepted.eicINTs
            if len(x) < 2 or len(y) < 2:
                x, y = [],[]
            if accepted.sample in selectedSamples:
                # update EIC plots
                samplesToHighlight.append([x,y])
                highlightedRTmin.append(accepted.rtmin)
                highlightedRTmax.append(accepted.rtmax)
                dataItems[i].setData(x = x,
                                     y = y,
                                     pen = 'r'
                                     )

                # highlight active points in peak distribution and intensity distributions
                highlightedPeakData.append([
                    accepted.mz,
                    accepted.rt,
                    accepted.into,
                    accepted.sample])

            else:
                if self.PRD.selectedSampleOnly.isChecked():
                    dataItems[i].setData(x = [],
                                         y = [],
                                         pen = 'k'
                                         )
                else:
                    dataItems[i].setData(x = x,
                                         y = y,
                                         pen = 'k'
                                         )
                counter += 1

        self.intensityDistributionAcceptedPoints.setData(
             x = [k[3] for k in highlightedPeakData],
             y = [k[2] for k in highlightedPeakData],
             pen = None,
             symbol = 'o',
        )

        self.peakDistributionAcceptedPoints.setData(
            x = [k[0] for k in highlightedPeakData],
            y = [k[1] for k in highlightedPeakData],
            pen = None,
            symbol = 'o'
        )

        self.linReg.setRegion([sum(highlightedRTmin)/len(highlightedRTmin), sum(highlightedRTmax)/len(highlightedRTmax)])
        if len(dataItems) > len(f.samples.values()):
            zeroFillItems = range(len(f.samples.values()), len(dataItems))
            for i in zeroFillItems:
                dataItems[i].setData(x = [], y = [])

        self.PRD.iLineMaxWide.setValue(f.minRTMin)
        self.PRD.iLineMinWide.setValue(f.maxRTMax)

        self.PRD.iLineMaxNarrow.setValue(f.maxRTMin)
        self.PRD.iLineMinNarrow.setValue(f.minRTMax)

        self.highlightedFeatureEICPlot.autoRange()

        ''' plot mass spectrum for highlighted hit '''
        dataItems = self.spectrumPlot.listDataItems()

        try:
            assert len(dataItems) == len(selectedSamples)
        except AssertionError:
            while len(self.spectrumPlot.listDataItems()) < len(selectedSamples):
                self.spectrumPlot.plot()
            dataItems = self.spectrumPlot.listDataItems()

        if len(dataItems) > len(selectedSamples):
            zeroFillItems = range(len(selectedSamples), len(dataItems))
            for i in zeroFillItems:
                dataItems[i].setData(x = [], y = [])


        # get sample object for highlighted sample
        for i, sample in enumerate(selectedSamples):
            s = f.samples[sample].accepted
            x,y = self.zeroFill(s.specMZs, s.specINTs)
            dataItems[i].setData(x = x, y = y, pen = 'k')
            if i == 0:
                self.msPlotText.setText('%.4f'%s.mz, color = 'k')
                self.msPlotText.setPos(s.mz,s.maxo + s.maxo*0.1)

        self.spectrumPlot.autoRange()
        return

    ''' Housekeeping and convenience functions '''

    def clearTable(self, table):
        self.FFW.xcmsFeatures.itemSelectionChanged.disconnect()
        while table.rowCount() > 0:
            table.removeRow(0)
        self.FFW.xcmsFeatures.itemSelectionChanged.connect(self.updateSelection)
        return

    def changeRowColor(self, row, colour):
        for c in range(self.FFW.xcmsFeatures.columnCount()):
            self.FFW.xcmsFeatures.item(row,c).setBackground(colour)
        return

    def addData(self, d):
        item = QtGui.QTableWidgetItem()
        item.setData(QtCore.Qt.EditRole, d)
        return item

    def getColor(self, feature):
        if feature.acceptedFeature == True: return (self.green, self.plotGreen)
        if feature.acceptedFeature == False: return (self.red, 'r')
        if feature.acceptedFeature == None: return (self.white, 'k')

    def setPlotAxisColor(self, plot, newPlotColor):
        axl = plot.getAxis('left')
        axb = plot.getAxis('bottom')
        axl.setPen(newPlotColor)
        axb.setPen(newPlotColor)
        return

    def alignText(self, table):
        rc = table.rowCount()
        cc = table.columnCount()
        for i in range(rc):
            for j in range(cc):
                try:
                    table.item(i, j).setTextAlignment(QtCore.Qt.AlignCenter)
                except:
                    pass
        return

    def getDimensions(self):
        rows = int(self.EED.numRows.value())
        cols = int(self.EED.numCols.value())
        total = rows*cols
        return rows, cols, total

    def getFeature(self, dataFileID, featureID):
        for featureSet in self.featureSetsList:
            if featureSet.dataFileID == dataFileID:
                return featureSet[featureID]

    def highlightFeature(self, clickedFeatureID, clickedDataFileID, returnRow = False):
        rc = self.FFW.xcmsFeatures.rowCount()
        for i in range(rc):
            dataFileID = int(str(self.FFW.xcmsFeatures.item(i, 0).text()))
            featureID = int(str(self.FFW.xcmsFeatures.item(i, 1).text()))

            if dataFileID == int(clickedDataFileID) and featureID == int(clickedFeatureID):
                if returnRow:
                    return i
                else:
                    self.FFW.xcmsFeatures.selectRow(i)
                    return

    def getFeatureFromPlotTitle(self, title):
        t = [s.strip(',').strip() for s in title.split(',')]
        DF = int(re.findall(r'\d+', t[2])[0])
        FI = int(re.findall(r'\d+', t[3])[0])
        return DF, FI

    def changeAssignmentOnClick(self, feature):
        if feature.acceptedFeature == True:
            feature.acceptedFeature = False
            return feature
        if feature.acceptedFeature == False:
            feature.acceptedFeature = None
            return feature
        if feature.acceptedFeature == None:
            feature.acceptedFeature = True
            return feature

    def zeroFill(self, xData, yData):
        x = np.repeat(xData, 3)
        y = np.dstack((np.zeros(yData.shape[0]), yData, np.zeros(yData.shape[0]))).flatten()
        return x, y

    def doAutoRecovery(self):
        '''
        2 types of recovery
        -------------------------------
        1) recover cases where candidate integration boundaries overlap with
            average of directly detected peak integration boundaries
        2) recover peaks within [rt tol] of peak group average by
            minimising the difference in intensity to the average
        '''

        def getAvg(d):
            return sum(d)/len(d)

        for featureSet in self.featureSetsList:
            for fn in featureSet.featureNums:
                f = featureSet[fn]

                l,h = f.getAcceptedCandidateData(['rtmin', 'rtmax'])
                avgLow, avgHigh = getAvg(l), getAvg(h)

                for sn in f.sampleNums:
                    s = f.samples[sn]

                    if s.accepted.filled == 0: continue

                    # get data for recovery candidates
                    sampleIDs, rtmins, rtmaxs, rts, mzs, intos, maxos = f.getSampleDataByFilledStatus(
                        ['sample','rtmin','rtmax','rt','mz','into','maxo'], 2, sample = sn
                    )

                    # if more than 1 recovery is possible, minimise difference in intensities
                    minIntDIfferenceIndex = None
                    minIntDifference = None
                    for i in range(len(sampleIDs)):
                        candidateRT = rts[i]
                        if fn == 77 and sn == 10:
                            print candidateRT, f.avgrt, abs(f.avgrt - candidateRT)
                        if abs(candidateRT - f.avgrt) < 120:
#                        candidateMin, candidateMax = rtmins[i], rtmaxs[i]
#                        if candidateMax > avgLow and candidateMax < avgHigh \
#                           or candidateMin > avgLow and candidateMin < avgHigh:

                            print fn, sampleIDs[i], f.avgrt, rts[i]

                            intDiff = abs(f.avginto - intos[i])

                            if minIntDifference:
                                if intDiff < minIntDifference:
                                    minIntDifference = intDiff
                                    minIntDIfferenceIndex = i
                            else:
                                minIntDIfferenceIndex = i
                                minIntDifference = intDiff

                    if minIntDIfferenceIndex:
                        s.acceptSampleRecoveryCandidate(minIntDIfferenceIndex)
                f.getMetaData()
        self.rewriteFeatureTable()
        self.drawFeatureMap()
        return

class EICViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        pg.ViewBox.__init__(self, *args, **kwds)
        self.setMouseMode(self.RectMode)

    ## reimplement right-click to zoom out
    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton:
            self.autoRange()

    def mouseDragEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton:
            ev.ignore()
        else:
            pg.ViewBox.mouseDragEvent(self, ev)

counter = 0

class FeatureMapViewBox(pg.ViewBox):
    # create custom signal that is emitted when
    # a rectangle is drawn
    # returns two lists
    mapSelectionChanged = QtCore.pyqtSignal(list, list)

    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton:
            self.autoRange()

    def mouseDragEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            ev.ignore()
        else:
            pg.ViewBox.mouseDragEvent(self, ev)

        ev.accept()
        pos = ev.pos()
        if ev.button() == QtCore.Qt.LeftButton:
            if ev.isFinish():
                self.rbScaleBox.hide()
                self.ax = QtCore.QRectF(Point(ev.buttonDownPos(ev.button())), Point(pos))
                self.ax = self.childGroup.mapRectFromParent(self.ax)
                self.Coords =  self.ax.getCoords()
                self.getdataInRect()
                self.changePointsColors()
            else:
                self.updateScaleBox(ev.buttonDownPos(), ev.pos())
#
    def getdataInRect(self):
        # Get the data from the Graphicsitem
        self.getDataItem()
        x = self.dataxy[0]
        y = self.dataxy[1]

        # Rect Edges
        Xbl = (self.Coords[0],self.Coords[1]) # bottom left
        Xbr = (self.Coords[2],self.Coords[1]) # bottom right
        Xtr = (self.Coords[2],self.Coords[3]) # top right
        Xtl = (self.Coords[0],self.Coords[3]) # top left

        #Make a list of [(x0,y0),(x1,y1) ...]
        self.xy = list()
        for i in range(len(x)):
                tmp = (x[i],y[i])
                self.xy.append(tmp)

        # matplotlib inside_poly function gets
        # datapoints that are within polygon
        self.insideIndex = inside_poly(self.xy,[Xbl, Xbr, Xtr, Xtl])

    def getDataItem(self):
        # get plotItem from scene
        items = pg.GraphicsScene.items(self.scene())
        self.ObjItemList = [x for x in items if isinstance(x, pg.PlotItem)]
        self.dataxy = self.ObjItemList[0].listDataItems()[0].getData()

    def changePointsColors(self):
        # emit signal carrying data and indices of selected poitns
        self.mapSelectionChanged.emit(self.xy, self.insideIndex)

class DataFile (object):
    def __init__(self, absName, id):
        self.absName = absName
        self.sampleID = id
        self.name = self.parseFileName(absName)
        self.spec = pymzml.run.Reader(self.absName)
        return

    def parseFileName(self, name):
        name = os.path.basename(name)
        name = name.split('.')[0].strip('.')
        return name

class EICTrace (object):
    def __init__(self):
        self.rts = []
        self.ints = []
        self.into = None
        return

def readMzXML(mzml_file, AmsLevel = 1):
    n = 0
    with mzxml.read(mzml_file) as reader:
        for scan in reader:
            lvl = int(scan['msLevel'])
            time = float(scan['retentionTime']) * 60
            n += 1
            if scan['msLevel'] != msLevel: continue
            mzs = scan['m/z array']
            ints = scan['intensity array']
            assert mzs.shape == ints.shape
            yield time, mzs, ints, lvl, n - 1

def readMzML(mzml_file, msLevel = 1):

    msrun = pymzml.run.Reader(str(mzml_file), build_index_from_scratch = True)
    for n, spectrum in enumerate(msrun):

        # only consider MS1 level
        if spectrum['ms level'] != msLevel: continue

        lvl = spectrum['ms level']

        try:
            time = spectrum['scan time'] * 60
        except:
            try:
                time = spectrum['scan start time'] * 60
            except Exception, e:
                print 'Warning, skipping spectrum %s' %n
                print 'Stack trace:'
                print str(e)
                continue

        try:
            mzs = np.array(spectrum.mz, dtype = "float32")
            ints = np.array(spectrum.i, dtype = 'float32')

            # if 'second' in unit:
            #     time /= 60 # HTCPP output files are in seconds

            # --> converting time units like this screws up correlation with
            # ht hits where ht hit units are actually in seconds
            assert mzs.shape == ints.shape
            yield time, mzs, ints, lvl, spectrum['id']

        except Exception, e:
            print 'Warning, skipping spectrum %s' %n
            print 'Stack trace:'
            print str(e)
            continue

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = XCMSView()

    screenShape = QtGui.QDesktopWidget().screenGeometry()
    window.resize(screenShape.width()*0.8, screenShape.height()*0.8)

    window.show()
    app.exec_()
