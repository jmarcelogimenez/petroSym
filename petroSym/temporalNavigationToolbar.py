# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 14:34:06 2015

@author: jgimenez
"""
import matplotlib
#matplotlib 1.3.1
#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg
#matplotlib 1.5.1
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT,FigureCanvasQTAgg

class NavigationToolbar2QTAgg(NavigationToolbar2QT):
    def _get_canvas(self, fig):
        return FigureCanvasQTAgg(fig)

try:
    import matplotlib.backends.qt4_editor.figureoptions as figureoptions
except ImportError:
    figureoptions = None
import os

from qt4_compat import QtCore, QtGui, _getSaveFileName, __version__
backend_version = __version__

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
        
class temporalNavigationToolbar( NavigationToolbar2QTAgg ):

    toolitems = (
        ('First', 'First Step', 'first_grey16', 'first'),
        ('Previous', 'Previous Step', 'prev_grey16', 'previous'),
        ('Play', 'Play/Pause Animation', 'start16', 'play'),
        ('Next', 'Next Step', 'next_grey16', 'proxima'),
        ('Last', 'Last Step', 'last_grey16', 'last'),
        (None, None, None, None),
        ('Refresh', 'Refresh', 'refresh16', 'refresh')
    )
      
    def _init_toolbar(self):
        self.coordinates = False
        self.basedir = ":/newPrefix/images/fromHelyx/" #os.path.join(matplotlib.rcParams[ 'datapath' ],'images')

        for text, tooltip_text, image_file, callback in self.toolitems:
            if text is None:
                self.addSeparator()
            else:
                a = self.addAction(self._icon(image_file + '.png'),
                                         text, getattr(self, callback))
                self._actions[callback] = a
                if callback in ['play']:
                    a.setCheckable(True)
                if tooltip_text is not None:
                    a.setToolTip(tooltip_text)

        
        self.display = QtGui.QLineEdit(self)
        self.display.setObjectName(_fromUtf8("display"))
        self.display.setEnabled(False)
        self.display.setText('0.00')
        self.display.setFixedWidth(50)
        self.addWidget(self.display)

    def first(self):
        print 'lastPos: %s'%self.canvas.parent().lastPos
        self.window().temporalFigure_update(self.canvas.parent(),'first')

    def previous(self):
        self.window().temporalFigure_update(self.canvas.parent(),'previous')
        
    def play(self):
        if self._actions['play'].isChecked(): 
            self.window().temporalFigure_update(self.canvas.parent(),'play')

    def proxima(self):
        self.window().temporalFigure_update(self.canvas.parent(),'next')

    def last(self):
        self.window().temporalFigure_update(self.canvas.parent(),'last')
        
    def refresh(self):
        self.window().temporalFigure_update(self.canvas.parent(),'refresh')