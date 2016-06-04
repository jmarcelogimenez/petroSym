# -*- coding: utf-8 -*-
"""
Created on Sat May 14 02:27:09 2016

@author: santiago
"""

from PyQt4 import QtCore,QtGui
from gravity_ui import Ui_gravity

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
        self.apply_button.setEnabled(False)
        return