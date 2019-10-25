# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'eicExplorer.ui'
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
        DockWidget.resize(948, 856)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.featureMapRB = QtGui.QRadioButton(self.dockWidgetContents)
        self.featureMapRB.setObjectName(_fromUtf8("featureMapRB"))
        self.horizontalLayout_3.addWidget(self.featureMapRB)
        self.chromatogramRB = QtGui.QRadioButton(self.dockWidgetContents)
        self.chromatogramRB.setObjectName(_fromUtf8("chromatogramRB"))
        self.horizontalLayout_3.addWidget(self.chromatogramRB)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.plots = GraphicsLayoutWidget(self.dockWidgetContents)
        self.plots.setObjectName(_fromUtf8("plots"))
        self.verticalLayout_3.addWidget(self.plots)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.prevButton = QtGui.QPushButton(self.dockWidgetContents)
        self.prevButton.setObjectName(_fromUtf8("prevButton"))
        self.horizontalLayout.addWidget(self.prevButton)
        self.nextButton = QtGui.QPushButton(self.dockWidgetContents)
        self.nextButton.setObjectName(_fromUtf8("nextButton"))
        self.horizontalLayout.addWidget(self.nextButton)
        self.label = QtGui.QLabel(self.dockWidgetContents)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.rowsLE = QtGui.QLineEdit(self.dockWidgetContents)
        self.rowsLE.setObjectName(_fromUtf8("rowsLE"))
        self.horizontalLayout.addWidget(self.rowsLE)
        self.label_2 = QtGui.QLabel(self.dockWidgetContents)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.colsLE = QtGui.QLineEdit(self.dockWidgetContents)
        self.colsLE.setObjectName(_fromUtf8("colsLE"))
        self.horizontalLayout.addWidget(self.colsLE)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout_3, 0, 0, 1, 1)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        DockWidget.setWindowTitle(_translate("DockWidget", "EIC Explorer", None))
        self.featureMapRB.setText(_translate("DockWidget", "Feature Map", None))
        self.chromatogramRB.setText(_translate("DockWidget", "Chromatograms", None))
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

