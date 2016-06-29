# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from bc_ui import Ui_bcUI
import os
from bcPatch import *
from utils import *

from PyFoam.RunDictionary.BoundaryDict import BoundaryDict
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


class bcUI(QtGui.QScrollArea, Ui_bcUI):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QScrollArea.__init__(self, parent)

        self.setupUi(self)
        
prototypes = {}
prototypes['wall'] = ['Wall', 'Custom']
prototypes['empty'] = ['Empty']
prototypes['patch'] = ['Pressure Inlet', 'Pressure Outlet', 'Velocity Inlet', 'Mass Flow Inlet', 'Outflow', 'Custom']
prototypes['cyclic'] = ['Cyclic']
prototypes['cyclicAMI'] = ['Cyclic AMI']
prototypes['wedge'] = ['Wedge']
prototypes['symmetry'] = ['Symmetry']

types = {}
types['wall'] = {}
types['wall']['U'] = ['fixedValue', 'zeroGradient', 'slip']
types['wall']['p'] = ['fixedValue', 'zeroGradient', 'fixedFluxPressure', 'uniformFixedValue']
types['wall']['p_rgh'] = ['fixedValue', 'zeroGradient', 'fixedFluxPressure', 'uniformFixedValue']
types['wall']['alpha'] = ['fixedValue', 'zeroGradient', 'uniformFixedValue', 'fixedGradient']
types['wall']['k'] = ['zeroGradient','kqRWallFunction']
types['wall']['epsilon'] = ['zeroGradient','epsilonWallFunction']
types['wall']['omega'] = ['zeroGradient','omegaWallFunction']
types['wall']['nut'] = ['zeroGradient']
types['wall']['nuTilda'] = ['zeroGradient']
types['wall']['nuSgs'] = ['zeroGradient']

types['empty'] = {}
types['empty']['U'] = ['empty']
types['empty']['p'] = ['empty']
types['empty']['p_rgh'] = ['empty']
types['empty']['alpha'] = ['empty']
types['empty']['k'] = ['empty']
types['empty']['epsilon'] = ['empty']
types['empty']['omega'] = ['empty']
types['empty']['nut'] = ['empty']
types['empty']['nuTilda'] = ['empty']
types['empty']['nuSgs'] = ['empty']

types['symmetry'] = {}
types['symmetry']['U'] = ['symmetry']
types['symmetry']['p'] = ['symmetry']
types['symmetry']['p_rgh'] = ['symmetry']
types['symmetry']['alpha'] = ['symmetry']
types['symmetry']['k'] = ['symmetry']
types['symmetry']['epsilon'] = ['symmetry']
types['symmetry']['omega'] = ['symmetry']
types['symmetry']['nut'] = ['symmetry']
types['symmetry']['nuTilda'] = ['symmetry']
types['symmetry']['nuSgs'] = ['symmetry']

types['wedge'] = {}
types['wedge']['U'] = ['wedge']
types['wedge']['p'] = ['wedge']
types['wedge']['p_rgh'] = ['wedge']
types['wedge']['alpha'] = ['wedge']
types['wedge']['k'] = ['wedge']
types['wedge']['epsilon'] = ['wedge']
types['wedge']['omega'] = ['wedge']
types['wedge']['nut'] = ['wedge']
types['wedge']['nuTilda'] = ['wedge']
types['wedge']['nuSgs'] = ['wedge']

types['cyclic'] = {}
types['cyclic']['U'] = ['cyclic']
types['cyclic']['p'] = ['cyclic']
types['cyclic']['p_rgh'] = ['cyclic']
types['cyclic']['alpha'] = ['cyclic']
types['cyclic']['k'] = ['cyclic']
types['cyclic']['epsilon'] = ['cyclic']
types['cyclic']['omega'] = ['cyclic']
types['cyclic']['nut'] = ['cyclic']
types['cyclic']['nuTilda'] = ['cyclic']
types['cyclic']['nuSgs'] = ['cyclic']

