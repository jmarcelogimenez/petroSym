# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from tracers_ui import tracersUI
import os
import utils
import copy
import numpy

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

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.RunDictionary.BoundaryDict import BoundaryDict

dicc = {}
dicc['type'] = 'scalarTransport';
dicc['functionObjectLibs'] =  ['"libutilityFunctionObjects.so"']
dicc['DT'] = '1e-10'
dicc['resetOnStartUp'] = 'false';
dicc['autoSchemes'] = 'false';
dicc['schemesField'] = 'T'; #solo valido para OF >= 3.0
dicc['patchName'] = 'inlet'
dicc['fvOptions'] = {}
dicc['fvOptions']['S'] = {}
dicc['fvOptions']['S']['type'] = 'scalarExplicitSetValue'
dicc['fvOptions']['S']['active'] = 'true'
dicc['fvOptions']['S']['selectionMode'] = 'cellSet'
dicc['fvOptions']['S']['cellSet'] = 'inletcells'
dicc['fvOptions']['S']['timeStart'] = '0'
dicc['fvOptions']['S']['duration'] = '1e6'
dicc['fvOptions']['S']['scalarExplicitSetValueCoeffs'] = {}
dicc['fvOptions']['S']['scalarExplicitSetValueCoeffs']['injectionRate'] = {}
dicc['fvOptions']['S']['scalarExplicitSetValueCoeffs']['injectionRate']['T0'] = 1

