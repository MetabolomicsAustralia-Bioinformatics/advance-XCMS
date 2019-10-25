import numpy as np
import pyqtgraph as pg
from pyqtgraph.Point import Point
from pyqtgraph.graphicsItems.ItemGroup import ItemGroup
from pyqtgraph.Qt import QtGui, QtCore
from matplotlib.mlab import inside_poly
from pyqtgraph.graphicsItems import ScatterPlotItem

#############################################################################
#############################################################################
#############################################################################

class ChildGroup(ItemGroup):
    sigItemsChanged = QtCore.Signal()
    def __init__(self, parent):
        print 'INIT'
        ItemGroup.__init__(self, parent)
        # excempt from telling view when transform changes
        self._GraphicsObject__inform_view_on_change = False
    def itemChange(self, change, value):
        ret = ItemGroup.itemChange(self, change, value)
        if change == self.ItemChildAddedChange or change == self.ItemChildRemovedChange:
            self.sigItemsChanged.emit()   
        return ret

class MyViewBox(pg.ViewBox):
      
    def mouseDragEvent(self, ev):
        
        if ev.button() == QtCore.Qt.RightButton:
            ev.ignore()    
        else:
            pg.ViewBox.mouseDragEvent(self, ev)
         
        ev.accept() 
        pos = ev.pos()
        if ev.button() == QtCore.Qt.RightButton:
            
            if ev.isFinish():  
                self.rbScaleBox.hide()
                self.ax = QtCore.QRectF(Point(ev.buttonDownPos(ev.button())), Point(pos))
                self.ax = self.childGroup.mapRectFromParent(self.ax) 
                self.Coords =  self.ax.getCoords()  
                self.getdataInRect()
                self.changePointsColors()
            else:
                self.updateScaleBox(ev.buttonDownPos(), ev.pos())
#           
    def getdataInRect(self):
        # Get the data from the Graphicsitem
        self.getDataItem()
        x = self.dataxy[0]
        y = self.dataxy[1]
        # Rect Edges
        Xbl = (self.Coords[0],self.Coords[1]) # bottom left
        Xbr = (self.Coords[2],self.Coords[1]) # bottom right
        Xtr = (self.Coords[2],self.Coords[3]) # top right
        Xtl = (self.Coords[0],self.Coords[3]) # top left
        #Make a list of [(x0,y0),(x1,y1) ...]
        self.xy = list()
        for i in x:
                tmp = (x[i],y[i])
                self.xy.append(tmp)            
#       exemple = inside_poly([(x0,y0),(x1,y1),...],[Xbl, Xbr, Xtr, Xtl])     
        self.insideIndex = inside_poly(self.xy,[Xbl, Xbr, Xtr, Xtl])    
                 
    def getDataItem(self):
        
        self.ObjItemList = pg.GraphicsScene.items(self.scene(),self.ax)
        self.dataxy = self.ObjItemList[0].listDataItems()[0].getData()
       
    def changePointsColors(self):
        
        print self.xy
        print self.insideIndex
        
#############################################################################
#############################################################################
#############################################################################
                  
app = QtGui.QApplication([])
mw = QtGui.QMainWindow()
mw.resize(800,500)
mw.show()

vb = MyViewBox()
pw = pg.PlotWidget(viewBox=vb)


a  = np.array([0,1,2,3,4,5,6,7,8,9,10])
b  = np.array([0,1,2,3,4,5,6,7,8,9,10])

curve0 = pw.plot(a,b, clickable=True, symbol = '+')

mw.setCentralWidget(pw)

#############################################################################
#############################################################################
#############################################################################

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()