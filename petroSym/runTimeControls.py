# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from runTimeControls_ui import Ui_runTimeControlsUI
import os

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


class runTimeControlsUI(QtGui.QScrollArea, Ui_runTimeControlsUI):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QScrollArea.__init__(self, parent)

        self.setupUi(self)
        
class runTimeControls(runTimeControlsUI):

    def __init__(self,folder):
        self.currentFolder = folder
        runTimeControlsUI.__init__(self)
        
        self.start_from.setValidator(QtGui.QDoubleValidator())
        self.end_time.setValidator(QtGui.QDoubleValidator())
        self.delta_time.setValidator(QtGui.QDoubleValidator())
        self.max_cfl.setValidator(QtGui.QDoubleValidator())
        self.max_cfl_alpha.setValidator(QtGui.QDoubleValidator())
        self.max_deltat.setValidator(QtGui.QDoubleValidator())
        self.write_control.setValidator(QtGui.QIntValidator())
        
        self.cb_start_from_ii = {}
        self.cb_start_from_iinv = ['startTime','firstTime','latestTime']
        self.cb_start_from_ii['startTime'] = 0        
        self.cb_start_from_ii['firstTime'] = 1
        self.cb_start_from_ii['latestTime'] = 2
        
        self.cb_write_control_ii = {}
        self.cb_write_control_iinv = ['timeStep', 'runTime', 'clockTime']
        self.cb_write_control_ii['timeStep'] = 0        
        self.cb_write_control_ii['runTime'] = 1
        self.cb_write_control_ii['clockTime'] = 2
        
        self.format_ii = {}
        self.format_iinv = ['ascii', 'binary']
        self.format_ii['ascii'] = 0
        self.format_ii['binary'] = 1
        
        self.compression_ii = {}
        self.compression_iinv = ['no', 'yes']
        self.compression_ii['off'] = 0
        self.compression_ii['on'] = 1
        self.compression_ii['no'] = 0
        self.compression_ii['yes'] = 1
        self.compression_ii['bas'] = 2
        
        self.loadData()
        
        self.pushButton.setEnabled(False)
        

    def loadData(self):
        filename = '%s/system/controlDict'%self.currentFolder
        parsedData = ParsedParameterFile(filename,createZipped=False)
        
        self.cb_start_from.setCurrentIndex(self.cb_start_from_ii[parsedData['startFrom']]) if parsedData.__contains__('startFrom') else None
        self.start_from.setText(str(parsedData['startTime'])) if parsedData.__contains__('startTime') else None
        self.start_from.setEnabled(False) if parsedData['startFrom'] != 'startTime' else None

        self.end_time.setText(str(parsedData['endTime'])) if parsedData.__contains__('endTime') else None
        self.delta_time.setText(str(parsedData['deltaT'])) if parsedData.__contains__('deltaT') else None
        
        if  parsedData.__contains__('adjustTimeStep') and parsedData['adjustTimeStep']=='yes':
            self.adjustable.setChecked(True)
            self.max_cfl.setEnabled(True)
            self.max_cfl_alpha.setEnabled(True)
            self.max_deltat.setEnabled(True)
        else:
            self.adjustable.setChecked(False)
            self.max_cfl.setEnabled(False)
            self.max_cfl_alpha.setEnabled(False)
            self.max_deltat.setEnabled(False)
        
        self.max_cfl.setText(str(parsedData['maxCo'])) if parsedData.__contains__('maxCo') else None
        self.max_cfl_alpha.setText(str(parsedData['maxAlphaCo'])) if parsedData.__contains__('maxAlphaCo') else None
        self.max_deltat.setText(str(parsedData['maxDeltaT'])) if parsedData.__contains__('maxDeltaT') else None

        self.cb_write_control.setCurrentIndex(self.cb_write_control_ii[parsedData['writeControl']]) if parsedData.__contains__('writeControl') else None
        self.write_control.setText(str(parsedData['writeInterval'])) if parsedData.__contains__('writeInterval') else None
        self.purge.setValue(parsedData['purgeWrite']) if parsedData.__contains__('purgeWrite') else None
        self.format.setCurrentIndex(self.format_ii[parsedData['writeFormat']]) if parsedData.__contains__('writeFormat') else None
        self.precision.setValue(parsedData['writePrecision']) if parsedData.__contains__('writePrecision') else None
        
        #self.compression.setCurrentIndex(self.compression_ii[str(parsedData['writeCompression'])]) if parsedData.__contains__('writeCompression') else None
        self.precision_time.setValue(parsedData['timePrecision']) if parsedData.__contains__('timePrecision') else None
        
    def onChange1(self, ii):
        self.start_from.setEnabled(True) if ii==0 else self.start_from.setEnabled(False)
        
    def onChange2(self, ii):
        if ii:
            self.max_cfl.setEnabled(True)
            self.max_cfl_alpha.setEnabled(True)
            self.max_deltat.setEnabled(True)
        else:
            self.max_cfl.setEnabled(False)
            self.max_cfl_alpha.setEnabled(False)
            self.max_deltat.setEnabled(False)
        
    def onChangeSomething(self):
        ready = True
        edits = self.findChildren(QtGui.QLineEdit)
        for E in edits:
            if E.isEnabled():
                if not E.text():
                        ready = False
        if ready:
            self.pushButton.setEnabled(True)
        else:
            self.pushButton.setEnabled(False)

    def aplicar(self):
        filename = '%s/system/controlDict'%self.currentFolder
        parsedData = ParsedParameterFile(filename,createZipped=False)
        
        parsedData['startFrom'] = self.cb_start_from_iinv[self.cb_start_from.currentIndex()]
        parsedData['startTime'] = str(self.start_from.text())
        parsedData['endTime'] = str(self.end_time.text())
        parsedData['deltaT'] = str(self.delta_time.text())
        if self.adjustable.isChecked():
            parsedData['adjustTimeStep'] = 'yes'
        else:
            parsedData['adjustTimeStep'] = 'no'
        parsedData['maxCo'] = str(self.max_cfl.text())
        parsedData['maxAlphaCo'] = str(self.max_cfl_alpha.text())
        parsedData['maxDeltaT'] = str(self.max_deltat.text())
        parsedData['writeControl'] = self.cb_write_control_iinv[self.cb_write_control.currentIndex()]
        parsedData['writeInterval'] = str(self.write_control.text())
        parsedData['purgeWrite'] = str(self.purge.value())
        parsedData['writePrecision'] = str(self.precision.value())
        parsedData['writeFormat'] = self.format_iinv[self.format.currentIndex()]
        parsedData['timePrecision'] = str(self.precision_time.value())
        parsedData['writeCompression'] = self.compression_iinv[self.compression.currentIndex()]
        parsedData['stopAt'] = 'endTime'
        
        parsedData.writeFile()
        
        self.pushButton.setEnabled(False)
        
        self.window().updateLogFiles()
        
        return

    def editar(self):
        #command = '$EDITOR %s/system/controlDict &'%self.currentFolder
        command = 'gedit %s/system/controlDict &'%self.currentFolder
        os.system(command)
        return
