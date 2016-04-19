# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 04:40:26 2016

@author: santiago
"""
import unittest
from petroSym.petroSym import *
import time
import subprocess
import signal
import os

class TestOpenGui(unittest.TestCase):
   """ Test case for open_gui """
   def test_open(self):
       #Ejecuto el comando petroSym durante 4 segundos y luego lo corto
       p = subprocess.Popen(['petroSym'])
       time.sleep(4)
       #p.poll() devuelve None si tuvo exito
       assert(p.poll()==None)
       #si llego hasta aca tuvo exito, entonces lo corto
       if (p.pid):
           os.kill(p.pid, signal.SIGKILL)
       

if __name__ == '__main__':
    unittest.main()
