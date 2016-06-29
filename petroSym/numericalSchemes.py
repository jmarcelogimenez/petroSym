# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
import sys
from numericalSchemes_ui import Ui_numericalSchemesUI
from copy import deepcopy
import os

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

ColumnWidth = 160

dicRobusto = {}

dicRobusto['ddtSchemes'] = {}
dicRobusto['ddtSchemes']['default'] = [False,'Euler','']
dicRobusto['gradSchemes'] = {}
dicRobusto['gradSchemes']['default'] = ['cellLimited','Gauss linear',1]
dicRobusto['divSchemes'] = {}
dicRobusto['divSchemes']['default'] = [False,'Gauss upwind','']
dicRobusto['divSchemes']['div(phi,U)'] = ['Gauss upwind']
dicRobusto['divSchemes']['div(phi,T)'] = ['Gauss upwind']
dicRobusto['divSchemes']['div(phi,T0)'] = ['Gauss upwind']
dicRobusto['divSchemes']['div(phi,T1)'] = ['Gauss upwind']
dicRobusto['divSchemes']['div(phi,T2)'] = ['Gauss upwind']
dicRobusto['divSchemes']['div(phi,T3)'] = ['Gauss upwind']
dicRobusto['divSchemes']['div(phi,T4)'] = ['Gauss upwind']
dicRobusto['divSchemes']['div(phi,T5)'] = ['Gauss upwind']
dicRobusto['divSchemes']['div(phi,T6)'] = ['Gauss upwind']
dicRobusto['divSchemes']['div(phi,T7)'] = ['Gauss upwind']
dicRobusto['divSchemes']['div(phi,T8)'] = ['Gauss upwind']
dicRobusto['divSchemes']['div(phi,omega)'] = ['Gauss upwind']
dicRobusto['divSchemes']['div(phi,k)'] = ['Gauss upwind']
dicRobusto['divSchemes']['div((nuEff*dev(T(grad(U)))))'] = ['Gauss linear']
dicRobusto['laplacianSchemes'] = {}
dicRobusto['laplacianSchemes']['default'] = ['','Gauss linear corrected','']
dicRobusto['interpolationSchemes'] = {}
dicRobusto['interpolationSchemes']['default'] = ['','linear','']
dicRobusto['snGradSchemes'] = {}
dicRobusto['snGradSchemes']['default'] = ['','corrected','']

dicIntermedio = {}
dicIntermedio['ddtSchemes'] = {}
dicIntermedio['ddtSchemes']['default'] = [False,'backward','']
dicIntermedio['gradSchemes'] = {}
dicIntermedio['gradSchemes']['default'] = ['none','Gauss linear',''] #deberia ir none en el primero
dicIntermedio['divSchemes'] = {}
dicIntermedio['divSchemes']['default'] = [False,'Gauss linear',''] #Ver bien este 
dicIntermedio['divSchemes']['div(phi,U)'] = ['Gauss linearUpwind grad(U)']
dicIntermedio['divSchemes']['div(phi,T)'] = ['Gauss vanLeer']
dicIntermedio['divSchemes']['div(phi,T0)'] = ['Gauss vanLeer']
dicIntermedio['divSchemes']['div(phi,T1)'] = ['Gauss vanLeer']
dicIntermedio['divSchemes']['div(phi,T2)'] = ['Gauss vanLeer']
dicIntermedio['divSchemes']['div(phi,T3)'] = ['Gauss vanLeer']
dicIntermedio['divSchemes']['div(phi,T4)'] = ['Gauss vanLeer']
dicIntermedio['divSchemes']['div(phi,T5)'] = ['Gauss vanLeer']
dicIntermedio['divSchemes']['div(phi,T6)'] = ['Gauss vanLeer']
dicIntermedio['divSchemes']['div(phi,T7)'] = ['Gauss vanLeer']
dicIntermedio['divSchemes']['div(phi,T8)'] = ['Gauss vanLeer']
dicIntermedio['divSchemes']['div(phi,omega)'] = ['Gauss upwind']
dicIntermedio['divSchemes']['div(phi,k)'] = ['Gauss upwind']
dicIntermedio['divSchemes']['div((nuEff*dev(T(grad(U)))))'] = ['Gauss linear']
dicIntermedio['laplacianSchemes'] = {}
dicIntermedio['laplacianSchemes']['default'] = ['','Gauss linear corrected','']
dicIntermedio['interpolationSchemes'] = {}
dicIntermedio['interpolationSchemes']['default'] = ['','linear','']
dicIntermedio['snGradSchemes'] = {}
dicIntermedio['snGradSchemes']['default'] = ['','corrected','']