class tracers(tracersUI):

    def __init__(self, currentFolder, nproc):
        tracersUI.__init__(self)
        self.currentFolder = currentFolder
        self.nproc = nproc
        [self.timedir,fields,self.currtime] = utils.currentFields(str(self.currentFolder),nproc=self.nproc)
        
        self.patches = []
        self.emptys = []
        self.colors = ['r', 'b', 'k', 'g', 'y', 'c']
        self.firstPlot = True
                
        self.loadCaseData()
        self.refreshTable()
        self.refreshTimeline()
        
        self.pushButton_3.setEnabled(False)

    def loadCaseData(self):
        filename = '%s/system/controlDict'%self.currentFolder
        self.parsedData = ParsedParameterFile(filename,createZipped=False)
        self.tracersData = []
        if 'functions' in self.parsedData.getValueDict().keys():
            for key in self.parsedData['functions'].keys():
                if self.parsedData['functions'][key]['type'] == 'scalarTransport':
                    tracer = {}
                    tracer['name'] = key
                    tracer['patchName'] = self.parsedData['functions'][key]['patchName']
                    tracer['startTime'] = self.parsedData['functions'][key]['fvOptions']['S']['timeStart']
                    #TODO: cargar aca
                    if tracer['patchName']=='point':
                        tracer['position'] = self.parsedData['functions'][key]['fvOptions']['S']['position']
                    self.tracersData.append(tracer)
                        
        if self.patches==[]:
            boundaries = BoundaryDict(str(self.currentFolder))
            self.patches = boundaries.patches()
            for ipatch in self.patches:
                if boundaries[ipatch]['type']=='empty':
                    self.emptys.append(ipatch)
                    
        self.pushButton_3.setEnabled(True)
        

    def refreshTable(self):
        for ii in range(self.tableWidget.rowCount()-1,-1,-1):
            self.tableWidget.removeRow(ii)
        
        for i in range(len(self.tracersData)):
            self.tableWidget.insertRow(i)
            item1 = QtGui.QTableWidgetItem()
            item2 = QtGui.QTableWidgetItem()
            item3 = QtGui.QTableWidgetItem()
            wdg1 = QtGui.QLineEdit()
            wdg2 = QtGui.QComboBox()
            wdg3 = QtGui.QLineEdit()
            wdg2.addItems(list(set(self.patches)-set(self.emptys)))
            wdg2.addItem('point')
            wdg2.setObjectName(str(i))
            
            wdg1.setText(str(self.tracersData[i]['startTime']))
            wdg2.setCurrentIndex(wdg2.findText(self.tracersData[i]['patchName']))
            #TODO: Hay que ver como cagarlo del archivo, preguntar a juan
            wdg3.setText(str(self.tracersData[i]['position'])) if self.tracersData[i]['patchName']=='point' else wdg3.setText("(0 0 0)")
            wdg3.setEnabled(False) if self.tracersData[i]['patchName']!='point' else wdg3.setEnabled(True)
            QtCore.QObject.connect(wdg2, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.change_combobox)
            wdg3.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("\({1}-?\d+\.?\d*(e-?\d)?\s-?\d+\.?\d*(e-?\d)?\s-?\d+\.?\d*(e-?\d)?\){1}")))
            QtCore.QObject.connect(wdg1,QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.checkAccept)
            
            self.tableWidget.setItem(i,0,item1)
            self.tableWidget.setCellWidget(i,0,wdg1)
            self.tableWidget.setItem(i,1,item2)
            self.tableWidget.setCellWidget(i,1,wdg2)
            self.tableWidget.setItem(i,2,item3)
            self.tableWidget.setCellWidget(i,2,wdg3)
            
        self.pushButton_3.setEnabled(True)

    def refreshTimeline(self):
        if not self.firstPlot:
            self.figureLayout.removeWidget(self.canvas)

        self.firstPlot = False
        fig = Figure((2.0, 1.5), dpi=100)
        self.canvas = FigureCanvas(fig)
        self.canvas.setParent(self)
        
        self.ax = fig.add_subplot(111)
        self.ax.clear()
        
        #levantar el controlDict y ver los tracers
        
        Tf = float(self.parsedData['endTime'])
        T = float(self.currtime)
        dT = float(self.parsedData['deltaT'])
        self.ax.set_ylim(0,1.1)
        self.ax.set_xlim(-10*dT,Tf)
        self.ax.plot([0,T-dT,T,T+dT,Tf],[0,0,1,0,0], 'k', marker='o', label='Current Time')
        i = 0
        for itracer in self.tracersData:
            Tini = float(itracer['startTime']) 
            if float(itracer['startTime'])<T:
                Tini = T
            self.ax.plot([0,Tini,Tini+dT,Tf],[0,0,1,1], self.colors[i%6], label=itracer['name'])
            i = i+1
        self.ax.set_title('Timeline')
        self.ax.set_xlabel('Time [s]')
        self.ax.set_ylabel('Event')
        self.ax.legend(loc=0, fontsize = 'small')       
        
        self.figureLayout.addWidget(self.canvas)
        
        self.pushButton_3.setEnabled(True)
        return
        
    def change_combobox(self):
        name = str(self.sender().objectName())
        c=self.tableWidget.cellWidget(int(name),2)
        
        if self.sender().currentText()=='point':
            c.setEnabled(True)
        else:
            c.setEnabled(False)
        
        print 'done'
        return

    def newTracer(self):
        i = self.tableWidget.rowCount()
        self.tableWidget.insertRow(i)
        item1 = QtGui.QTableWidgetItem()
        item2 = QtGui.QTableWidgetItem()
        item3 = QtGui.QTableWidgetItem()
        wdg1 = QtGui.QLineEdit()
        wdg2 = QtGui.QComboBox()
        wdg3 = QtGui.QLineEdit()
        wdg2.addItems(list(set(self.patches)-set(self.emptys)))
        wdg2.addItem('point')
        wdg2.setObjectName(str(i))
        wdg3.setEnabled(False)
        wdg1.setText('0')
        wdg3.setText('(0 0 0)')
        QtCore.QObject.connect(wdg2, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.change_combobox)
        wdg3.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("\({1}-?\d+\.?\d*(e-?\d)?\s-?\d+\.?\d*(e-?\d)?\s-?\d+\.?\d*(e-?\d)?\){1}")))
        QtCore.QObject.connect(wdg1,QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.checkAccept)
        self.tableWidget.setItem(i,0,item1)
        self.tableWidget.setCellWidget(i,0,wdg1) 
        self.tableWidget.setItem(i,1,item2)
        self.tableWidget.setCellWidget(i,1,wdg2)
        self.tableWidget.setItem(i,2,item3)
        self.tableWidget.setCellWidget(i,2,wdg3)
        
        
        self.pushButton_3.setEnabled(True)
                
    def removeTracer(self):
        ii = self.tableWidget.currentRow()
        if ii==-1:
            QtGui.QMessageBox.about(self, "ERROR", "No tracer selected")
            return
        w = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Removing", "Do you want to remove tracer data?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
        ret = w.exec_()
        if(QtGui.QMessageBox.Yes == ret):
            self.tableWidget.removeRow(ii)
            self.drawTracers()
            self.pushButton_3.setEnabled(False)
        return        
        
    def saveCaseData(self):
        saved = self.drawTracers(True)
        if saved:
            self.pushButton_3.setEnabled(False)

    def drawTracers(self, doTopoSet=False):

        for dd in self.tracersData:
            del self.parsedData['functions'][dd['name']]
        
        if 'functions' not in self.parsedData.getValueDict().keys():
            self.parsedData['functions'] = {}
            
        patches = []
        for i in range(self.tableWidget.rowCount()):
            patchName = str(self.tableWidget.cellWidget(i,1).currentText())
            newkey = 'T%s'%str(i)
            tracer = copy.deepcopy(dicc)
            cellsetname = '%s_c'%patchName
            
            tracer['fvOptions']['S']['timeStart'] = str(self.tableWidget.cellWidget(i,0).text())
            tracer['fvOptions']['S']['cellSet'] = cellsetname
            tracer['patchName'] = patchName
            if patchName=='point':
                tracer['fvOptions']['S']['position'] = {} if 'position' not in tracer['fvOptions']['S'].keys() else None
                #TODO: Verificar que sea correcto el punto
                tracer['fvOptions']['S']['position'] = self.tableWidget.cellWidget(i,2).text()
                
            del tracer['fvOptions']['S']['scalarExplicitSetValueCoeffs']['injectionRate']['T0']
            tracer['fvOptions']['S']['scalarExplicitSetValueCoeffs']['injectionRate'][newkey] = '1'            
            self.parsedData['functions'][newkey] = tracer
            patches.append(patchName)
        self.parsedData.writeFile()
        
        if doTopoSet:
            spatches = set(patches)
            ii = 0
            cmd = 'cp %s/caseDicts/topoSetDict %s/system/.'%(os.path.dirname(os.path.realpath(__file__)),self.currentFolder)
            os.system(cmd)
            
            filename = '%s/system/topoSetDict'%self.currentFolder
            topoSetData = ParsedParameterFile(filename,createZipped=False)     
            
            #armo el topoSet de manera de generar los cellSet deseados
            for ipatch in spatches:
                cellsetname = '%s_c'%ipatch
                facesetname = '%s_f'%ipatch
                if not os.path.isfile('%s/constant/polyMesh/sets/%s'%(self.currentFolder,cellsetname)):
                    if ii>0:
                        topoSetData['actions'].append(topoSetData['actions'][0])
                        topoSetData['actions'].append(topoSetData['actions'][1])
                    topoSetData['actions'][ii]['name'] = facesetname
                    topoSetData['actions'][ii]['sourceInfo']['name'] = ipatch
                    topoSetData['actions'][ii+1]['name'] = cellsetname
                    topoSetData['actions'][ii+1]['sourceInfo']['set'] = facesetname                
                    ii = ii+2
            topoSetData.writeFile()
                        
            cmd = 'topoSet -case %s > run_topoSet.log &'%self.currentFolder
            os.system(cmd)
        
        self.loadCaseData()
        self.refreshTable()
        self.refreshTimeline()
        
        return True
        
        
    def checkAccept(self):
        
        ready = True
        edits = self.findChildren(QtGui.QLineEdit)
        for E in edits:
            if E.isEnabled():
                if not E.text():
                        ready = False
        if ready:
            self.pushButton_3.setEnabled(True)
        else:
            self.pushButton_3.setEnabled(False)