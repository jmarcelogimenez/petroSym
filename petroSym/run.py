# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from run_ui import Ui_runUI
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
import os
from reset import *
from time import localtime, strftime, struct_time
from logTab import *
from ExampleThread import *
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

class runUI(QtGui.QScrollArea, Ui_runUI):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QScrollArea.__init__(self, parent)
        self.setupUi(self)
        
class runWidget(runUI):
    
    def __init__(self, currentFolder, solvername):
        runUI.__init__(self)
        self.solvername = solvername
        self.currentFolder = currentFolder

    def setCurrentFolder(self, currentFolder, solvername):
        self.currentFolder = currentFolder
        self.solvername = solvername
        [self.timedir,self.fields,self.currtime] = currentFields(self.currentFolder,nproc=self.window().nproc)
        
        #Si abro la gui y hay un caso corriendo, desabilito estos botones
        if (self.window().runningpid!= -1):
            self.pushButton_run.setEnabled(False)
            self.pushButton_reset.setEnabled(False)
        
        if self.window().nproc<=1:
            self.type_serial.setChecked(True)
            self.type_parallel.setChecked(False)            
        else:
            self.type_serial.setChecked(False)
            self.type_parallel.setChecked(True)            
            self.num_proc.setValue(self.window().nproc)
            
        self.pushButton_decompose.setEnabled(False)
        self.changeType()

    def runCase(self):
    
#        if self.window().nproc>1:        
#            w = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Is the case decomposed?", "Simulation will be done only if case decompositione was done previously. Continue?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
#            ret = w.exec_()
#            if(QtGui.QMessageBox.No == ret):
#                return
        
        #modifico el control dict porque pude haber parado la simulacion        
        filename = '%s/system/controlDict'%self.currentFolder
        parsedData = ParsedParameterFile(filename,createZipped=False)
        parsedData['stopAt'] = 'endTime'
        parsedData.writeFile()
        
        self.window().removeFilesPostPro()
        
        #retraso un minuto la edicion del control dict
        tt = list(localtime())
        tt[4] = (tt[4]-1)%60 #Agrego el modulo porque cuando el min es 0, 0-1 = -1
        command = 'touch -d "%s" %s'%(strftime("%Y-%m-%d %H:%M:%S", struct_time(tuple(tt))),filename)
        os.system(command)
        
        filename1 = '%s/run.log'%self.currentFolder
        filename2 = '%s/error.log'%self.currentFolder
        self.window().newLogTab('Run',filename1)
        if self.window().nproc<=1:
            command = '%s -case %s 1> %s 2> %s &'%(self.solvername,self.currentFolder,filename1,filename2)
        else:
            command = 'mpirun -np %s %s -case %s -parallel > %s & '%(str(self.window().nproc),self.solvername,self.currentFolder,filename1)
        os.system(command)
        
        command = 'pidof %s'%self.solvername
        import subprocess
        self.window().runningpid = subprocess.check_output(command, shell=True)
        self.window().runningpid.replace('\n','') #Me lo devuelve con un espacio al final
        self.window().runningpid = int(self.window().runningpid) #Y como string
        self.window().save_config()
        
        self.pushButton_run.setEnabled(False)
        self.pushButton_reset.setEnabled(False)
        self.window().findChild(logTab,'%s/run.log'%self.currentFolder).findChild(QtGui.QPushButton,'pushButton_3').setEnabled(True)
        self.window().updateLogFiles()
        
    def changeType(self):
        nprocOld = self.window().nproc
        if self.type_serial.isChecked():
            self.num_proc.setEnabled(False)
            if nprocOld==1:            
                self.pushButton_decompose.setText('Apply')
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/save16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            else:
                self.pushButton_decompose.setText('Apply and Reconstruct Case')
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/reconstruct16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.pushButton_decompose.setIcon(icon)
            self.pushButton_reconstruct.setEnabled(False)
            self.pushButton_decompose.setEnabled(True)
        else:
            self.num_proc.setEnabled(True)
            self.pushButton_decompose.setText('Apply and Decompose Case')
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/decompose16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.pushButton_decompose.setIcon(icon)
            self.pushButton_reconstruct.setEnabled(False)
            self.pushButton_decompose.setEnabled(True)

    def resetCase(self):
        w = reset()
        result = w.exec_()
        if result:
            command = 'pyFoamClearCase.py %s %s'%(w.getParams(), self.currentFolder)
            os.system(command)
            if w.deleteSnapshots():
                command = 'rm -rf %s/snapshots'%self.currentFolder                
                os.system(command)
            if w.resetFigures():
                self.window().resetFigures(w.deletePostpro(),w.deleteSnapshots())
            filename = '%s/system/controlDict'%self.currentFolder
            parsedData = ParsedParameterFile(filename,createZipped=False)
            parsedData['startFrom'] = 'startTime'            
            parsedData['startTime'] = '0'
            parsedData.writeFile()
            self.window().typeFile = {}
            self.window().pending_files = []
            self.window().pending_dirs = []
            self.window().updateLogFiles()
            
            self.type_serial.setChecked(True)
            self.type_parallel.setChecked(False)
            self.window().nproc = 1
            self.changeType()
                        
            self.window().save_config()


    def decomposeCase(self):
        nprocOld = self.window().nproc
        if self.type_serial.isChecked():
            if nprocOld>1:
                self.reconstructCase()
            self.window().nproc = 1                
        else:
            if nprocOld == self.num_proc.value():
                QtGui.QMessageBox.about(self, "ERROR", "Case already decomposed.")
                return            
            if nprocOld>1 and nprocOld != self.num_proc.value():
                QtGui.QMessageBox.about(self, "ERROR", "The case must be reconstructed before decompose with other number of processors.")
                return
            self.window().nproc = self.num_proc.value()
            
            #modifico el diccionario
            filename = '%s/system/decomposeParDict'%(self.currentFolder)
            parsedData = ParsedParameterFile(filename,createZipped=False)
            parsedData['numberOfSubdomains'] = self.window().nproc
            parsedData.writeFile()        
        
            #voy a descomponer solo los campos que estoy utilizando en el solver, el resto los dejo intactos
            command = 'mv %s %s.bak'%(self.timedir,self.timedir)
            os.system(command)
            
            command = 'mkdir %s'%(self.timedir)
            os.system(command)
            
            for ifield in self.fields:
                command = 'cp %s.bak/%s %s/.'%(self.timedir,ifield,self.timedir)
                os.system(command)
            
            filename = '%s/decompose.log'%self.currentFolder
            self.window().newLogTab('Decompose',filename)
            command = 'decomposePar -force -case %s -time %s > %s'%(self.currentFolder,self.currtime,filename)
            os.system(command)
    
            command = 'rm -r %s'%(self.timedir)
            os.system(command)
            
            command = 'mv %s.bak %s'%(self.timedir,self.timedir)
            os.system(command)
            
        self.window().save_config()            
        return
        
        
    def reconstructCase(self):

        if int(self.currtime)==0:
            QtGui.QMessageBox.about(self, "ERROR", "Time step 0 already exists")            
        else:
            filename = '%s/reconstruct.log'%self.currentFolder
            self.window().newLogTab('Reconstruct',filename)
            command = 'reconstructPar -case %s -time %s > %s'%(self.currentFolder,self.currtime,filename)
            os.system(command)
        return