dicAltoOrden = {}
dicAltoOrden['ddtSchemes'] = {}
dicAltoOrden['ddtSchemes']['default'] = [False,'CrankNicolson',1]
dicAltoOrden['gradSchemes'] = {}
dicAltoOrden['gradSchemes']['default'] = ['none','Gauss linear',''] #deberia ir none en el primero
dicAltoOrden['divSchemes'] = {}
dicAltoOrden['divSchemes']['default'] = [False,'Gauss linear',''] #Ver bien este 
dicAltoOrden['divSchemes']['div(phi,U)'] = ['Gauss linearUpwind grad(U)']
dicIntermedio['divSchemes']['div(phi,T)'] = ['Gauss vanLeer']
dicIntermedio['divSchemes']['div(phi,T0)'] = ['Gauss vanLeer']
dicIntermedio['divSchemes']['div(phi,T1)'] = ['Gauss vanLeer']
dicIntermedio['divSchemes']['div(phi,T2)'] = ['Gauss vanLeer']
dicIntermedio['divSchemes']['div(phi,T3)'] = ['Gauss vanLeer']
dicIntermedio['divSchemes']['div(phi,T4)'] = ['Gauss vanLeer']
dicIntermedio['divSchemes']['div(phi,T5)'] = ['Gauss vanLeer']
dicIntermedio['divSchemes']['div(phi,T6)'] = ['Gauss vanLeer']
dicIntermedio['divSchemes']['div(phi,T7)'] = ['Gauss vanLeer']
dicIntermedio['divSchemes']['div(phi,T8)'] = ['Gauss vanLeer']
dicAltoOrden['divSchemes']['div(phi,omega)'] = ['Gauss linearUpwind default']
dicAltoOrden['divSchemes']['div(phi,k)'] = ['Gauss linearUpwind default']
dicAltoOrden['divSchemes']['div((nuEff*dev(T(grad(U)))))'] = ['Gauss linear']
dicAltoOrden['laplacianSchemes'] = {}
dicAltoOrden['laplacianSchemes']['default'] = ['','Gauss linear corrected','']
dicAltoOrden['interpolationSchemes'] = {}
dicAltoOrden['interpolationSchemes']['default'] = ['','linear','']
dicAltoOrden['snGradSchemes'] = {}
dicAltoOrden['snGradSchemes']['default'] = ['','corrected','']

dicSchemes = {}
dicSchemes = ['ddtSchemes','gradSchemes','divSchemes','laplacianSchemes','interpolationSchemes','snGradSchemes']


#Primer termino: lugar del string en el que va (Si aparece)
#Ver si es recomendable que en el caso de los chb aparezca un término mas que es el string que va (Por ahora solo bounded)
dicAvanzadas = {}
dicAvanzadas['ddtSchemes'] = {}
dicAvanzadas['ddtSchemes']['solver'] = [0,2,3] #Primer termino: fila en la que va #Segundo termino cantidad de parametros (Que siempre estan) #Tercer termino cantidad de parametros (Que pueden o no estar)
dicAvanzadas['ddtSchemes'][0] = [1,'Time: ',2,'ddtSchemes',3,['Euler','CrankNicolson','backward'],ColumnWidth]
dicAvanzadas['ddtSchemes'][1] = [0,'Bounded: ',3,'chb_ddtSchemes_bounded']
dicAvanzadas['ddtSchemes']['CrankNicolson'] = {}
dicAvanzadas['ddtSchemes']['CrankNicolson']['solver'] = ['CrankNicolson',1]
dicAvanzadas['ddtSchemes']['CrankNicolson'][0] = [2,'Blending: ',0,'line_ddtSchemes_blending',"-?\d+\.?\d*e-?\d+",1]

