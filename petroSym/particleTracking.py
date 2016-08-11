# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from particleTracking_ui import particleTrackingUI
import utils
import copy


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


dicc = {}
dicc['type'] = 'particleTracking';
dicc['functionObjectLibs'] =  ['"libmyUtilityFunctionObjects.so"']
dicc['resetOnStartUp'] = 'false'
dicc['tInjStart'] = 0
dicc['tInjEnd'] = 0
dicc['npByDt'] = 1
dicc['center'] = '(0 0 0)'
dicc['r0'] =  '(0 0 0)'
dicc['rho'] = 1000
dicc['d'] = 0.01
dicc['rhop'] = 1000
dicc['e'] = 1
dicc['mu'] = 0.01
dicc['outputControl'] = 'timeStep'
dicc['outputType'] = 'interval'
dicc['outputInterval'] = 1

outputTypeData = ['interval','point']
doubleData = [1,2,6,7,8,9,10]
intData = [3]
vecData = [4,5]
lineEdit = [1,2,3,4,5,6,7,8,9,10]
comboBox = [11]
spin = [12]

class particleTracking(particleTrackingUI):

    def __init__(self, currentFolder,nproc):
        particleTrackingUI.__init__(self)
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
        self.trackingData = []
        if 'functions' in self.parsedData.getValueDict().keys():
            for key in self.parsedData['functions'].keys():
                if self.parsedData['functions'][key]['type'] == 'particleTracking':
                    D = self.parsedData['functions'][key]
                    track = {}
                    track['name'] = key
                    track['tInjStart'] = D['tInjStart'] if D.__contains__('tInjStart') else dicc['tInjStart']  
                    track['tInjEnd'] = D['tInjEnd'] if D.__contains__('tInjEnd') else dicc['tInjEnd']  
                    track['npByDt'] = D['npByDt'] if D.__contains__('npByDt') else dicc['npByDt']  
                    track['center'] = D['center'] if D.__contains__('center') else dicc['center']  
                    track['r0'] = D['r0'] if D.__contains__('r0') else dicc['r0']  
                    track['rho'] = D['rho'] if D.__contains__('rho') else dicc['rho']  
                    track['d'] = D['d'] if D.__contains__('d') else dicc['d']  
                    track['rhop'] = D['rhop'] if D.__contains__('rhop') else dicc['rhop']  
                    track['mu'] = D['mu'] if D.__contains__('mu') else dicc['mu']  
                    track['e'] = D['e'] if D.__contains__('e') else dicc['e']
                    track['outputType'] = D['outputType'] if D.__contains__('outputType') else dicc['outputType']
                    track['outputInterval'] = D['outputInterval'] if D.__contains__('outputInterval') else dicc['outputInterval']
                    
                    self.trackingData.append(track)
                        
        self.pushButton_3.setEnabled(True)
        

    def refreshTable(self):
        for ii in range(self.tableWidget.columnCount()-1,-1,-1):
            self.tableWidget.removeColumn(ii)
        
        for i in range(len(self.trackingData)):
            self.tableWidget.insertColumn(i)
            N = 13
            items = [QtGui.QTableWidgetItem() for irow in range(N)]
            wdgs = [QtGui.QLineEdit() for irow in range(N-2)]
            
            wdgs[0].setText(str(self.trackingData[i]['name']))
            wdgs[0].setEnabled(False)
            wdgs[1].setText(str(self.trackingData[i]['tInjStart']))
            wdgs[2].setText(str(self.trackingData[i]['tInjEnd']))
            wdgs[3].setText(str(self.trackingData[i]['npByDt']))
            wdgs[4].setText(str(self.trackingData[i]['center']))
            wdgs[5].setText(str(self.trackingData[i]['r0']))
            wdgs[6].setText(str(self.trackingData[i]['rho']))
            wdgs[7].setText(str(self.trackingData[i]['d']))
            wdgs[8].setText(str(self.trackingData[i]['rhop']))
            wdgs[9].setText(str(self.trackingData[i]['mu']))
            wdgs[10].setText(str(self.trackingData[i]['e']))
            
            wdgs.append(QtGui.QComboBox())
            wdgs[11].addItems(outputTypeData)
            wdgs[11].setObjectName(str(i))
            wdgs[11].setCurrentIndex(wdgs[11].findText(self.trackingData[i]['outputType']))

            wdgs.append(QtGui.QSpinBox())
            wdgs[12].setMinimum(1)
            wdgs[12].setMaximum(1000)
            wdgs[12].setValue(self.trackingData[i]['outputInterval'])
            wdgs[12].setEnabled(False) if self.trackingData[i]['outputType']!='interval' else wdgs[12].setEnabled(True)
        
            for irow in range(N):
                if irow in doubleData:
                    wdgs[irow].setValidator(QtGui.QDoubleValidator())
                if irow in intData:
                    wdgs[irow].setValidator(QtGui.QIntValidator())
                if irow in vecData:
                    wdgs[irow].setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("\({1}-?\d+\.?\d*(e-?\d)?\s-?\d+\.?\d*(e-?\d)?\s-?\d+\.?\d*(e-?\d)?\){1}")))
                if irow in lineEdit:
                    QtCore.QObject.connect(wdgs[irow],QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.checkAccept)
                if irow in spin:
                    QtCore.QObject.connect(wdgs[irow],QtCore.SIGNAL(_fromUtf8("valueChanged(QString)")), self.checkAccept)
                if irow in comboBox:
                    QtCore.QObject.connect(wdgs[irow], QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.checkAccept)
                    QtCore.QObject.connect(wdgs[irow], QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.change_combobox)
                
                self.tableWidget.setItem(irow,i,items[irow])
                self.tableWidget.setCellWidget(irow,i,wdgs[irow]) 
                
            
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
        for itrack in self.trackingData:
            Tini = float(itrack['tInjStart']) 
            Tend = float(itrack['tInjEnd']) 
            if Tini<T:
                Tini = T
            if Tend>Tf:
                Tend = Tf
            self.ax.plot([0,Tini-dT/10,Tini,Tend,Tend+dT/10,Tf],[0,0,1,1,0,0], self.colors[i%6], label=itrack['name'])
            i = i+1
        self.ax.set_title('Timeline')
        self.ax.set_xlabel('Time [s]')
        self.ax.set_ylabel('Event')
        self.ax.legend(loc=0, fontsize = 'small')       
        
        self.figureLayout.addWidget(self.canvas)
        
        self.pushButton_3.setEnabled(True)
        
    def change_combobox(self):
        name = str(self.sender().objectName())
        c=self.tableWidget.cellWidget(12,int(name))
        
        if self.sender().currentText()=='interval':
            c.setEnabled(True)
        else:
            c.setEnabled(False)
        
        print 'done'
        return

    def newTracer(self):
        i = self.tableWidget.columnCount()
        self.tableWidget.insertColumn(i)
        
        N = 13
        items = [QtGui.QTableWidgetItem() for irow in range(N)]
        wdgs = [QtGui.QLineEdit() for irow in range(N-2)]
        
        wdgs[0].setText(str('newCloud'))
        wdgs[1].setText(str(dicc['tInjStart']))
        wdgs[2].setText(str(dicc['tInjEnd']))
        wdgs[3].setText(str(dicc['npByDt']))
        wdgs[4].setText(str(dicc['center']))
        wdgs[5].setText(str(dicc['r0']))
        wdgs[6].setText(str(dicc['rho']))
        wdgs[7].setText(str(dicc['d']))
        wdgs[8].setText(str(dicc['rhop']))
        wdgs[9].setText(str(dicc['mu']))
        wdgs[10].setText(str(dicc['e']))
        
        wdgs.append(QtGui.QComboBox())
        wdgs[11].addItems(outputTypeData)
        wdgs[11].setObjectName(str(i))

        wdgs.append(QtGui.QSpinBox())
        wdgs[12].setMinimum(1)
        wdgs[12].setMaximum(1000)
            
        for irow in range(N):
            if irow in doubleData:
                wdgs[irow].setValidator(QtGui.QDoubleValidator())
            if irow in intData:
                wdgs[irow].setValidator(QtGui.QIntValidator())
            if irow in vecData:
                wdgs[irow].setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("\({1}-?\d+\.?\d*(e-?\d)?\s-?\d+\.?\d*(e-?\d)?\s-?\d+\.?\d*(e-?\d)?\){1}")))
            if irow in lineEdit:
                QtCore.QObject.connect(wdgs[irow],QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.checkAccept)
            if irow in spin:
                QtCore.QObject.connect(wdgs[irow],QtCore.SIGNAL(_fromUtf8("valueChanged(QString)")), self.checkAccept)
            if irow in comboBox:
                QtCore.QObject.connect(wdgs[irow], QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.checkAccept)
                QtCore.QObject.connect(wdgs[irow], QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.change_combobox)
            
            self.tableWidget.setItem(irow,i,items[irow])
            self.tableWidget.setCellWidget(irow,i,wdgs[irow]) 
                
        self.pushButton_3.setEnabled(True)
                

    def removeTracer(self):
        ii = self.tableWidget.currentColumn()
        if ii==-1:
            QtGui.QMessageBox.about(self, "ERROR", "None cloud selected")
            return
        w = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Removing", "Do you want to remove all particle cloud data?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
        ret = w.exec_()
        if(QtGui.QMessageBox.Yes == ret):
            self.tableWidget.removeColumn(ii)
            self.drawTracers()
            self.pushButton_3.setEnabled(False)
        return
        
    def saveCaseData(self):
        saved = self.drawTracers()
        if saved:
            self.pushButton_3.setEnabled(False)
        
    def drawTracers(self):

        for i in range(self.tableWidget.columnCount()):
            ct = str(self.tableWidget.cellWidget(4,i).text())
            r0 = str(self.tableWidget.cellWidget(5,i).text())            
            if ct[-1]!=')' or  r0[-1]!=')':
                QtGui.QMessageBox.about(self, "Error", "Wrong regular expression in vector type")
                return False
                
            tini = float(self.tableWidget.cellWidget(1,i).text())
            tend = float(self.tableWidget.cellWidget(2,i).text())
            
            if tend<tini:
                QtGui.QMessageBox.about(self, "ERROR", "Wrong seeding interval")
                return False                

        for dd in self.trackingData:
            del self.parsedData['functions'][dd['name']]
        
        if 'functions' not in self.parsedData.getValueDict().keys():
            self.parsedData['functions'] = {}
            
        for i in range(self.tableWidget.columnCount()):
            track = copy.deepcopy(dicc)
            
            keyname =  str(self.tableWidget.cellWidget(0,i).text())
            track['tInjStart'] = str(self.tableWidget.cellWidget(1,i).text())
            track['tInjEnd'] = str(self.tableWidget.cellWidget(2,i).text())
            track['npByDt'] = str(self.tableWidget.cellWidget(3,i).text())
            track['center'] = str(self.tableWidget.cellWidget(4,i).text())
            track['r0'] = str(self.tableWidget.cellWidget(5,i).text())
            track['rho'] = str(self.tableWidget.cellWidget(6,i).text())
            track['d'] = str(self.tableWidget.cellWidget(7,i).text())
            track['rhop'] = str(self.tableWidget.cellWidget(8,i).text())
            track['mu'] = str(self.tableWidget.cellWidget(9,i).text())
            track['e'] = str(self.tableWidget.cellWidget(10,i).text())
            track['outputType'] = str(self.tableWidget.cellWidget(11,i).currentText()) #TODO: ver aca que va
            track['outputInterval'] = str(self.tableWidget.cellWidget(12,i).value())
            
            while keyname in self.parsedData['functions'].keys():
                keyname = keyname+'1'                
            self.parsedData['functions'][keyname] = track
            
        self.parsedData.writeFile()

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