# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from mesh_ui import Ui_meshUI
from blockmesh_ui import Ui_blockmeshDialog
from ExampleThread import *
from utils import *
import time
import subprocess
from myNavigationToolbar import *

from PyFoam.RunDictionary.BoundaryDict import BoundaryDict
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from numpy import arange

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

class meshUI(QtGui.QScrollArea, Ui_meshUI):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QScrollArea.__init__(self, parent)
        self.setupUi(self)

class meshWidget(meshUI):

    def __init__(self):
        meshUI.__init__(self)
        self.canvas = ''
        self.toolbar = ''
        self.fig = ''
        
        for iatt in self.__dict__.keys():
            if 'bm_' in iatt:
                self.__getattribute__(iatt).setValidator(QtGui.QDoubleValidator())

    def setCurrentFolder(self, currentFolder):
        self.currentFolder = currentFolder
        self.nproc = self.window().nproc
        [self.timedir,self.fields,self.currtime] = currentFields(str(self.currentFolder),nproc=self.nproc)
    
    def createMesh(self):
        #--Creacion del log (instantaneo)
        command = 'touch %s/createMesh.log'%self.currentFolder
        os.system(command)
        
        #--Abrir ventana de log
        self.window().newLogTab('Create Mesh','%s/createMesh.log'%self.currentFolder)
        
        #--Creo un thread para blockMesh y conecto su finalizacion con checkMesh
        command = 'blockMesh -case %s > %s/createMesh.log'%(self.currentFolder,self.currentFolder)
        
        threadblockmesh = ExampleThread(command)
        self.connect(threadblockmesh, QtCore.SIGNAL("finished()"), self.checkMesh)
        self.connect(threadblockmesh, QtCore.SIGNAL("finished()"), threadblockmesh.terminate)
        threadblockmesh.start()
        
    def blockMesh(self):
        about = QtGui.QDialog()
        blockmesh = Ui_blockmeshDialog()        
        about.setFixedSize(454,186)
        blockmesh.setupUi(about)
        about.exec_()


    def checkMesh(self):
        #-- Desabilitar los botones
        self.pushButton_check.setEnabled(False)        
        self.pushButton_import.setEnabled(False)
        self.pushButton_view.setEnabled(False)
        self.pushButton_create.setEnabled(False)
        self.comboBox_histo.setEnabled(False)
        #--Crear el log
        command = 'touch %s/checkMesh.log'%self.currentFolder
        os.system(command)
        #--Crear la ventana del log
        self.window().newLogTab('Check Mesh','%s/checkMesh.log'%self.currentFolder)
        
        #--Creo un thread para checkMesh y lo inicio
        command = 'checkMesh -case %s > %s/checkMesh.log'%(self.currentFolder,self.currentFolder)
        self.threadcheckmesh = ExampleThread(command)
        self.connect(self.threadcheckmesh, QtCore.SIGNAL("finished()"), self.loadMeshData)
        self.connect(self.threadcheckmesh, QtCore.SIGNAL("finished()"), self.threadcheckmesh.terminate)
        self.threadcheckmesh.start()
        
        #--Comando meshQuality
        command = 'meshQuality -case %s -time 0 > %s/meshQuality.log'%(self.currentFolder,self.currentFolder)
        subprocess.Popen([command],shell=True)

    def importMesh(self):
        dialog = QtGui.QFileDialog(self)
        dialog.setNameFilter("Fluent 2D Mesh Files (*.msh) ;; Fluent 3D Mesh Files (*.msh) ;; GMSH Mesh Files (*.msh)")
        dialog.setWindowTitle('Select Mesh to Import')
        dialog.setDirectory(self.currentFolder)
        if dialog.exec_():
            #-- Desabilitar los botones
            self.pushButton_check.setEnabled(False)        
            self.pushButton_import.setEnabled(False)
            self.pushButton_view.setEnabled(False)
            self.pushButton_create.setEnabled(False)
            self.comboBox_histo.setEnabled(False)            
            
            filename = dialog.selectedFiles()[0];
            tipo = dialog.selectedNameFilter()
            if 'Fluent 3D' in tipo:
                utility = 'fluent3DMeshToFoam'
            elif 'Fluent 2D' in tipo:
                utility = 'fluentMeshToFoam'
            elif 'GMSH' in tipo:
                utility = 'gmshToFoam'
            
            with open(filename,'r') as fil:
                l1=fil.readline()   
                
            if '$MeshFormat' in l1 and utility!='gmshToFoam': #Agregar la logica para las dos restantes
                w = QtGui.QMessageBox(QtGui.QMessageBox.Information, "Error", "Bad Mesh Format")
                w.exec_()
                self.pushButton_check.setEnabled(True)                
                self.pushButton_import.setEnabled(True)        
                self.pushButton_create.setEnabled(True)
                self.pushButton_view.setEnabled(True)
                self.comboBox_histo.setEnabled(True)                
                return
            
            command = 'touch %s/importMesh.log'%self.currentFolder
            os.system(command)            
            self.window().newLogTab('Import Mesh','%s/importMesh.log'%self.currentFolder)
            
            command = '%s -case %s %s > %s/importMesh.log' %(utility, self.currentFolder, filename, self.currentFolder)
            #os.system(command)
            self.threadimportmesh = ExampleThread(command)
            self.connect(self.threadimportmesh, QtCore.SIGNAL("finished()"), self.updateFieldFiles)
            self.connect(self.threadimportmesh, QtCore.SIGNAL("finished()"), self.checkMesh)
            self.connect(self.threadimportmesh, QtCore.SIGNAL("finished()"), self.threadimportmesh.terminate)
            self.threadimportmesh.start()
            
            #self.updateFieldFiles()
            
        #self.checkMesh()

    def drawGeo(self):
        command = 'pyFoamDisplayBlockMesh.py %s/constant/polyMesh/blockMeshDict &'%self.currentFolder
        os.system(command)

    def saveBlockMesh(self):
        return

    def editBlockMesh(self):
        return

    def loadMeshData(self):
        filename = '%s/checkMesh.log'%self.currentFolder
        if os.path.isfile(filename):
            
            with open(filename, 'r') as log:
                content = log.readlines()
                for i in range(len(content)):
                    linea = content[i]

                    self.label_npoints.setText(linea.replace('\n','').strip()) if 'points:' in linea else None
                    self.label_ncells.setText(linea.replace('\n','').strip()) if 'cells:' in linea else None
                    self.label_nfaces.setText(linea.replace('\n','').strip()) if '   faces: ' in linea else None
                    self.label_nifaces.setText(linea[:-1].strip()) if 'internal faces: ' in linea else None
                    if 'bounding box' in linea:
                        limits = linea.replace('(','').replace(')','').strip().split()
                        self.label_xrange.setText('x Range: [%s, %s]'%(limits[4],limits[7]))
                        self.label_yrange.setText('y Range: [%s, %s]'%(limits[5],limits[8]))
                        self.label_zrange.setText('z Range: [%s, %s]'%(limits[6],limits[9]))
                    self.label_nhexa.setText(linea.replace('\n','').strip()) if 'hexa' in linea else None
                    self.label_nprisms.setText(linea.replace('\n','').strip()) if 'prism' in linea else None
                    self.label_nwedges.setText(linea.replace('\n','').strip()) if 'wedges:' in linea and 'tet' not in linea else None
                    self.label_npyramids.setText(linea.replace('\n','').strip()) if 'pyramids:' in linea else None
                    self.label_ntet.setText(linea.replace('\n','').strip()) if 'tet wedges:' in linea else None
                    self.label_ntetra.setText(linea.replace('\n','').strip()) if 'tetra' in linea else None
                    self.label_npoly.setText(linea[:-1].strip()) if 'polyhedra:' in linea else None
                log.close()
        else:
            QtGui.QMessageBox(QtGui.QMessageBox.Information, "Error", "CheckMesh must be executed before").exec_()
                    
        self.pushButton_check.setEnabled(True)          
        self.pushButton_import.setEnabled(True)   
        self.pushButton_create.setEnabled(True)
        self.pushButton_view.setEnabled(True)
        self.comboBox_histo.setEnabled(True)

    def drawStatistics(self):
        print 'En draw statistics'
        if self.comboBox_histo.currentIndex()==0:
            return
        filename = '%s/meshQuality.log'%self.currentFolder
        if os.path.isfile(filename):
            if self.canvas != '':
                self.verticalLayout_draw.removeWidget(self.canvas)
                self.canvas.destroy()
                self.canvas.close()
                self.canvas = ''
                import matplotlib
                item=self.groupBox_draw.findChild(matplotlib.backends.backend_qt4agg.FigureCanvasAgg)
                item.close()
                item.deleteLater()
                
            if self.toolbar != '':
                self.verticalLayout_draw.removeWidget(self.toolbar)
                self.toolbar.destroy()
                self.toolbar.close()
                self.toolbar = ''
                #import matplotlib
                #item=self.groupBox_draw.findChild(matplotlib.backends.backend_qt4agg.FigureCanvasAgg)
                #item.close()
                #item.deleteLater()
                
            keys = ['nonOrth','skew','vol']
            bins = {}
            bins['nonOrth'] = range(0,95,10)
            bins['skew'] = [x / 100.0 for x in range(25, 520, 50)]
            width = [2.5,0.25]
            maxV = 0.0
            minV = 0.0
            ikey = self.comboBox_histo.currentIndex()-1

            data = []
            log = open(filename, 'r')
            for linea in log:
                if keys[ikey] in linea:
                    datastr = linea.strip().split()[1:]
                if keys[ikey]=='vol':
                    maxV = float(linea.strip().split()[1]) if 'maxVol' in linea else maxV
                    minV = float(linea.strip().split()[1]) if 'minVol' in linea else maxV

            for i in datastr:
                data.append(int(i))
            if keys[ikey]=='vol':
                #bins[keys[ikey]] =  [x for x in drange(minV,maxV*1.05,(maxV-minV)/10)]
                if(maxV-minV)>1e-12:
                    bins[keys[ikey]] =  arange(1,maxV*1.05/minV,(maxV/minV)/10.0)
                    width.append((maxV-minV)/40.0)
                else:
                    bins[keys[ikey]] =  [minV*x for x in range(1,11)]
                    width.append(0.25*minV)

            for i in range(len(data)):
                data[i] = 1 if data[i]<1 else data[i]

            self.fig = Figure((1.5, 1.0), dpi=100)
            self.canvas = FigureCanvas(self.fig)
            
            self.canvas.setParent(self.groupBox_draw)
            ax = self.fig.add_subplot(111)
            ax.bar(bins[keys[ikey]], data, width[ikey])

            for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + \
             ax.get_xticklabels() + ax.get_yticklabels()):
                 item.set_fontsize(7)
                 
            self.toolbar = myNavigationToolbar(self.canvas,self)
            self.toolbar.removeAction(self.toolbar.actions()[7]) #elimino el boton de eliminar
            
            self.toolbar.setFixedHeight(32)
            
            self.verticalLayout_draw.addWidget(self.canvas,1)
            self.verticalLayout_draw.addWidget(self.toolbar,0,QtCore.Qt.AlignCenter)
            

        return

    def viewMesh(self):
        filequa = '%s/meshQuality.log'
        if not os.path.isfile(filequa):
            command = 'meshQuality -case %s -time 0 > %s/meshQuality.log &'%(self.currentFolder,self.currentFolder)
            os.system(command)
        #command = 'pvpython /usr/local/bin/pyFoamPVLoadState.py --state=meshNonOrth.pvsm %s &'%self.currentFolder
        command = 'pvpython /usr/local/bin/pyFoamPVLoadState.py --state=meshNonOrthWhite.pvsm %s &'%self.currentFolder
        os.system(command)

        return

    def updateFieldFiles(self):
        #tengo que releer cada uno de los campos en el directorio actual,
        #pisar los boundaries por los que aparece en constant/polyMesh/boundary
        #imponerles alguna CB por defecto dependiendo del tipo de patch
        boundaries = BoundaryDict(self.currentFolder)
        #veo los campos que tengo en el directorio inicial
        [timedir,fields,currtime] = currentFields(self.currentFolder, nproc = self.window().nproc, filterTurb=False)
        
        fileDict = '%s/system/changeDictionaryPetroSym'%self.currentFolder
        dictDict = []
        if os.path.isfile(fileDict):
            dictDict = ParsedParameterFile(fileDict,createZipped=False)

        for ifield in fields:
            if dictDict==[]:
                filename = '%s/%s'%(timedir,ifield)
                fieldData = ParsedParameterFile(filename,createZipped=False)
            else:
                fieldData = dictDict['dictionaryReplacement'][ifield]

            oldKeys = fieldData['boundaryField'].keys()
            fieldData['boundaryField'] = {}
            for ipatch in boundaries.getValueDict():
                if ipatch not in fieldData['boundaryField']:
                    if boundaries[ipatch]['nFaces']==0:
                        continue
                    patchDict={}
                    if ifield in unknowns:
                        if boundaries[ipatch]['type']=='empty':
                            patchDict['type'] = 'empty'
                            if ipatch in oldKeys:
                                patchDict['ZZvalue'] = '0'
                        else:
                            patchDict['type'] = 'zeroGradient'
                            if ipatch in oldKeys:
                                patchDict['ZZvalue'] = '0'
                    else:
                        patchDict['type'] = 'calculated'
                        if ipatch in oldKeys:
                                patchDict['ZZvalue'] = '0'
                    fieldData['boundaryField'][ipatch] = patchDict
            
            # poner el campo interno uniforme en cero
            if types[ifield] == 'scalar':
                fieldData['internalField'] = 'uniform 0'
            elif types[ifield] == 'vector':
                fieldData['internalField'] = 'uniform (0 0 0)'

            if dictDict==[]:
                fieldData.writeFile()

        if dictDict!=[]:
            dictDict.writeFile()
            dictDictBak = ParsedParameterFile(fileDict,createZipped=False)
            keysDict = dictDict['dictionaryReplacement'].keys()
            dictDictBak['dictionaryReplacement'] = {}
            for ikey in keysDict:
                if ikey in self.fields:
                    dictDictBak['dictionaryReplacement'][ikey] = dictDict['dictionaryReplacement'][ikey]
            dictDictBak.writeFileAs('%s/system/changeDictionaryPetroSym.bak'%self.currentFolder)
            
            command = 'sed -i "s/ZZ/~/g" %s/system/changeDictionaryPetroSym.bak'%(self.currentFolder)
            os.system(command)
            
            #chequear que no bloquee
            if self.window().nproc<=1:
                command = 'changeDictionary -case %s -dict %s/system/changeDictionaryPetroSym.bak > %s/changeDictionary.log &'%(self.currentFolder,self.currentFolder,self.currentFolder)
            else:
                command = 'mpirun -np %s changeDictionary -case %s -dict %s/system/changeDictionaryPetroSym.bak -parallel > %s/changeDictionary.log &'%(str(self.nproc),self.currentFolder,self.currentFolder,self.currentFolder)
            os.system(command)
            
        return
