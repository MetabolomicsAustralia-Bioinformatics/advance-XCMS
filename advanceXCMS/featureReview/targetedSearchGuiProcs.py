import os, sys
import pymzml
from PyQt4 import QtCore, QtGui
import pyqtgraph as pg

import pickle
import numpy as np

from pyteomics import mzxml, auxiliary
from advanceXCMS.gui.targetedSearch import Ui_Dialog as TSGui
from advanceXCMS.shared import Common as common

try:
    import better_exceptions
except:
    pass
import time

class DataFile (object):
    def __init__(self, absName):
        self.absName = absName
        self.name = self.parseFileName(absName)
        self.spec = pymzml.run.Reader(self.absName)
        return

    def parseFileName(self, name):
        name = os.path.basename(name)
        name = name.split('.')[0].strip('.')
        return name


class Standard (object):
    def __init__(self, name, mz, rt, index):
        self.name = name
        self.mz = float(mz)
        self.rt = float(rt)
        self.index = index

class TargetedSearch( QtGui.QDialog, TSGui, QtCore.QRunnable):
    def __init__(self, standards = [], dataFiles = [], parent = None):

        pg.setConfigOption('background','w')
        pg.setConfigOption('foreground','k')

        super(TargetedSearch, self).__init__(parent)
        self.setupUi(self)

        self.setWindowTitle('Targeted Metabolite Search')

        self.dataFiles = dataFiles
        self.standards = standards

        self.green = QtGui.QColor(200,255,200)
        self.red = QtGui.QColor(255,200,200)
        self.orange = QtGui.QColor(255, 225, 200)

        if self.standards:
            self.addStandardsToStandardsTable()
        if self.dataFiles:
            self.dataFiles = [DataFile(f) for f in self.dataFiles]
            self.addDataFilesToDataFilesTable()

        self.activeSamples = []
        self.msActive = False

        self.splitter.setSizes([400,100])
        self.splitter_2.setSizes([500,100])
        self.splitter_3.setSizes([100,600])

        self.plot = pg.PlotItem(viewBox = EICViewBox())
        self.plot.setLabel(axis = 'left', text = 'Intensity')
        self.plot.setLabel(axis = 'bottom', text = 'Retention Time (s)')
        self.eicPlot.addItem(self.plot)

        # add iLine to EIC
        self.iLine = pg.InfiniteLine(angle = 90, movable = True, pen = 'b')
        self.linReg = pg.LinearRegionItem()

        self.mzTolEntry.setText('0.03')
        self.rtDisplayEntry.setText('100')
        self.formatTables()
        self.connections()
        return

    @staticmethod
    def getStandardEICs(standards, files):
    #def run(self, standards, files):
        dialog = TargetedSearch(standards, files)
        result = dialog.exec_()
        return

    def formatTables(self):
        tables = [
            [ self.refStandardsTable, [0,2,3] ],
            [ self.samplesTable, [] ]
        ]

        for table in tables:
            t = table[0]
            restrict = table[1]

            t.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

            t.setSortingEnabled(True)
            tableHeader = t.horizontalHeader()
            cc = t.columnCount()
            for c in range(cc):
                if c in restrict:
                    mode = QtGui.QHeaderView.ResizeToContents
                else:
                    mode = QtGui.QHeaderView.Stretch

                tableHeader.setResizeMode(c, mode)

            t.verticalHeader().setVisible(False)

        return

    def connections(self):
        self.addDataFilesButton.clicked.connect(self.addDataFiles)
        self.extractEICsButton.clicked.connect(self.extractEICs)
        self.refStandardsTable.itemSelectionChanged.connect(self.updatePlot)
        self.selectedOnlyCB.toggled.connect(self.updatePlot)
        self.samplesTable.itemSelectionChanged.connect(self.getSelectedSamples)
        self.showIntegrationCB.toggled.connect(self.addRemoveIntegration)
        self.showSpectrumCB.toggled.connect(self.addRemoveMS)
        self.browseButton.clicked.connect(self.addRefs)
        self.iLine.sigDragged.connect(self.updateMS)
        self.iLine.sigPositionChangeFinished.connect(self.updateMS)
        return

    def updateMS(self):
        selectedSample = self.activeSamples[0]
        activeFile = None

        for f in self.dataFiles:
            if f.name == selectedSample:
                activeFile = f

        t0 = time.time()

        activeFile = self.dataFiles[0]

        iLineVal = float(self.iLine.value())
        scanNumber = np.argmin(np.absolute(activeFile.scanTimes - iLineVal))
        specIndex = activeFile.scanIndices[scanNumber]

        t1 = time.time()

        spec = activeFile.spec[specIndex]

        t2 = time.time()
        mz, i = self.zeroFill(np.array(spec.mz), np.array(spec.i))
        t3 = time.time()
        self.MSDataItem.setData(x = mz, y = i)
        t4 = time.time()

