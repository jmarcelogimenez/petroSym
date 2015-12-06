# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from materials_ui import Ui_materialsUI
from materialsABM import *
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


class materialsUI(QtGui.QScrollArea, Ui_materialsUI):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QScrollArea.__init__(self, parent)

        self.setupUi(self)
        
class materials(materialsUI):
    
    def __init__(self,currentFolder,iphase):
        materialsUI.__init__(self)
        self.currentFolder = currentFolder
        self.iphase = iphase
        self.loadData()
        print self.data
        self.setData()
        
        
    def loadData(self):        
        filename = '%s/constant/transportProperties'%self.currentFolder
        self.parsedData = ParsedParameterFile(filename,createZipped=False)
        keys = self.parsedData.getValueDict().keys()
        if 'phases' in keys:
            self.data = self.parsedData[self.parsedData['phases'][self.iphase]].getValueDict()
        else:
            self.data = self.parsedData.getValueDict()        
        return
        
    def setData(self):
        for key in self.data.keys():
            if hasattr(self, key):
                if key=='name':
                    self.__getattribute__(key).setText(str(self.data[key]))
                elif key in self.__dict__.keys():
                    self.__getattribute__(key).setText(str(self.data[key][-1]))
        return
        
    def toABM(self):
        w = materialsABM()
        result = w.exec_()
        if result:
            data = w.getSelectedData()
            if data:
                keys = self.parsedData.getValueDict().keys()
                if 'phases' in keys:
                    oldname = self.parsedData['phases'][self.iphase]
                    newname = data['name']
                    del self.parsedData[oldname]
                    self.parsedData['phases'][self.iphase] = newname
                    self.parsedData[newname] = data
                    self.data = self.parsedData[self.parsedData['phases'][self.iphase]].getValueDict()
                else:
                    keys = data.keys()
                    for key in keys:
                        self.parsedData[key] = data[key]
                    self.data = self.parsedData.getValueDict() 
                self.parsedData.writeFile()
                self.setData()
        return