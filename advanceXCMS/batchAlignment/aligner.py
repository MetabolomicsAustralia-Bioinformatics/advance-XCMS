import os, sys, copy, pickle

from PyQt4 import QtCore, QtGui
import pyqtgraph as pg
import numpy as np

from advanceXCMS.shared.annotation import gen_library as gl

from xlsxwriter.workbook import Workbook
import alignPeaks2 as alignPeaks
from advanceXCMS.gui import batchAlignmentGUI
from advanceXCMS.shared import Common as common

from advanceXCMS.shared import commonClasses as commonClasses

# this is a hack to make sure objects pickled with prev versions acn still be imported
try:
    sys.path.append('/home/mleeming/Code/maProjects/eicClassifier/advanceXCMS/shared')
except:
    pass

try:
    import better_exceptions
except:
    pass


class Dialog(QtGui.QDialog):
    ''' Subclass QDialog and override resizeEvent method
        --> include table resize rows with each window resize
    '''
    def __init__(self, parent = None):
        super(Dialog, self).__init__(parent = parent)
        return

    def resizeEvent(self, event):
        self.consensusFeatures.resizeRowsToContents()
        self.batchDetails.resizeRowsToContents()
        return

class My_PolyLineSegment(pg.LineSegmentROI):
    # Used internally by PolyLineROI
    def __init__(self, *args, **kwds):
        self._parentHovering = False
        pg.LineSegmentROI.__init__(self, *args, **kwds)

    def setParentHover(self, hover):
        # set independently of own hover state
        if self._parentHovering != hover:
            self._parentHovering = hover
            self._updateHoverColor()

    def _makePen(self):
        if self.mouseHovering or self._parentHovering:
            return pg.functions.mkPen(255, 255, 0)
        else:
            return self.pen

    def hoverEvent(self, ev):
        # accept drags even though we discard them to prevent competition with parent ROI
        # (unless parent ROI is not movable)
        try:
            if self.parentItem().translatable:
                ev.acceptDrags(QtCore.Qt.LeftButton)
        except:
            return
        return pg.LineSegmentROI.hoverEvent(self, ev)


class MyROI(pg.PolyLineROI):
    ''' SubClass roi to override segClicked and add handle functions
    '''
    def segmentClicked(self):
        return
    def setMouseHover(self):
        return
    def setMouseHover(self, hover):
        return
    def addSegment(self, h1, h2, index=None):
        #seg = pg.graphicsItems.ROI._PolyLineSegment(handles=(h1, h2), pen=self.pen, parent=self, movable=False)
        seg = My_PolyLineSegment(handles=(h1, h2), pen=self.pen, parent=self, movable=False)
        if index is None:
            self.segments.append(seg)
        else:
            self.segments.insert(index, seg)
        seg.sigClicked.connect(self.segmentClicked)
        seg.setAcceptedMouseButtons(QtCore.Qt.LeftButton)
        seg.setZValue(self.zValue()+1)
        for h in seg.handles:
            h['item'].setDeletable(False)
            h['item'].setAcceptedMouseButtons(h['item'].acceptedMouseButtons() | QtCore.Qt.LeftButton) ## have these handles take left clicks too, so that handles cannot be added on top of other handles
        return