#        print
#        print t1-t0
#        print t2-t1
#        print t3-t2
#        print t4-t3
#        print '----------------'
#        print t0+t1+t2+t3+t4
        return

    def addRemoveIntegration(self):
        showInt = self.showIntegrationCB.isChecked()
        if not showInt:
            self.plot.removeItem(self.linReg)
        else:
            self.plot.addItem(self.linReg)
            self.updateLinReg()
        return

    def updateLinReg(self):
        highlightedRow = int(str(self.refStandardsTable.selectionModel().selectedRows()[0].row()))

        # careful, row indices no longer correlate with order of standards list once table is sorted by user
        standardIndex = int(self.refStandardsTable.item(highlightedRow,0).text())
        standard = self.standards[standardIndex]

        self.linReg.setRegion([standard.rt-20, standard.rt+20])
        return

    def addRemoveMS(self):
        showMS = self.showSpectrumCB.isChecked()
        if not showMS:
            self.eicPlot.removeItem(self.MS)
            self.plot.removeItem(self.iLine)
            self.msActive = False
        else:
            self.MS = self.eicPlot.addPlot(row = 1, col = 0, viewBox = EICViewBox())
            # self.MS = self.eicPlot.addPlot(row = 1, col = 0)
            self.MS.setLabel(axis = 'left', text = 'Intensity')
            self.MS.setLabel(axis = 'bottom', text = 'm/z')
            self.MSDataItem = self.MS.plot(x = [], y = [], pen = 'k')
            self.plot.addItem(self.iLine)
            self.msActive = True
            try:
                self.activeSamples = self.activeSamples[0]
                self.updatePlot()
            except IndexError:
                pass
        return

    def addRefs(self):
        ''' fill standards table from library file '''
        inFile = str(QtGui.QFileDialog.getOpenFileName(self, 'Select Metabolite library File'))

        if inFile == '': return

        if1 = open(inFile,'r').readlines()
        for i, l in enumerate(if1):
            name, rt, mz = [x.strip(',').strip('$').strip() for x in l.split('$')]
            self.standards.append(Standard(name, mz, rt, i))

        self.addStandardsToStandardsTable()
        return

    def addStandardsToStandardsTable(self):
        self.clearTable(self.refStandardsTable)

        for i, s in enumerate(self.standards):
            self.refStandardsTable.insertRow(i)
            self.refStandardsTable.setItem(i, 0, self.addData(int(i)))
            self.refStandardsTable.setItem(i, 1, self.addData(str(s.name)))
            self.refStandardsTable.setItem(i, 2, self.addData(float(s.rt)))
            try: # wtf
                m = s.mz
            except:
                m = s.mass
            self.refStandardsTable.setItem(i, 3, self.addData(float(m)))

            numMatched = len(s.matchedFeatures)
            if numMatched == 0: color = self.red
            elif numMatched == 1: color = self.green
            else: color = self.orange

            for c in range(self.refStandardsTable.columnCount()):
                self.refStandardsTable.item(i, c).setBackground(color)

        return

    def addDataFiles(self):
        # Select files
        inFiles = sorted([str(_) for _ in QtGui.QFileDialog.getOpenFileNames(self, 'Select mzML Files')])
        self.dataFiles = [DataFile(f) for f in inFiles]
        return

    def addDataFilesToDataFilesTable(self):
        self.clearTable(self.samplesTable)
        for i, d in enumerate(self.dataFiles):
            self.samplesTable.insertRow(i)
            self.samplesTable.setItem(i, 0, self.addData(d.name))
        return

    def updatePlot(self):
        highlightedRow = int(str(self.refStandardsTable.selectionModel().selectedRows()[0].row()))

        # careful, row indices no longer correlate with order of standards list once table is sorted by user
        standardIndex = int(self.refStandardsTable.item(highlightedRow,0).text())
        standard = self.standards[standardIndex]

        print standard.name, standard.rt, standard.mz

        if len(self.plot.listDataItems()) == len(self.dataFiles):
            pass
        else:
            self.plot.clear()
            for d in self.dataFiles:
                self.plot.plot()

        selectedOnly = self.selectedOnlyCB.isChecked()

        counter = 0
        globalmax = 0
        dataItems = self.plot.listDataItems()
        for k, v in standard.eicTraces.iteritems():
            rts, ints = v
            if k in self.activeSamples:
                pen = 'r'
            else:
                pen = 'k'
            if selectedOnly and k not in self.activeSamples:
                rts, ints = [],[]
            else:
                try:
                    rangemax = np.max(ints[np.where((rts > standard.rt - 100) & (rts < standard.rt + 100))])
                    if rangemax > globalmax:
                        globalmax = rangemax
                except:
                    print ints
            dataItems[counter].setData(rts, ints, pen = pen)
            counter += 1

        if self.showSpectrumCB.isChecked():
            self.iLine.setValue(standard.rt)

        rtTol = int(self.rtDisplayEntry.text())
        self.plot.setXRange(standard.rt - rtTol, standard.rt + rtTol)
        self.plot.setYRange(0, globalmax)
        self.updateLinReg()
        return

    def extractEICs(self):
        mztol = float(str(self.mzTolEntry.text()))
        for s in self.standards:
            s.ll = s.mz - mztol
            s.hl = s.mz + mztol
            s.eicTraces = {}
            for f in self.dataFiles:
                s.eicTraces[f.name] = [[],[]]

        for f in self.dataFiles:
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
                    s.eicTraces[name][0].append(time)

                    eicInt = 0
                    mzsubset = np.where((mzs > s.ll) & (mzs < s.hl))
                    if mzsubset[0].shape[0] > 0: eicInt += np.sum(ints[mzsubset])
                    s.eicTraces[name][1].append(eicInt)

            f.scanTimes = np.asarray(f.scanTimes)
            f.scanIndices = np.asarray(f.scanIndices)

        for s in self.standards:
            for k, v in s.eicTraces.iteritems():
                v[0] = np.asarray(v[0])
                v[1] = np.asarray(v[1])

        self.refStandardsTable.selectRow(0)
        return

    ''' helper function '''
    def addData(self, d):
        item = QtGui.QTableWidgetItem()
        item.setData(QtCore.Qt.EditRole, d)
        return item

    def parseFileName(self, name):
        name = os.path.basename(name)
        name = name.split('.')[0].strip('.')
        return name

    def getSelectedSamples(self):
        highlightedRows = self.samplesTable.selectionModel().selectedRows()
        self.activeSamples = []
        for row in highlightedRows:
            highlightedRow = row.row()
            self.activeSamples.append( str(self.samplesTable.item(highlightedRow, 0).text()) )
        self.updatePlot()
        return

    def zeroFill(self, xData, yData):
        x = np.repeat(xData, 3)
        y = np.dstack((np.zeros(yData.shape[0]), yData, np.zeros(yData.shape[0]))).flatten()
        return x, y

    def clearTable(self, table):
        while table.rowCount() > 0:
            table.removeRow(0)
        return

def readMzXML(mzml_file, msLevel = 1):
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

    msrun = pymzml.run.Reader(str(mzml_file))
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

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    app.processEvents()

    window = TargetedSearch()

    screenShape = QtGui.QDesktopWidget().screenGeometry()
    window.resize(screenShape.width()*0.8, screenShape.height()*0.8)

    window.show()
    app.exec_()
