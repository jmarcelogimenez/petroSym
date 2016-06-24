# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from materialsABM_ui import materialsABMUI
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

emptys = {}
emptys['name'] = 'newMaterial'
emptys['rho'] = ['rho','[ 1 -3 0 0 0 0 0 ]',0]
emptys['mu'] = ['mu','[ 1 -1 -1 0 0 0 0 ]',0]
emptys['nu'] = ['nu','[ 0 2 -1 0 0 0 0 ]',0]
emptys['Cp'] = ['Cp','[ 0 2 -2 -1 0 0 0 ]',0]
emptys['Prt'] = ['Prt','[ 0 0 0 0 0 0 0 ]',0]
emptys['DT'] = ['DT','[ 1 1 -3 -1 0 0 0 ]',0]
emptys['Pr'] = ['Pr','[ 0 0 0 0 0 0 0 ]',0]
emptys['TRef'] = ['TRef','[ 0 0 0 1 0 0 0 ]',0]
emptys['pRef'] = ['pRef','[ 1 -1 -2 0 0 0 0 ]',0]
emptys['beta'] = ['beta','[ 0 0 0 -1 0 0 0 ]',0]

class materialsABM(materialsABMUI):

    def __init__(self):
        materialsABMUI.__init__(self)
        
        for key in emptys.keys():
            if key != 'name':
                self.__getattribute__(key).setValidator(QtGui.QDoubleValidator())
        
        filename = '%s/caseDicts/materialProperties.incompressible'%os.path.dirname(os.path.realpath(__file__)) #Path de python
        from os.path import expanduser
        self.home = expanduser('~')
        filename2 = '%s/.config/petroSym/materialProperties.incompressible'%self.home #Path en home
        
        if not os.path.isfile(filename2) or (os.path.isfile(filename2) and os.path.getsize(filename2) == 0): #Si no existe, o existe y esta vacio
            command = 'mkdir -p %s/.config/petroSym/'%self.home #-p por si ya existe el directorio
            os.system(command)
            command = 'cp %s %s/.config/petroSym/'%(filename,self.home) #copio el archivo
            os.system(command)
        
        parsedData = ParsedParameterFile(filename2,createZipped=False)
            
        self.defaults = parsedData['defaults']
        self.userLibrary = parsedData['userLibrary']
        
        for key in self.defaults.keys():
            self.list_default.addItem(key)
            
        for key in self.userLibrary.keys():
            self.list_user.addItem(key)
        
        self.list_default.item(0).setSelected(True)
        self.changeSelectionDefault()
                

    def loadUserLibrary(self):
        filename = '%s/.config/petroSym/materialProperties.incompressible'%self.home #Path en home
        parsedData = ParsedParameterFile(filename,createZipped=False)
            
        self.userLibrary = parsedData['userLibrary']
        self.list_user.clear()
        for key in self.userLibrary.keys():
            self.list_user.addItem(key)
        
    def saveUserLibrary(self):
        filename = '%s/.config/petroSym/materialProperties.incompressible'%self.home #Path en home
        parsedData = ParsedParameterFile(filename,createZipped=False)
        parsedData['userLibrary'] = self.userLibrary
        parsedData.writeFile()
        
        return

    def changeSelectionDefault(self):
        if not self.list_default.selectedItems():
            #print 'No hay selected'
            return
        key = str(self.list_default.selectedItems()[0].text())
        for item in self.list_user.selectedItems():
            item.setSelected(False)
        
        self.updateParameters(self.defaults[key])   
        
        self.OnOff(False)
        return
    
    def changeSelectionUser(self):
        if not self.list_user.selectedItems():
            return
        key = str(self.list_user.selectedItems()[0].text())
        for item in self.list_default.selectedItems():
            item.setSelected(False)
        self.updateParameters(self.userLibrary[key])
        self.OnOff(True)
        return
        
    def updateParameters(self,data):
        for key in emptys.keys():
            if key=='name':
                self.__getattribute__(key).setText(str(data[key]))
            elif key in self.__dict__.keys():
                self.__getattribute__(key).setText(str(data[key][-1]))
    
    def OnOff(self,V):
        keys = emptys.keys()
        for key in keys:
            self.__getattribute__(key).setEnabled(V)
        self.button_remove.setEnabled(V)
        self.button_save.setEnabled(V)
        
    def new(self):
        self.updateParameters(emptys)
        self.OnOff(True)
        for item in self.list_default.selectedItems():
            item.setSelected(False)
        for item in self.list_user.selectedItems():
            item.setSelected(False)
        self.button_remove.setEnabled(False)
        return
        
    def copy(self):
        data = self.getSelectedData()
        if data:
            self.updateParameters(data)
            texto = str(self.name.text()) + "_copy"
            self.name.setText(texto)
            self.OnOff(True)    
        
        return
        
    def getSelectedData(self):
        ditem = self.list_default.selectedItems()
        data = False
        if len(ditem):
            data = self.defaults[str(ditem[0].text())]
        else:
            uitem = self.list_user.selectedItems()
            if len(uitem):
                data = dict(self.userLibrary[str(uitem[0].text())])
        return data
        
    def remove(self):
        uitem = self.list_user.selectedItems()
        if len(uitem):
            w = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Caution", "Are you sure to remove?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
            ret = w.exec_()
            if(QtGui.QMessageBox.Yes == ret):
                del self.userLibrary[str(uitem[0].text())]
                self.saveUserLibrary()
                self.loadUserLibrary()
                #print 'ojo que no cambia la seleccion luego de eliminar'                
                self.list_default.setFocus()
                self.list_default.item(0).setSelected(True)
                self.changeSelectionDefault()
                
        return
        
    def changeEdit(self):
        ready = True
        edits = self.findChildren(QtGui.QLineEdit)
        for E in edits:
            if E.isEnabled():
                if not E.text():
                    ready = False
        if ready:
            self.button_save.setEnabled(True)
        else:
            self.button_save.setEnabled(False)
        
        
    def addMaterial(self):
        name = str(self.name.text())
        self.userLibrary[name] = self.defaults['air'].copy()
        keys = emptys.keys()
        for key in keys:
            if key=='name':
                self.userLibrary[name][key] = str(self.__getattribute__(key).text())
            else:
                self.userLibrary[name][key][-1] = str(self.__getattribute__(key).text())
        self.saveUserLibrary()
        self.loadUserLibrary()  
        
    def accept(self):
        if not self.list_default.selectedItems() and not self.list_user.selectedItems():
            w = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Caution", "Nothing selected, please select a material", QtGui.QMessageBox.Ok)
            w.exec_()
            return
        materialsABMUI.accept(self)