types['cyclicAMI'] = {}
types['cyclicAMI']['U'] = ['cyclicAMI']
types['cyclicAMI']['p'] = ['cyclicAMI']
types['cyclicAMI']['p_rgh'] = ['cyclicAMI']
types['cyclicAMI']['alpha'] = ['cyclicAMI']
types['cyclicAMI']['k'] = ['cyclicAMI']
types['cyclicAMI']['epsilon'] = ['cyclicAMI']
types['cyclicAMI']['omega'] = ['cyclicAMI']
types['cyclicAMI']['nut'] = ['cyclicAMI']
types['cyclicAMI']['nuTilda'] = ['cyclicAMI']
types['cyclicAMI']['nuSgs'] = ['cyclicAMI']

types['patch'] = {}
types['patch']['U'] = ['fixedValue', 'zeroGradient', 'slip', 'flowRateInletVelocity', 'uniformFixedValue','inletOutlet']
types['patch']['p'] = ['fixedValue', 'zeroGradient', 'totalPressure']
types['patch']['p_rgh'] = ['fixedValue', 'zeroGradient', 'totalPressure']
types['patch']['alpha'] = ['fixedValue', 'zeroGradient', 'inletOutlet']
types['patch']['k'] = ['zeroGradient','fixedValue']
types['patch']['epsilon'] = ['zeroGradient','fixedValue']
types['patch']['omega'] = ['zeroGradient','fixedValue']
types['patch']['nut'] = ['zeroGradient','fixedValue']
types['patch']['nuTilda'] = ['zeroGradient','fixedValue']
types['patch']['nuSgs'] = ['zeroGradient','fixedValue']

extras = {}
extras['U'] = {}
extras['U']['fixedValue'] = ['value','[m/s]',['uniform'],3]
extras['U']['zeroGradient'] = []
extras['U']['slip'] = []
#extras['U']['flowRateInletVelocity'] = ['volumetricFlowRate','[m3/s]',['constant','table'],1]
extras['U']['flowRateInletVelocity'] = ['volumetricFlowRate','[m3/s]',['constant'],1]
#extras['U']['uniformFixedValue'] = ['uniformValue','[m/s]',['constant','table'],3]
extras['U']['uniformFixedValue'] = ['uniformValue','[m/s]',['constant'],3]
extras['U']['inletOutlet'] = ['value','[m/s]',['uniform'],3,'inletValue','[m/s]',['uniform'],3]
extras['U']['wedge'] = []
extras['U']['empty'] = []
extras['U']['symmetry'] = []

extras['p'] = {}
extras['p']['fixedValue'] = ['value','[m2/s2]',['uniform'],1]
extras['p']['zeroGradient'] = []
extras['p']['totalPressure'] = ['p0','[m2/s2]',['uniform'],1]
#extras['p']['uniformFixedValue'] = ['p0','[m2/s2]',['constant','table'],1]
extras['p']['uniformFixedValue'] = ['p0','[m2/s2]',['constant'],1]
extras['p']['fixedFluxPressure'] = []
extras['p']['wedge'] = []
extras['p']['empty'] = []
extras['p']['symmetry'] = []

extras['p_rgh'] = extras['p'].copy()
#extras['p_rgh']['uniformFixedValue'] = ['p0','[Pa]',['constant','table'],1]
extras['p_rgh']['uniformFixedValue'] = ['p0','[Pa]',['constant'],1]
extras['p_rgh']['fixedValue'] = ['value','[Pa]',['uniform'],1]

extras['alpha'] = {}
extras['alpha']['fixedValue'] = ['value','[-]',['uniform'],1]
extras['alpha']['zeroGradient'] = []
extras['alpha']['inletOutlet'] = ['inletValue','[-]',['uniform'],1]
extras['alpha']['wedge'] = []
extras['alpha']['empty'] = []
extras['alpha']['symmetry'] = []

