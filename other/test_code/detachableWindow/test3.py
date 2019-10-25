
from PyQt4 import QtCore, QtGui

class Window(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('Dock Widgets')
        self.setTabPosition( QtCore.Qt.TopDockWidgetArea , QtGui.QTabWidget.North )
        self.setDockOptions( QtGui.QMainWindow.ForceTabbedDocks )

        self.dockList = []
        for dockName in 'First Second Third Fourth'.split():
            dock = QtGui.QDockWidget(dockName)
            dock.setWidget(QtGui.QListWidget())
            dock.setAllowedAreas(QtCore.Qt.TopDockWidgetArea)
            self.addDockWidget(QtCore.Qt.TopDockWidgetArea, dock)

            self.dockList.append( dock )


        if len(self.dockList) > 1:
            for index in range(0, len(self.dockList) - 1):
                self.tabifyDockWidget(self.dockList[index],self.dockList[index + 1])



if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec_()


