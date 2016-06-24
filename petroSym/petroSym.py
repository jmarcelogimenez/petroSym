from PyQt4 import QtGui, QtCore
from Tkinter import Tk

#cambiar a:
#from petroSym.petroSym_ui import petroSymUI
#from petroSym.popUpNew import *
#from petroSym.popUpNewFigure import *
#from petroSym.figureResiduals import *
#from petroSym.figureGeneralSnapshot import *
#from petroSym.figureSampledLine import *
#from petroSym.runTimeControls import *
#from petroSym.numericalSchemes import *
#from petroSym.solverSettings import *
#from petroSym.materials import *
#from petroSym.solutionModeling import *
#from petroSym.mesh import *
#from petroSym.run import *
#from petroSym.bc import *
#from petroSym.initialConditions import *
#from petroSym.postpro import *
#from petroSym.logTab import *
from petroSym_ui import petroSymUI
from popUpNew import *
from popUpNewFigure import *
from figureResiduals import *
from figureTracers import *
from figureGeneralSnapshot import *
from figureSampledLine import *
from runTimeControls import *
from numericalSchemes import *
from solverSettings import *
from materials import *
from solutionModeling import *
from mesh import *
from run import *
from bc import *
from initialConditions import *
from postpro import *
from logTab import *
from perpetualTimer import *
from loading_ui import *
from turbulence import *
from tracers import *
from gravity import *
from particleTracking import *
import os
from math import *
import time
import threading
import pickle

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

