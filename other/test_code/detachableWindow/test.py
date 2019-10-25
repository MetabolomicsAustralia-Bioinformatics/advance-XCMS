
'''
See this SO question
https://stackoverflow.com/questions/14872763/how-to-pop-out-a-separate-window-from-a-tabwidget-in-pyside-qt

'''
import sys
from PyQt4 import QtGui, QtCore


class Tab(QtGui.QWidget):
    popOut = QtCore.pyqtSignal(QtGui.QWidget)
    popIn = QtCore.pyqtSignal(QtGui.QWidget)

    def __init__(self, parent=None):
        super(Tab, self).__init__(parent)
        print 'Tab created'
        popOutButton = QtGui.QPushButton('Pop Out')
        popOutButton.clicked.connect(lambda: self.popOut.emit(self))
        popInButton = QtGui.QPushButton('Pop In')
        popInButton.clicked.connect(lambda: self.popIn.emit(self))

        layout = QtGui.QHBoxLayout(self)
        layout.addWidget(popOutButton)
        layout.addWidget(popInButton)


class Window(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__()

        self.button = QtGui.QPushButton('Add Tab')
        self.button.clicked.connect(self.createTab)
        self._count = 0
        self.tab = QtGui.QTabWidget()
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.button)
        layout.addWidget(self.tab)

    def createTab(self):
        tab = Tab()
        tab.setWindowTitle('%d' % self._count)
        tab.popIn.connect(self.addTab)
        tab.popOut.connect(self.removeTab)
        self.tab.addTab(tab, '%d' % self._count)
        self._count += 1

    def addTab(self, widget):
        print 'addTab'
        if self.tab.indexOf(widget) == -1:
            widget.setWindowFlags(QtCore.Qt.Widget)
            self.tab.addTab(widget, widget.windowTitle())

    def removeTab(self, widget):
        print 'removeTab'
        index = self.tab.indexOf(widget)
        if index != -1:
            self.tab.removeTab(index)
            widget.setWindowFlags(QtCore.Qt.Window)
            widget.show()


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    w = Window()
    w.show()

    sys.exit(app.exec_())
