import sys
#
#def trace(frame, event, arg):
#    if event == 'call' and 'advance' in frame.f_code.co_filename:
#        print "%s, %s:%d" % (event, frame.f_code.co_filename, frame.f_lineno)
#    return trace
#
#sys.settrace(trace)
#

# import faulthandler
# faulthandler.enable()

import os, multiprocessing
from PyQt4 import QtCore, QtGui
from gui import launch

class LaunchDialog ( QtGui.QDialog, launch.Ui_Dialog ):
    def __init__(self, parent = None):
        super(LaunchDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('advanceXCMS')
        self.viewXCMSButton.clicked.connect(self.launchXCMSView)
#        self.alignBatchButton.clicked.connect(self.launchBatchAlignment)

    def launchXCMSView(self):
        from featureReview.viewXCMSGuiProcs import XCMSView
        window = XCMSView()
        screenShape = QtGui.QDesktopWidget().screenGeometry()
        window.resize(screenShape.width()*0.8, screenShape.height()*0.8)
        #self.close() # close splash screen
        window.show()
        return
#
#    def launchBatchAlignment(self):
#        from batchAlignment.aligner import BatchAlignment as aligner
#        window = aligner()
#        window.show()
#        window.exec_()
#        return
#
def main():
    app = QtGui.QApplication(sys.argv)

    from featureReview.viewXCMSGuiProcs import XCMSView
    window = XCMSView()
    screenShape = QtGui.QDesktopWidget().screenGeometry()
    window.resize(screenShape.width()*0.8, screenShape.height()*0.8)
    #self.close() # close splash screen
    window.show()


#    gui = LaunchDialog()
#    gui.show()
    sys.exit(app.exec_())
    return

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