extras['k'] = {}
extras['k']['fixedValue'] = ['value','[m2/s2]',['uniform'],1]
extras['k']['wedge'] = []
extras['k']['empty'] = []
extras['k']['symmetry'] = []
extras['k']['zeroGradient'] = []
extras['k']['kqRWallFunction'] = ['value','[m2/s2]',['uniform'],1]

extras['epsilon'] = {}
extras['epsilon']['wedge'] = []
extras['epsilon']['fixedValue'] = ['value','[m2/s3]',['uniform'],1]
extras['epsilon']['empty'] = []
extras['epsilon']['symmetry'] = []
extras['epsilon']['zeroGradient'] = []
extras['epsilon']['epsilonWallFunction'] = ['value','[m2/s3]',['uniform'],1]

extras['omega'] = {}
extras['omega']['wedge'] = []
extras['omega']['fixedValue'] = ['value','[1/s]',['uniform'],1]
extras['omega']['empty'] = []
extras['omega']['symmetry'] = []
extras['omega']['zeroGradient'] = []
extras['omega']['omegaWallFunction'] = ['value','[1/s]',['uniform'],1]

extras['nuT'] = {}
extras['nuT']['wedge'] = []
extras['nuT']['fixedValue'] = ['value','[m2/s2]',['uniform'],1]
extras['nuT']['empty'] = []
extras['nuT']['symmetry'] = []
extras['nuT']['zeroGradient'] = []


extras['nuTilda'] = {}
extras['nuTilda']['wedge'] = []
extras['nuTilda']['fixedValue'] = ['value','[m2/s2]',['uniform'],1]
extras['nuTilda']['empty'] = []
extras['nuTilda']['symmetry'] = []
extras['nuTilda']['zeroGradient'] = []

extras['nuSgs'] = {}
extras['nuSgs']['wedge'] = []
extras['nuSgs']['fixedValue'] = ['value','[m2/s2]',['uniform'],1]
extras['nuSgs']['empty'] = []
extras['nuSgs']['symmetry'] = []
extras['nuSgs']['zeroGradient'] = []

