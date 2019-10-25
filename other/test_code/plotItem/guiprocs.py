
from PyQt4 import QtCore, QtGui
import pyqtgraph as pg
try:
    import better_exceptions
except:
    pass

import plotTestUI

import sys
import random as rd


class guiProcs (QtGui.QMainWindow, plotTestUI.Ui_Form):

    def __init__ (self, parent = None):

        pg.setConfigOption('background','w')
        pg.setConfigOption('foreground','k')

        super(guiProcs,self).__init__(parent)
        self.setupUi(self)

        self.printItems()
        self.listItems.clicked.connect(self.printItems)
        self.add.clicked.connect(self.addPlot)
        self.remove.clicked.connect(self.removePlot)

        self.xData = []
        self.yData = []
        self.makeData()
        self.makePlots()

    def makePlots(self):
        self.dataPlot1 = pg.PlotItem()
        for i in range(len(self.xData)):
            self.dataPlot1.addItem(
                pg.PlotDataItem(x = self.xData[i], y = self.yData[i])
            )


    def makeData(self):
        n = 10
        for i in range(3):
            self.xData.append([rd.randint(0,10) for x in range(n)])
            self.yData.append([rd.randint(0,10) for x in range(n)])

    def main(self):
        self.show()

    def addPlot(self):
        self.plot.addItem(self.dataPlot1)

    def removePlot(self):
        self.plot.removeItem(self.dataPlot1)

    def printItems(self):
        print
        items = self.plot.scene().items()
        for i in items:
            print i
        print

def main():
    app = QtGui.QApplication(sys.argv)
    gui = guiProcs()
    gui.main()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
