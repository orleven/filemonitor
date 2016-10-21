#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'leven'

# import psyco
import os
from lib.core import arghandle
from lib.controller import controller
class Program(object):
    def __init__(self):
        self.scriptPath = os.path.dirname(os.path.realpath(__file__))
        self.arguments = arghandle.ArgHandle(self.scriptPath)
        if self.arguments .getFlag():
            self.controller = controller.Controller(self.scriptPath)
            self.controller.working()
        else:
            print "Parameter format is not correct !\nPlease look for help e.g. -h"

if __name__ == '__main__':
    Program()