class bcWidget(bcUI):

    def __init__(self,folder,nproc):
        self.currentFolder = folder
        bcUI.__init__(self)
        
        self.icones = {}
        self.icones['wall'] = QtGui.QIcon()
        self.icones['wall'].addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/wall16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.icones['empty'] = QtGui.QIcon()
        self.icones['empty'].addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/empty16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.icones['patch'] = QtGui.QIcon()
        self.icones['patch'].addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/patch16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.icones['cyclic'] = QtGui.QIcon()
        self.icones['cyclic'].addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/cyclic16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.icones['cyclicAMI'] = QtGui.QIcon()
        self.icones['cyclicAMI'].addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/cyclicAMI16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.icones['wedge'] = QtGui.QIcon()
        self.icones['wedge'].addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/wedge16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.icones['symmetry'] = QtGui.QIcon()
        self.icones['symmetry'].addPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/symmetry16.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)

        
        self.boundaries = BoundaryDict(str(self.currentFolder))
        
        self.nproc = nproc

        #veo los campos que tengo en el directorio inicial
        [self.timedir,self.fields,self.currtime] = currentFields(self.currentFolder,nproc=self.nproc)
        #print self.fields
        self.loadData()
        
        self.comboBox.setEnabled(False)        
        

    def loadData(self):
        self.listWidget.clear()
        for ipatch in self.boundaries.patches():
            Item = QtGui.QListWidgetItem()
            Item.setIcon(self.icones[self.boundaries[ipatch]['type']])
            Item.setText(_translate("bcWidget", ipatch, None))
            self.listWidget.addItem(Item)
        
        self.pushButton.setEnabled(False)
        self.addTabs()

    def changeSelection(self):
        ipatch = str(self.listWidget.currentItem().text())
        self.comboBox.clear()
        self.comboBox.addItems(prototypes[self.boundaries[ipatch]['type']])
        self.addTabs(ipatch)
        return
        
    def addTabs(self,ipatch=None):
        for itab in range(self.tabWidget.count()):
            layout = self.tabWidget.widget(itab).findChildren(QtGui.QVBoxLayout)[0]
            self.clearLayout(layout,0)
        self.tabWidget.clear()
        
        fileDict = '%s/system/changeDictionaryPetroSym'%self.currentFolder
        dictDict = []
        if os.path.isfile(fileDict):
            dictDict = ParsedParameterFile(fileDict,createZipped=False)
                
        for ifield in self.fields:
            if ifield not in unknowns:
                continue
            widget = QtGui.QWidget()
            layout = QtGui.QVBoxLayout(widget)
            if ipatch:
                if dictDict==[]:                
                    filename = '%s/%s'%(self.timedir,ifield)
                    parsedData = ParsedParameterFile(filename,listLengthUnparsed=20,createZipped=False)
                    thisPatch = parsedData['boundaryField'][ipatch]
                else:
                    thisPatch = dictDict['dictionaryReplacement'][ifield]['boundaryField'][ipatch]
                
                newComboBox = QtGui.QComboBox()
                newComboBox.addItems(types[self.boundaries[ipatch]['type']][ifield])
                #aca hay que llamar a este evento solo si se cambia                
                index = newComboBox.findText(thisPatch['type'])
                newComboBox.setCurrentIndex(index) if index!=-1 else None                    
                layout.addWidget(newComboBox)
                extraInfo = extras[ifield][thisPatch['type']]
                self.addExtraInfo(layout,extraInfo)
                QtCore.QObject.connect(newComboBox, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.onChangeComboType)
                
                #cargo los datos desde el diccionario
                L = range(layout.count())
                L = L[1:-1]
                iExtra = 0
                for l in L:
                    layout2 = layout.itemAt(l).layout()
                    if layout2:
                        if layout2.itemAt(1).widget().currentText() != 'table':
                            data = str(thisPatch[extraInfo[iExtra*4]])
                            data = data.replace('(','').replace(')','').split()
                            if layout2.count()==3:
                                layout2.itemAt(1).widget().setCurrentIndex(layout2.itemAt(1).widget().findText(data[0]))
                                layout2.itemAt(2).widget().setText(data[1])
                            else:
                                layout2.itemAt(1).widget().setCurrentIndex(layout2.itemAt(1).widget().findText(data[0]))
                                layout2.itemAt(2).widget().setText(data[1])
                                layout2.itemAt(3).widget().setText(data[2])
                                layout2.itemAt(4).widget().setText(data[3])                             
                        else:
                            None
                            #determinar que hacer si quiero cargar una table!!!     
                            #('table', [[0, 0.0], [1e6-0.01, 0.0], [1e6, 1.0], [1e6, 1.0]])
                            #tabla = self.getTabla(itab)
                            #parsedData['boundaryField'][ipatch][extraInfo[iExtra*4]] = ('table',tabla)
                        iExtra = iExtra+1
            
            spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
            layout.addItem(spacerItem)
        
            self.tabWidget.addTab(widget, ifield)
            self.tabWidget.setTabText(self.tabWidget.count(),ifield)

    def onChangeComboType(self):
        ii = self.tabWidget.currentIndex()
        ifield = str(self.tabWidget.tabText(ii))
        widget = self.tabWidget.currentWidget()
        if widget:
            itype = str(widget.findChildren(QtGui.QComboBox)[0].currentText())
            layout = widget.findChildren(QtGui.QVBoxLayout)[0]
            self.clearLayout(layout, 1)
            self.addExtraInfo(layout,extras[ifield][itype])
        self.checkData()
            
            
    def onEditValue(self):
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

    def addExtraInfo(self,layout,extraInfo):
        if extraInfo != []:
            for i in range(len(extraInfo)/4):
                layout2 = QtGui.QHBoxLayout()
                label = QtGui.QLabel()
                label.setText('%s %s'%(extraInfo[i*4],extraInfo[i*4+1]))
                layout2.addWidget(label)
                
                if extraInfo[i*4+2]:
                    cb = QtGui.QComboBox()
                    cb.addItems(extraInfo[i*4+2])
                    layout2.addWidget(cb)
                    
                for j in range(extraInfo[i*4+3]):
                    ledit = QtGui.QLineEdit()
                    ledit.setValidator(QtGui.QDoubleValidator())
                    layout2.addWidget(ledit)
                    QtCore.QObject.connect(ledit, QtCore.SIGNAL(_fromUtf8("textEdited(QString)")), self.checkData)
                layout.addLayout(layout2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        layout.addItem(spacerItem)
        
    def changePrototype(self):
        return
        
    def saveBCs(self):
        
        ipatch = str(self.listWidget.currentItem().text())
        
        fileDict = '%s/system/changeDictionaryPetroSym'%self.currentFolder
        dictDict = []
        if os.path.isfile(fileDict):
            dictDict = ParsedParameterFile(fileDict,createZipped=False)
            
        for itab in range(self.tabWidget.count()):
            ifield = str(self.tabWidget.tabText(itab))
            itype = str(self.tabWidget.widget(itab).findChildren(QtGui.QComboBox)[0].currentText())
            layout = self.tabWidget.widget(itab).findChildren(QtGui.QVBoxLayout)[0]
            if dictDict == []:
                filename = '%s/%s'%(self.timedir,ifield)
                parsedData = ParsedParameterFile(filename,listLengthUnparsed=20,createZipped=False)
                thisPatch = parsedData['boundaryField'][ipatch]
            else:
                thisPatch = dictDict['dictionaryReplacement'][ifield]['boundaryField'][ipatch]

            thisPatch = {}
            thisPatch['type'] = itype
            
            if itype == 'zeroGradient':
                thisPatch['ZZvalue'] = '0'
                
            #debo tomar los valores extras, si los tiene
            extraInfo = extras[ifield][itype]
            L = range(layout.count())
            L = L[1:-1]
            iExtra = 0
            #print ipatch
            
            for l in L:
                layout2 = layout.itemAt(l).layout()
                if layout2:
                    if layout2.itemAt(1).widget().currentText() != 'table':
                        if layout2.count()==3:
                             thisPatch[extraInfo[iExtra*4]] = '%s %s' %(layout2.itemAt(1).widget().currentText(),layout2.itemAt(2).widget().text())
                        else:
                             thisPatch[extraInfo[iExtra*4]] = '%s (%s %s %s)' %(layout2.itemAt(1).widget().currentText(),layout2.itemAt(2).widget().text(),layout2.itemAt(3).widget().text(),layout2.itemAt(4).widget().text())
                    else:
                        #determinar que hacer si quiero cargar una table!!!     
                        #('table', [[0, 0.0], [1e6-0.01, 0.0], [1e6, 1.0], [1e6, 1.0]])
                        tabla = self.getTabla(itab)
                        thisPatch[extraInfo[iExtra*4]] = ('table',tabla)
                    iExtra = iExtra+1
            
            if dictDict == []:
                parsedData['boundaryField'][ipatch] = thisPatch
                parsedData.writeFile()
            else:
                dictDict['dictionaryReplacement'][ifield]['boundaryField'][ipatch] = thisPatch
                dictDict.writeFile()
                dictDictBak = ParsedParameterFile(fileDict,createZipped=False)
                keysDict = dictDict['dictionaryReplacement'].keys()
                dictDictBak['dictionaryReplacement'] = {}
                for ikey in keysDict:
                    if ikey in self.fields:
                        dictDictBak['dictionaryReplacement'][ikey] = {}
                        dictDictBak['dictionaryReplacement'][ikey]['boundaryField'] = dictDict['dictionaryReplacement'][ikey]['boundaryField']
                dictDictBak.writeFileAs('%s/system/changeDictionaryPetroSym.bak'%self.currentFolder)
                
                command = 'sed -i "s/ZZ/~/g" %s/system/changeDictionaryPetroSym.bak'%(self.currentFolder)
                os.system(command)
                
                #chequear que no bloquee
                if self.nproc<=1:
                    command = 'changeDictionary -case %s -dict %s/system/changeDictionaryPetroSym.bak 1> %s/changeDictionary.log 2> %s/error.log &'%(self.currentFolder,self.currentFolder,self.currentFolder,self.currentFolder)
                else:
                    command = 'mpirun -np %s changeDictionary -case %s -dict %s/system/changeDictionaryPetroSym.bak -parallel 1> %s/changeDictionary.log 2> %s/error.log &'%(str(self.nproc),self.currentFolder,self.currentFolder,self.currentFolder,self.currentFolder)
                os.system(command)
        self.pushButton.setEnabled(False)
        return
        
        
    def getTable(self,itab):
        table = [[0, 0],[1, 0]]
        return table
        
    def checkData(self):
        ready = True
        for itab in range(self.tabWidget.count()):
            edits = self.tabWidget.widget(itab).findChildren(QtGui.QLineEdit)
            for E in edits:
                if E.isEnabled():
                    if not E.text():
                        ready = False
        if ready:
            self.pushButton.setEnabled(True)
        else:
            self.pushButton.setEnabled(False)
            
            
    def changePatchType(self,item):
        texto = str(item.text())
        w = bcPatch(self.boundaries[texto]['type'])
        result = w.exec_()
        if result:
            patchType = w.getPatchType()
            self.boundaries[texto]['type'] = patchType
            self.boundaries.writeFile()
            
            fileDict = '%s/system/changeDictionaryPetroSym'%self.currentFolder
            dictDict = []
            if os.path.isfile(fileDict):
                dictDict = ParsedParameterFile(fileDict,createZipped=False)
                
            for ifield in self.fields:
                
                if dictDict==[]:
                    filename = '%s/%s'%(self.timedir,ifield)
                    fieldData = ParsedParameterFile(filename,listLengthUnparsed=20,createZipped=False)
                else:
                    fieldData = dictDict['dictionaryReplacement'][ifield]

                newDict = {}
                if patchType == 'empty':
                    newDict['type'] = 'empty'
                    newDict['ZZvalue'] = '0'
                else:
                    if ifield in unknowns:
                        newDict['type'] = 'zeroGradient'
                        newDict['ZZvalue'] = '0'
                    else:
                        newDict['type'] = 'calculated'
                        newDict['ZZvalue'] = '0'
                
                fieldData['boundaryField'][texto] = newDict

                if dictDict==[]:
                    fieldData.writeFile()
                else:
                    dictDict['dictionaryReplacement'][ifield] = fieldData
            
            if dictDict!=[]:
                dictDict.writeFile()
                dictDictBak = ParsedParameterFile(fileDict,createZipped=False)
                keysDict = dictDict['dictionaryReplacement'].keys()
                dictDictBak['dictionaryReplacement'] = {}
                for ikey in keysDict:
                    if ikey in self.fields:
                        dictDictBak['dictionaryReplacement'][ikey] = {}
                        dictDictBak['dictionaryReplacement'][ikey]['boundaryField'] = dictDict['dictionaryReplacement'][ikey]['boundaryField']
                dictDictBak.writeFileAs('%s/system/changeDictionaryPetroSym.bak'%self.currentFolder)
                
                command = 'sed -i "s/ZZ/~/g" %s/system/changeDictionaryPetroSym.bak'%(self.currentFolder)
                os.system(command)
                
                #chequear que no bloquee
                if self.nproc<=1:
                    command = 'changeDictionary -case %s -dict %s/system/changeDictionaryPetroSym.bak 1> %s/changeDictionary.log 2> %s/error.log &'%(self.currentFolder,self.currentFolder,self.currentFolder,self.currentFolder)
                else:
                    command = 'mpirun -np %s changeDictionary -case %s -dict %s/system/changeDictionaryPetroSym.bak -parallel 1> %s/changeDictionary.log 2> %s/error.log &'%(str(self.nproc),self.currentFolder,self.currentFolder,self.currentFolder,self.currentFolder)
                os.system(command)
            
            self.loadData()