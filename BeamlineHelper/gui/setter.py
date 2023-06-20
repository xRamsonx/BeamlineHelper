#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 20:04:36 2023

@author: kai
"""
from PyQt5.QtWidgets import QVBoxLayout, QComboBox, QFormLayout
import numpy as np


class Setter(QVBoxLayout):
    def __init__(self,beamtime):
        super().__init__()
        self.beamtime =beamtime
        self.currentSelection={}
        self.currentFile=QComboBox()
        self.currentFile.setEditable(True)
        self.currentFile.setInsertPolicy(QComboBox.NoInsert)
        self.currentFile.activated.connect(self.update)
        
        self.currentMeasurement=QComboBox()
        self.currentMeasurement.setEditable(True)
        self.currentMeasurement.setInsertPolicy(QComboBox.NoInsert)
        self.currentMeasurement.activated.connect(self.update)
        
        self.currentScantype=QComboBox()
        self.currentScantype.setEditable(True)
        self.currentScantype.setInsertPolicy(QComboBox.NoInsert)
        self.currentScantype.activated.connect(self.update)
        
        self.currentSampletype=QComboBox()
        self.currentSampletype.activated.connect(self.update)
        
        self.currentSample=QComboBox()
        self.currentSample.setEditable(True)
        self.currentSample.setInsertPolicy(QComboBox.NoInsert)
        self.currentSample.activated.connect(self.update)
        
        #self.currenStartTime=QtWidgets.QComboBox()
        #self.currenEndTime=QtWidgets.QComboBox()
        
        form = QFormLayout()
        form.addRow("File:",self.currentFile)
        form.addRow("Measurement:",self.currentMeasurement)
        form.addRow("Scantype:",self.currentScantype)
        form.addRow("Sampletype:",self.currentSampletype)
        form.addRow("Sample:",self.currentSample)
        
        self.addLayout(form)
        self.addStretch()
        
    def update(self):
        self.currentSelection={'Filename':self.currentFile.currentText(),
                     'Measurement':self.currentMeasurement.currentText(),
                     'Command':self.currentScantype.currentText(),
                     'Sampletype':self.currentSampletype.currentText(),
                     'Sample':self.currentSample.currentText()}
        restriction=list(set(self.currentSelection.values()))
        restriction.remove('')
        if restriction == []: 
            restriction=False       
        confList=self.beamtime.config.get_list(['Filename','Measurement','Command','Sampletype','Sample'], restrictions=restriction)
        self.currentFile.clear()
        self.currentFile.addItems(np.append([""],confList['Filename']))
        self.currentFile.setCurrentText(self.currentSelection['Filename'])
        self.currentMeasurement.clear()
        self.currentMeasurement.addItems(np.append([""],confList['Measurement']))
        self.currentMeasurement.setCurrentText(self.currentSelection['Measurement'])
        self.currentScantype.clear()
        self.currentScantype.addItems(np.append([""],confList['Command']))
        self.currentScantype.setCurrentText(self.currentSelection['Command'])
        self.currentSampletype.clear()
        self.currentSampletype.addItems(np.append([""],confList['Sampletype']))
        self.currentSampletype.setCurrentText(self.currentSelection['Sampletype'])
        self.currentSample.clear()
        self.currentSample.addItems(np.append([""],confList['Sample']))
        self.currentSample.setCurrentText(self.currentSelection['Sample'])
        # self.update_plot()