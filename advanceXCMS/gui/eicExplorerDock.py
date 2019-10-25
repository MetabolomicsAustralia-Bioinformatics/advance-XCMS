# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'eicExplorerDock.ui'
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
        DockWidget.resize(841, 747)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        DockWidget.setFont(font)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.eicExplorerLayout = GraphicsLayoutWidget(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.eicExplorerLayout.setFont(font)
        self.eicExplorerLayout.setObjectName(_fromUtf8("eicExplorerLayout"))
        self.verticalLayout_3.addWidget(self.eicExplorerLayout)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.prevButton = QtGui.QPushButton(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.prevButton.setFont(font)
        self.prevButton.setObjectName(_fromUtf8("prevButton"))
        self.horizontalLayout.addWidget(self.prevButton)
        self.nextButton = QtGui.QPushButton(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.nextButton.setFont(font)
        self.nextButton.setObjectName(_fromUtf8("nextButton"))
        self.horizontalLayout.addWidget(self.nextButton)
        spacerItem = QtGui.QSpacerItem(200, 20, QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtGui.QLabel(self.dockWidgetContents)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.numRows = QtGui.QSpinBox(self.dockWidgetContents)
        self.numRows.setProperty("value", 4)
        self.numRows.setObjectName(_fromUtf8("numRows"))
        self.horizontalLayout.addWidget(self.numRows)
        self.label_2 = QtGui.QLabel(self.dockWidgetContents)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.numCols = QtGui.QSpinBox(self.dockWidgetContents)
        self.numCols.setProperty("value", 2)
        self.numCols.setObjectName(_fromUtf8("numCols"))
        self.horizontalLayout.addWidget(self.numCols)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout_3, 0, 0, 1, 1)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        DockWidget.setWindowTitle(_translate("DockWidget", "EIC Explorer", None))
        self.prevButton.setText(_translate("DockWidget", "Previous", None))
        self.nextButton.setText(_translate("DockWidget", "Next", None))
        self.label.setText(_translate("DockWidget", "rows", None))
        self.label_2.setText(_translate("DockWidget", "cols", None))

from pyqtgraph import GraphicsLayoutWidget

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    DockWidget = QtGui.QDockWidget()
    ui = Ui_DockWidget()
    ui.setupUi(DockWidget)
    DockWidget.show()
    sys.exit(app.exec_())

