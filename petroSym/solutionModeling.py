# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from solutionModeling_ui import Ui_solutionModelingUI
import os
from tracers import *

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


available = set(['icoFoam','pimpleFoam','interFoam'])

Steady = set([])
Transient = set(['icoFoam','pimpleFoam','interFoam'])
Incompressible = set(['icoFoam','pimpleFoam','interFoam'])
Compressible = set([])
Turbulence = set(['pimpleFoam','interFoam'])
Multiphase = set(['interFoam'])
Buoyancy = set([])

RASModels = ['kEpsilon','kOmega','kOmegaSST']
LESModels = ['Smagorinsky']


class solutionModelingUI(QtGui.QScrollArea, Ui_solutionModelingUI):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QScrollArea.__init__(self, parent)

        self.setupUi(self)
        
class solutionModeling(solutionModelingUI):

    def __init__(self, currentFolder, currentSolver):
        solutionModelingUI.__init__(self)
        self.currentFolder = currentFolder
        self.currentSolver = currentSolver
        self.label_solver.setText(currentSolver)
        self.listWidget.addItems(list(available))
        self.pushButton.setEnabled(False)
        
    def getData(self):
        data = {}
        return data
        
    def setData(self, data):
        return
        
    def aplicar(self):
        solvername = str(self.listWidget.currentItem().text())
        if solvername != self.currentSolver:
        
            quit_msg = "Caution! Current software version will replace all data! Continue?"
            reply = QtGui.QMessageBox.question(self, 'Message', quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.window().resetCase(solvername)                
                self.window().meshW.updateFieldFiles()
            
        if self.groupBox_turbulence.isEnabled():
            filename = '%s/constant/turbulenceProperties'%self.currentFolder
            tprop = ParsedParameterFile(filename,createZipped=False)    
            if self.radioTurb2.isChecked():
                RASModelName = str(self.comboBoxTurb.currentText())
                filename = '%s/constant/RASProperties'%self.currentFolder
                Rprop = ParsedParameterFile(filename,createZipped=False)
                Rprop['RASModel'] = RASModelName
                Rprop.writeFile()
                tprop['simulationType'] = 'RASModel'
            elif self.radioTurb3.isChecked():
                LESModelName = str(self.comboBoxTurb.currentText())
                filename = '%s/constant/LESProperties'%self.currentFolder
                Lprop = ParsedParameterFile(filename,createZipped=False)
                Lprop['LESModel'] = LESModelName
                Lprop.writeFile()
                tprop['simulationType'] = 'LESModel'
            else:
                tprop['simulationType'] = 'laminar'
                tprop.writeFile()
                return
            
            tprop.writeFile()
            
        self.pushButton.setEnabled(False)
                

        return
        
    def editTracers(self):
        w = tracers(self.currentFolder)
        result = w.exec_()
        if result:
            w.saveCaseData(True)
        
    def filtering(self):
        nowAvail = available
        if self.radioFlow1.isChecked():
            nowAvail = set.intersection(Compressible,nowAvail)
        if self.radioFlow2.isChecked():
            nowAvail = set.intersection(Incompressible,nowAvail)
        if self.radioTime1.isChecked():
            nowAvail = set.intersection(Steady,nowAvail)
        if self.radioTime2.isChecked():
            nowAvail = set.intersection(Transient,nowAvail)
        if self.checkBoxTurbulence.checkState() == QtCore.Qt.Checked:
            nowAvail = set.intersection(Turbulence,nowAvail)
            self.groupBox_turbulence.setEnabled(True)
        else:
            self.groupBox_turbulence.setEnabled(False)
        if self.checkBoxMultiphase.checkState() == QtCore.Qt.Checked:
            nowAvail = set.intersection(Multiphase,nowAvail)
        if self.checkBoxBuoyancy.checkState() == QtCore.Qt.Checked:
            nowAvail = set.intersection(Buoyancy,nowAvail)
        self.listWidget.clear()
        self.listWidget.addItems(list(nowAvail))        
        return
        
    def changeTurbList(self):
        self.comboBoxTurb.clear()
        if self.radioTurb1.isChecked():
            self.comboBoxTurb.addItems([])
        if self.radioTurb2.isChecked():
            self.comboBoxTurb.addItems(RASModels)
        if self.radioTurb3.isChecked():
            self.comboBoxTurb.addItems(LESModels)
            
    def changeSolverSelection(self):
        if self.listWidget.currentRow() == -1:
            self.pushButton.setEnabled(False)
        else:
            self.pushButton.setEnabled(True)