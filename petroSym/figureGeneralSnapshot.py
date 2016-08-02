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

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

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
        mainImage.setScaledContents(True)
        mainImage.setSizePolicy(QtGui.QSizePolicy.Ignored,QtGui.QSizePolicy.Ignored)


        plotLayout = QtGui.QVBoxLayout()
        plotLayout.addWidget(temporal_toolbar)
        plotLayout.addWidget(mainImage,1)
        plotLayout.addWidget(toolbar,0,QtCore.Qt.AlignCenter)
        
        self.setLayout(plotLayout)
        self.lastPos = -1
        self.dirList = []
        self.currentFolder = currentFolder

        canvas.setMinimumSize(canvas.size())
        
    def plot(self):
        ii = self.objectName()
        desired = '%s/postProcessing/snapshots/%s/%s/%s.png'%(self.currentFolder,ii,self.dirList[self.lastPos],ii)
        if not os.path.isfile(desired):
            if self.window().nproc == 1:
                command = 'pvpython /usr/local/bin/pyFoamPVSnapshot.py --time=%s --state-file=%s/%s.pvsm  --file-prefix="%s/snapshot" --no-casename --no-timename --no-offscreen-rendering %s'%(self.dirList[self.lastPos],self.currentFolder,ii,self.currentFolder,self.currentFolder)
            else:
                command = 'pvpython /usr/local/bin/pyFoamPVSnapshot.py --parallel-times --time=%s --state-file=%s/%s.pvsm  --file-prefix="%s/snapshot" --no-casename --no-timename --no-offscreen-rendering %s'%(self.dirList[self.lastPos],self.currentFolder,ii,self.currentFolder,self.currentFolder)

            print command
            
            os.system(command)
            filename = '%s/snapshot_00000.png'%self.currentFolder
            while not os.path.isfile(filename):
                None
            command = 'mv %s %s/postProcessing/snapshots/%s/%s/%s.png'%(filename,self.currentFolder,ii,self.dirList[self.lastPos],ii)
            os.system(command)
        mainImage = self.findChild(QtGui.QLabel,'mainImage')
        mainImage.setPixmap(QtGui.QPixmap(_fromUtf8(desired)))

        timeLegend = self.findChild(QtGui.QLineEdit)
        timeLegend.setText(self.dirList[self.lastPos])

    def resetFigure(self):
        self.lastPos = -1
        self.dirList = []
       
        mainImage = self.findChild(QtGui.QLabel,'mainImage')
        mainImage.setText(_fromUtf8(""))
        mainImage.setPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/emptyFigure.png")))
        mainImage.setObjectName(_fromUtf8("mainImage"))
        
        
    def accept(self):
        filename = '%s/system/controlDict'%(self.currentFolder)
        parsedData = ParsedParameterFile(filename,createZipped=False)
        if 'functions' not in parsedData.getValueDict().keys():
            parsedData['functions'] = {}
        if str(self.objectName()) not in parsedData['functions'].keys():
            parsedData['functions'][str(self.objectName())] = {}
        
        parsedData['functions'][str(self.objectName())]['type'] = 'snapshots'
        parsedData['functions'][str(self.objectName())]['outputControl'] = 'outputTime'
        parsedData['functions'][str(self.objectName())]['functionObjectLibs'] =  ['"libsnapshotsFunctionObjects.so"']
        
        parsedData.writeFile()