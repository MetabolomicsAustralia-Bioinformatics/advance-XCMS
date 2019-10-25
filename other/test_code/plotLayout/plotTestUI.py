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
        self.widget = QtGui.QWidget(Form)
        self.widget.setGeometry(QtCore.QRect(90, 60, 591, 681))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.plotArea = GraphicsLayoutWidget(self.widget)
        self.plotArea.setObjectName(_fromUtf8("plotArea"))
        self.verticalLayout_2.addWidget(self.plotArea)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.add = QtGui.QPushButton(self.widget)
        self.add.setObjectName(_fromUtf8("add"))
        self.horizontalLayout_3.addWidget(self.add)
        self.remove = QtGui.QPushButton(self.widget)
        self.remove.setObjectName(_fromUtf8("remove"))
        self.horizontalLayout_3.addWidget(self.remove)
        self.listItems = QtGui.QPushButton(self.widget)
        self.listItems.setObjectName(_fromUtf8("listItems"))
        self.horizontalLayout_3.addWidget(self.listItems)
        self.clear = QtGui.QPushButton(self.widget)
        self.clear.setObjectName(_fromUtf8("clear"))
        self.horizontalLayout_3.addWidget(self.clear)
        self.UpdateData = QtGui.QPushButton(self.widget)
        self.UpdateData.setObjectName(_fromUtf8("UpdateData"))
        self.horizontalLayout_3.addWidget(self.UpdateData)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.rows = QtGui.QLineEdit(self.widget)
        self.rows.setObjectName(_fromUtf8("rows"))
        self.horizontalLayout.addWidget(self.rows)
        self.horizontalLayout_4.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(self.widget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.cols = QtGui.QLineEdit(self.widget)
        self.cols.setObjectName(_fromUtf8("cols"))
        self.horizontalLayout_2.addWidget(self.cols)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.add.setText(_translate("Form", "add", None))
        self.remove.setText(_translate("Form", "remove", None))
        self.listItems.setText(_translate("Form", "listItems", None))
        self.clear.setText(_translate("Form", "clear", None))
        self.UpdateData.setText(_translate("Form", "UpdateData", None))
        self.label.setText(_translate("Form", "rows", None))
        self.rows.setText(_translate("Form", "2", None))
        self.label_2.setText(_translate("Form", "cols", None))
        self.cols.setText(_translate("Form", "2", None))

from pyqtgraph import GraphicsLayoutWidget

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

