import sys
from PyQt4 import QtCore, QtGui
from eicExplorerDock import Ui_DockWidget as Eed
from featureMapDock import Ui_DockWidget as Fmd
from peakRecoveryDock import Ui_DockWidget as Prd
from filesAndFeaturesWidget import Ui_Form as Ffw


'''
https://stackoverflow.com/questions/3531031/qmainwindow-with-only-qdockwidgets-and-no-central-widget

'''
#
#class D1 (QtGui.QDockWidget, Ui_DockWidget):
#    def __init__(self):
#        QtGui.QDockWidget.__init__(self)
#        self.dock = Ui_DockWidget()
#        self.dock.setupUi(self)
#
'''
https://stackoverflow.com/questions/18683097/pass-a-parent-class-as-an-argument
'''
def makeDock(parent):
    class Dock (QtGui.QDockWidget, parent):
        def __init__(self):
            pg.setconfigoption('background','w')
            pg.setconfigoption('foreground','k')
            QtGui.QDockWidget.__init__(self)
            self.dock = parent()
            self.setupUi(self)
            return
    return Dock()

class CentralWidget(QtGui.QWidget, Ffw):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.widget = Ffw()
        self.setupUi(self)
        return

class Window(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('Dock Widgets')
        self.setTabPosition( QtCore.Qt.TopDockWidgetArea , QtGui.QTabWidget.North )
        self.setDockOptions( QtGui.QMainWindow.ForceTabbedDocks )

        self.FFW = CentralWidget()
        self.setCentralWidget(self.FFW)

        self.dockList = []
        for lx in [Eed, Fmd, Prd]:
            #dock = Dock(lx)
            dock = makeDock(lx)
            #dock.setAllowedAreas(QtCore.Qt.TopDockWidgetArea)
            self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock)
            self.dockList.append(dock)


        if len(self.dockList) > 1:
            for index in range(len(self.dockList)-1):
                self.tabifyDockWidget(self.dockList[index], self.dockList[index + 1])
#        dock = D1()

#        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, dock)
#
#        dock = w1.Ui_DockWidget()
#        dock.setupUi(self)
#


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec_()
