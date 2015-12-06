# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 14:32:15 2015

@author: jgimenez
"""

from paraview.simple import *

"""Returns all views. If viewtype is specified, only the views of the
   specified type are returned"""
val = []
for aProxy in servermanager.ProxyManager().GetProxiesInGroup("views").values():
    if aProxy.IsA("vtkSMViewProxy") and \
        (viewtype is None or aProxy.GetXMLName() == viewtype):
        val.append(aProxy)
