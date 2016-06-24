# -*- coding: utf-8 -*-
"""
Created on Sat May 14 02:27:09 2016

@author: santiago
"""

from PyQt4 import QtCore,QtGui
from gravity_ui import Ui_gravity
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

class gravityUI(QtGui.QScrollArea, Ui_gravity):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QScrollArea.__init__(self, parent)

        self.setupUi(self)

class gravity(gravityUI):
    
    def __init__(self, currentFolder, currentSolver):
        gravityUI.__init__(self)
        self.currentFolder = currentFolder
        self.currentSolver = currentSolver
        self.gx.setValidator(QtGui.QDoubleValidator())
        self.gy.setValidator(QtGui.QDoubleValidator())
        self.gz.setValidator(QtGui.QDoubleValidator())
        QtCore.QObject.connect(self.gx,QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.checkAccept)
        QtCore.QObject.connect(self.gy,QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.checkAccept)
        QtCore.QObject.connect(self.gz,QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.checkAccept)
        
        self.loadCaseData()
        
        self.apply_button.setEnabled(False)
        
        return
        
    def loadCaseData(self):
        filename = '%s/constant/g'%self.currentFolder
        if os.path.isfile(filename):
            self.parsedData = ParsedParameterFile(filename,createZipped=False)
        else:
            command = 'cp %s/templates/template_%s/constant/g %s/constant/.'% (os.path.dirname(os.path.realpath(__file__)),self.currentSolver,self.currentFolder)
            os.system(command)
            self.parsedData = ParsedParameterFile(filename,createZipped=False)
        self.gx.setText(str(self.parsedData['value'][0]))
        self.gy.setText(str(self.parsedData['value'][1]))
        self.gz.setText(str(self.parsedData['value'][2]))
        
    def saveData(self):
        self.parsedData['value'][0] = float(self.gx.text())
        self.parsedData['value'][1] = float(self.gy.text())
        self.parsedData['value'][2] = float(self.gz.text())
        self.parsedData.writeFile()
        
        self.apply_button.setEnabled(False)
        
        
    def checkAccept(self):
        
        ready = True
        edits = self.findChildren(QtGui.QLineEdit)
        for E in edits:
            if E.isEnabled():
                if not E.text():
                        ready = False
        if ready:
            self.apply_button.setEnabled(True)
        else:
            self.apply_button.setEnabled(False)
        
        
        