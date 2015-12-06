# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from solverSettings_ui import Ui_solverSettingsUI
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


class solverSettingsUI(QtGui.QScrollArea, Ui_solverSettingsUI):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QScrollArea.__init__(self, parent)

        self.setupUi(self)
        
class solverSettings(solverSettingsUI):

    def __init__(self,folder):
        self.currentFolder = folder
        solverSettingsUI.__init__(self)
        self.loadData()
        self.pushButton.setEnabled(False)
        

    def loadData(self):
        filename = '%s/system/fvSolution'%self.currentFolder
        parsedData = ParsedParameterFile(filename,createZipped=False)
        #do something with parsed Data
        return
        
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
        filename = '%s/system/fvSolution'%self.currentFolder
        parsedData = ParsedParameterFile(filename,createZipped=False)
        
        #modify data
        parsedData.writeFile()
        
        self.pushButton.setEnabled(False)
        return

    def editar(self):
        #command = '$EDITOR %s/system/controlDict &'%self.currentFolder
        command = 'gedit %s/system/fvSolution &'%self.currentFolder
        os.system(command)
        return