dicAvanzadas['gradSchemes'] = {}
dicAvanzadas['gradSchemes']['solver'] = [1,2,3]
dicAvanzadas['gradSchemes'][0] = [1,'Gradient: ',2,'gradSchemes',5,['Gauss linear','Gauss cubic','Gauss midPoint', 'leastSquares', 'fourth'],ColumnWidth]
dicAvanzadas['gradSchemes'][1] = [0,'Limiting Scheme: ',2,'gradSchemes',3,['none','cellLimited','faceLimited'],ColumnWidth-68]
dicAvanzadas['gradSchemes']['cellLimited'] = {}
dicAvanzadas['gradSchemes']['cellLimited']['solver'] = ['cellLimited',1]
dicAvanzadas['gradSchemes']['cellLimited'][0] = [2,'Coefficient: ',0,'line_gradSchemes_celllim_coeff',"-?\d+\.?\d*e-?\d+",1]
dicAvanzadas['gradSchemes']['faceLimited'] = {}
dicAvanzadas['gradSchemes']['faceLimited']['solver'] = ['faceLimited',1]
dicAvanzadas['gradSchemes']['faceLimited'][0] = [2,'Coefficient: ',0,'line_gradSchemes__fecelim_coeff',"-?\d+\.?\d*e-?\d+",1]

dicAvanzadas['divSchemes'] = {}
dicAvanzadas['divSchemes']['solver'] = [2,2,3]
dicAvanzadas['divSchemes'][0] = [1,'Convection: ',2,'divSchemes',7,['Gauss upwind','Gauss linearUpwind','Gauss linear','Gauss limitedLinear','Gauss QUICK','Gauss vanLeer','Gauss MUSCL'],ColumnWidth]
dicAvanzadas['divSchemes'][1] = [0,'Bounded: ',3,'chb_divSchemes_bounded']
dicAvanzadas['divSchemes']['Gauss limitedLinear'] = {}
dicAvanzadas['divSchemes']['Gauss limitedLinear']['solver'] = ['Gauss limitedLinear',1]
dicAvanzadas['divSchemes']['Gauss limitedLinear'][0] = [2,'Value: ',0,'line_divSchemes_limitedlinear',"-?\d+\.?\d*e-?\d+",1]

dicAvanzadas['laplacianSchemes'] = {}
dicAvanzadas['laplacianSchemes']['solver'] = [3,2,2]
dicAvanzadas['laplacianSchemes'][0] = [0,'Laplacian: ',2,'laplacianSchemes',4,['Gauss linear corrected','Gauss linear uncorrected','Gauss linear limited','Gauss linear orthogonal'],ColumnWidth+3]
dicAvanzadas['laplacianSchemes'][1] = ['','',-1,'',-1,'',-1]
dicAvanzadas['laplacianSchemes']['Gauss linear limited'] = {}
dicAvanzadas['laplacianSchemes']['Gauss linear limited']['solver'] = ['Gauss linear limited',1]
dicAvanzadas['laplacianSchemes']['Gauss linear limited'][0] = [1,'Value: ',0,'line_lapSchemes_linearlimited',"-?\d+\.?\d*e-?\d+",1]

dicAvanzadas['interpolationSchemes'] = {}
dicAvanzadas['interpolationSchemes']['solver'] = [4,1,1]
dicAvanzadas['interpolationSchemes'][0] = [0,'Interpolation: ',2,'interpolationSchemes',3,['linear','cubic','midPoint'],ColumnWidth]

