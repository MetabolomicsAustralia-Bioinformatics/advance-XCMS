# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'w3.ui'
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
        DockWidget.resize(400, 300)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.gridLayout = QtGui.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.fontComboBox = QtGui.QFontComboBox(self.dockWidgetContents)
        self.fontComboBox.setObjectName(_fromUtf8("fontComboBox"))
        self.verticalLayout.addWidget(self.fontComboBox)
        self.comboBox_2 = QtGui.QComboBox(self.dockWidgetContents)
        self.comboBox_2.setObjectName(_fromUtf8("comboBox_2"))
        self.verticalLayout.addWidget(self.comboBox_2)
        self.comboBox = QtGui.QComboBox(self.dockWidgetContents)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.verticalLayout.addWidget(self.comboBox)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        DockWidget.setWindowTitle(_translate("DockWidget", "DockWidget", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    DockWidget = QtGui.QDockWidget()
    ui = Ui_DockWidget()
    ui.setupUi(DockWidget)
    DockWidget.show()
    sys.exit(app.exec_())

