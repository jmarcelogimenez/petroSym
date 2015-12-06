# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 14:34:06 2015

@author: jgimenez
"""
import matplotlib
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

class myNavigationToolbar( NavigationToolbar2QTAgg ):

    toolitems = (
        ('Home', 'Reset original view', 'zoomReset16', 'home'),
        #('Back', 'Back to  previous view', 'back', 'back'),
        #('Forward', 'Forward to next view', 'forward', 'forward'),
        #(None, None, None, None),
        ('Pan', 'Pan axes with left mouse, zoom with right', 'cursor16', 'pan'),
        ('Zoom', 'Zoom to rectangle', 'zoomToArea16', 'zoom'),
        (None, None, None, None),
        ('Subplots', 'Configure subplots', 'fit16', 'configure_subplots'),
        ('Save', 'Save the figure', 'save16', 'save_figure'),
        (None, None, None, None),
        ('Remove', 'Remove Figure', 'win_close16', 'remove'),
      )
      
    def _init_toolbar(self):
        self.coordinates = True
        self.basedir = ":/newPrefix/images/fromHelyx/" #os.path.join(matplotlib.rcParams[ 'datapath' ],'images')

        for text, tooltip_text, image_file, callback in self.toolitems:
            if text is None:
                self.addSeparator()
            else:
                a = self.addAction(self._icon(image_file + '.png'),
                                         text, getattr(self, callback))
                self._actions[callback] = a
                if callback in ['zoom', 'pan']:
                    a.setCheckable(True)
                if tooltip_text is not None:
                    a.setToolTip(tooltip_text)

        if figureoptions is not None:
            a = self.addAction(self._icon("edit16.png"),
                               'Customize', self.edit_parameters)
            a.setToolTip('Edit curves line and axes parameters')

        self.buttons = {}

        # Add the x,y location widget at the right side of the toolbar
        # The stretch factor is 1 which means any resizing of the toolbar
        # will resize this label instead of the buttons.
        if self.coordinates:
            self.locLabel = QtGui.QLabel( "", self )
            self.locLabel.setAlignment(
                    QtCore.Qt.AlignRight | QtCore.Qt.AlignTop )
            self.locLabel.setSizePolicy(
                QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                  QtGui.QSizePolicy.Ignored))
            labelAction = self.addWidget(self.locLabel)
            labelAction.setVisible(True)

        # reference holder for subplots_adjust window
        self.adj_window = None

    if figureoptions is not None:
        def edit_parameters(self):
            allaxes = self.canvas.figure.get_axes()
            if len(allaxes) == 1:
                axes = allaxes[0]
            else:
                titles = []
                for axes in allaxes:
                    title = axes.get_title()
                    ylabel = axes.get_ylabel()
                    if title:
                        fmt = "%(title)s"
                        if ylabel:
                            fmt += ": %(ylabel)s"
                        fmt += " (%(axes_repr)s)"
                    elif ylabel:
                        fmt = "%(axes_repr)s (%(ylabel)s)"
                    else:
                        fmt = "%(axes_repr)s"
                    titles.append(fmt % dict(title = title,
                                         ylabel = ylabel,
                                         axes_repr = repr(axes)))
                item, ok = QtGui.QInputDialog.getItem(self, 'Customize',
                                                      'Select axes:', titles,
                                                      0, False)
                if ok:
                    axes = allaxes[titles.index(unicode(item))]
                else:
                    return

            figureoptions.figure_edit(axes, self)

    def save_figure(self, *args):
        filetypes = self.canvas.get_supported_filetypes_grouped()
        sorted_filetypes = filetypes.items()
        sorted_filetypes.sort()
        default_filetype = self.canvas.get_default_filetype()

        startpath = matplotlib.rcParams.get('savefig.directory', '')
        startpath = os.path.expanduser(startpath)
        start = os.path.join(startpath, self.canvas.get_default_filename())
        filters = []
        selectedFilter = None
        for name, exts in sorted_filetypes:
            exts_list = " ".join(['*.%s' % ext for ext in exts])
            filter = '%s (%s)' % (name, exts_list)
            if default_filetype in exts:
                selectedFilter = filter
            filters.append(filter)
        filters = ';;'.join(filters)
        fname = _getSaveFileName(self, "Choose a filename to save to",
                                        start, filters, selectedFilter)
        if fname:
            if startpath == '':
                # explicitly missing key or empty str signals to use cwd
                matplotlib.rcParams['savefig.directory'] = startpath
            else:
                # save dir for next time
                matplotlib.rcParams['savefig.directory'] = os.path.dirname(unicode(fname))
            try:
                self.canvas.print_figure( unicode(fname) )
            except Exception as e:
                QtGui.QMessageBox.critical(
                    self, "Error saving file", str(e),
                    QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
                    
    def remove(self):
        self.window().removeFigure(self.canvas.parent())
        
    def disableButtons(self):
        for act in self._actions:
            if act != 'remove':
                self._actions[act].setEnabled(False)
        