class petroSym(petroSymUI):
    def __init__(self):
        petroSymUI.__init__(self)

        self.currentFolder = '.'
        self.solvername = 'pimpleFoam'
        self.acceptturb = ['pimpleFoam','interFoam','simpleFoam']
        
        #self.thread_watcher = QtCore.QThread(self)
        #self.thread_watcher.start()
        
        #clase que chequea actualizaciones de directorios y archivos
        self.fs_watcher = QtCore.QFileSystemWatcher()
        self.fs_watcher.fileChanged.connect(self.file_changed2)
        self.fs_watcher.directoryChanged.connect(self.directory_changed2)
        
        #self.fs_watcher.moveToThread(self.thread_watcher)

        self.pending_files = []
        self.pending_dirs = []        
        self.runningpid = -1
        self.update_watcher()
        
        self.firstPlot = 1

        self.typeFile = {}
        self.lastPos = {}

        self.qscrollLayout = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.qscrollLayout.setGeometry(QtCore.QRect(0, 0, 500, 300))
        self.qfigWidgets = [];
        self.nPlots = 0
        self.typeFigure = ['Residuals', 'Tracers', 'Probes', 'Sampled Line', 'General Snapshot']
        self.colors = ['r', 'b', 'k', 'g', 'y', 'c']

        self.addNewFigureButton()
        
        QtCore.QObject.connect(self.qfigWidgets[self.nPlots], QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.addNewFigure)

        self.scrollAreaWidgetContents.setLayout(self.qscrollLayout)

        QtCore.QObject.connect(self.tabWidget_2, QtCore.SIGNAL("tabCloseRequested(int)"), self.closeLogTab)

        self.meshW = meshWidget()
        self.meshW.setParent(self)
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.tab_mesh)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.horizontalLayout_3.addWidget(self.meshW)
        
        self.runW = runWidget(self.currentFolder, self.solvername)
        self.runW.setParent(self)
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.tab_run)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.horizontalLayout_4.addWidget(self.runW)
        
        self.postproW = postproWidget(self.currentFolder)
        self.postproW.setParent(self)
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.tab_postpro)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.horizontalLayout_5.addWidget(self.postproW)
        
        #apago todas las opciones hasta que se abra algun caso
        self.OnOff(False)
        
        self.activeTimer = QtCore.QTimer(self)
        self.activeTimer.setInterval(0.2*1000);
        #activeTimer->setSingleShot(true);
        self.connect(self.activeTimer, QtCore.SIGNAL("timeout()"), self.update_watcher);
        self.activeTimer.start()

    def updateMeshPanel(self):
        QtGui.QMessageBox.about(self, "ERROR", "Primero se debe calcular!")
        
    def loadingmbox(self,title,msg):
        self.w = QtGui.QMessageBox(QtGui.QMessageBox.Information,title,msg)
        time.sleep(1)
        QtGui.QApplication.processEvents()
        self.w.show()
        time.sleep(1)
        QtGui.QApplication.processEvents()

    def openCase(self):
        QFileDialog=QtGui.QFileDialog()
        posibleDir = str(QFileDialog.getExistingDirectory(self, 'Open Folder', './',  QtGui.QFileDialog.DontUseNativeDialog | QtGui.QFileDialog.ShowDirsOnly))
        
        if posibleDir:
            if os.path.isdir('%s/system'%posibleDir) and os.path.isdir('%s/constant'%posibleDir):
                #--Ventana de loading
                self.loadingmbox("Opening","Loading the selected case...")
                #--Loading
                self.currentFolder = posibleDir
                QtGui.QApplication.processEvents()
                self.load_config()
                self.OnOff(True)
            else:
                w = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Error", "The selected directory is not an OpenFOAM case")
                w.exec_()
            
            self.w.close()


    def saveAsCase(self):
        oldFolder = self.currentFolder
        self.currentFolder = str(QtGui.QFileDialog.getExistingDirectory(self, 'Save As...', './'))
        
        w = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Save As", "Do you want to keep the running folders? (If not, only the folders 0, system and constant will copy)", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
        ret = w.exec_()
        import subprocess
        if(QtGui.QMessageBox.Yes == ret):
            command = 'cp -r %s/. %s' % (oldFolder,self.currentFolder)
            subprocess.check_call(command,shell=True)
        else:
            command = 'pyFoamCloneCase.py %s %s' % (oldFolder,self.currentFolder)
            subprocess.check_call(command,shell=True)
            oldCase = oldFolder.split('/')
            oldCase = oldCase[len(oldCase)-1]
            command = 'mv %s/%s/* %s/.' % (self.currentFolder,oldCase,self.currentFolder)
            subprocess.check_call(command,shell=True)
            command = 'rm -r %s/%s' % (self.currentFolder,oldCase)
            subprocess.check_call(command,shell=True)
        
        self.save_config()

    def newCase(self):
        if not os.getenv('FOAM_TUTORIALS'):
            QtGui.QMessageBox(QtGui.QMessageBox.Critical, "Error", "OpenFOAM environment variables are not set. Closing").exec_()
            return ''

        w = popUpNew()
        result = w.exec_()

        if result:
            data = w.getData()
            self.currentFolder = os.path.join(data[1],data[0])
            if os.path.isdir('%s/system'%self.currentFolder) and os.path.isdir('%s/constant'%self.currentFolder):
                self.loadingmbox("Opening","Opening selected case...")
                QtGui.QApplication.processEvents()
                self.load_config()
            else:
                self.loadingmbox("Creating","Creating selected case...")
                #Levantar dependiendo del caso predefinido elegido
                #typeSim = data[2]
                typeSim = 'Skimmer Tank'
                if typeSim == 'Skimmer Tank':
                    command = 'cp -r %s/templates/template_pimpleFoam/* %s/.' % (os.path.dirname(os.path.realpath(__file__)),self.currentFolder)
                    os.system(command)
                    self.solvername = 'pimpleFoam'
                elif typeSim =='Generic':
                    #command = 'cp -r %s/templates/template_icoFoam/* %s/.' % (os.path.dirname(__file__),self.currentFolder)
                    command = 'cp -r %s/templates/template_icoFoam/* %s/.' % (os.path.dirname(os.path.realpath(__file__)),self.currentFolder)
                    os.system(command)
                    self.solvername = 'icoFoam'
                #para que pueda sacar algunos datos
                self.meshW.setCurrentFolder(self.currentFolder)
                QtGui.QApplication.processEvents()
                self.meshW.createMesh()

            self.OnOff(True)
            self.meshW.setCurrentFolder(self.currentFolder)
            self.runW.setCurrentFolder(self.currentFolder,self.solvername)
            self.postproW.setCurrentFolder(self.currentFolder)
        
        self.w.close()
        return result

    def saveCase(self):
        if self.currentFolder=='.':
            self.currentFolder = str(QtGui.QFileDialog.getExistingDirectory(self, 'Save As...', './'))
        print('Se guarda como %s',self.currentFolder)
        self.save_config()

    def openTerminal(self):
        os.system('gnome-terminal --working-directory=%s &'%self.currentFolder)
        #os.system('$TERM . &')

    def openBrowse(self):
        os.system('nautilus %s &'%self.currentFolder)

    def openParaview(self):
        os.system('paraFoam -builtin -case %s &'%self.currentFolder)
        
    def closeEvent(self, evnt):
        #self.timer.cancel()
        if self.currentFolder == '.':
            evnt.accept()
        else:
            quit_msg = "Do you want to save and close the program?"
            reply = QtGui.QMessageBox.question(self, 'Message', quit_msg, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Discard, QtGui.QMessageBox.Cancel)
        
            if reply == QtGui.QMessageBox.Ok:
                self.save_config()
                evnt.accept()
            elif reply == QtGui.QMessageBox.Discard:
                evnt.accept()
            else:
                evnt.ignore()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    
    def runCase(self):
        self.runW.runCase()

    def addNewFigure(self, index):
        if index<2:
            return
        index = index - 2
        addFigure = False
        
        print self.typeFigure[index]
        if self.typeFigure[index] == 'Residuals':
            w = figureResiduals(self.currentFolder)
            result = w.exec_()
            filename = ''
            if result:
                data = w.getData()
                [bas1,bas2,currtime] = currentFields(self.currentFolder)
                addFigure = True
                filename = '%s/postProcessing/%s/%s/residuals.dat'%(self.currentFolder,str(data['name']),currtime)
                if(os.path.isfile(filename)):
                    w = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Caution", "The output file already exists, do yo want to remove it? (If not, you must choose another log name)", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
                    ret = w.exec_()
                    if(QtGui.QMessageBox.Yes == ret):
                        command = 'rm %s/%s'%(self.currentFolder,filename)
                        os.system(command)
                    else:
                        addFigure = False
            if addFigure:
                ww = figureResidualsWidget(self.scrollAreaWidgetContents, data['name'])
                self.pending_files.append(filename)

        if self.typeFigure[index] == 'Tracers':
            w = figureTracers(self.currentFolder)        
            result = w.exec_()
            filename = ''
            
            if result:
                [bas1,bas2,currtime] = currentFields(self.currentFolder)
                
                data = w.getData()
                addFigure = True
                filename = '%s/postProcessing/%s/%s/faceSource.dat'%(self.currentFolder,str(data['name']),currtime)
                if(os.path.isfile(filename)):
                    w = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Caution", "The output file already exists, do yo want to remove it? (If not, you must choose another log name)", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
                    ret = w.exec_()
                    if(QtGui.QMessageBox.Yes == ret):
                        command = 'rm %s'%filename
                        os.system(command)
                    else:
                        addFigure = False
            if addFigure:
                ww = figureTracersWidget(self.scrollAreaWidgetContents, data['name'])
                self.pending_files.append(filename)

        if self.typeFigure[index] == 'Sampled Line':
            w = figureSampledLine(self.currentFolder)
            result = w.exec_()
            if result:
                data = w.getData()
                #print data
                dirname = 'postProcessing/%s'%data['name']
                addFigure = True
                if(os.path.isdir('%s/%s'%(self.currentFolder,dirname))):
                    w = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Caution", "The output directory '%s' already exists, do yo want to remove it?"%'%s/%s'%(self.currentFolder,dirname), QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
                    ret = w.exec_()
                    if(QtGui.QMessageBox.Yes == ret):
                        command = 'rm -r %s/%s'%(self.currentFolder,dirname)
                        os.system(command)
                    else:
                        addFigure = False                
                if data['autorefreshing']=='Yes' and addFigure:
                    self.pending_dirs.append(dirname)
            
            if addFigure:
                ww = figureSampledLineWidget(self.scrollAreaWidgetContents, data['name'])
                        
        if self.typeFigure[index] == 'General Snapshot':
            fileName = QtGui.QFileDialog.getOpenFileName(self, 'Select Paraview State', self.currentFolder, 'Paraview state (*.pvsm)');
            newdir = ''
            data_name = ''
            if fileName:
                data_name = os.path.basename(fileName)
                data_name = data_name[:-5]
                newdir = '%s/snapshots/%s'%(self.currentFolder,data_name)
                addFigure = True
                if os.path.isdir('%s'%newdir):
                    w = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Caution", "The output directory '%s' already exists, do yo want to remove it?"%(newdir), QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
                    ret = w.exec_()
                    if(QtGui.QMessageBox.Yes == ret):
                        command = 'rm -r %s'%newdir
                        os.system(command)
                    else:
                        addFigure = False
            if addFigure:
                ww = figureGeneralSnapshotWidget(self.scrollAreaWidgetContents)     
                command = 'mkdir -p %s'%(newdir)
                os.system(command)
                #hago una copia del pvsm para tenerlo siempre accesible
                command = 'cp %s %s/%s.pvsm'%(fileName,self.currentFolder,data_name)
                os.system(command)
            else:
                print 'Nothing Selected'

        if addFigure:
            i = self.nPlots
            self.qfigWidgets.insert(i, ww)

            #agrego el nuevo plot
            self.qscrollLayout.addWidget(self.qfigWidgets[i],i/2,i%2)
            #vuelvo a ubicar el boton
            self.qscrollLayout.addWidget(self.qfigWidgets[i+1],(i+1)/2,(i+1)%2)
            self.nPlots = self.nPlots+1
            self.qfigWidgets[i].setObjectName(data['name'])
            
            #Guardo la configuracion si agrego una figura, acordarse de sacarla
            #si la elimino
            self.save_config()

        self.qfigWidgets[self.nPlots].setCurrentIndex(0)
        return
        
    
    def resetFiguresTimes(self):
        for i in range(self.nPlots):
            self.qfigWidgets[i].lastPos = -1
        return
        
    def resetFigures(self,postpro=False,snapshots=False):
        #print 'Reset figures'
        [bas1,bas2,currtime] = currentFields(self.currentFolder)
        for i in range(self.nPlots):
            if isinstance(self.qfigWidgets[i],figureResidualsWidget) and postpro:
                self.qfigWidgets[i].resetFigure()
                filename = 'postProcessing/%s/%s/residuals.dat'%(self.qfigWidgets[i].objectName(),currtime)
                self.pending_files.append(filename)
            elif isinstance(self.qfigWidgets[i],figureTracersWidget) and postpro:
                self.qfigWidgets[i].resetFigure()
                filename = 'postProcessing/%s/%s/faceSource.dat'%(self.qfigWidgets[i].objectName(),currtime)
                self.pending_files.append(filename)
            elif isinstance(self.qfigWidgets[i],figureSampledLineWidget) and postpro:  
                self.qfigWidgets[i].resetFigure()
                dirname = 'postProcessing/%s'%self.qfigWidgets[i].objectName()
                #Solo agregar si se eligio autorefreshing             
                self.pending_dirs.append(dirname)  
            elif isinstance(self.qfigWidgets[i],figureGeneralSnapshotWidget) and snapshots:  
                self.qfigWidgets[i].resetFigure()
            else:
                None

    def newLogTab(self,name,filename):

        new_tab = logTab(filename,self.currentFolder)

        already = False
        if  self.lastPos.has_key(filename):
            for i in range(self.tabWidget_2.count()):
                if self.tabWidget_2.widget(i).objectName()==filename:
                    self.findChild(QtGui.QWidget,filename).findChild(QtGui.QPlainTextEdit,_fromUtf8("textEdit")).clear()
                    already = True
                    break

        if not already:
            self.tabWidget_2.addTab(new_tab, name)
            self.tabWidget_2.widget(self.tabWidget_2.count()-1).setObjectName(filename)
        
        if not os.path.isfile(filename):
            command = 'touch %s'%filename
            os.system(command)
        
        if filename not in self.fs_watcher.files():
            self.fs_watcher.addPath(filename)
            
        if filename not in self.pending_files: #Si se crea y no esta, se agrega a las pendientes de revision
            self.pending_files.append(filename)
        
        self.lastPos[filename] = 0
        self.typeFile[filename] = 'log'


    def closeLogTab(self,i):
