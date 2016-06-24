# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from initialConditions_ui import Ui_initialConditionsUI
import os
from utils import *
from ExampleThread import *

from PyFoam.RunDictionary.BoundaryDict import BoundaryDict
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

from utils import types

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

unknowns = ['U','p','p_rgh','alpha','k','epsilon','omega','nut','nuTilda']

class initialConditionsUI(QtGui.QScrollArea, Ui_initialConditionsUI):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QScrollArea.__init__(self, parent)

        self.setupUi(self)


class initialConditionsWidget(initialConditionsUI):

    def __init__(self,folder,nproc):
        self.currentFolder = folder
        initialConditionsUI.__init__(self)
        self.nproc = nproc
        [self.timedir,self.fields,currtime] = currentFields(self.currentFolder,nproc=self.nproc)
        self.addTabs()

        #--Ver si runPFlow esta habilitado
        for itab in range(self.tabWidget.count()):
            ifield = self.tabWidget.tabText(itab)
            if ifield=='U':                
                filename = '%s/system/fvSolution'%self.currentFolder
                parsedData2 = ParsedParameterFile(filename,createZipped=False)
                cb = self.tabWidget.widget(itab).findChildren(QtGui.QCheckBox)[0]
                
                if ('potentialFlowEnabled' in parsedData2.content.keys()):
                    val = parsedData2['potentialFlowEnabled']
                    if val=='yes':
                        cb.setChecked(True)
        
        self.pushButton.setEnabled(False)
        
    def setInitialConditions(self,field):
        filename = '%s/%s' % (self.timedir,field)
        filenamefield = ParsedParameterFile(filename,listLengthUnparsed=20,createZipped=False)
        unifield = filenamefield['internalField']
        if (unifield.isUniform()):
            return unifield.val
        else:
            return 'error'
        
        
    def addTabs(self,ipatch=None):
        for itab in range(self.tabWidget.count()):
            layout = self.tabWidget.widget(itab).findChildren(QtGui.QVBoxLayout)[0]
            self.clearLayout(layout,0)
        self.tabWidget.clear()
        for ifield in self.fields:
            if ifield not in unknowns:
                continue
            widget = QtGui.QWidget()
            layout = QtGui.QVBoxLayout(widget)
            
            layout2 = QtGui.QHBoxLayout()
            cb = QtGui.QComboBox()
            cb.addItems(['uniform','nonuniform'])
            values = self.setInitialConditions(ifield)
            layout2.addWidget(cb)
            if types[ifield]=='scalar':
                ledit = QtGui.QLineEdit()
                ledit.setValidator(QtGui.QDoubleValidator())
                if type(values)!=str:
                    ledit.setText(str(values))
                QtCore.QObject.connect(ledit, QtCore.SIGNAL(_fromUtf8("textEdited(QString)")), self.checkData)
                layout2.addWidget(ledit)                    
            else:
                for j in range(3):
                    ledit = QtGui.QLineEdit()
                    ledit.setValidator(QtGui.QDoubleValidator())
                    if type(values)!=str:
                        ledit.setText(str(values.vals[j]))
                    layout2.addWidget(ledit)
                    QtCore.QObject.connect(ledit, QtCore.SIGNAL(_fromUtf8("textEdited(QString)")), self.checkData)
                    
            layout.addLayout(layout2)
            if ifield=='U':
                qbutton = QtGui.QCheckBox()
                qbutton.setText('Initialize from potential flow')
                layout.addWidget(qbutton)
                QtCore.QObject.connect(qbutton, QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), self.onPotentialFlow)
                QtCore.QObject.connect(qbutton, QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), self.checkData)
            
            spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
            layout.addItem(spacerItem)
        
            self.tabWidget.addTab(widget, ifield)
            self.tabWidget.setTabText(self.tabWidget.count(),ifield)

    def onPotentialFlow(self):
        
        for itab in range(self.tabWidget.count()):
            ifield = self.tabWidget.tabText(itab)
            if ifield=='U':
                print ifield
                layout = self.tabWidget.widget(itab).findChildren(QtGui.QVBoxLayout)[0]
                cb = self.tabWidget.widget(itab).findChildren(QtGui.QCheckBox)[0]
                
                layout2 = layout.itemAt(0).layout()
                for i in range(layout2.count()):
                    if isinstance(layout2.itemAt(i), QtGui.QWidgetItem):
                        layout2.itemAt(i).widget().setEnabled(not cb.isChecked())
                
                if cb.isChecked():
                    layoutH = QtGui.QHBoxLayout()
                    layoutH.setObjectName('RunFlowButton')
                    self.runButton = QtGui.QPushButton()
                    self.runButton.setText(' Run Potential Flow')
                    
                    icon = QtGui.QIcon()
                    from os import path
                    filename = _fromUtf8(path.join(path.dirname(__file__),"images/fromHelyx/next_grey16.png"))
                    icon.addPixmap(QtGui.QPixmap(filename),QtGui.QIcon.Normal,QtGui.QIcon.Off)
                    self.runButton.setIcon(icon)
                    
                    QtCore.QObject.connect(self.runButton, QtCore.SIGNAL(_fromUtf8("pressed()")), self.runPotentialFlow)
                    layoutH.addWidget(self.runButton)
                    layout.addLayout(layoutH)
                else:
                    layH = self.tabWidget.widget(itab).findChildren(QtGui.QHBoxLayout,'RunFlowButton')[0]
                    layV = self.tabWidget.widget(itab).findChildren(QtGui.QVBoxLayout)[0]
                    self.clearLayout(layH,0)
                    layV.removeItem(layH)
                break
            
    def runPotentialFlow(self):        
        self.runButton.setEnabled(False)
        command = 'touch %s/potentialFoam.log'%self.currentFolder
        os.system(command)
        
        #--Abrir ventana de log
        self.window().newLogTab('Potential Foam','%s/potentialFoam.log'%self.currentFolder)
        
        #--Creo un thread para potentialFoam
        if int(self.nproc)<=1:
            command = 'potentialFoam -case %s > %s/potentialFoam.log'%(self.currentFolder,self.currentFolder)
        else:
            command = 'mpirun -np %s potentialFoam -case %s -parallel > %s/potentialFoam.log'%(str(self.nproc), self.currentFolder,self.currentFolder)

        self.threadpotentialFoam = ExampleThread(command)
        self.connect(self.threadpotentialFoam, QtCore.SIGNAL("finished()"), self.enableButton) #Esto es una porqueria pero no encontre otra forma
        self.connect(self.threadpotentialFoam, QtCore.SIGNAL("finished()"), self.threadpotentialFoam.terminate)
        self.threadpotentialFoam.start()
        
    def enableButton(self):
        self.runButton.setEnabled(True)

    def clearLayout(self, layout, dejar):
        for i in reversed(range(layout.count())):
            if i>= dejar:
                item = layout.itemAt(i)
        
                if isinstance(item, QtGui.QWidgetItem):
                    item.widget().close()
                    item.widget().deleteLater()
                    # or
                    # item.widget().setParent(None)
                elif isinstance(item, QtGui.QSpacerItem):
                    None
                    # no need to do extra stuff
                else:
                    self.clearLayout(item.layout(),0)
        
                # remove the item from layout
                layout.removeItem(item)

       
    def setConditions(self):
        runPotentialFlow = 0
        for itab in range(self.tabWidget.count()):
            ifield = self.tabWidget.tabText(itab)
            layout = self.tabWidget.widget(itab).findChildren(QtGui.QVBoxLayout)[0]
            filename = '%s/%s'%(self.timedir,ifield)
            parsedData = ParsedParameterFile(filename,listLengthUnparsed=20,createZipped=False)
            layout2 = layout.itemAt(0).layout()
            if layout2.count()==2:
                parsedData['internalField'] = '%s %s'%(layout2.itemAt(0).widget().currentText(),layout2.itemAt(1).widget().text())
            else:
                parsedData['internalField'] = '%s (%s %s %s)'%(layout2.itemAt(0).widget().currentText(),layout2.itemAt(1).widget().text(),layout2.itemAt(2).widget().text(),layout2.itemAt(3).widget().text())
            
            parsedData.writeFile()
        
            if ifield == 'U': #and self.tabWidget.widget(itab).findChildren(QtGui.QCheckBox)[0].isChecked():
                #QtGui.QMessageBox.about(self, "ERROR", 'Debe simularse con potentialFoam, hacer!!')
                parsedData['internalField'] = '%s (%s %s %s)'%('uniform',0,0,0)
                filename = '%s/system/fvSolution'%self.currentFolder
                parsedData2 = ParsedParameterFile(filename,createZipped=False)
                
                if ('potentialFlowEnabled' not in parsedData2.content.keys()): #Si no existe (nunca abrio al gui) la creo
                    parsedData2['potentialFlowEnabled'] = {}            
                    
                cb = self.tabWidget.widget(itab).findChildren(QtGui.QCheckBox)[0]
                parsedData2['potentialFlowEnabled'] = 'yes' if cb.isChecked() else 'no'
                
                parsedData2.writeFile()
                
        
        self.pushButton.setEnabled(False)
        return
        
    def checkData(self):
#        ready = True
#        for itab in range(self.tabWidget.count()):
#            edits = self.tabWidget.widget(itab).findChildren(QtGui.QLineEdit)
#            for E in edits:
#                if E.isEnabled():
#                    if not E.text():
#                        ready = False
#        if ready:
        self.pushButton.setEnabled(True)
#        else:
#            self.pushButton.setEnabled(False)