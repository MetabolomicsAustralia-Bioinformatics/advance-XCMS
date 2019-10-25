import numpy as np
from PyQt4 import QtCore, QtGui
import pyqtgraph as pg
import sys
import better_exceptions

import regionSelectGUI

from pyqtgraph.Point import Point
from pyqtgraph.graphicsItems.ItemGroup import ItemGroup
from pyqtgraph.Qt import QtGui, QtCore
from matplotlib.mlab import inside_poly
from pyqtgraph.graphicsItems import ScatterPlotItem



class CustomViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        pg.ViewBox.__init__(self, *args, **kwds)
        self.setMouseMode(self.RectMode)

    ## reimplement right-click to zoom out
    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton:
            self.autoRange()
            print ev

    def mouseDragEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton:
            ev.ignore()
        else:
            pg.ViewBox.mouseDragEvent(self, ev)

class MyViewBox(pg.ViewBox):
    # create custom signal that is emitted when
    # a rectangle is drawn
    # returns two lists
    mapSelectionChanged = QtCore.pyqtSignal(list, list)

    def mouseDragEvent(self, ev):

        if ev.button() == QtCore.Qt.RightButton:
            ev.ignore()
        else:
            pg.ViewBox.mouseDragEvent(self, ev)

        ev.accept()
        pos = ev.pos()
        if ev.button() == QtCore.Qt.RightButton:

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

class guiProcs (QtGui.QMainWindow, regionSelectGUI.Ui_MainWindow):
    def __init__(self, parent = None):

        pg.setConfigOption('background','w')
        pg.setConfigOption('foreground','k')

        super(guiProcs,self).__init__(parent)
        self.setupUi(self)

        x = np.random.rand(10)*1000
        y = np.random.rand(10)*100

        self.plot1 = self.plot.addPlot(
            col = 1, row = 1,
            viewBox = MyViewBox()
        )

        # connect to custom signal
        self.plot1.vb.mapSelectionChanged.connect(self.success)

        self.plot1.plot(x,y, symbol = 'o', symbolPen = 'r', pen = None, symbolBrush = 'r' )

    def success(self, data, highlightedPointsIndices):
        print
        print 'highlighted points are:'
        for i in highlightedPointsIndices:
            print data[i]

    def printResults(self, r):
        print 'Results are', r

    def main(self):
        self.show()


def main():
    app = QtGui.QApplication(sys.argv)
    gui = guiProcs()
    gui.main()
    sys.exit(app.exec_())


if __name__ == '__main__':
#    multiprocessing.freeze_support()
    main()