#        print "Cerrando tabla de log"
        
        filename = self.tabWidget_2.widget(i).objectName()
        
        if 'run' in filename and self.runningpid != -1:
            w = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Error", "You can't close the run tab while a case is running", QtGui.QMessageBox.Ok)
            w.exec_()
            return
        
        if (str(filename) in self.lastPos.keys()):
            del self.lastPos[str(filename)]
        if (str(filename) in self.typeFile.keys()):
            del self.typeFile[str(filename)]
            
        self.fs_watcher.removePath(str(filename))
        #command = 'rm %s'%filename
        #os.system(command)
        self.tabWidget_2.removeTab(i)
        toModify = self.findChild(QtGui.QWidget,filename)        
        textEdit = toModify.findChild(QtGui.QPlainTextEdit,_fromUtf8("textEdit"))
        textEdit.clear()
        toModify.deleteLater()
        self.save_config()
        
    def file_changed2(self,path):
        path = str(path)
        if os.path.isfile(path):
            self.fs_watcher.removePath(path)
        if path not in self.pending_files:
            self.pending_files.append(path)
        if os.path.isfile(path):
            self.fs_watcher.addPath(path)
        
    def directory_changed2(self,path):
        path = str(path)
        if os.path.isdir(path):
            self.fs_watcher.removePath(path)
        if path not in self.pending_dirs:
            self.pending_dirs.append(path)
        if os.path.isdir(path):
            self.fs_watcher.addPath(path)
        

    def file_changed(self,path):
