# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from reset_ui import resetUI
import os

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


class reset(resetUI):

    def __init__(self):
        resetUI.__init__(self)
        self.params = {}
        self.params['cb1'] = ' --processors-remove'
        self.params['cb2'] = ' --vtk-keep'
        self.params['cb3'] = ' --keep-last'
        self.params['cb4'] = ' --keep-parallel'
        self.params['cb5'] = ' --keep-postprocessing'

    def getParams(self):
        texto = ''
        for key in self.params:
            if self.__getattribute__(key).isChecked():
                texto = texto + self.params[key]
        return texto
        
    def resetFigures(self):
        return True
        
    def deleteSnapshots(self):
        return not self.__getattribute__('cb6').isChecked()
        
    def deletePostpro(self):
        return not self.__getattribute__('cb5').isChecked()