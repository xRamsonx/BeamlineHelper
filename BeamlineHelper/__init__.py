#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 11:07:30 2023

@author: kai
"""
import warnings 
warnings.simplefilter('module')
#import the standard functionalities
from BeamlineHelper.beamtime import Beamtime
from BeamlineHelper.config import Config
from BeamlineHelper.datafile import DataFile
from BeamlineHelper.plot import Plot
from BeamlineHelper.scan import Scan
from BeamlineHelper.misc import Commands
from BeamlineHelper.gui import StartWindow

#delete some aliases to make it streamlined
#del beamtime,config,datafile,plot,scan

#define __all__ for import * applications

#handle originpro for the cases that origin is not installed on the machine (eg. Linux)
try:
    #check if originpro is installed
    import originpro
    print('originpro installed')
    from BeamlineHelper.origin import OriginLoader
    __all__=['Beamtime','Config','DataFile','Plot','Scan','Commands','StartWindow','OriginLoader']
except:
    warnings.warn('\noriginpro is not installed.\nIf you want to use origin, make sure you installed origin on your machine and install originpro manualy using \'pip install originpro\' ',ImportWarning,stacklevel=2)
    __all__=['Beamtime','Config','DataFile','Plot','Scan','Commands','StartWindow']



