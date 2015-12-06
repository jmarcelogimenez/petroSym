# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from bcPatch_ui import bcPatchUI
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


class bcPatch(bcPatchUI):

    def __init__(self, tipo):
        bcPatchUI.__init__(self)
        ii = 0
        while(self.comboBox.itemText(ii) != tipo):
            ii = ii + 1
        self.comboBox.setCurrentIndex(ii)
        
    def getPatchType(self):
        return str(self.comboBox.currentText())