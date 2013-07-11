# To change this template, choose Tools | Templates
# and open the template in the editor.
# coding: utf-8
__author__="albert"
__date__ ="$7.10.2011 11:49:29$"

import inspect


class Material(object):
    
    def __init__(self):
        self.id = 0
        self.type = 0
        self.type_spec = 0.0
        self.storativity = []
        self.sorption = []
        self.dualporosity = []
        self.sorptionfraction = []
        self.geometry = []
        self.reactions = []
        
    def __str__(self):
        boring = dir(type('dummy', (object,), {}))
        it = [item
            for item in inspect.getmembers(self)
            if item[0] not in boring]
        return str(it)
    