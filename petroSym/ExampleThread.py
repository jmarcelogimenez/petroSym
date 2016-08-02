# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 18:01:53 2016

@author: santiago
"""

#import threading
from PyQt4.QtCore import QThread
import os
import subprocess

class ExampleThread(QThread):
    def __init__(self, cmd):
        QThread.__init__(self)
        self.cmd = cmd
        
    def __del__(self):
        return
        self.wait()
        #self.terminate()

    def run(self):
        #os.system(self.cmd)
        p=subprocess.Popen([self.cmd],shell=True)
        p.wait()