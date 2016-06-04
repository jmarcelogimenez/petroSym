# -*- coding: utf-8 -*-
"""
Created on Sat Apr 30 12:06:05 2016

@author: santiago
"""

from threading import Timer,Thread,Event

class perpetualTimer():

   def __init__(self,t,hFunction):
      self.t=t
      self.hFunction = hFunction
      self.thread = Timer(self.t,self.handle_function)

   def handle_function(self):
      self.hFunction()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()