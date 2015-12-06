# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from postpro_ui import Ui_postproUI
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.RunDictionary.BoundaryDict import BoundaryDict
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from utils import *

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

class postproUI(QtGui.QScrollArea, Ui_postproUI):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QScrollArea.__init__(self, parent)
        self.setupUi(self)
        
apps = {}
apps['Vorticity'] = 'vorticity'
apps['Mach Number'] = 'Mach'
apps['Courant Number'] = 'Co'
apps['Pecklet Number'] = 'Pe'
apps['Stream Function'] = 'streamFunction'
apps['Enstrophy'] = 'enstrophy'
apps['Q Criterion Number'] = 'Q'
apps['y Plus RAS'] = 'yPlusRAS'
apps['y Plus LES'] = 'yPlusLES'
apps['Wall Velocity Gradient'] = 'wallGradU'
apps['Average'] = 'patchAverage'
apps['Integral'] = 'patchIntegrate'

class postproWidget(postproUI):
    
    def __init__(self,currentFolder):
        postproUI.__init__(self)
    
    def setCurrentFolder(self, currentFolder):
        self.currentFolder = currentFolder
        #filling data
        [timedir,self.fields,currtime] = currentFields(str(self.currentFolder))
        self.field_3.clear()
        self.field_3.addItems(self.fields)
        self.boundaries = BoundaryDict(str(self.currentFolder))
        self.bou_3.clear()        
        self.bou_3.addItems(self.boundaries.patches())
        
    def openParaview(self):
        os.system('paraFoam -builtin -case %s &'%self.currentFolder)

    def exportData(self):
        opt = str(self.comboBox.currentText())
        filename = '%s/export.log'%self.currentFolder
        self.window().newLogTab('Export',filename)
        if opt=='VTK':
            action = 'foamToVTK -case %s > %s &' %(self.currentFolder,filename)
        elif opt=='Fluent':
            action = 'foamMeshToFluent -case %s &' %(self.currentFolder)
            os.system(action)
            'cp caseDicts/foamDataToFluentDict %s/system/foamDataToFluentDict'%self.currentFolder
            os.system(action)
            parsedData = ParsedParameterFile('%s/system/foamDataToFluentDict'%self.currentFolder,createZipped=False)
            ii = 10
            for ifield in self.fields:
                if ifield not in parsedData.getValueDict().keys():
                    parsedData[ifield] = ii
                    ii = ii + 1                        
            action = 'foamDataToFluent -case %s > %s &' %(self.currentFolder,filename)
        elif opt=='Ensight':
            action = 'foamToEnsight -case %s > %s &' %(self.currentFolder,filename)
        os.system(action)
        return
    
    def calculate1(self):
        tt = ''
        if self.time_1.currentText()=='Latest Time':
            tt = '-latestTime'
        filename = '%s/field_calculation.log'%self.currentFolder
        self.window().newLogTab('Postpro Field',filename)
        action = '%s -case %s %s > %s'%(apps[str(self.field_1.currentText())],self.currentFolder, tt, filename)
        os.system(action)
        return

    def calculate2(self):
        tt = ''
        if self.time_2.currentText()=='Latest Time':
            tt = '-latestTime'
        filename = '%s/walls_calculation.log'%self.currentFolder
        if self.field_2.currentText()=='y Plus RAS':
            if not os.path.isfile('%s/constant/RASProperties'%self.currentFolder):
                QtGui.QMessageBox(QtGui.QMessageBox.Information, "Caution", "Action can not be done!").exec_()
                return
        if self.field_2.currentText()=='y Plus LES':
            if not os.path.isfile('%s/constant/LESProperties'%self.currentFolder):
                QtGui.QMessageBox(QtGui.QMessageBox.Information, "Caution", "Action can not be done!").exec_()
                return
        self.window().newLogTab('Postpro Wall',filename)
        action = '%s -case %s %s > %s'%(apps[str(self.field_2.currentText())],self.currentFolder, tt, filename)
        os.system(action)
        return
        
    def calculate3(self):
        tt = ''
        if self.time_3.currentText()=='Latest Time':
            tt = '-latestTime'
        filename = '%s/patch_calculation.log'%self.currentFolder
        self.window().newLogTab('Postpro Patch',filename)
        fieldName = str(self.field_3.currentText())
        patchName = str(self.bou_3.currentText())
        action = '%s -case %s  %s %s %s > %s &' %(apps[str(self.type_3.currentText())],self.currentFolder,tt,fieldName,patchName,filename)
        os.system(action)
        
        return
    
    