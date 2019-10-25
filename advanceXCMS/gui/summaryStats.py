# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'summaryStats.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_DockWidget(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName(_fromUtf8("DockWidget"))
        DockWidget.resize(946, 750)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        DockWidget.setFont(font)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(self.dockWidgetContents)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.massAccuracyLayout = GraphicsLayoutWidget(self.groupBox)
        self.massAccuracyLayout.setObjectName(_fromUtf8("massAccuracyLayout"))
        self.gridLayout.addWidget(self.massAccuracyLayout, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(self.dockWidgetContents)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.rtDriftLayout = GraphicsLayoutWidget(self.groupBox_2)
        self.rtDriftLayout.setObjectName(_fromUtf8("rtDriftLayout"))
        self.gridLayout_2.addWidget(self.rtDriftLayout, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        DockWidget.setWindowTitle(_translate("DockWidget", "Results Summary", None))
        self.groupBox.setTitle(_translate("DockWidget", "Mass Accuracy", None))
        self.groupBox_2.setTitle(_translate("DockWidget", "Retention Time Drift", None))

from pyqtgraph import GraphicsLayoutWidget

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    DockWidget = QtGui.QDockWidget()
    ui = Ui_DockWidget()
    ui.setupUi(DockWidget)
    DockWidget.show()
    sys.exit(app.exec_())