dicAvanzadas['snGradSchemes'] = {}
dicAvanzadas['snGradSchemes']['solver'] = [5,2,2]
dicAvanzadas['snGradSchemes'][0] = [0,'snGradient: ',2,'snGradSchemes',7,['corrected','uncorrected','limited','orthogonal','faceCorrected','linearFit','quadraticFit'],ColumnWidth]
dicAvanzadas['snGradSchemes'][1] = ['','',-1,'',-1,'',-1]
dicAvanzadas['snGradSchemes']['limited'] = {}
dicAvanzadas['snGradSchemes']['limited']['solver'] = ['limited',1]
dicAvanzadas['snGradSchemes']['limited'][0] = [1,'Value: ',0,'line_lapSchemes_limited',"-?\d+\.?\d*e-?\d+",0.5]
dicAvanzadas['snGradSchemes']['linearFit'] = {}
dicAvanzadas['snGradSchemes']['linearFit']['solver'] = ['linearFit',1]
dicAvanzadas['snGradSchemes']['linearFit'][0] = [1,'Value: ',0,'line_lapSchemes_linearFit',"-?\d+\.?\d*e-?\d+",1]
dicAvanzadas['snGradSchemes']['quadraticFit'] = {}
dicAvanzadas['snGradSchemes']['quadraticFit']['solver'] = ['quadraticFit',1]
dicAvanzadas['snGradSchemes']['quadraticFit'][0] = [1,'Value: ',0,'line_lapSchemes_quadraticFit',"-?\d+\.?\d*e-?\d+",1]


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


class numericalSchemesUI(QtGui.QScrollArea, Ui_numericalSchemesUI):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QScrollArea.__init__(self, parent)

        self.setupUi(self)
        
