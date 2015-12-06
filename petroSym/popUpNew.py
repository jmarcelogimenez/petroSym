from PyQt4 import QtGui, QtCore
from popUpNew_ui import popUpNewUI
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

class popUpNew(popUpNewUI):

    def __init__(self):
        self.caselocation = ''
        self.casename = ''
        popUpNewUI.__init__(self)
        self.lineEdit_parent.setText(self.caselocation)
        self.label_case.setText(self.casename)

    def chooseFolder(self):
        posibleDir = QtGui.QFileDialog.getExistingDirectory(self, 'Case Location', self.caselocation);
        if posibleDir:
            if os.path.isdir('%s/system'%posibleDir) and os.path.isdir('%s/constant'%posibleDir):
                for button in self.buttonGroup.buttons():
                    button.setEnabled(False)                        
            else:
                for button in self.buttonGroup.buttons():
                    button.setEnabled(True)
                self.radioButton_2.setEnabled(False)
                self.radioButton_3.setEnabled(False)
            self.caselocation = str(posibleDir)
            self.lineEdit_parent.setText(os.path.dirname(self.caselocation))
            self.label_case.setText(os.path.basename(self.caselocation))


    def accept(self):
        if not self.lineEdit_parent.text():
             QtGui.QMessageBox(QtGui.QMessageBox.Critical, "Error", "Select a folder to open or create a case").exec_()
             return
             
        if self.radioButton.isEnabled() and self.buttonGroup.checkedId()==-1:
            QtGui.QMessageBox(QtGui.QMessageBox.Critical, "Error", "Select a type of simulation").exec_()
            return
            
        self.done(self.Accepted)

    def getData(self):
        if self.buttonGroup.checkedButton():
            typeSim = str(self.buttonGroup.checkedButton().text())
        else:
            typeSim = 'loaded'
        return [str(self.label_case.text()), str(self.lineEdit_parent.text()), typeSim]
        #return [self.label_case.text(), self.lineEdit_parent.text()]
    #    print "se acepta"