class BatchAlignment (Dialog, batchAlignmentGUI.Ui_Dialog):

    def __init__(self, parent = None):

        pg.setConfigOption('background','w')
        pg.setConfigOption('foreground','k')

        super(BatchAlignment, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Align Batches')
        self.batches = []
        self.consensus = []
        self.deletedConsensus = []
        self.libraryFile = None

        # add check boxes
        self.activeBatchesGrid = QtGui.QGridLayout()
        self.activeBatchesGroupBox.setLayout(self.activeBatchesGrid)

        ''' Table column size policy '''
        tables = [self.batchFileTable, self.batchDetails,
                  self.consensusFeatures, self.assignmentTable,
                  self.sampleDetails]

        for t in tables:
            t.verticalHeader().setVisible(False)
            t.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
            self.setTableHeaderPolicy(t)

        ''' Enable table sorting '''
        self.batchFileTable.setSortingEnabled(True)
        self.batchDetails.setSortingEnabled(True)
        self.sampleDetails.setSortingEnabled(True)

        ''' Splitter Ratios '''
        # self.splitter_2.setStretchFactor(10,0.6)
        self.splitter_5.setSizes([100,300])
        self.splitter_3.setSizes([600,200,600])
        #self.splitter_3.setStretchFactor(0, 0.5)

        self.batchCounter = 1
        self.preparePlots()
        self.connections()

        ''' Display Colours '''
        self.green = QtGui.QColor(151,252,198)
        self.red = QtGui.QColor(239,115,115)
        self.orange = QtGui.QColor(255, 205, 147)
        self.colorSet = ['b', 'm', 'y', 'k', 'c', 'r'] # k = black

        ''' for testing '''
#        self.loadBatches()
#        self.doAlignment()
#        self.doConsensusGroupAnnotation()

    def connections(self):
        self.loadBatchesButton.clicked.connect(self.loadBatches)
        self.consensusFeatures.itemSelectionChanged.connect(self.updateConsensusFeatureDisplays)
        self.roiLine.sigRegionChangeFinished.connect(self.setNewAcceptedFeature)
        self.sampleDetails.itemSelectionChanged.connect(self.updateEICPlot)
        self.sampleDetails.itemSelectionChanged.connect(self.updateMSPlot)
        self.filledOnly.toggled.connect(self.activeBatchesToggled)
        self.selectedSamplesOnly.toggled.connect(self.updateEICPlot)
        self.updateAssignment.clicked.connect(self.updateAcceptedAssignment)
        self.reIntegrateRegion.clicked.connect(self.doReintegration)
        self.restoreDefaultIntegrationButton.clicked.connect(self.restoreDefaultIntegration)
        self.selectLibraryFile.clicked.connect(self.getLibFile)
        self.doConsensusAnnotation.clicked.connect(self.doConsensusGroupAnnotation)
        self.runAlignmentButton.clicked.connect(self.doAlignment)
        self.browseResults.clicked.connect(self.getOutputFIleName)
        self.saveResults.clicked.connect(self.writeResutls)
        self.recoverMissingConsensusCandidatesButton.clicked.connect(self.recoverMissingConsensusCandidates)
        self.deleteConsensusGroupButton.clicked.connect(self.deleteConsensusFeature)
        self.undoDeleteConsensusGroupButton.clicked.connect(self.undoRemoveConsensusFeature)
        self.recoverALLMissingConsensusCandidatesButton.clicked.connect(self.recoverALLMissingConsensusCandidates)
        return


    def preparePlots(self):
        self.featureMapPlot = self.featureMap.addPlot()
        self.featureMapPlot.addLegend()
        self.featureMapPlot.setLabel(axis = 'left', text = 'Retention Time (s)')
        self.featureMapPlot.setLabel(axis = 'bottom', text = 'm/z')
        self.featureMapPlot.enableAutoScale()

        self.featureAlignmentViewBox = pg.ViewBox()
        self.roiPoints = []
        self.roiLine = MyROI(self.roiPoints, closed = False, movable = False, removable = False, pen = 'k')
        self.featureAlignmentViewBox.addItem(self.roiLine)
        self.featureAlignmentPlot = self.featureAlignment.addPlot(viewBox = self.featureAlignmentViewBox)
        self.featureAlignmentPlot.setLabel(axis = 'left', text = 'Retention Time (s)')
        self.featureAlignmentPlot.setLabel(axis = 'bottom', text = 'Batch Number')
        self.featureAlignmentPlot.enableAutoScale()

        self.intensityMapPlot = self.intensityMap.addPlot()
        self.intensityMapPlot.setLabel(axis = 'left', text = 'Intensity')
        self.intensityMapPlot.setLabel(axis = 'bottom', text = 'Sample Number')
        self.intensityMapPlot.enableAutoScale()

        self.eicPlot = self.eicTrace.addPlot()
        self.eicPlot.setLabel(axis = 'left', text = 'Intensity')
        self.eicPlot.setLabel(axis = 'bottom', text = 'Retention Time (s)')
        self.eicPlot.enableAutoScale()
        self.linReg = pg.LinearRegionItem()
        self.eicPlot.addItem(self.linReg)

        self.msPlot = self.msTrace.addPlot()
        self.msPlot.setLabel(axis = 'left', text = 'Intensity')
        self.msPlot.setLabel(axis = 'bottom', text = 'm/z')
        self.msPlot.enableAutoScale()
        return

    def setTableHeaderPolicy(self, table):
        tableHeader = table.horizontalHeader()
        cc = table.columnCount()
        for c in range(cc):
            tableHeader.setResizeMode(c, QtGui.QHeaderView.Stretch)
        return

    def getLibFile(self):
        inFile = QtGui.QFileDialog.getOpenFileName(self, "Load metabolite library file")
        print 'library file is:', inFile
        if str(inFile):
            self.libraryFileDisplay.setText(os.path.basename(str(inFile)))
            self.libraryFile = str(inFile)
        return

    def loadBatches(self):
        '''
        Read in data from pickled FeatureSet objects
        - Take features marked as Accepted only
        Add Batch entries to batch files table
        Add columns to batch tables
        '''

        # Select files
        inFiles = sorted([str(_) for _ in QtGui.QFileDialog.getOpenFileNames(self, 'Select Batch Files')])

        for inFile in inFiles:
            try:
                batch = pickle.load(open(inFile,'rb'))

                if isinstance(batch, list):
                    assert len(inFiles) == 1 and len(batch) == 3
                    print 'list'
                    self.batches, self.consensus, self.deletedConsensus = batch
                    break

                elif isinstance(batch, commonClasses.FeatureSet):
                    print 'featureset'

                    batch.batchCounter = self.batchCounter
                    batch.batchFileName = inFile
                    if not hasattr(batch, 'batchFileName'):
                        batch.addAttrToFeatures('batchFileName', inFile)
                    else:
                        print 'batch reference already present ---> skipping'

                        print 'batch file name is', batch.batchFileName
                        batch.batchFileName = batch.batchFileName.split('_accepted_only_XCG_batchCounter')[0]
                        print 'batch file name is', batch.batchFileName
                    batch.addAttrToFeatures('consensusGroup', -1)
                    batch.addAttrToFeatures('batchCounter', batch.batchCounter)
                    batch.addAttrToFeatures('usedInAlignmentGoup', 0)

                else:
                    print 'Skipping unknown file type:', str(inFile)
                    continue

            except Exception, e:
                print '-------------------------------------------'
                print 'WARNING: Unable to open file', inFile
                print '-------------------------------------------'
                print 'Exception:', str(e)
                print '-------------------------------------------'
                return

            # Need to save memory
            # --> move through batch and remove data for unaccepted or rejected features
            featuresToDelete = [fn for fn in batch.featureNums if batch.featureDict[fn].acceptedFeature != True]
            print 'length of feature dict before deletion:', len(batch.featureDict.keys())
            for ftd in featuresToDelete:
                del batch.featureDict[ftd]
                batch.featureNums.remove(ftd)
            print 'length of feature dict after deletion:', len(batch.featureDict.keys())

            pickle.dump(batch, open('%s_accepted_only_XCG_batchCounter_%s.p'%(inFile, self.batchCounter),'wb'))
            self.batches.append(batch)

            self.batchCounter += 1

        # complete setup
        self.doInitialisation()
        return

    def doInitialisation(self):
        ''' Add data from loaded files into display tables/plots
            - Called regardless of input type (.xfv, .xcg)
        '''

        # add data to feature map plot
        for i, batch in enumerate(self.batches):

            mz, rt = batch.getFeatureMapAndSummaryData(['avgmz','avgrt'], annotatedOnly = False)
            self.featureMapPlot.plot(
                mz, rt, pen = None,
                symbol = 'o',
                symbolBrush = self.colorSet[i],
                name = os.path.basename(batch.batchFileName)
            )

        # add to batch files table
        self.clearTable(self.batchFileTable)
        for rc, batch in enumerate(self.batches):
            self.batchFileTable.insertRow(rc)
            self.batchFileTable.setItem(rc, 0, self.addData(batch.batchCounter))
            self.batchFileTable.setItem(rc, 1, self.addData(os.path.basename(batch.batchFileName)))
            self.batchFileTable.setItem(rc, 2, self.addData(len(batch.featureNums)))

        self.batchFileTable.resizeRowsToContents()
        self.alignText(self.batchFileTable)

        self.updateBatchDetailsTable()
        self.prepareChromatogramPlot()
        self.addBatchActivationCheckBoxes()

        self.updateConsensusFeaturesTable()
        return

    def updateBatchDetailsTable(self):

        def checkConsensusGrouping(self, targetFeatureNumber, targetBatchID):
            for c in self.consensus:
                for v in c.acceptedFeatures.values():
                    try:
                        if v.featureNumber == targetFeatureNumber and v.batchCounter == targetBatchID:
                            return c.consensusID
                    except:
                        return -1
            return -1

        # add data to batch table
        self.clearTable(self.batchDetails)
        add = self.batchDetails.setItem
        rc = 0
        for batch in self.batches:
            for fn in batch.featureNums:
                f = batch.featureDict[fn]
                self.batchDetails.insertRow(rc)

                f.consensusGroup = checkConsensusGrouping(self, fn, f.batchCounter)

                #if consensusGroup:
                #    print consensusGroup
                add(rc, 0, self.addData(f.batchCounter))
                add(rc, 1, self.addData(fn))
                add(rc, 2, self.addData(f.consensusGroup))
                add(rc, 3, self.addData(f.acceptedAssignment.name if f.acceptedAssignment else ''))
                add(rc, 4, self.addData(f.acceptedAssignment.massError if f.acceptedAssignment else ''))
                add(rc, 5, self.addData(f.avgmz))
                add(rc, 6, self.addData(f.avgrt))
                add(rc, 7, self.addData(f.avginto))
                add(rc, 8, self.addData(f.numFilled))
                rc += 1

        self.batchDetails.resizeRowsToContents()
        self.alignText(self.batchDetails)
        return

    def deleteActivationCheckBoxes(self):
        # clear existing check boxes from layout
        for b in self.batches:
            if not hasattr(b, 'checkbox'): continue
            cb = b.checkbox
            self.activeBatchesGrid.removeWidget(cb)
            cb.deleteLater()
            del cb
            del b.checkbox
        return

    def addBatchActivationCheckBoxes(self):
        self.deleteActivationCheckBoxes()
        row = 0
        for i, batch in enumerate(self.batches):
            if i % 2 == 0: col = 0
            else: col = 1

            batch.checkbox = QtGui.QCheckBox()
            batch.checkbox.setChecked(True)
            batch.checkbox.setText('Batch %s' %batch.batchCounter)
            batch.checkbox.stateChanged.connect(self.activeBatchesToggled)
            self.activeBatchesGrid.addWidget(batch.checkbox, row, col)
            if col == 1:
                row += 1
        return

    def doConsensusGroupAnnotation(self):
        print '\nRunning consensus group annotation'
        print '--------------------------------------------------'

        if len(self.consensus) == 0:
            return
        if not self.libraryFile:
            print 'Please select library file'
            return
        try:
            # get input data
            ppmTol = float(self.annotationppmTol.text())
            rtTol = float(self.annotationrtTol.text())
        except:
            print 'Error in ppm or rt tolerance specification'
            return

        if self.posIonCB.isChecked():
            polarity = 'pos'
        elif self.negIonCB.isChecked():
            polarity = 'neg'
        else:
            print 'Error in ion mode selection'
            return

        gl.doAnnotation(self.consensus, self.libraryFile, ppmTol, rtTol, polarity, dataType = 'consensus')
        self.updateConsensusFeaturesTable()
        self.updateBatchDetailsTable()
        print '...Done\n'
        return

    def doAlignment(self):
        print '\nRunning alignment'
        print '--------------------------------------'
        ppmTol = float(str(self.ppmTol.text()))
        rtTol = float(str(self.rtTol.text()))
        print 'ppm error tolerance:', ppmTol
        print 'RT error tolerance', rtTol
        self.consensus = alignPeaks.doInitialAlignment(self.batches, rtTol, ppmTol)
        print 'Found alignments for %s feature groups' %len(self.consensus)
        self.updateConsensusFeaturesTable()
        return

    def updateConsensusFeaturesTable(self):

        self.consensusFeatures.itemSelectionChanged.disconnect()

        def isConflicted(tf, tfConsensusID):
            if tf == None: return False

            for c in self.consensus:
                if tfConsensusID == c.consensusID: continue
                acceptedFeatureInBatch = c.acceptedFeatures[tf.batchCounter]
                if tf == acceptedFeatureInBatch:
                    return True
            return False

        try:
            highlightedRows = int(str(self.consensusFeatures.selectionModel().selectedRows()[0].row()))
        except:
            highlightedRows = 0
        # clear current entries:
        self.clearTable(self.consensusFeatures)

        add = self.consensusFeatures.setItem
        for i, c in enumerate(self.consensus):
            self.consensusFeatures.insertRow(i)
            add(i, 0, self.addData(c.consensusID))
            add(i, 1, self.addData(c.consensusavgmz))
            add(i, 2, self.addData(c.consensusavgrt))
            add(i, 3, self.addData(c.consensusavgints))
            add(i, 4, self.addData(c.consensusintSTDEV))
            add(i, 5, self.addData(c.consensusnumfilled))
            add(i, 6, self.addData(c.acceptedAssignment.name if c.acceptedAssignment else ''))

        nextCol = 7
        while self.consensusFeatures.columnCount() > 7:
            self.consensusFeatures.removeColumn(7)
        for i, b in enumerate(self.batches):
            self.consensusFeatures.insertColumn(i+nextCol)
            for j, c in enumerate(self.consensus):
                accCandidate = c.acceptedFeatures[b.batchCounter]
                conflict = isConflicted(accCandidate, c.consensusID)
                numCandidates = len(c.consensusMap[b.batchCounter])
                add(j, i+nextCol, self.addData(numCandidates))
                # need to check that the accepted sample is not also accepted in any other consensus group
                if conflict: colour = self.orange
                else: colour = self.green if numCandidates != 0 else self.red
                self.consensusFeatures.item(j, i+nextCol).setBackground(colour)

        self.consensusFeatures.itemSelectionChanged.connect(self.updateConsensusFeatureDisplays)
        self.alignText(self.consensusFeatures)

        self.consensusFeatures.resizeRowsToContents()
        self.consensusFeatures.selectRow(highlightedRows)
        return

    def updateConsensusFeatureDisplays(self):
        ''' Called when the highlighted entry in the Consensus Features table is changed
        '''

        self.updateSampleTable()
        self.updateFeatureGroupingPlots()
        self.updateEICPlot()
        self.updateMSPlot()
        self.updateAssignmentsTable()
        return

    def updateAssignmentsTable(self):

        c = self.getHighlightedConsensusFeature()

        self.clearTable(self.assignmentTable)
        add = self.assignmentTable.setItem
        for i in range(len(c.assignmentCandidates)):
            self.assignmentTable.insertRow(i)
            add(i, 0, self.addData(c.assignmentCandidates[i].name))
            add(i, 1, self.addData(c.assignmentCandidates[i].massError))
            add(i, 2, self.addData(c.assignmentCandidates[i].rtError))
        self.alignText(self.assignmentTable)
        return

    def updateMSPlot(self):
        c = self.getHighlightedConsensusFeature()

        # get selected samples
        highlightedRows = self.sampleDetails.selectionModel().selectedRows()
        selectedSamples = [int(str(self.sampleDetails.item(i.row(),1).text())) for i in highlightedRows]
        selectedSamplesBatches = [int(str(self.sampleDetails.item(i.row(),0).text())) for i in highlightedRows]

        if len(selectedSamples) != 1: return

        self.msPlot.clear()
        sample = selectedSamples[0]
        batch = selectedSamplesBatches[0]

        for acceptedFeatureBatch in sorted(c.acceptedFeatures.keys()):
            if batch != acceptedFeatureBatch: continue
            acceptedFeature = c.acceptedFeatures[acceptedFeatureBatch]
            for sn in acceptedFeature.sampleNums:
                if sample != sn: continue
                f = acceptedFeature.samples[sn].accepted

                x,y = self.zeroFill(f.specMZs, f.specINTs)

                self.msPlot.plot(
                    x = x,
                    y = y,
                    pen = 'k'
                )

                text = pg.TextItem(text = '%.4f'%f.mz, color = 'k', anchor = (0.5,0))
                self.msPlot.addItem(text)
                text.setPos(f.mz,f.maxo + f.maxo*0.1)

        return

    def updateEICPlot(self):

        #
        c = self.getHighlightedConsensusFeature()

        # get selected samples
        highlightedRows = self.sampleDetails.selectionModel().selectedRows()
        selectedSamples = [int(str(self.sampleDetails.item(i.row(),1).text())) for i in highlightedRows]
        selectedSamplesBatches = [int(str(self.sampleDetails.item(i.row(),0).text())) for i in highlightedRows]
        plotDataItems = self.eicPlot.listDataItems()

        # data for linear region setting
        highlightedRTmin, highlightedRTmax = [], []

        plotDataItemCounter = 0
        for acceptedFeatureBatch in sorted(c.acceptedFeatures.keys()):
            # decide if batch is active
            batch = self.getBatchFromBatchCounterID(acceptedFeatureBatch)
            if not batch.checkbox.isChecked(): continue
            acceptedFeature = c.acceptedFeatures[acceptedFeatureBatch]
            if not hasattr(acceptedFeature, 'sampleNums'): continue

            for sn in acceptedFeature.sampleNums:
                if self.selectedSamplesOnly.isChecked() and sn not in selectedSamples:
                    continue
                if self.selectedSamplesOnly.isChecked() and acceptedFeatureBatch not in selectedSamplesBatches:
                    continue

                f = acceptedFeature.samples[sn].accepted

                if sn in selectedSamples and acceptedFeatureBatch in selectedSamplesBatches:
                    color = 'r'
                    # want to highlight ROI average for only selected samples
                    highlightedRTmax.append(f.rtmax - acceptedFeature.avgrt + c.consensusavgrt)
                    highlightedRTmin.append(f.rtmin - acceptedFeature.avgrt + c.consensusavgrt)
                else:
                    color = 'k'

                adjustedRTs = f.eicRTs - acceptedFeature.avgrt + c.consensusavgrt, # rescale x axis of all chromatograms
                plotDataItems[plotDataItemCounter].setData(
                    x = adjustedRTs[0],
                    y = f.eicINTs,
                    pen = color,
                    symbol = None
                )
                plotDataItemCounter += 1

        while plotDataItemCounter < len(plotDataItems):
            plotDataItems[plotDataItemCounter].setData(
                x = [],
                y = []
            )
            plotDataItemCounter += 1

        if len(highlightedRTmin) > 0:
            self.linReg.setRegion([sum(highlightedRTmin)/len(highlightedRTmin), sum(highlightedRTmax)/len(highlightedRTmax)])
        else:
            self.linReg.setRegion([0,1])
        return

    def activeBatchesToggled(self):
        c = self.getHighlightedConsensusFeature()

        self.updateSampleTable()
        self.updateEICPlot()
        try:
            self.updateSampleTable.selectRow(0)
        except:
            pass
        return

    def updateSampleTable(self):
        self.sampleDetails.itemSelectionChanged.disconnect()
        self.sampleDetails.setSortingEnabled(False)

        c = self.getHighlightedConsensusFeature()

        # add sample data to table
        self.clearTable(self.sampleDetails)
        r = 0
        add = self.sampleDetails.setItem

        # ensure dict is sorted before reading off sample data
        for acceptedFeatureBatch in sorted(c.acceptedFeatures.keys()):
            acceptedFeature = c.acceptedFeatures[acceptedFeatureBatch]

            # decide if batch is active
            batch = self.getBatchFromBatchCounterID(acceptedFeatureBatch)
            if not batch.checkbox.isChecked(): continue

            if not hasattr(acceptedFeature, 'sampleNums'): continue

            for sn in acceptedFeature.sampleNums:

                f = acceptedFeature.samples[sn].accepted
                if self.filledOnly.isChecked() and f.filled != 1:
                    continue

                self.sampleDetails.insertRow(r)
                add(r, 0, self.addData(acceptedFeature.batchCounter))
                add(r, 1, self.addData(f.sample))
                add(r, 2, self.addData(f.mz))
                add(r, 3, self.addData(f.rt))
                add(r, 4, self.addData(f.filled))
                add(r, 5, self.addData(f.into))
                add(r, 6, self.addData(f.maxo))
                r += 1

        self.sampleDetails.selectRow(0)
        self.alignText(self.sampleDetails)
        self.sampleDetails.setSortingEnabled(True)
        self.sampleDetails.itemSelectionChanged.connect(self.updateEICPlot)
        self.sampleDetails.itemSelectionChanged.connect(self.updateMSPlot)
        return

    def updateFeatureGroupingPlots(self):

        c = self.getHighlightedConsensusFeature()

        self.featureAlignmentPlot.clear()
        self.intensityMapPlot.clear()

        # do feature alignment first
        # --> get all points for any potential matches

        batches, rts, samples, ints = self.getAllMatchesPlotData(c)
        self.featureAlignmentPlot.plot(batches,rts, pen = None, symbol = 'o')

        # plot intensity map
        # get ints for samples in accepted features
        self.intensityMapPlot.plot(samples, ints, pen = None, symbol = 'o')

        self.roiPoints = []
        # ensure dict is sorted before reading off sample data
        for acceptedFeatureBatch in sorted(c.acceptedFeatures.keys()):
            try:
                af = c.acceptedFeatures[acceptedFeatureBatch]
                self.roiPoints.append([af.batchCounter, af.avgrt])
            except AttributeError:
                continue
        # add region of interest line
        self.roiLine.sigRegionChangeFinished.disconnect(self.setNewAcceptedFeature)
        self.roiLine.setPoints(self.roiPoints)
        self.roiLine.sigRegionChangeFinished.connect(self.setNewAcceptedFeature)
        return

    def setNewAcceptedFeature(self):
        print
        print 'update accepted consensus feature'

        c = self.getHighlightedConsensusFeature()

        handles = self.roiLine.getLocalHandlePositions()
        state = self.roiLine.getState()
        self.roiPoints = []

        # need to get a list of all possible points
        for i,a in enumerate(state['points']):
            rx = a.x()
            ry = a.y()

            batch = int(round(rx))
            candidates = c.consensusMap[batch]

            rts, features = self.getConsensusCandidatesFromSpecificBatch(
                batch, candidates
            )

            miny = np.argmin(np.abs(rts - ry))

            self.roiPoints.append([batch, rts[miny]])
            c.acceptedFeatures[batch] = features[miny]

            # recalc group metadata
            c.getMetaData()
        self.updateConsensusFeaturesTable()
        self.updateConsensusFeatureDisplays()
        return

    def updateAcceptedAssignment(self):
        # get selected consensus candidate
        c = self.getHighlightedConsensusFeature()

        # get selected annotation
        highlightedRow = int(str(self.assignmentTable.selectionModel().selectedRows()[0].row()))
        newAssignment = str(self.assignmentTable.item(highlightedRow,0).text())

        for ca in c.assignmentCandidates:
            if ca.name == newAssignment:
                c.acceptedAssignment = ca
                break

        #self.consensusFeatures.itemSelectionChanged.disconnect()
        self.updateConsensusFeaturesTable()
        #self.consensusFeatures.itemSelectionChanged.connect(self.updateConsensusFeatureDisplays)
        return

    def doReintegration(self):
        # get ROI boundaries
        low,high = self.linReg.getRegion()

        # get selected features
        c = self.getHighlightedConsensusFeature()

        # get selected samples
        highlightedRows = self.sampleDetails.selectionModel().selectedRows()
        selectedSamples = [int(str(self.sampleDetails.item(i.row(),1).text())) for i in highlightedRows]
        selectedSamplesBatches = [int(str(self.sampleDetails.item(i.row(),0).text())) for i in highlightedRows]

        def getBaseLineSubtract(m, b, x):
            return m*x + b

        for acceptedFeatureBatch in sorted(c.acceptedFeatures.keys()):
            # decide if batch is active
            batch = self.getBatchFromBatchCounterID(acceptedFeatureBatch)
            if not batch.checkbox.isChecked(): continue

            acceptedFeature = c.acceptedFeatures[acceptedFeatureBatch]
            for sn in acceptedFeature.sampleNums:
                if sn not in selectedSamples:
                    continue
                if acceptedFeatureBatch not in selectedSamplesBatches:
                    continue

                f = acceptedFeature.samples[sn].accepted

                '''
                Be careful here:
                    - EIC RTs in plot have been adjusted to be centered at the consensus group avg RT
                    - This adjustment is reflected in the ROI boundaries
                    - Need to reverse this before doing integration
                '''
                adjlow = low - c.consensusavgrt + acceptedFeature.avgrt
                adjhigh = high - c.consensusavgrt + acceptedFeature.avgrt

                mask = np.where(
                    (f.eicRTs > adjlow) & (f.eicRTs < adjhigh)
                )

                # save default integrations if not present
                if not hasattr(f, 'originalrtmax'):
                    f.originalIntO = copy.deepcopy(f.into)
                    f.originalMaxO = copy.deepcopy(f.maxo)
                    f.originalrtmin = copy.deepcopy(f.rtmin)
                    f.originalrtmax = copy.deepcopy(f.rtmax)

                eicRTsub = f.eicRTs[mask]
                eicINTsub = f.eicINTs[mask]

                lowRT, highRT = eicRTsub[0], eicRTsub[-1]
                lowInt, highInt = eicINTsub[0], eicINTsub[-1]

                m = (highInt - lowInt) / (highRT - lowRT)
                b = lowInt - m*lowRT

#                baseArea = 0
#                newArea = 0
#                for p in range(eicRTsub.shape[0]):
#                    rt, intensity = eicRTsub[p], eicINTsub[p]
#                    base = getBaseLineSubtract(m,b,rt)
#                    new = intensity - base
#                    newArea += new
#                    baseArea += base
#
#                if newArea < baseArea:
#                    newArea = baseArea

                newArea = 0
                for p in range(eicRTsub.shape[0]):
                    rt, intensity = eicRTsub[p], eicINTsub[p]
                    base = getBaseLineSubtract(m,b,rt)
                    new = intensity - base
                    newArea += new

                if newArea < 0:
                    newArea = 0

                #print 'old:', f.into, 'new:', int(newArea)
                f.into = int(newArea)
                f.rtmin = adjlow
                f.rtmax = adjhigh

            # recalculate batch metadata
            acceptedFeature.getMetaData()

        # recalculate consensus metadata
        c.getMetaData(doannotation = False)

        self.updateConsensusFeaturesTable()
        self.updateSampleTable()
        return

    def restoreDefaultIntegration(self):
        c = self.getHighlightedConsensusFeature()

        for acceptedFeatureBatch in sorted(c.acceptedFeatures.keys()):
            # decide if batch is active
            batch = self.getBatchFromBatchCounterID(acceptedFeatureBatch)

            acceptedFeature = c.acceptedFeatures[acceptedFeatureBatch]
            for sn in acceptedFeature.sampleNums:
                f = acceptedFeature.samples[sn].accepted

                # account for samples that have not yet been reIntegrated
                if not hasattr(f, 'originalrtmax'): continue

                f.into = copy.deepcopy(f.originalIntO)
                f.maxo = copy.deepcopy(f.originalMaxO)
                f.rtmin = copy.deepcopy(f.originalrtmin)
                f.rtmax = copy.deepcopy(f.originalrtmax)

            # recalculate batch metadata
            acceptedFeature.getMetaData()

        print
        print c.consensusavgints
        # recalculate consensus averages
        c.getMetaData(doannotation = False)
        print c.consensusavgints
        print

        self.updateConsensusFeaturesTable()
        self.updateSampleTable()
        return

    def getOutputFIleName(self):
        fileName = str(QtGui.QFileDialog.getSaveFileName(self, 'Write Results File', selectedFilter='*.xvf'))
        self.outputFileName.setText(fileName)
        return

    def writeResutls(self):
        outputFile = str(self.outputFileName.text())

        if outputFile == '':
            return

        of1 = open(outputFile, 'wt')

        # want columns as individual columns
        # and rows as samples
        data = []

        def getConsensusWithoutGaps(consensus):
            for i, c in enumerate(consensus):
                gaps = c.areTheereBatchGaps()
                if len(gaps) == 0:
                    return i

        titleBatch = getConsensusWithoutGaps(self.consensus)

        names = ['# Metabolite', '# RT (s)', '# m/z']
        for acceptedFeatureBatch in sorted(self.consensus[titleBatch].acceptedFeatures.keys()):
            acceptedFeature = self.consensus[titleBatch].acceptedFeatures[acceptedFeatureBatch]
            for sn in acceptedFeature.sampleNums:
                f = acceptedFeature.samples[sn].accepted
                names.append(os.path.basename(f.sampleName))
        data.append(names)

        for c in self.consensus:
            if len(c.areTheereBatchGaps()) > 0: continue
            try:
                name = c.acceptedAssignment.name
            except AttributeError:
                name = '-'
            cData = [name, c.consensusavgrt, c.consensusavgmz]

            # ensure dict is sorted before reading off sample data
            for acceptedFeatureBatch in sorted(c.acceptedFeatures.keys()):
                acceptedFeature = c.acceptedFeatures[acceptedFeatureBatch]
                for sn in acceptedFeature.sampleNums:
                    f = acceptedFeature.samples[sn].accepted
                    cData.append(f.into)
            data.append(cData)

        dataT = zip(*data)
        for d in dataT:
            of1.write('%s\n' %(', '.join([str(i) for i in d])))
        of1.close()

        # write pickle object
        if '.' in outputFile:
            outputFile = outputFile.split('.')[0] + '.pickle'
        else:
            outputFile += '.pickle'


        '''
        Note:
          -  batch activation checkboxes are saved to the consensusgroup batches
          -  these are pyqt objects and cannot be pickled
          -  need to remove them first
        '''

        self.deleteActivationCheckBoxes()

        pickle.dump([self.batches, self.consensus, self.deletedConsensus], open( outputFile, "wb" ) )

        self.addBatchActivationCheckBoxes()
        return


    def recoverALLMissingConsensusCandidates(self):
        '''
        '''

        fullBatchFileNames = [b.batchFileName for b in self.batches]

        for fbn in fullBatchFileNames:
            # get batch with unaccepted features only
            print '\n Processing recovery for batch', fbn
            print '-------------------------------------------------------------'

            fullBatch = pickle.load(open(fbn, 'rb'))



            for i, c in enumerate(self.consensus):
                print 'Processing consensus item:', i
                targetMZ = c.consensusavgmz

                ppm = float(50.0)
                factor = ppm / 1000000

                lowMZ = float(targetMZ) * (1 - factor)
                highMZ = float(targetMZ) * (1 + factor)

                for acceptedFeatureBatch in sorted(c.acceptedFeatures.keys()):

                    # get batch with accepted features only
                    batch = self.getBatchFromBatchCounterID(acceptedFeatureBatch)


                    if batch.batchFileName != fbn:
                        print 'batch name mismatch --> skipping'
                        continue

                    # go through samples and find feature near toleranes
                    for fn in fullBatch.featureNums:
                        f = fullBatch.featureDict[fn]
                        if f.avgmz > lowMZ and f.avgmz < highMZ:

                            featureNumber = f.featureNumber
                            if featureNumber not in c.consensusMap[acceptedFeatureBatch]:
                                print '    Candidate not in consensusMap, adding...'
                                c.consensusMap[acceptedFeatureBatch].append(featureNumber)

                                f.consensusGroup = c.consensusID
                                f.batchCounter = acceptedFeatureBatch

                                # add accepted features for cases where no candidates previously existed
                                if c.acceptedFeatures[acceptedFeatureBatch] == None:
                                    print '\n----------------------------------------------'
                                    print 'Recovering missing consensus feature'
                                    print '\n----------------------------------------------'
                                    c.acceptedFeatures[acceptedFeatureBatch] = f
                                    c.getMetaData()

                                if featureNumber not in batch.featureDict.keys():
                                    print '    Candidate not in batch feature dict, adding...'
                                    batch.featureDict[featureNumber] = f

            del fullBatch

        self.updateConsensusFeatureDisplays()
        self.updateConsensusFeaturesTable()
        return


    def recoverMissingConsensusCandidates(self):
        '''
        '''
        c = self.getHighlightedConsensusFeature()


        targetMZ = c.consensusavgmz

        ppm = float(50.0)
        factor = ppm / 1000000

        lowMZ = float(targetMZ) * (1 - factor)
        highMZ = float(targetMZ) * (1 + factor)

        for acceptedFeatureBatch in sorted(c.acceptedFeatures.keys()):

            # get batch with accepted features only
            batch = self.getBatchFromBatchCounterID(acceptedFeatureBatch)

            # get batch with unaccepted features only
            fullBatch = pickle.load(open(batch.batchFileName, 'rb'))
            print '\n Processing recovery for batch', acceptedFeatureBatch
            print '-------------------------------------------------------------'
            print 'num entries in full batch:', len(fullBatch.featureNums)
            # go through samples and find feature near toleranes
            for fn in fullBatch.featureNums:
                f = fullBatch.featureDict[fn]
                if f.avgmz > lowMZ and f.avgmz < highMZ:

                    featureNumber = f.featureNumber
                    print 'Original batch file name:', batch.batchFileName
                    print 'Found candidate', featureNumber
                    print 'target mz:', targetMZ, 'candidate mz:', f.avgmz
                    print 'consensusMap batch entries are\n',c.consensusMap[acceptedFeatureBatch]
                    if featureNumber not in c.consensusMap[acceptedFeatureBatch]:
                        print '    Candidate not in consensusMap, adding...'


                        f.consensusGroup = c.consensusID
                        f.batchCounter = acceptedFeatureBatch

                        c.consensusMap[acceptedFeatureBatch].append(featureNumber)
                        # add accepted features for cases where no candidates previously existed
                        if c.acceptedFeatures[acceptedFeatureBatch] == None:
                            c.acceptedFeatures[acceptedFeatureBatch] = f
                            c.getMetaData()

                        print '    FeatureSet batch entries are\n', batch.featureDict.keys()
                        if featureNumber not in batch.featureDict.keys():
                            print '    Candidate not in batch feature dict, adding...'
                            batch.featureDict[featureNumber] = f

        self.updateConsensusFeatureDisplays()
        self.updateConsensusFeaturesTable()
        return

    def deleteConsensusFeature(self):
        c = self.getHighlightedConsensusFeature()

        index = None
        for i, entry in enumerate(self.consensus):
            if entry.consensusID == c.consensusID:
                index = i
                break

        self.deletedConsensus.append(self.consensus[index])
        del self.consensus[index]
        self.updateConsensusFeaturesTable()
        return

    def undoRemoveConsensusFeature(self):
        try:
            self.consensus.append(self.deletedConsensus.pop())
        except IndexError:
            return
        self.consensus.sort(key = lambda c: c.consensusID)
        self.updateConsensusFeaturesTable()
        return

    ''' Helper functions
    '''
    def addData(self, d):
        item = QtGui.QTableWidgetItem()
        item.setData(QtCore.Qt.EditRole, d)
        return item

    def clearTable(self, table):
        while table.rowCount() > 0:
            table.removeRow(0)
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

    def getConsensusObjectByID(self, ID):
        for c in self.consensus:
            if c.consensusID == ID:
                return c

    def getAllMatchesPlotData(self, c):
        batches, rts = [],[]
        for b in self.batches:
            for fn in c.consensusMap[b.batchCounter]:
                batches.append(b.batchCounter)
                rts.append(b.featureDict[fn].avgrt)

        samples, ints = [],[]
        i = 1

        # ensure dict is sorted before reading off sample data
        for acceptedFeatureBatch in sorted(c.acceptedFeatures.keys()):
            af = c.acceptedFeatures[acceptedFeatureBatch]
            # af == feature objects of accetped candidates
            try:
                batch_ints = af.getAcceptedCandidateData(['into'])[0]
            except AttributeError:
                continue

            ints += batch_ints
            for j in range(len(batch_ints)):
                samples.append(i)
                i += 1

        return batches, rts, samples, ints

    def getConsensusCandidatesFromSpecificBatch(self, batch, targetFeatureNums):
        for b in self.batches:
            if b.batchCounter != batch: continue
            b.getMetaData()
            features = []
            for fn in b.featureNums:
                if fn in targetFeatureNums:
                    features.append(b.featureDict[fn])

            rts = np.asarray([_.avgrt for _ in features])
            return rts, features

    def getTotalNumSamples(self):
        nSamples = 0
        for batch in self.batches:
            for fn in batch.featureNums:
                nSamples += len(batch.featureDict[fn].sampleNums)
                break
        return nSamples

    def prepareChromatogramPlot(self):
        for n in range(self.getTotalNumSamples()):
            self.eicPlot.addItem(pg.PlotDataItem())
        return

    def getBatchFromBatchCounterID(self, batchCounter):
        for b in self.batches:
            if b.batchCounter == batchCounter:
                return b

    def getHighlightedConsensusFeature(self):
        highlightedRows = int(str(self.consensusFeatures.selectionModel().selectedRows()[0].row()))
        selectedConsensusGroupID = int(self.consensusFeatures.item(highlightedRows,0).text())
        return self.getConsensusObjectByID(selectedConsensusGroupID)

    def zeroFill(self, xData, yData):
        x = np.repeat(xData, 3)
        y = np.dstack((np.zeros(yData.shape[0]), yData, np.zeros(yData.shape[0]))).flatten()
        return x, y

def main():
    app = QtGui.QApplication(sys.argv)
    gui = BatchAlignment()
    gui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
