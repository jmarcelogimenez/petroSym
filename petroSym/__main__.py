from PyQt4 import QtGui, QtCore

#cambiar a:
from petroSym import *

import pkg_resources

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
                

def main():
    
    import sys, time
    app = QtGui.QApplication(sys.argv)
    from os import path
    pixmap = QtGui.QPixmap(path.join(path.dirname(__file__),"images/splash.png"))
    splash = QtGui.QSplashScreen(pixmap,QtCore.Qt.WindowStaysOnTopHint)
    splash.show()
    app.processEvents()
    #time.sleep(5) 
    window = petroSym()
    splash.finish(window);
    w = window.newCase()
    if not w:
        window.close()
        sys.exit()
    else:
        window.show()
        sys.exit(app.exec_())

if __name__ == '__main__':
    main()