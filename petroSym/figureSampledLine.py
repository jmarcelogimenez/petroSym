# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from figureSampledLine_ui import figureSampledLineUI

from myNavigationToolbar import *
from temporalNavigationToolbar import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

from utils import *
import pylab


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


# sampleSet
#  {
#    type sets;
#    interpolationScheme cellPoint;
#    outputControl timeStep;
#    outputInterval 20;
#    setFormat raw;
#    sets
#      (
#        data
#
#        {
#          type uniform;
#          axis y;
#          start (0.05 0 0);
#          end (0.05 0.1 0);
#          nPoints 50;
#
#        }
#      );
#    fields
#      (
#        U
#        p
#      );
#  }
#

class figureSampledLine(figureSampledLineUI):

    def __init__(self, currentFolder):
        figureSampledLineUI.__init__(self)
        self.currentFolder = currentFolder        
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
        
        [self.timedir,self.fields,bas] = currentFields(self.currentFolder)
        
        self.comboBox.clear()
        for field in self.fields:
#            if types[field] == 'vector':
#                for idim in ['x','y','z']:
#                    self.comboBox.addItem('%s%s'%(field,idim))
#            elif types[field] == 'scalar':
            self.comboBox.addItem(field)
            
        self.p1_x.setValidator(QtGui.QDoubleValidator())
        self.p1_y.setValidator(QtGui.QDoubleValidator())
        self.p1_z.setValidator(QtGui.QDoubleValidator())
        self.p2_x.setValidator(QtGui.QDoubleValidator())
        self.p2_y.setValidator(QtGui.QDoubleValidator())
        self.p2_z.setValidator(QtGui.QDoubleValidator())
        
    def getData(self):
        data = {}
        data['nsteps'] = self.spinBox.value()        
        data['field'] = self.comboBox.currentText()
        data['p1x'] = self.p1_x.text()
        data['p1y'] = self.p1_y.text()
        data['p1z'] = self.p1_z.text()
        data['p2x'] = self.p2_x.text()
        data['p2y'] = self.p2_y.text()
        data['p2z'] = self.p2_z.text()
        data['nop'] = self.nop.value()
        data['name'] = str(self.name.text())
        data['autorefreshing'] = self.autorefreshing.currentText()
        
        return data
        
    def setData(self,data):
        
        #self.spinBox.setValue(data['nsteps']) if 'nsteps' in data.keys() else None
        #self.nop.setValue(data['nop']) if 'nop' in data.keys() else None
        self.name.setText(data['name']) if 'name' in data.keys() else None
        
        #self.comboBox.setCurrentText(data['field']) if 'field' in data.keys()  else None
        #self.comboBox.setCurrentText(data['autorefreshing']) if 'autorefreshing' in data.keys() else None
        
        self.p1_x.setText(data['p1x']) if 'p1x' in data.keys() else None
        self.p1_y.setText(data['p1y']) if 'p1y' in data.keys() else None
        self.p1_z.setText(data['p1z']) if 'p1z' in data.keys() else None
        self.p2_x.setText(data['p2x']) if 'p2x' in data.keys() else None
        self.p2_y.setText(data['p2y']) if 'p2y' in data.keys() else None
        self.p2_z.setText(data['p2z']) if 'p2z' in data.keys() else None
        
        filename = '%s/system/controlDict'%(self.currentFolder)
        parsedData = ParsedParameterFile(filename,createZipped=False)
        if 'functions' in parsedData.getValueDict().keys():
            if data['name'] in parsedData['functions'].keys():
                dicc = parsedData['functions'][data['name']]
                if dicc['type']=='sets':
                    self.name.setText(data['name'])
                    self.spinBox.setValue(dicc['outputInterval'])                    
        
        return data
        
    def ckeckAccept(self):

        ready = True
        edits = self.findChildren(QtGui.QLineEdit)
        for E in edits:
            if E.isEnabled():
                if not E.text():
                    ready = False
        if ready:
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
        
        
    def accept(self):
        filename = '%s/system/controlDict'%(self.currentFolder)
        parsedData = ParsedParameterFile(filename,createZipped=False)
        if 'functions' not in parsedData.getValueDict().keys():
            parsedData['functions'] = {}
        if str(self.name.text()) not in parsedData['functions'].keys():
            parsedData['functions'][str(self.name.text())] = {}
        
        parsedData['functions'][str(self.name.text())]['type'] = 'sets'
        parsedData['functions'][str(self.name.text())]['outputControl'] = 'timeStep'
        parsedData['functions'][str(self.name.text())]['outputInterval'] = self.spinBox.value()
        parsedData['functions'][str(self.name.text())]['setFormat'] = 'raw'
        parsedData['functions'][str(self.name.text())]['interpolationScheme'] = 'cellPoint'
        ifield = self.comboBox.currentText()
        if ifield not in self.fields:
            #significa que es un vector
            axis = 'distance' #ifield[-1]
            ifield = ifield[0:-1]
        else:
            axis = 'distance' #por las dudas        
        parsedData['functions'][str(self.name.text())]['fields'] = [ifield]
        
        dicc = {}
        dicc['nPoints'] = self.nop.text()
        dicc['start'] = '(%s %s %s)'%(str(self.p1_x.text()),str(self.p1_y.text()),str(self.p1_z.text()))
        dicc['end'] = '(%s %s %s)'%(str(self.p2_x.text()),str(self.p2_y.text()),str(self.p2_z.text()))
        dicc['type'] = 'uniform'
        dicc['axis'] = axis
        parsedData['functions'][str(self.name.text())]['sets'] = ['data',dicc]
        
        parsedData.writeFile()
        
        self.done(self.Accepted)
            