#        print "En file changed"
        path = str(path)
        self.fs_watcher.removePath(path)
        
        if self.typeFile[path]=='log':
            toModify = self.findChild(QtGui.QWidget,path)
            textEdit = toModify.findChild(QtGui.QPlainTextEdit,_fromUtf8("textEdit"))
            
            N = self.lastPos[path]
            with open(path, 'r') as yourFile:
                yourFile.seek(N)
                newTexto = yourFile.read()
            if(len(newTexto)>1):                
                #textEdit.insertPlainText(newTexto) #Este no mueve el cursor
                textEdit.appendPlainText(newTexto)  #Este si
                QtGui.QApplication.processEvents()
                self.lastPos[path] = N + len(newTexto)
                
        if self.typeFile[path]=='plot':
            key = ''
            for qfw in self.qfigWidgets:
                ikey = qfw.objectName()
                if 'postProcessing/%s'%ikey in path:
                    key = ikey
                    break

            if key == '':
                self.fs_watcher.addPath(path)
                return

            if 'residuals.dat' in path:
                frWidget = self.findChild(figureResidualsWidget,key)
                frWidget.plot(path)

            if 'faceSource.dat' in path:
                ftWidget = self.findChild(figureTracersWidget,key)
                ftWidget.plot(path)
                
        self.fs_watcher.addPath(path)

    def directory_changed(self,path):
        self.fs_watcher.removePath(path)
        if not os.path.exists(path):
            return
        #busco a cual se corresponde
        keys = []

        if 'postProcessing' in path:
            for qfw in self.qfigWidgets:
                key = qfw.objectName()
                if 'postProcessing/%s'%key in path:
                    keys.append(key)
                    break
        else:
            for qfw in self.qfigWidgets:
                key = qfw.objectName()
                if 'snapshots/%s'%key in path:
                    keys.append(key)
                    break

        if keys==[]:
            self.fs_watcher.addPath(path)
            return


        for ii in keys:
            figW = self.findChild(QtGui.QWidget,ii)
            newdirs = list(set(os.listdir(path))-set(figW.dirList))
            newdirs.sort(key=lambda x: os.stat(os.path.join(path, x)).st_mtime)
            if figW:
                figW.dirList.extend(newdirs)
                figW.lastPos = len(figW.dirList)-1
                if figW.lastPos>0:
                    figW.plot()

        self.fs_watcher.addPath(path)


    def update_watcher(self):
