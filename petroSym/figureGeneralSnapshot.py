# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 13:08:19 2015

@author: jgimenez
"""

from PyQt4 import QtGui, QtCore
from figureSampledLine_ui import figureSampledLineUI
import os

from myNavigationToolbar import *
from temporalNavigationToolbar import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

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

           
class figureGeneralSnapshotWidget(QtGui.QWidget):

    def __init__(self, scrollAreaWidgetContents):         
        QtGui.QWidget.__init__(self)
        self.setParent(scrollAreaWidgetContents)
        
        canvas = FigureCanvas(Figure((3.0, 2.0), dpi=100))
        canvas.setParent(self)
        toolbar = myNavigationToolbar(canvas, self)
        toolbar.disableButtons()
        temporal_toolbar = temporalNavigationToolbar(canvas, self)

        mainImage = QtGui.QLabel(self)
        mainImage.setText(_fromUtf8(""))
        mainImage.setPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/fromHelyx/emptyFigure.png")))
        mainImage.setObjectName(_fromUtf8("mainImage"))

        plotLayout = QtGui.QVBoxLayout()
        plotLayout.addWidget(temporal_toolbar)
        plotLayout.addWidget(mainImage)
        plotLayout.addWidget(toolbar)
        
        self.setLayout(plotLayout)

        canvas.setMinimumSize(canvas.size())