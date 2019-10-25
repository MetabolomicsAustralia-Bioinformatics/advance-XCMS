# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plotTestUI.ui'
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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(747, 788)
        self.plot = GraphicsLayoutWidget(Form)
        self.plot.setGeometry(QtCore.QRect(90, 60, 581, 581))
        self.plot.setObjectName(_fromUtf8("plot"))
        self.listItems = QtGui.QPushButton(Form)
        self.listItems.setGeometry(QtCore.QRect(350, 710, 99, 27))
        self.listItems.setObjectName(_fromUtf8("listItems"))
        self.add = QtGui.QPushButton(Form)
        self.add.setGeometry(QtCore.QRect(140, 680, 99, 27))
        self.add.setObjectName(_fromUtf8("add"))
        self.remove = QtGui.QPushButton(Form)
        self.remove.setGeometry(QtCore.QRect(470, 660, 99, 27))
        self.remove.setObjectName(_fromUtf8("remove"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.listItems.setText(_translate("Form", "listItems", None))
        self.add.setText(_translate("Form", "add", None))
        self.remove.setText(_translate("Form", "remove", None))

from pyqtgraph import GraphicsLayoutWidget

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