#        print "Actualizando el watcher"
        i = 0
        while i<len(self.pending_files):
            filename = self.pending_files[i]
            #print 'file: '+filename
            
            if os.path.isfile(filename):
                #print 'Se agrega %s'%filename
                    
                #self.fs_watcher.addPath(filename)
                self.pending_files.pop(i)
                #una vez que se cual es la grafica
                if 'log' in filename:                
                    self.typeFile[filename] = 'log'
                else:
                    self.typeFile[filename] = 'plot'

                self.file_changed(filename)
            else:
                i = i+1
        i = 0
        while i<len(self.pending_dirs):
            dirname = self.pending_dirs[i]
#            print 'dir: '+dirname
            if os.path.isdir(dirname):
#                print 'Agrego %s'%dirname
                self.fs_watcher.addPath(dirname)
                self.pending_dirs.pop(i)
                #una vez que se cual es la grafica
                self.directory_changed(dirname)
            else:
                i = i+1

        #Chequear si la corrida termino (Si esta corriendo algo)
        import psutil
        if self.runningpid != -1 and not(psutil.pid_exists(self.runningpid)):
            tab=self.findChild(logTab,'%s/run.log'%self.currentFolder)
            if tab:
                tab.stopRun()
            else:
                #Si exploto el caso y me quedo corriendo
                self.runningpid = -1
                self.save_config()
                self.window().runW.pushButton_run.setEnabled(True)
                self.window().runW.pushButton_reset.setEnabled(True)

    def save_config(self):
        filename = '%s/petroSym.config'%self.currentFolder
        config = {}
        #aca hay que cargar todas las selecciones de combobox,etc
        config['nPlots'] = self.nPlots
        
        #estos 5 deberian volar
        config['typeFile'] =  self.typeFile
        config['lastPos'] = str(self.lastPos)
        config['solver'] = str(self.solvername)

        config['namePlots'] = []
        config['typePlots'] = []
        for i in range(self.nPlots):
            config['namePlots'].append(str(self.qfigWidgets[i].objectName()))
            if isinstance(self.qfigWidgets[i],figureResidualsWidget):  
                config['typePlots'].append('Residuals')
            if isinstance(self.qfigWidgets[i],figureTracersWidget):  
                config['typePlots'].append('Tracers')
            elif isinstance(self.qfigWidgets[i],figureSampledLineWidget):  
                config['typePlots'].append('Sampled Line')
            elif isinstance(self.qfigWidgets[i],figureGeneralSnapshotWidget):  
                config['typePlots'].append('General Snapshot')
            else:
                config['typePlots'].append(' ')
        
        config['runningpid'] = self.runningpid

        output = open(filename, 'wb')
        pickle.dump(config, output)
        output.close()


    def load_config(self):
        filename = '%s/petroSym.config'%self.currentFolder
        
        if os.path.isfile(filename):
            pkl_file = open(filename, 'rb')
            config = pickle.load(pkl_file)
            pkl_file.close()
            #preguntar si existe cada campo!!!!!
            wrongFile = 0
            wrongFile = 1 if 'nPlots' not in config.keys() else wrongFile
            wrongFile = 1 if 'namePlots' not in config.keys() else wrongFile
            wrongFile = 1 if 'typePlots' not in config.keys() else wrongFile
            wrongFile = 1 if 'typeFile' not in config.keys() else wrongFile
            wrongFile = 1 if 'runningpid' not in config.keys() else wrongFile
                        
            if wrongFile:
                QtGui.QMessageBox.about(self, "ERROR", "Corrupted File")
                return
            
            for i in range(self.nPlots):
                self.removeFigure(self.qfigWidgets[self.nPlots-i])
            
            self.fs_watcher.removePaths(self.fs_watcher.files())
            self.fs_watcher.removePaths(self.fs_watcher.directories())
            self.pending_files = []
            self.pending_dirs = []
            
            self.nPlots = config['nPlots']
            namePlots = config['namePlots']
            typePlots = config['typePlots']
            self.typeFile = config['typeFile']
            self.solvername = config['solver']
            self.runningpid = config['runningpid']
            
            #Ver si hay algun proceso corriendo que ejecute con la gui 
            #cuando la abro nuevamente
            import psutil
            if self.runningpid != -1 and psutil.pid_exists(self.runningpid):
                filename = '%s/run.log'%self.currentFolder
                self.window().newLogTab('Run',filename)
                self.pending_files.append(filename)
            
            [bas1,bas2,currtime] = currentFields(self.currentFolder)
            for i in range(self.nPlots):
                if typePlots[i]=='Residuals':
                    ww = figureResidualsWidget(self.scrollAreaWidgetContents,namePlots[i])
                    filename = '%s/postProcessing/%s/%s/residuals.dat'%(self.currentFolder,namePlots[i],currtime)
                    ww.lastPos = -1
                    self.pending_files.append(filename)
                    
                    filename2 = '%s/postProcessing/%s'%(self.currentFolder,namePlots[i])
                    if os.path.isdir(filename2):    
                        latest = -1
                        listdirs = os.listdir(filename2)
                        listdirsfloat = []
                        for ikey in listdirs:
                            listdirsfloat.append(float(ikey))
                        listdirsfloat.sort()
                        
                        for j in range(len(listdirsfloat)-1):
                            filename2 = '%s/postProcessing/%s'%(self.currentFolder,namePlots[i])
                            if listdirsfloat[j].is_integer():
                                filename2 += '/%s/residuals.dat'%str(int(listdirsfloat[j]))
                            else:
                                filename2 += '/%s/residuals.dat'%str(listdirsfloat[j])
                            ww.plot(filename2)
                            ww.lastPos = -1
                        
                        if listdirsfloat[len(listdirsfloat)-1].is_integer():
                            latest = int(listdirsfloat[len(listdirsfloat)-1])
                        else:
                            latest = listdirsfloat[len(listdirsfloat)-1]
                        filename2 = '%s/postProcessing/%s/%s/residuals.dat'%(self.currentFolder,namePlots[i],str(latest))
                        self.pending_files.append(filename2)
                    
                elif typePlots[i]=='Sampled Line':
                    ww = figureSampledLineWidget(self.scrollAreaWidgetContents,namePlots[i])      
                    dirname = 'postProcessing/%s'%namePlots[i]
                    #Solo agregar si se eligio autorefreshing
                    self.pending_dirs.append(dirname)
                elif typePlots[i]=='General Snapshot':
                    ww = figureGeneralSnapshotWidget(self.scrollAreaWidgetContents)
                elif typePlots[i]=='Tracers':
                    ww = figureTracersWidget(self.scrollAreaWidgetContents,namePlots[i])
                    filename = '%s/postProcessing/%s/%s/faceSource.dat'%(self.currentFolder,namePlots[i],currtime)
                    self.pending_files.append(filename)
                    
                    filename2 = '%s/postProcessing/%s'%(self.currentFolder,namePlots[i])
                    if os.path.isdir(filename2):    
                        latest = -1
                        listdirs = os.listdir(filename2)
                        listdirsfloat = []
                        for ikey in listdirs:
                            listdirsfloat.append(float(ikey))
                        listdirsfloat.sort()
                        
                        for j in range(len(listdirsfloat)-1):
                            filename2 = '%s/postProcessing/%s'%(self.currentFolder,namePlots[i])
                            if listdirsfloat[j].is_integer():
                                filename2 += '/%s/faceSource.dat'%str(int(listdirsfloat[j]))
                            else:
                                filename2 += '/%s/faceSource.dat'%str(listdirsfloat[j])
                            ww.lastPos = -1
                            ww.plot(filename2)
                        
                        if listdirsfloat[len(listdirsfloat)-1].is_integer():
                            latest = int(listdirsfloat[len(listdirsfloat)-1])
                        else:
                            latest = listdirsfloat[len(listdirsfloat)-1]
                        filename2 = '%s/postProcessing/%s/%s/faceSource.dat'%(self.currentFolder,namePlots[i],str(latest))
                        ww.lastPos = -1
                        self.pending_files.append(filename2)
                
                ww.setObjectName(namePlots[i])
                self.qfigWidgets.insert(i,ww)
                self.qfigWidgets[i].setObjectName(namePlots[i])
                self.qscrollLayout.addWidget(self.qfigWidgets[i],i/2,i%2)
            self.qscrollLayout.addWidget(self.qfigWidgets[self.nPlots],self.nPlots/2,self.nPlots%2)
                
        self.meshW.setCurrentFolder(self.currentFolder)
        self.runW.setCurrentFolder(self.currentFolder,self.solvername)
        filename = '%s/constant/polyMesh/points'%self.currentFolder
        if not os.path.isfile(filename):
            self.meshW.createMesh()
        self.postproW.setCurrentFolder(self.currentFolder)
        self.meshW.loadMeshData()
        
    def removeFilesPostPro(self):
        [bas1,bas2,currtime] = currentFields(self.currentFolder)
        for i in range(self.nPlots):
            namePlot = str(self.qfigWidgets[i].objectName())
            if isinstance(self.qfigWidgets[i],figureResidualsWidget):  
                filename = '%s/postProcessing/%s/%s/residuals.dat'%(self.currentFolder,namePlot,currtime)
                if os.path.isfile(filename):
                    command = 'rm %s'%filename
                    os.system(command)
                
                if (len(self.qfigWidgets[i].dataPlot)>0 and self.qfigWidgets[i].dataPlot[len(self.qfigWidgets[i].dataPlot)-1][0] > float(currtime)):
                    self.qfigWidgets[i].resetFigure()
                else:
                    self.qfigWidgets[i].lastPos = -1

            if isinstance(self.qfigWidgets[i],figureTracersWidget):  
                filename = '%s/postProcessing/%s/%s/faceSource.dat'%(self.currentFolder,namePlot,currtime)
                
                if os.path.isfile(filename):                
                    command = 'rm %s'%filename
                    os.system(command)
                
                if len(self.qfigWidgets[i].dataPlot)>0:
                    print 'lastpos: '+str(self.qfigWidgets[i].dataPlot[len(self.qfigWidgets[i].dataPlot)-1][0])
                print 'currtime: '+str(currtime)
                print 'len: '+str(len(self.qfigWidgets[i].dataPlot))
                if (len(self.qfigWidgets[i].dataPlot)>0 and self.qfigWidgets[i].dataPlot[len(self.qfigWidgets[i].dataPlot)-1][0] > float(currtime)):
                    self.qfigWidgets[i].resetFigure()
                else:
                    self.qfigWidgets[i].lastPos = -1
        return
    
    def updateLogFiles(self):
        #print 'Updating log Files'
        [bas1,bas2,currtime] = currentFields(self.currentFolder)
        #spf = set(self.pending_files)
        for i in range(self.nPlots):
            namePlot = str(self.qfigWidgets[i].objectName())
            filename = ''
            if isinstance(self.qfigWidgets[i],figureResidualsWidget):  
                filename = '%s/postProcessing/%s/%s/residuals.dat'%(self.currentFolder,namePlot,currtime)
                self.pending_files.append(filename)
            if isinstance(self.qfigWidgets[i],figureTracersWidget):  
                filename = '%s/postProcessing/%s/%s/faceSource.dat'%(self.currentFolder,namePlot,currtime)
                self.pending_files.append(filename)
            
            if os.path.isfile(filename):
                if filename not in self.fs_watcher.files():
                    self.fs_watcher.addPath(filename)
            
            #spf.add(filename)
        #self.pending_files = list(spf)
        
    def resetCase(self, solvername):
        #print 'ResetCase'
        self.solvername = solvername
        self.pending_files = []
        self.pending_dirs = []
        self.fs_watcher.removePaths(self.fs_watcher.files())
        self.fs_watcher.removePaths(self.fs_watcher.directories())
        
        if solvername == 'pimpleFoam':
            command = 'rm -rf %s/*' % self.currentFolder
            os.system(command)
            command = 'cp -r %s/templates/template_pimpleFoam/* %s/.' % (os.path.dirname(os.path.realpath(__file__)),self.currentFolder)
            os.system(command)            
        elif solvername =='icoFoam':
            command = 'rm -rf %s/*' % self.currentFolder
            os.system(command)
            command = 'cp -r %s/templates/template_icoFoam/* %s/.' % (os.path.dirname(os.path.realpath(__file__)),self.currentFolder)
            os.system(command)
            
        for i in range(self.nPlots):
            self.qscrollLayout.removeWidget(self.qfigWidgets[0])
            self.qfigWidgets[0].deleteLater()
            for i in xrange(1,self.nPlots+1): #voy hasta +1 porque tengo el boton
                self.qfigWidgets[i-1] = self.qfigWidgets[i]
                self.qscrollLayout.addWidget(self.qfigWidgets[i-1],(i-1)/2,(i-1)%2)
        
        self.meshW.createMesh()
        self.nPlots = 0
        
        self.meshW.setCurrentFolder(self.currentFolder)
        self.runW.setCurrentFolder(self.currentFolder,self.solvername)
        self.postproW.setCurrentFolder(self.currentFolder)
    
        return

    def removeFigure(self, figW):
        removeItem = 0
        for i in xrange(self.nPlots):
            if figW==self.qfigWidgets[i]:
                removeItem = i
                break
            
        if isinstance(self.qfigWidgets[i],figureResidualsWidget):  
                figuretype = 'residuals.dat'
        if isinstance(self.qfigWidgets[i],figureTracersWidget):  
                figuretype = 'faceSource.dat'

        self.qscrollLayout.removeWidget(self.qfigWidgets[removeItem])
        self.qfigWidgets[removeItem].deleteLater()
        for i in xrange(removeItem+1,self.nPlots+1): #voy hasta +1 porque tengo el boton
            self.qfigWidgets[i-1] = self.qfigWidgets[i]
            self.qscrollLayout.addWidget(self.qfigWidgets[i-1],(i-1)/2,(i-1)%2)
        self.nPlots = self.nPlots-1
        
        #Elimino la figura del controlDict
        filename = '%s/system/controlDict'%(self.currentFolder)
        parsedData = ParsedParameterFile(filename,createZipped=False)
        if 'functions' in parsedData.getValueDict().keys():
            if figW.objectName() in parsedData['functions'].keys():
                del parsedData['functions'][figW.objectName()]                
        parsedData.writeFile()
        
        #La elimino del .config
        self.save_config()
        
        #La elimino de pending files (Ver los dos que faltan)
        [bas1,bas2,currtime] = currentFields(self.currentFolder)
        filename = '%s/postProcessing/%s/%s/%s'%(self.currentFolder,figW.objectName(),currtime,figuretype)
        
        if filename in self.pending_files:
            self.pending_files.remove(filename)

    def temporalFigure_update(self,figW,action):
        print 'hacer %s en %s'%(action,figW.objectName())
        if figW.lastPos==-1 and action != 'refresh':
            return
        if action == 'first':
            figW.lastPos = 0
            figW.plot()
        elif action == 'previous':
            if figW.lastPos>0:
                figW.lastPos = figW.lastPos - 1
                figW.plot()
        elif action == 'next':
            if figW.lastPos<len(figW.dirList)-1:
                figW.lastPos = figW.lastPos + 1
                figW.plot()
        elif action == 'last':
            figW.lastPos = len(figW.dirList) - 1
            figW.plot()
        elif action == 'play':
            figW.lastPos = 0
            button = figW.findChild(temporalNavigationToolbar)._actions['play']
            while figW.lastPos<=len(figW.dirList)-1 and button.isChecked():
                figW.plot()
                figW.lastPos = figW.lastPos + 1
                QtGui.QApplication.processEvents()
                if isinstance(figW,figureGeneralSnapshotWidget):
                    time.sleep(0.1)

            if figW.lastPos==len(figW.dirList):
                figW.lastPos = figW.lastPos - 1
                button.setChecked(False)
        elif action == 'refresh':
            ii = figW.objectName()
            if isinstance(figW,figureSampledLineWidget):
                path = '%s/postProcessing/%s'%(self.currentFolder,ii)
            elif isinstance(figW,figureGeneralSnapshotWidget):
                path = '%s/snapshots/%s'%(self.currentFolder,ii)

            newdirs = list(set(os.listdir(path))-set(figW.dirList))
            newdirs.sort(key=lambda x: os.stat(os.path.join(path, x)).st_mtime)
            figW.dirList.extend(newdirs)
            figW.lastPos = len(figW.dirList) - 1

            if figW.lastPos>0:
                figW.plot()

    def doPlot(self,figW):
        ii = figW.objectName()
        print 'por hace plot de %s type: %s'%(ii,self.dirType[ii])
       
        if isinstance(figW,figureSampledLineWidget):
                       
            figW.plot()

        if  self.dirType[ii]=='General Snapshot':
            desired = '%s/snapshots/%s/%s/%s.png'%(self.currentFolder,ii,self.dirList[ii][self.lastPos[ii]],ii)
            print desired
            if os.path.isfile(desired)==False:
                command = 'pvpython /usr/local/bin/pyFoamPVSnapshot.py --time=%s --state-file=%s/%s.pvsm  --file-prefix="snapshot" --no-casename --no-timename %s'%(self.dirList[ii][self.lastPos[ii]],self.currentFolder,ii,self.currentFolder)
                os.system(command)
                while os.path.isfile('snapshot_00000.png')==False:
                    None
                command = 'mv snapshot_00000.png %s/snapshots/%s/%s/%s.png'%(self.currentFolder,ii,self.dirList[ii][self.lastPos[ii]],ii)
                os.system(command)
            mainImage = figW.findChild(QtGui.QLabel,'mainImage')
            mainImage.setPixmap(QtGui.QPixmap(_fromUtf8(desired)))

            timeLegend = figW.findChild(QtGui.QLineEdit)
            timeLegend.setText(self.dirList[ii][self.lastPos[ii]])


    def updateCaseSetup(self,QTreeWidgetItem):

        if not QTreeWidgetItem:
            return
            
        if self.solvername in self.acceptturb:
            self.treeWidget.topLevelItem(0).child(0).setDisabled(False)
        else:
            self.treeWidget.topLevelItem(0).child(0).setDisabled(True)
            
        menu = QTreeWidgetItem.text(0)
        #print menu
        if menu=='Solution Modeling':
            #para el solution modeling no tengo un diccionario
            widget = solutionModeling(self.currentFolder,self.solvername)
        elif menu=='Turbulence':
            widget = turbulence(self.currentFolder,self.solvername)
        elif menu=='Gravity':
            widget = gravity(self.currentFolder,self.solvername)
            widget.setDisabled(True) #Gravity desactivada por el momento
        elif menu=='Run Time Controls':
            widget = runTimeControls(self.currentFolder)
        elif 'phase' in menu:
            #alguna de las fases (valido solo hasta 9 phases)        
            widget = materials(self.currentFolder,int(menu[-1])-1)
        elif menu=='Boundary Conditions':
            widget = bcWidget(self.currentFolder)
        elif menu=='Initial Conditions':
            widget = initialConditionsWidget(self.currentFolder)
        elif menu=='Numerical Schemes':
            widget = numericalSchemes(self.currentFolder)
        elif menu=='Solver Settings':
            widget = solverSettings(self.currentFolder,self.solvername)
        elif menu=='Tracers':
            widget = tracers(self.currentFolder)
        elif menu=='Particle Tracking':
            widget = particleTracking(self.currentFolder)
            #result = w.exec_()
            #if result:
            #    w.saveCaseData(True)
            #return
        else:
            #do nothing
            return           
        
        self.splitter_3.widget(1).deleteLater()
        self.splitter_3.insertWidget(1,widget)
        #scrollArea_case_setup.layout().addWidget(widget, 0, 1, 1, 1)
        return

    def OnOff(self,V):
        self.splitter.setEnabled(V)
        self.actionSave.setEnabled(V)
        self.actionSave_As.setEnabled(V)
        self.actionTerminal.setEnabled(V)
        self.actionBrowse.setEnabled(V)
        self.actionRun.setEnabled(V)
        self.actionParaview.setEnabled(V)

    def addNewFigureButton(self):
        self.qfigWidgets.append(QtGui.QComboBox(self.scrollAreaWidgetContents))
        self.qfigWidgets[self.nPlots].setObjectName(_fromUtf8("newFigureComboBox"))
        self.qfigWidgets[self.nPlots].addItem(_fromUtf8("Select New Figure"))
        self.qfigWidgets[self.nPlots].insertSeparator(1)
        self.qfigWidgets[self.nPlots].addItems(self.typeFigure)
        self.qscrollLayout.addWidget(self.qfigWidgets[self.nPlots],self.nPlots/2,self.nPlots%2)