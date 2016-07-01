# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from figureSampledLine_ui import figureSampledLineUI
import os

from myNavigationToolbar import *
from temporalNavigationToolbar import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

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

           
class figureGeneralSnapshotWidget(QtGui.QWidget):

    def __init__(self, scrollAreaWidgetContents, currentFolder):         
        QtGui.QWidget.__init__(self)
        self.setParent(scrollAreaWidgetContents)
        
        canvas = FigureCanvas(Figure((3.0, 2.0), dpi=100))
        canvas.setParent(self)
        toolbar = myNavigationToolbar(canvas, self)
        toolbar.disableButtons()
        temporal_toolbar = temporalNavigationToolbar(canvas, self)

        mainImage = QtGui.QLabel(self)
        mainImage.setText(_fromUtf8(""))
        mainImage.setPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/emptyFigure.png")))
        mainImage.setObjectName(_fromUtf8("mainImage"))

        plotLayout = QtGui.QVBoxLayout()
        plotLayout.addWidget(temporal_toolbar)
        plotLayout.addWidget(mainImage)
        plotLayout.addWidget(toolbar)
        
        self.setLayout(plotLayout)
        self.lastPos = -1
        self.dirList = []
        self.currentFolder = currentFolder

        canvas.setMinimumSize(canvas.size())
        
    def plot(self):
        ii = self.objectName()
        desired = '%s/snapshots/%s/%s/%s_%s.png'%(self.currentFolder,ii,self.lastPos,ii,self.lastPos)
        #print desired
        print self.lastPos
        newdirsnapshot = '%s/snapshots/%s/%s'%(self.currentFolder,ii,self.lastPos)
        if not os.path.isfile(desired):
            command = 'pvpython /usr/local/bin/pyFoamPVSnapshot.py --time=%s --state-file=%s/%s.pvsm  --file-prefix="snapshot" --no-casename --no-timename --no-offscreen-rendering %s'%(self.lastPos,self.currentFolder,ii,self.currentFolder)
            os.system(command)
            dirsnapshot=os.path.dirname(os.path.realpath(__file__))
            filename = '%s/snapshot_00000.png'%dirsnapshot
            while not os.path.isfile(filename):
                None            
            command = 'mkdir -p %s'%newdirsnapshot
            os.system(command)
            command = 'mv %s %s/snapshots/%s/%s/%s_%s.png'%(filename,self.currentFolder,ii,self.lastPos,ii,self.lastPos)
            os.system(command)
        mainImage = self.findChild(QtGui.QLabel,'mainImage')
        mainImage.setPixmap(QtGui.QPixmap(_fromUtf8(desired)))

        timeLegend = self.findChild(QtGui.QLineEdit)
        timeLegend.setText(str(self.lastPos))
        self.dirList.extend(newdirsnapshot)
        print newdirsnapshot
        
    def resetFigure(self):
        self.lastPos = -1
        self.dirList = []
       
        mainImage = self.findChild(QtGui.QLabel,'mainImage')
        mainImage.setText(_fromUtf8(""))
        mainImage.setPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/emptyFigure.png")))
        mainImage.setObjectName(_fromUtf8("mainImage"))
        