class figureSampledLineWidget(QtGui.QWidget):

    def __init__(self, scrollAreaWidgetContents, dataname):         
        QtGui.QWidget.__init__(self)
        self.setParent(scrollAreaWidgetContents)
        fig = Figure((3.0, 2.0), dpi=100)
        canvas = FigureCanvas(fig)
        canvas.setParent(self)
        toolbar = myNavigationToolbar(canvas, self)
        temporal_toolbar = temporalNavigationToolbar(canvas, self)
        axes = fig.add_subplot(111)
        axes.autoscale(True)
        axes.set_yscale('log')
        axes.set_title(dataname)
        
         # place plot components in a layout
        plotLayout = QtGui.QVBoxLayout()
        plotLayout.addWidget(temporal_toolbar)
        plotLayout.addWidget(canvas)
        plotLayout.addWidget(toolbar)
        self.setLayout(plotLayout)

        canvas.setMinimumSize(canvas.size())
        
        self.name = dataname
        self.dirList = []
        self.dirType = 'Sampled Line'
        self.lastPos = -1
        self.colors = ['r', 'b', 'k', 'g', 'y', 'c']
        self.labels = ['_x','_y','_z']

    def plot(self):
        if self.lastPos<0:
            return
        canvas = self.findChild(FigureCanvas)
        timeLegend = self.findChild(QtGui.QLineEdit)
        axes = canvas.figure.gca()
        filename = '%s/postProcessing/%s/%s/data_U.xy'%(self.window().currentFolder,self.name,self.dirList[self.lastPos])
        data = pylab.loadtxt(filename)
        if len(data)>0:
            axes.clear()
            #@TODO
            #Fijarse que el sample guarda todos los datos de velocidad, y axis indica el eje de las abcisas
            if data.shape[1]>1:
                for ii in range(data.shape[1]-1):
                    axes.plot(data[:,0],data[:,ii+1],self.colors[ii]) #, label=self.labels[ii])
            else:
                axes.plot(data[:,0],data[:,1],'r',label='self.name')
                
            timeLegend.setText(self.dirList[self.lastPos])
            axes.set_title(self.name)
            axes.set_xlabel('distance')
            #axes.set_ylabel('|R|')
            axes.legend(loc=2, fontsize = 'small')
        canvas.draw()

    def resetFigure(self):
        self.dirList = []
        self.dirType = 'Sampled Line'
        self.lastPos = -1
        self.colors = ['r', 'b', 'k', 'g', 'y', 'c']
        self.labels = ['_x','_y','_z']
        
        canvas = self.findChild(FigureCanvas)
        canvas.figure.gca().cla()
        canvas.draw()