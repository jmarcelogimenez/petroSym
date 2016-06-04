# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from solutionModeling_ui import Ui_solutionModelingUI
import os
#from tracers import *

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


actualsolvers = set(['pimpleFoam','icoFoam','interFoam','simpleFoam'])

available = set(['pimpleFoam','icoFoam'])

pimpleFoam_setup_force = set(['Transient','Incompressible'])
pimpleFoam_setup_optional = set(['Turbulence'])
icoFoam_setup_force = set(['Transient','Incompressible'])
icoFoam_setup_optional = set([])
interFoam_setup_force = set(['Transient','Incompressible'])
interFoam_setup_optional = set(['Turbulence','Multiphase'])
simpleFoam_setup_force = set(['Steady','Incompressible'])
simpleFoam_setup_optional = set(['Turbulence'])

solvers_setup = dict()
solvers_setup['force'] = [pimpleFoam_setup_force,icoFoam_setup_force,interFoam_setup_force,simpleFoam_setup_force]
solvers_setup['optional'] = [pimpleFoam_setup_optional,icoFoam_setup_optional,interFoam_setup_optional,simpleFoam_setup_optional]

Steady = set([])
Transient = set(['icoFoam','pimpleFoam','interFoam'])
Incompressible = set(['icoFoam','pimpleFoam','interFoam'])
Compressible = set([])
Turbulence = set(['pimpleFoam','interFoam'])
Multiphase = set(['interFoam'])
Buoyancy = set([])


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
        folder=currentFolder.split('/')
        self.label_folder.setText(folder[len(folder)-1])
        
        info = ''
        for i in range(len(solvers_setup['force'])):
            if (self.currentSolver == list(actualsolvers)[i]):
                for j in range(len(solvers_setup['force'][i])):
                    info = info+list(solvers_setup['force'][i])[j]
                    if j != len(solvers_setup['force'][i])-1:
                        info = info+', '
               
        self.label_info.setText(info)
        self.radioFlow2.setChecked(True)
        self.radioTime2.setChecked(True)
        self.pushButton.setEnabled(False)
        
    def getData(self):
        data = {}
        return data
        
    def setData(self, data):
        return
        
    def show_info(self):
        from solvers_info_ui import Ui_solvers_info
        about = QtGui.QDialog()
        info = Ui_solvers_info()
        about.setFixedSize(389,208)
        info.setupUi(about)
        about.exec_()
        return
        
    def aplicar(self):
        solvername = str(self.listWidget.currentItem().text())
        
        if solvername not in available:
            w=QtGui.QMessageBox(QtGui.QMessageBox.Information, "ERROR", "Solver Not Available!")
            w.exec_()
            return
        
        if solvername != self.currentSolver:
        
            quit_msg = "Caution! Current software version will replace all data! Continue?"
            reply = QtGui.QMessageBox.question(self, 'Message', quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.window().resetCase(solvername)                
                self.window().meshW.updateFieldFiles()
            
        self.pushButton.setEnabled(False)

        return
        
#    def editTracers(self):
#        w = tracers(self.currentFolder)
#        result = w.exec_()
#        if result:
#            w.saveCaseData(True)
            
    def filtering(self):
        actualChecked_force = set([])
        actualChecked_optional = set([])
        
        if self.radioFlow1.isChecked():
            actualChecked_force.add('Compressible')
        if self.radioFlow2.isChecked():
            actualChecked_force.add('Incompressible')
        if self.radioTime1.isChecked():
            actualChecked_force.add('Steady')
        if self.radioTime2.isChecked():
            actualChecked_force.add('Transient')
        if self.checkBoxTurbulence.checkState() == QtCore.Qt.Checked:
            actualChecked_optional.add('Turbulence')
            #self.groupBox_turbulence.setEnabled(True)
        #else:
            #self.groupBox_turbulence.setEnabled(False)
        if self.checkBoxMultiphase.checkState() == QtCore.Qt.Checked:
            actualChecked_optional.add('Multiphase')
        if self.checkBoxBuoyancy.checkState() == QtCore.Qt.Checked:
            actualChecked_optional.add('Buoyancy')
            
        self.listWidget.clear()
        
        for i in range(len(solvers_setup['force'])):
            if actualChecked_force == solvers_setup['force'][i]:
                if len(actualChecked_optional.difference(solvers_setup['optional'][i])) == 0:
                    self.listWidget.addItem(list(actualsolvers)[i])
                else:
                    continue
                
        return
        
#    def filtering(self):
#        nowAvail = available
#        if self.radioFlow1.isChecked():
#            nowAvail = set.intersection(Compressible,nowAvail)
#        if self.radioFlow2.isChecked():
#            nowAvail = set.intersection(Incompressible,nowAvail)
#        if self.radioTime1.isChecked():
#            nowAvail = set.intersection(Steady,nowAvail)
#        if self.radioTime2.isChecked():
#            nowAvail = set.intersection(Transient,nowAvail)
#        if self.checkBoxTurbulence.checkState() == QtCore.Qt.Checked:
#            nowAvail = set.intersection(Turbulence,nowAvail)
#            self.groupBox_turbulence.setEnabled(True)
#        else:
#            self.groupBox_turbulence.setEnabled(False)
#        if self.checkBoxMultiphase.checkState() == QtCore.Qt.Checked:
#            nowAvail = set.intersection(Multiphase,nowAvail)
#        if self.checkBoxBuoyancy.checkState() == QtCore.Qt.Checked:
#            nowAvail = set.intersection(Buoyancy,nowAvail)
#        self.listWidget.clear()
#        self.listWidget.addItems(list(nowAvail))    
#        return
            
    def changeSolverSelection(self):
        if self.listWidget.currentRow() == -1:
            self.pushButton.setEnabled(False)
        else:
            self.pushButton.setEnabled(True)