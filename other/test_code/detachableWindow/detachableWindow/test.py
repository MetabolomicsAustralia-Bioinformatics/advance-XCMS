import sys
from PyQt4 import QtCore, QtGui
from w1 import Ui_DockWidget as l1
from w2 import Ui_DockWidget as l2
from w3 import Ui_DockWidget as l3

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
            QtGui.QDockWidget.__init__(self)
            self.dock = parent()
            self.setupUi(self)
            return
    return Dock()

class Window(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('Dock Widgets')
        self.setTabPosition( QtCore.Qt.TopDockWidgetArea , QtGui.QTabWidget.North )
        self.setDockOptions( QtGui.QMainWindow.ForceTabbedDocks )


        self.dockList = []
        for lx in [l1,l2,l3]:
            #dock = Dock(lx)
            dock = makeDock(lx)
            dock.setAllowedAreas(QtCore.Qt.TopDockWidgetArea)
            self.addDockWidget(QtCore.Qt.TopDockWidgetArea, dock)
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
