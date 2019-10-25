
from PyQt4 import QtCore, QtGui
import pyqtgraph as pg
try:
    import better_exceptions
except:
    pass

import plotTestUI

import sys
import random as rd
import numpy as np

class guiProcs (QtGui.QMainWindow, plotTestUI.Ui_Form):

    def __init__ (self, parent = None):

        pg.setConfigOption('background','w')
        pg.setConfigOption('foreground','k')

        super(guiProcs,self).__init__(parent)
        self.setupUi(self)

    #    self.printItems()
    #    self.listItems.clicked.connect(self.printItems)
    #    self.add.clicked.connect(self.addPlot)
    #    self.remove.clicked.connect(self.removePlot)
        self.clear.clicked.connect(self.clearPlots)
        self.add.clicked.connect(self.addData)
        self.UpdateData.clicked.connect(self.updateData)
        self.rows.textChanged.connect(self.redrawPlotLayout)
        self.cols.textChanged.connect(self.redrawPlotLayout)

        self.xData = []
        self.yData = []

        self.plots = []

        self.redrawPlotLayout()

    def addData(self):
        return
    def updateData(self):
        for p in self.plots:

            for item in p.listDataItems():
                p.removeItem(item)

            for c in ['r','b','k']:
                x,y = self.makeData()
                p.addItem(
                    pg.PlotDataItem(x = x, y = y, pen = c)
                )
        return

    def redrawPlotLayout(self):
        self.clearPlots()
        self.plots = []
        try:
            rows = int(self.rows.text())
            cols = int(self.cols.text())
        except:
            return

        for r in range(rows):
            for c in range(cols):
                plt = self.plotArea.addPlot(row = r, col = c)
                self.plots.append(plt)
        return

    def clearPlots(self):
        for item in self.plots:
            self.plotArea.removeItem(item)
        return

    def makeData(self):
        n = 10
        x = np.array([rd.randint(0,10) for _ in range(n)])
        y = np.array([rd.randint(0,10) for _ in range(n)])
        return x, y

    def main(self):
        self.show()

    def addPlot(self):
        self.plot.addItem(self.dataPlot1)

    def removePlot(self):
        self.plot.removeItem(self.dataPlot1)

    def printItems(self):
        items = self.plot.scene().items()
        for i in items:
            print i
        return

def main():
    app = QtGui.QApplication(sys.argv)
    gui = guiProcs()
    gui.main()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
