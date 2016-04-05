# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

## En lugar de utilizar un if en currentIndex, usarlo como un índice de lista
## Evitar que haya decisiones en el generateItems, por lo cual es necesario modificar la estructura que genera las combobox

from PyQt4 import QtGui, QtCore
from solverSettings_ui import Ui_solverSettingsUI
import os
from utils import * #Para currentFields
from collections import OrderedDict
from copy import deepcopy
from os import path

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
        
dicTemplate = OrderedDict()
dicTemplate['solvers'] = OrderedDict()
dicTemplate['solvers']['GAMG'] = OrderedDict()
dicTemplate['solvers']['GAMG']['solver'] = ['GAMG']
dicTemplate['solvers']['GAMG']['smoother'] = ['GaussSeidel']
dicTemplate['solvers']['GAMG']['cacheAgglomeration'] = ['on']
dicTemplate['solvers']['GAMG']['agglomerator'] = ['faceAreaPair']
dicTemplate['solvers']['GAMG']['nCellsInCoarsestLevel'] = [10]
dicTemplate['solvers']['GAMG']['mergeLevels'] = [1]
dicTemplate['solvers']['GAMG']['nPreSweeps'] = [0]
dicTemplate['solvers']['GAMG']['nPostSweeps'] = [1]
dicTemplate['solvers']['GAMG']['tolerance'] = [1e-8]
dicTemplate['solvers']['GAMG']['relTol'] = [0.01]
dicTemplate['solvers']['PBiCG'] = OrderedDict()
dicTemplate['solvers']['PBiCG']['solver'] = ['PBiCG']
dicTemplate['solvers']['PBiCG']['preconditioner'] = ['DILU']
dicTemplate['solvers']['PBiCG']['tolerance'] = [1e-8]
dicTemplate['solvers']['PBiCG']['relTol'] = [0]
dicTemplate['solvers']['PCG'] = OrderedDict()
dicTemplate['solvers']['PCG']['solver'] = ['PCG']
dicTemplate['solvers']['PCG']['preconditioner'] = ['DIC']
dicTemplate['solvers']['PCG']['tolerance'] = [1e-8]
dicTemplate['solvers']['PCG']['relTol'] = [0]
dicTemplate['solvers']['smoothSolver'] = OrderedDict()
dicTemplate['solvers']['smoothSolver']['solver'] = ['smoothSolver']
dicTemplate['solvers']['smoothSolver']['smoother'] = ['GaussSeidel']
dicTemplate['solvers']['smoothSolver']['nSweeps'] = [2]
dicTemplate['solvers']['smoothSolver']['tolerance'] = [1e-8]
dicTemplate['solvers']['smoothSolver']['relTol'] = [0]
dicTemplate['solvers']['PIMPLE'] = OrderedDict()
dicTemplate['solvers']['PIMPLE']['nNonOrthogonalCorrectors'] = [1]
dicTemplate['solvers']['PIMPLE']['nCorrectors'] = [1]
dicTemplate['solvers']['PIMPLE']['nOuterCorrectors'] = [1]
dicTemplate['solvers']['PIMPLE']['pRefCell'] = [0]
dicTemplate['solvers']['PIMPLE']['pRefValue'] = [0.0]
dicTemplate['solvers']['PIMPLE']['momentumPredictor'] = ['on']
dicTemplate['solvers']['relaxationFactors'] = OrderedDict()
dicTemplate['solvers']['relaxationFactors']['fields'] = OrderedDict()

unknowns = ['U','p','pFinal','UFinal','k','kFinal','epsilon','epsilonFinal','nuTilda','nuTildaFinal','omega','omegaFinal']
dic_unknowsSymetric = ['p','pFinal']
dic_unknowsNoSymetric = ['U','UFinal','k','kFinal','epsilon','epsilonFinal','omega','omegaFinal','nuTilda','nuTildaFinal']
dic_solversPIMPLE = ['pimpleFoam']
dic_solversSIMPLE = ['simpleFoam']
dic_solversPISO = ['icoFoam']