class numericalSchemes(numericalSchemesUI):

    def __init__(self,folder):
        self.currentFolder = folder
        numericalSchemesUI.__init__(self)
        self.loadData()
        self.addTabs()
        
        if ('schemeType' not in self.parsedData.content.keys()): #Si no existe (nunca abrio al gui) la creo
            self.parsedData['schemeType'] = {}            
            self.parsedData['schemeType']='Custom'
            
        schemeType = self.parsedData['schemeType']
        Index = 0 if schemeType=='Robust' else 1 if schemeType=='Intermediate' else 2 if schemeType==['High', 'Order'] else 3 if schemeType=='Custom' else -1
        self.cb_basic_options.setCurrentIndex(Index)
        self.pushButton.setEnabled(False)
        
        self.grid_avanzada.setColumnMinimumWidth(0, 10)        
        self.grid_avanzada.setColumnMinimumWidth(1, 10)        
        self.grid_avanzada.setColumnMinimumWidth(2, 10)
        self.grid_avanzada.setColumnStretch(0,60)
        self.grid_avanzada.setAlignment(QtCore.Qt.AlignLeft)
        
    def addTabs(self):
        
        for keys1 in dicSchemes:
            for keys2 in range(0,dicAvanzadas[keys1]['solver'][1]):
                self.generateItems(dicAvanzadas[keys1][keys2],self.grid_avanzada,keys2,dicAvanzadas[keys1]['solver'][0],keys1)

    def loadData(self):
        filename = '%s/system/fvSchemes'%self.currentFolder
        self.parsedData = ParsedParameterFile(filename,createZipped=False)
        
        return
        
    def onChangeSomething(self):
        self.pushButton.setEnabled(True)
        
        if (sys._getframe().f_back.f_code.co_name != 'onChangeSomething3'):    
            cb = self.groupBox1.findChild(QtGui.QComboBox,'cb_basic_options')
            Index = 3
            cb.setCurrentIndex(Index)
            
            
    def onChangeSomething2(self):
        sender = self.sender() #La cb que la activo
        scheme = sender.objectName()
        scheme = unicode(scheme)
        
        #Si existe un item en la columna 2 (Los opcionales) borrarlo, total si existe para otro scheme se va a crear de nuevo abajo        
        row = dicAvanzadas[scheme]['solver'][0]
        item = self.grid_avanzada.itemAtPosition(row,2)
        if item:
            if (scheme!='gradSchemes') or ((scheme=='gradSchemes') and (sender.currentText() not in dicAvanzadas['gradSchemes'][0][5])):
                self.clearLayout(item,0)
                self.grid_avanzada.removeItem(item)
        
        for keys1 in dicAvanzadas[scheme].keys():
            
            if keys1 == sender.currentText():
                for keys2 in range(0,dicAvanzadas[scheme][keys1]['solver'][1]):
                    self.generateItems(dicAvanzadas[scheme][keys1][keys2],self.grid_avanzada,keys2+dicAvanzadas[scheme]['solver'][1],dicAvanzadas[scheme]['solver'][0],scheme)
                return
                
    def onChangeSomething3(self):
        self.pushButton.setEnabled(True)
        sender = self.sender()
        
        CurrentIndex = sender.currentIndex()
        if (CurrentIndex==0):
            dic = dicRobusto
        elif (CurrentIndex==1):
            dic = dicIntermedio
        elif (CurrentIndex==2):
            dic = dicAltoOrden
        else: 
            if (sys._getframe().f_back.f_code.co_name != 'onChangeSomething'): #Si no vine desde onchangesomething (Osea cuando modifico un widget cualquiera)
                self.setCustom() #Aca va la logica de lectura para custom
            return
        
        for keys in dicSchemes:
            layH = self.grid_avanzada.findChild(QtGui.QHBoxLayout,keys+str(0))
            cb = layH.itemAt(1).widget()
            for i in range(cb.count()):
                if (dic[keys]['default'][1]==cb.itemText(i)):
                    cb.setCurrentIndex(i)
                    break
            if (dic[keys]['default'][0]!=''):
                layH = self.grid_avanzada.findChild(QtGui.QHBoxLayout,keys+str(1))
                if layH:
                    widget = layH.itemAt(1)
                    if widget:
                        widget = widget.widget()
                        name = widget.staticMetaObject.className()
                        if (name == 'QCheckBox'):
                            widget.setChecked(dic[keys]['default'][0])
                        elif (name == 'QComboBox'):
                            for i in range(widget.count()):
                                if (widget.itemText(i)==dic[keys]['default'][0]):
                                    widget.setCurrentIndex(i)
                                
            if (dic[keys]['default'][2]!=''):
                layH = self.grid_avanzada.findChild(QtGui.QHBoxLayout,keys+str(2))
                if layH:
                    widget = layH.itemAt(1)
                    if widget:
                        widget = widget.widget()
                        name = widget.staticMetaObject.className()
                        if (name == 'QLineEdit'):
                            widget.setText(str(dic[keys]['default'][2]))

    def clearLayout(self, layout, dejar):
        for i in reversed(range(layout.count())):
            if i>= dejar:
                item = layout.itemAt(i)
        
                if isinstance(item, QtGui.QWidgetItem):
                    item.widget().close()
                    item.widget().deleteLater()
                elif isinstance(item, QtGui.QSpacerItem):
                    None
                else:
                    self.clearLayout(item.layout(),0)
                
                layout.removeItem(item)    
        

    def aplicar(self):
    
        currentIndex=self.cb_basic_options.currentIndex()
        dicGuardar = {}
        dicGuardar=dicRobusto if (currentIndex==0) else dicIntermedio if (currentIndex==1) else dicAltoOrden if (currentIndex==2) else {}
        
        if dicGuardar != {}: #Si entro por un basic
            keysdic = dicGuardar.keys()
            keysdivSchemes = dicGuardar['divSchemes'].keys()
            keysdivSchemes.remove('default')
            for keys in keysdic:
                    data = ''
                    keys = unicode(keys)
                    if (type(dicGuardar[keys]['default'][0]) is bool):
                        data=data+'bounded ' if dicGuardar[keys]['default'][0]==True else ''
                    else:
                        if dicGuardar[keys]['default'][0]!='none' and dicGuardar[keys]['default'][0]!='':
                            data=data+dicGuardar[keys]['default'][0]
                            data=data+' '
                        
                    data=data+dicGuardar[keys]['default'][1]
                    if (dicGuardar[keys]['default'][2] != ''):
                        data=data+' '+str(dicGuardar[keys]['default'][2])
                    
                    self.parsedData[unicode(keys)]['default'] = data
                    
            for keys in keysdivSchemes:
                if keys not in self.parsedData['divSchemes'].keys():
                    self.parsedData['divSchemes'][keys] = {}
                self.parsedData['divSchemes'][unicode(keys)] = dicGuardar['divSchemes'][keys][0]
        
        else: #Si entro por un advanced
            keysdic = dicAvanzadas.keys()
            for keys in keysdic:
                data = {}
                keys = unicode(keys)
                for i in range(dicAvanzadas[keys]['solver'][1]): #Son 3 columnas
                    layoutH = self.grid_avanzada.findChild(QtGui.QHBoxLayout,keys+str(i))
                    pos = dicAvanzadas[keys][i][0]
                    if (not layoutH): 
                        continue
                    widget = layoutH.itemAt(1)
                    if (not widget): 
                        continue
                    widget= widget.widget()
                    name = widget.staticMetaObject.className()
                    if (name == 'QComboBox'):
                        if widget.currentText()=='none':
                            data[pos] = ''
                        else:
                            data[pos] = str(widget.currentText())
                        if (widget.currentText() in dicAvanzadas[keys].keys()):
                            for i in range(dicAvanzadas[keys][str(widget.currentText())]['solver'][1]):
                                layoutH = self.grid_avanzada.findChild(QtGui.QHBoxLayout,keys+'2') #3 columna, los opcionales
                                widgetN = layoutH.itemAt(1).widget()
                                if (widgetN.text()==''):
                                    widgetN.setText(str(dicAvanzadas[keys][str(widget.currentText())][i][5]))
                                pos = dicAvanzadas[keys][str(widget.currentText())][i][0]
                                data[pos] = widgetN.text()
                    elif (name == 'QCheckBox'):
                        if widget.isChecked():
                            data[pos] = 'Bounded'
                    elif (name == 'QLineEdit'):
                        data[pos] = widget.text()
                    
                strr = " ".join(str(v) for v in data.itervalues())
                self.parsedData[unicode(keys)]['default'] = strr
            
        self.parsedData['schemeType'] = str(self.cb_basic_options.currentText())
        self.parsedData.writeFile()
        
        self.pushButton.setEnabled(False)
        return

    def editar(self):
        command = 'gedit %s/system/fvSchemes &'%self.currentFolder
        os.system(command)
        return

    """
    Función generateItems()
    
    dic: Diccionario del cual se sacarán los datos para generar cada campo particular dentro del layout vertical.
    layoutV: Layout vertical al cual se agregará el layout horizontal generado en la función.
    ifield: Entero que se utiliza para ir llevando la cuenta del lugar que ocupará el campo en el GridLayout.
    
    Descripción:
    Función que crea un layout horizontal que tiene como estructura un string a la izquierda, y un objeto identificado por el tipo a la derecha.
    Luego agrega ese layout horizontal al layout vertical dado.
    
    """
                
    def generateItems(self, dic, layoutV, column, row, scheme):
        
        layoutH = QtGui.QHBoxLayout()
        textlabel = QtGui.QLabel()
        textlabel.setText(dic[1])
        layoutH.addWidget(textlabel)
        textlabel.setFixedWidth(ColumnWidth-55)
        #textlabel.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        tipo = dic[2] 
        layoutH.setObjectName(scheme+str(column))
        
        if tipo==0:
            line = QtGui.QLineEdit()
            line.setObjectName(dic[3])
            rx = QtCore.QRegExp(dic[4])
            validator = QtGui.QRegExpValidator(rx,line)
            line.setValidator(validator)
            line.setText(str(dic[5]))
            line.setFixedWidth(ColumnWidth-100)
            layoutH.addWidget(line)
            QtCore.QObject.connect(line, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.onChangeSomething)
        elif tipo==1:
            spin = QtGui.QSpinBox()
            spin.setObjectName(dic[3])
            layoutH.addWidget(spin)
            spin.setFixedWidth(ColumnWidth-100)
            QtCore.QObject.connect(spin, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.onChangeSomething)
        elif tipo==2:
            cb = QtGui.QComboBox()
            cb.setObjectName(dic[3])
            cb.addItems(dic[5])
            layoutH.addWidget(cb)            
            QtCore.QObject.connect(cb, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.onChangeSomething)
            if dic[3] in dicSchemes:
                QtCore.QObject.connect(cb, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.onChangeSomething2)            
            cb.setFixedWidth(dic[6])
            cb.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        elif tipo==3:
            cbox = QtGui.QCheckBox()
            cbox.setObjectName(dic[3])
            layoutH.addWidget(cbox)
            QtCore.QObject.connect(cbox, QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), self.onChangeSomething)
        
        layoutV.addLayout(layoutH,row,column)
        
    def setCustom(self):
        keys1 = self.parsedData.content.keys()
        dicPrimeras = ['none','cellLimited','faceLimited','Bounded']
        for key1 in keys1:
            if key1 not in dicSchemes:
                continue
            parsedData = deepcopy(self.parsedData[key1]['default'])
            
            import PyFoam
            if type(parsedData) is PyFoam.Basics.DataStructures.BoolProxy: #Error de booleanProxy (?)
                parsedData=str(parsedData)
            
            if (type(parsedData) is str):
                parsedData = parsedData.split()
            
            cantParam = dicAvanzadas[key1]['solver'][2]
            data = list()
            data.insert(0,'') 
            data.insert(1,'') 
            data.insert(2,'')
            if cantParam==1:
                data[0]= parsedData[0]
            elif cantParam==2:
                if (type(parsedData) is str):
                    data[0]=parsedData
                else:
                    if self.RepresentsInt(parsedData[len(parsedData)-1]):
                        data[1]=parsedData[len(parsedData)-1]
                        parsedData.remove(parsedData[len(parsedData)-1])
                    data[0]=" ".join(str(v) for v in parsedData)
            elif cantParam==3:
                if (type(parsedData) is str):
                    data[1]=parsedData
                else:
                    if (parsedData[0] in dicPrimeras):
                        data[0]=parsedData[0]
                        parsedData.remove(parsedData[0])
                    if len(parsedData)>1:
                        if self.RepresentsInt(parsedData[len(parsedData)-1]):
                            data[2]=parsedData[len(parsedData)-1]
                            parsedData.remove(parsedData[len(parsedData)-1])
                    data[1]=" ".join(str(v) for v in parsedData)
            
            for i in range(0,2):
                if (type(data[i]) is not str): #Error de booleanProxy (?)
                    data[i]=str(data[i])
            #print data
            for i in range(dicAvanzadas[key1]['solver'][1]): #Son 3 columnas
                layoutH = self.grid_avanzada.findChild(QtGui.QHBoxLayout,key1+str(i))
                pos = dicAvanzadas[key1][i][0]
                
                if (not layoutH): 
                    continue
                widget = layoutH.itemAt(1)
                if (not widget): 
                    continue
                widget= widget.widget()                
                text = data[pos]
                name = widget.staticMetaObject.className()
                if (name == 'QComboBox'):
                    text=text.strip()
                    index = widget.findText(text)
                    if index>=0:                    
                        widget.setCurrentIndex(index)
                    if (text in dicAvanzadas[key1].keys()):
                        for i in range(dicAvanzadas[key1][text]['solver'][1]):
                            layoutH = self.grid_avanzada.findChild(QtGui.QHBoxLayout,key1+'2') #3 columna, los opcionales
                            widgetN = layoutH.itemAt(1).widget()
                            pos = dicAvanzadas[key1][text][i][0]
                            text=data[pos]
                            widgetN.setText(str(text))
                elif (name == 'QCheckBox'):
                    if text == 'Bounded':
                        widget.setChecked(True)
                elif (name == 'QLineEdit'):
                        if text!='':                        
                            widget.setText(str(text))
                        
    def RepresentsInt(self,s):
            if type(s) is not str:
                s = str(s)
            if s.replace('.', '').isdigit():
                return True
            else:
                return False