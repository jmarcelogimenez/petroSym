# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
import os
import time
from time import localtime, strftime, struct_time

from utils import command_window

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

class logTab(QtGui.QWidget):
    
    def __init__(self, filename, currentFolder):
        self.currentFolder = currentFolder
        self.filename = filename
        QtGui.QWidget.__init__(self)
        self.setObjectName(filename)
        new_gridLayout = QtGui.QGridLayout(self)
        new_gridLayout.setObjectName(_fromUtf8("new_gridLayout"))
        new_pushButton = QtGui.QPushButton(self)
        new_pushButton.setText(_fromUtf8(""))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/fileSave16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        new_pushButton.setIcon(icon3)
        new_pushButton.setObjectName(_fromUtf8("pushButton"))
        new_gridLayout.addWidget(new_pushButton, 0, 1, 1, 1)
        new_textEdit = QtGui.QPlainTextEdit(self)
        palette = QtGui.QPalette()
        command_window(palette)
        new_textEdit.setPalette(palette)
        new_textEdit.setUndoRedoEnabled(False)
        new_textEdit.setReadOnly(True)
        new_textEdit.setObjectName(_fromUtf8("textEdit"))
        new_gridLayout.addWidget(new_textEdit, 1, 0, 1, 4)
        new_pushButton_2 = QtGui.QPushButton(self)
        new_pushButton_2.setText(_fromUtf8(""))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/browseFile16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        new_pushButton_2.setIcon(icon4)
        new_pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        new_gridLayout.addWidget(new_pushButton_2, 0, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        new_gridLayout.addItem(spacerItem2, 0, 3, 1, 1)
        new_pushButton_3 = QtGui.QPushButton(self)
        new_pushButton_3.setEnabled(False)
        new_pushButton_3.setText(_fromUtf8(""))
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/stop16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        new_pushButton_3.setIcon(icon5)
        new_pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        new_gridLayout.addWidget(new_pushButton_3, 0, 0, 1, 1)
        
        if 'run.log' in filename:
            new_pushButton_3.setEnabled(True)
            
        QtCore.QObject.connect(new_pushButton,QtCore.SIGNAL(_fromUtf8("pressed()")), self.saveLog)
        QtCore.QObject.connect(new_pushButton_2,QtCore.SIGNAL(_fromUtf8("pressed()")), self.openLog)
        QtCore.QObject.connect(new_pushButton_3,QtCore.SIGNAL(_fromUtf8("pressed()")), self.stopRun)
    
    def stopRun(self):
            
        filename = '%s/system/controlDict'%self.currentFolder
        parsedData = ParsedParameterFile(filename,createZipped=False)
        parsedData['stopAt'] = 'writeNow'
        parsedData.writeFile()
        time.sleep(0.1)
        
        self.findChild(QtGui.QPushButton,'pushButton_3').setEnabled(False)

#        while 1:
#            command = 'ps | cut -d " " -f 7 | grep Foam > %s/runningNow'%self.currentFolder
#            os.system(command)
#            f = open('%s/runningNow'%self.currentFolder, 'r')
#            if not f.read():
#                break
#            f.close()
#            time.sleep(0.1)
        
        import psutil
        import utils
        self.progress = QtGui.QProgressBar()
        self.progress.setWindowTitle("Saving the current data... Hold tight")        
        resolution = utils.get_screen_resolutions()
        self.progress.setGeometry(int(resolution[0])/2 - 175,int(resolution[1])/2,350,30)
        self.progress.show()

        i=0
        while psutil.pid_exists(self.window().runningpid):
            #retraso un minuto la edicion del control dict
            tt = list(localtime())
            tt[4] = (tt[4]+1)%60 #Agrego el modulo porque cuando el min es 0, 0-1 = -1
            command = 'touch -d "%s" %s'%(strftime("%Y-%m-%d %H:%M:%S", struct_time(tuple(tt))),filename)
            os.system(command)
            
            self.progress.setValue(i)
            QtGui.QApplication.processEvents()
            i=i+0.1
            time.sleep(0.1)

        self.progress.setValue(100)
        self.progress.close()
        if psutil.pid_exists(self.window().runningpid):
            command = 'kill %s'%self.window().runningpid
            os.system(command)

        self.window().runningpid = -1
        self.window().save_config()
        self.window().runW.pushButton_run.setEnabled(True)
        self.window().runW.pushButton_reset.setEnabled(True)
        self.window().tab_mesh.setEnabled(True)
        self.window().refresh_pushButton.setEnabled(True)
        leave = [1,5]
        for i in range(self.window().treeWidget.topLevelItemCount()):
            if i not in leave:
                self.window().treeWidget.topLevelItem(i).setDisabled(False)
        #self.window().updateLogFiles()
        
    def saveLog(self):
        outfile = QtGui.QFileDialog.getSaveFileName(self, 'Select filename', self.currentFolder, 'Log File (*.log)');
        if outfile:
            command = 'cp %s %s'%(self.filename,outfile)
            os.system(command)
        
    def openLog(self):
        command = 'gedit %s &'%self.filename
        os.system(command)