dicPCG = {}
dicPCG['solver'] = ['PCG',3]
dicPCG[0] = ['preconditioner','Preconditioner: ',2,'cb_pre_pcg',4,['DIC','FDIC','diagonal','none'],1]
dicPCG[1] = ['tolerance','Tolerance: ',0,'line_tolerance_pcg',"-?\d+\.?\d*e-?\d+",1e-6]
dicPCG[2] = ['relTol','Relative Tolerance: ',0,'line_reltolerance_pcg',"-?\d+\.?\d*e-?\d+",0]

dicPBiCG = {}
dicPBiCG['solver'] = ['PBiCG',3]
dicPBiCG[0] = ['preconditioner','Preconditioner: ',2,'cb_pre_pbicg',3,['DILU','diagonal','none'],1]
dicPBiCG[1] = ['tolerance','Tolerance: ',0,'line_tolerance_pbicg',"-?\d+\.?\d*e-?\d+",1e-6]
dicPBiCG[2] = ['relTol','Relative Tolerance: ',0,'line_reltolerance_pbicg',"-?\d+\.?\d*e-?\d+",0]

dicGAMG = {}
dicGAMG['solver'] = ['GAMG',9]
dicGAMG[0] = ['smoother','Smoother: ',2,'cb_smoother_gamg',3,['GaussSeidel','DIC','DICGaussSeidel']]
dicGAMG[1] = ['cacheAgglomeration','Cache Agglomeration: ',3,'chb_agg_gamg'] #3 checkbox
dicGAMG[2] = ['agglomerator','Agglomerator: ',2,'cb_agg_gamg',1,['faceAreaPair'],1]
dicGAMG[3] = ['nCellsInCoarsestLevel','Cells In Coarsest Level: ',1,'spin_cicl_gamg']
dicGAMG[4] = ['mergeLevels','Merge Levels: ',1,'spin_mergl_gamg']
dicGAMG[5] = ['nPreSweeps','Pre Sweeps: ',1,'spin_presw_gamg']
dicGAMG[6] = ['nPostSweeps','Post Sweeps: ',1,'spin_postsw_gamg']
dicGAMG[7] = ['tolerance','Tolerance: ',0,'line_tolerance_gamg',"-?\d+\.?\d*e-?\d+",1e-6]
dicGAMG[8] = ['relTol','Relative Tolerance: ',0,'line_reltolerance_gamg',"-?\d+\.?\d*e-?\d+",0]

dicSmoothSolver = {}
dicSmoothSolver['solver'] = ['smoothSolver',4]
dicSmoothSolver[0] = ['smoother','Smoother: ',2,'cb_smoother_ss',3,['GaussSeidel','DIC','DICGaussSeidel']] #2 combobox
dicSmoothSolver[1] = ['nSweeps','Sweeps: ',1,'spin_Sweeps_ss'] #1 spinbox
dicSmoothSolver[2] = ['tolerance','Tolerance: ',0,'line_tolerance_ss',"-?\d+\.?\d*e-?\d+",1e-6] #0 lineedit
dicSmoothSolver[3] = ['relTol','Relative Tolerance: ',0,'line_reltol_ss',"-?\d+\.?\d*e-?\d+",0] #0 lineedit

dicPIMPLE = {}
dicPIMPLE['solver'] = ['PIMPLE',6]
dicPIMPLE[0] = ['nNonOrthogonalCorrectors','Non-Orthogonal Correctors: ',1,'spin_nonoc_pim']
dicPIMPLE[1] = ['nOuterCorrectors','Outer Correctors: ',1,'spin_outcor_pim']
dicPIMPLE[2] = ['nCorrectors','Correctors: ',1,'spin_cor_pim']
dicPIMPLE[3] = ['momentumPredictor','Momentum Predictor: ',3,'chb_mom_pim']
dicPIMPLE[4] = ['pRefCell','Cell: ',1,'spin_refcell_pim']
dicPIMPLE[5] = ['pRefValue','Value: ',0,'line_refval_pim',"-?\d+\.?\d*e-?\d+",0]

dicRelaxation = {}
dicRelaxation['solver'] = ['Relaxation',0] #Inicialmente

class solverSettingsUI(QtGui.QScrollArea, Ui_solverSettingsUI):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QScrollArea.__init__(self, parent)

        self.setupUi(self)
        
class solverSettings(solverSettingsUI):

    def __init__(self,folder,solvername):
        self.currentFolder = folder
        self.solvername = solvername
        solverSettingsUI.__init__(self)
        self.loadData()
        self.addTabs()  
        self.pushButton.setEnabled(False)
        
        
    def addTabs(self,ipatch=None):
        self.tabWidget.clear()
        
        self.CurrentWidgetIndexDict = dict() #Dict que guarda el indice del solver actual
        self.OriginalWidgetIndexDict = dict() #Dict que guarda el indice del solver original        
        
        for ifield in self.fields:
            if ifield not in unknowns:
                continue
            
            widget = QtGui.QWidget()
            widget.setObjectName(ifield)
            #layoutV = QtGui.QVBoxLayout(widget)
            layoutV = QtGui.QGridLayout(widget)
            
            layoutH = QtGui.QHBoxLayout()
            label = QtGui.QLabel()
            label.setText('Solver: ')
            layoutH.addWidget(label)
            layoutV.addLayout(layoutH,1,0)

            layoutH = QtGui.QHBoxLayout()
            cb = QtGui.QComboBox()
            cb.setObjectName(ifield) #Le pongo el mismo nombre que el campo para la busqueda en el boton de aplicar
            
            if ifield in dic_unknowsSymetric:
                cb.addItems(['PCG','GAMG','Smooth Solver'])
            else:
                cb.addItems(['PBiCG','GAMG','Smooth Solver'])
                
            layoutH.addWidget(cb) 
            #layoutV.addLayout(layoutH)
            layoutV.addLayout(layoutH,1,1)
            
            if (not self.parsedData.content.has_key('solvers')):
                self.parsedData.content['solvers'] = {}
            
            #Por default, si no existe el campo en el documento, que empiece con smoothsolver (Porque es comun para simetricos y no simetricos)
            if (not self.parsedData.content['solvers'].has_key(ifield)):
                templateparsedData = deepcopy(self.templateparsedDataI)
                self.parsedData.content['solvers'][ifield] = templateparsedData['solvers']['smoothSolver']
            
            #Alguna manera mas limpia de hacer esto? 
            if (self.parsedData['solvers'][ifield]['solver'] == 'PBiCG') or (self.parsedData['solvers'][ifield]['solver'] == 'PCG'):
                cb.setCurrentIndex(0)
            elif self.parsedData['solvers'][ifield]['solver'] == 'GAMG':
                cb.setCurrentIndex(1)
            elif self.parsedData['solvers'][ifield]['solver'] == 'smoothSolver':
                cb.setCurrentIndex(2)                   
            
            spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
            layoutV.addItem(spacerItem)            
            
            self.tabWidget.addTab(widget, ifield)
            self.CurrentWidgetIndexDict[cb.objectName()] = cb.currentIndex() #Para la primer vez
            self.OriginalWidgetIndexDict[cb.objectName()] = cb.currentIndex() #Parche para que el cambio de ventanas no pierda los datos
            self.modifyTables(self.tabWidget.widget(self.tabWidget.count() - 1),True)
            self.tabWidget.setTabText(self.tabWidget.count(),ifield)
    
            QtCore.QObject.connect(cb, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.onChangeTables)
        
        if self.solvername in dic_solversPIMPLE:
            #PIMPLE
            widget = QtGui.QWidget()
            widget.setObjectName('PIMPLE')
            #layoutV = QtGui.QVBoxLayout(widget)
            layoutV = QtGui.QGridLayout(widget)
            solver = dicPIMPLE['solver'][0]
            
            for ifield in range(0,dicPIMPLE['solver'][1]):
                self.generateItems(dicPIMPLE[ifield],layoutV,ifield)
            
            self.OriginalWidgetIndexDict['PIMPLE'] = -1 #Para que no patee setValues
            self.setValues(False,dicPIMPLE,solver,widget,'PIMPLE')
            
            spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
            layoutV.addItem(spacerItem)            
            self.tabWidget.addTab(widget, solver)
            
            #Relaxation
            widget = QtGui.QWidget()
            widget.setObjectName('Relaxation')
            #layoutV = QtGui.QVBoxLayout(widget)
            layoutV = QtGui.QGridLayout(widget)
            solver = dicRelaxation['solver'][0]
            
            i=0            
            for ifield in self.fieldsoriginal: #Cargo todos los que haya en el dic
                dicRelaxation[i] = [ifield,ifield+": ",0,"line_"+ifield+"_relax","0\.\d+|1|0\.\d+e-\d+|1e-\d+",1]
                i=i+1   
            dicRelaxation['solver'][1] = i
                
            for ifield in range(0,dicRelaxation['solver'][1]):
                self.generateItems(dicRelaxation[ifield],layoutV,ifield)
                
            self.OriginalWidgetIndexDict['Relaxation'] = -1 #Para que no patee setValues
            self.setValues(False,dicRelaxation,solver,widget,'Relaxation')
                
            spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
            layoutV.addItem(spacerItem)            
            self.tabWidget.addTab(widget, solver)
            

    def loadData(self):
        self.filename = '%s/system/fvSolution'%self.currentFolder        
        self.filename2 = path.join(path.dirname(__file__),"templates/fvSolutionTemplate")
        
        self.parsedData = ParsedParameterFile(self.filename,createZipped=False)
        self.templateparsedDataI = ParsedParameterFile(self.filename2,createZipped=False)
        
        #self.fields = self.parsedData['solvers'].keys() #No hay que meter todos 
        [self.timedir,self.fields,currtime] = currentFields(self.currentFolder)
        
        if self.solvername in dic_solversPIMPLE:
            self.fieldsoriginal = deepcopy(self.fields)
            for ifield in self.fieldsoriginal:
                newfield = ifield+"Final"
                self.fields.append(newfield)
        
        return
        
    def modifyTables(self,widget,creation):
            #Es mas barato modificar todo, o solo donde estoy parado?
        
            #Estas siempre van a existir
            #layout = widget.findChildren(QtGui.QVBoxLayout)[0] 
            layout = widget.findChildren(QtGui.QGridLayout)[0]           
            cb = widget.findChildren(QtGui.QComboBox)[0] #La cb de los solver
            noCreado = creation or (self.CurrentWidgetIndexDict[cb.objectName()] != cb.currentIndex()) #Boleano que me dice si cambio de solver
            solver = cb.objectName()
            currentIndex = cb.currentIndex()
            self.clearLayout(layout,2)
            
            if currentIndex == 0:
                
                #self.clearLayout(layout,1)
                
                if solver in dic_unknowsSymetric:
                    for ifield in range(0,dicPCG['solver'][1]):
                        self.generateItems(dicPCG[ifield],layout,ifield)
                                        
                    self.setValues(creation,dicPCG,solver,widget,currentIndex)
                else:
                    for ifield in range(0,dicPBiCG['solver'][1]):
                        self.generateItems(dicPBiCG[ifield],layout,ifield)
                                        
                    self.setValues(creation,dicPBiCG,solver,widget,currentIndex)
                
            elif currentIndex == 1:
                
                #self.clearLayout(layout,1)  #Limpio y creo de nuevo
                
                self.changeValuesOnCB(0,[['GaussSeidel','DIC','DICGaussSeidel'],['GaussSeidel']],dicGAMG,(solver in dic_unknowsSymetric))
                
                for ifield in range(0,dicGAMG['solver'][1]):
                    self.generateItems(dicGAMG[ifield],layout,ifield)
                
                self.setValues(creation,dicGAMG,solver,widget,currentIndex)
            
            elif currentIndex == 2:
                
                #self.clearLayout(layout,1)
                
                self.changeValuesOnCB(0,[['GaussSeidel','DIC','DICGaussSeidel'],['GaussSeidel']],dicSmoothSolver,(solver in dic_unknowsSymetric))
                
                for ifield in range(0,dicSmoothSolver['solver'][1]):
                    self.generateItems(dicSmoothSolver[ifield],layout,ifield)
                                
                self.setValues(creation,dicSmoothSolver,solver,widget,currentIndex)
                    
            spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
            layout.addItem(spacerItem)
            
            self.CurrentWidgetIndexDict[cb.objectName()] = cb.currentIndex()
            
    
    def onChangeTables(self):
        self.modifyTables(self.tabWidget.currentWidget(),False) #Se modifica solo donde estoy parado
        
    def onChangeSomething(self): # Se activa solo cuando todos los campos de textos estan llenos (esta mal eso)
        self.pushButton.setEnabled(True)
    
    def aplicar(self):
        
        for itab in range(self.tabWidget.count()):
            
            widget = self.tabWidget.widget(itab)
            if widget.objectName() not in unknowns:
                continue
            
            cb = widget.findChildren(QtGui.QComboBox)[0] #Esta es la cb del solver
            
            templateparsedData = deepcopy(self.templateparsedDataI) #dicTemplate
            currentIndex = cb.currentIndex()
            solver = cb.objectName()
            
            if currentIndex == 0:
               
               if solver in dic_unknowsSymetric:
                   self.parsedData['solvers'][solver] = templateparsedData['solvers']['PCG']
                   for ifield in range(0,dicPCG['solver'][1]):
                       self.saveItems(widget,dicPCG,ifield,self.parsedData['solvers'][solver])
               else:
                   self.parsedData['solvers'][solver] = templateparsedData['solvers']['PBiCG']
                   for ifield in range(0,dicPBiCG['solver'][1]):
                       self.saveItems(widget,dicPBiCG,ifield,self.parsedData['solvers'][solver])
                
            elif currentIndex == 1:
                self.parsedData['solvers'][solver] = templateparsedData['solvers']['GAMG']
                    
                self.changeValuesOnCB(0,[['GaussSeidel','DIC','DICGaussSeidel'],['GaussSeidel']],dicGAMG,(solver in dic_unknowsSymetric))
                
                for ifield in range(0,dicGAMG['solver'][1]):
                    self.saveItems(widget,dicGAMG,ifield,self.parsedData['solvers'][solver])
                
            elif currentIndex == 2:
                self.parsedData['solvers'][solver] = templateparsedData['solvers']['smoothSolver']
                    
                self.changeValuesOnCB(0,[['GaussSeidel','DIC','DICGaussSeidel'],['GaussSeidel']],dicSmoothSolver,(solver in dic_unknowsSymetric))
                
                for ifield in range(0,dicSmoothSolver['solver'][1]):
                    self.saveItems(widget,dicSmoothSolver,ifield,self.parsedData['solvers'][solver])
                
            self.CurrentWidgetIndexDict[cb.objectName()] = cb.currentIndex()
            self.OriginalWidgetIndexDict[cb.objectName()] = cb.currentIndex()   
        
        #PIMPLE  
        widget = self.tabWidget.findChild(QtGui.QWidget,'PIMPLE')
        templateparsedData = deepcopy(self.templateparsedDataI)
        self.parsedData['PIMPLE'] = templateparsedData['solvers']['PIMPLE']
        for ifield in range(0,dicPIMPLE['solver'][1]):
            self.saveItems(widget,dicPIMPLE,ifield,self.parsedData['PIMPLE'])
            
        #Relaxation          
        widget = self.tabWidget.findChild(QtGui.QWidget,'Relaxation')        
        templateparsedData = deepcopy(self.templateparsedDataI)        
        self.parsedData['relaxationFactors'] = templateparsedData['solvers']['relaxationFactors']
        self.parsedData['relaxationFactors']['fields'] = templateparsedData['solvers']['relaxationFactors']['fields']
        for ifield in range(0,dicRelaxation['solver'][1]):
            self.saveItems(widget,dicRelaxation,ifield,self.parsedData['relaxationFactors']['fields'])
        
        #####
        self.parsedData.writeFile()
        self.pushButton.setEnabled(False)
        return

    def editar(self):
        #command = '$EDITOR %s/system/controlDict &'%self.currentFolder
        command = 'gedit %s/system/fvSolution &'%self.currentFolder
        os.system(command)
        return
        
    def clearLayout(self, layout, dejar):
        for i in reversed(range(layout.count())):
            if i>= dejar:
                item = layout.itemAt(i)
        
                if isinstance(item, QtGui.QWidgetItem):
                    item.widget().close()
                    item.widget().deleteLater()
                    # or
                    # item.widget().setParent(None)
                elif isinstance(item, QtGui.QSpacerItem):
                    None
                    # no need to do extra stuff
                else:
                    self.clearLayout(item.layout(),0)
        
                # remove the item from layout
                layout.removeItem(item)
                
    """
    Función generateItems()
    
    dic: Diccionario del cual se sacarán los datos para generar cada campo particular dentro del layout vertical.
    layoutV: Layout vertical al cual se agregará el layout horizontal generado en la función.
    ifield: Entero que se utiliza para ir llevando la cuenta del lugar que ocupará el campo en el GridLayout.
    
    Descripción:
    Función que crea un layout horizontal que tiene como estructura un string a la izquierda, y un objeto identificado por el tipo a la derecha.
    Luego agrega ese layout horizontal al layout vertical dado.
    
    """
                
    def generateItems(self, dic, layoutV, ifield):
        
        layoutH = QtGui.QHBoxLayout()
        textlabel = QtGui.QLabel()
        textlabel.setText(dic[1])
        layoutH.addWidget(textlabel)
        layoutV.addLayout(layoutH,ifield+2,0)
        tipo = dic[2]
        
        layoutH = QtGui.QHBoxLayout()
        if tipo==0:
            line = QtGui.QLineEdit()
            line.setObjectName(dic[3])
            rx = QtCore.QRegExp(dic[4])
            validator = QtGui.QRegExpValidator(rx,line)
            line.setValidator(validator)
            line.setText(str(dic[5])) #Por default, cuidado!
            line.setFixedWidth(120)
            layoutH.addWidget(line)
            QtCore.QObject.connect(line, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.onChangeSomething)
        elif tipo==1:
            spin = QtGui.QSpinBox()
            spin.setObjectName(dic[3])
            spin.setFixedWidth(120)
            layoutH.addWidget(spin)
            QtCore.QObject.connect(spin, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.onChangeSomething)
        elif tipo==2:
            cb = QtGui.QComboBox()
            cb.setObjectName(dic[3])
            cb.addItems(dic[5])
            cb.setFixedWidth(120)
            layoutH.addWidget(cb)
            QtCore.QObject.connect(cb, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.onChangeSomething)
        elif tipo==3:
            cbox = QtGui.QCheckBox()
            cbox.setObjectName(dic[3])
            cbox.setFixedWidth(120)
            layoutH.addWidget(cbox)
            QtCore.QObject.connect(cbox, QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), self.onChangeSomething)
        
        #layoutV.addLayout(layoutH)
        layoutV.setAlignment(QtCore.Qt.AlignLeft)
        layoutH.setAlignment(QtCore.Qt.AlignLeft)
        layoutV.addLayout(layoutH,ifield+2,1)
    
    """
    Función saveItems()
    
    widget: Widget del cual estoy guardando los datos.
    dic: Diccionario que me proveerá el nombre del objeto específico que estoy buscando para guardar su valor (Es el tercer campo en todos los casos) y
    el nombre del string que se escribe en fvSolution (El primer campo en todos los casos).
    ifield: Entero que se utiliza para saber en que key estoy del diccionario.
    dicE: Diccionario de salida, adonde se guardaran los datos.
    
    Descripción:    
    Función para guardar los datos en un widget en un diccionario dado.
    
    """
    
    def saveItems(self, widget, dic, ifield, dicE):
        tipo = dic[ifield][2]
        
        if tipo==0:
            line = widget.findChild(QtGui.QLineEdit,dic[ifield][3])
            if not line.text():
                dicE[dic[ifield][0]] = str(dic[ifield][5])
            else:
                dicE[dic[ifield][0]] = str(line.text())
        elif tipo==1:
            spin = widget.findChild(QtGui.QSpinBox,dic[ifield][3])
            dicE[dic[ifield][0]] = str(spin.value())
        elif tipo==2:
            cb = widget.findChild(QtGui.QComboBox,dic[ifield][3])
            for i in range(0,dic[ifield][4]):                
                if cb.currentIndex() == i:
                    dicE[dic[ifield][0]] = dic[ifield][5][i]
                    break
        elif tipo==3:
            cbox = widget.findChild(QtGui.QCheckBox,dic[ifield][3])
            if cbox.isChecked():
                dicE[dic[ifield][0]] = 'on'
            else:
                dicE[dic[ifield][0]] = 'off'
                
    """
    Función setValues()
    
    creation: Booleano que define si es la primera vez que se llama la función (creation en true)
    dic: dic: Diccionario que me proveerá el nombre del objeto específico que estoy buscando para guardar su valor (Es el tercer campo en todos los casos) y
    el resto de los atributos según el tipo de objeto.
    solver: Tipo del solver con el que se llama la función (Solo para fields)
    widget: Widget que se pasa por referencia y sobre el cual incluye objetos la función
    state: Variable utilizada para dos casos: Si la función es llamada por una pestaña que es un field, state será el valor actual del CB que indica el tipo de solver,
    si este es igual al original del campo, se cargaran los datos que estén en fvSolution, sino por default los del template. 
    En otro caso, si no estoy en una pestaña de fields, state tendrá el nombre de la pestaña a crear (Por ejemplo, PIMPLE, Relaxation, etc)
    
    Descripción:
    Función que setea, según el caso, valores leídos en fvSolution o leídos en el template en cada uno de los widget.
    """
    
    def setValues(self, creation, dic, solver, widget, state):
        
        ###NO ME CONVENCE
        if creation or (self.OriginalWidgetIndexDict[solver] == state): #Si es la primer vez que lo creo, o si el estado original era ese (Solo para fields)
            parsedData = self.parsedData['solvers'][solver]
        elif state == 'PIMPLE': #Si lo llamo para PIMPLE
                if self.parsedData.content.has_key('PIMPLE'):                    
                    parsedData = self.parsedData['PIMPLE']
                else:
                    tempparsedData = deepcopy(self.templateparsedDataI)
                    parsedData = tempparsedData['solvers']['PIMPLE']
        elif state == 'Relaxation':
                if self.parsedData.content.has_key('relaxationFactors'):                    
                    parsedData = self.parsedData['relaxationFactors']['fields']
                else:
                    tempparsedData = deepcopy(self.templateparsedDataI.currentText())
                    parsedData = tempparsedData['solvers']['relaxationFactors']['fields']
        else: #Sino que cargue la plantilla
            tempparsedData = deepcopy(self.templateparsedDataI)
            parsedData = tempparsedData['solvers'][dic['solver'][0]]
        #######
        
        for ifield in range(0,dic['solver'][1]):
            tipo = dic[ifield][2]
            
            if dic[ifield][0] not in parsedData.keys(): #Si hay alguna que falta, no importa ?
                continue
            
            data = parsedData[dic[ifield][0]]
            
            if tipo==0:
                line = widget.findChild(QtGui.QLineEdit,dic[ifield][3])
                line.setText(str(data))
            elif tipo==1:
                spin = widget.findChild(QtGui.QSpinBox,dic[ifield][3])
                spin.setValue(int(data))
            elif tipo==2:
                cb = widget.findChild(QtGui.QComboBox,dic[ifield][3])
                for i in range(0,dic[ifield][4]):                
                    if str(data) == dic[ifield][5][i]:
                        cb.setCurrentIndex(i)
                        break
            elif tipo==3:
                cbox = widget.findChild(QtGui.QCheckBox,dic[ifield][3])
                cbox.setChecked(str(data)=='on' or str(data)=='yes')
    """
    Función changeValuesOnCB()

    numberkey: Número que representa la key en la cual se ubica la CB a cambiar
    values: Lista de listas, con tantas listas como opciones
    
    """
    
    
    def changeValuesOnCB(self,numberkey,values,dic,condition):
        
        if condition:
            dic[numberkey][4] = len(values[0])
            dic[numberkey][5] = values[0]
        else:
            dic[numberkey][4] = len(values[1])
            dic[numberkey][5] = values[1]
            
                
        