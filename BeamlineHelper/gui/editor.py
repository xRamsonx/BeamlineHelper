#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 19:34:29 2023

@author: kai
"""
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QMessageBox, QComboBox, QFileDialog
from PyQt5.QtCore import pyqtSignal
import numpy as np
import sys
import subprocess
import os

import BeamlineHelper as bh

class Editor(QWidget):
    reload = pyqtSignal()
    def __init__(self, datapath,beamtime):
        super().__init__()
        self.datapath = datapath
        self.beamtime = beamtime
        edit_timeline_button = QPushButton("Edit timeline")
        edit_timeline_button.clicked.connect(self.edit_timeline)
        
        edit_collumns_button = QPushButton("Edit timeline collumns")
        edit_collumns_button.clicked.connect(self.edit_collumns)
        
        edit_axis_button = QPushButton("Edit axis")
        edit_axis_button.clicked.connect(self.edit_axis)
        
        export_to_origin_button = QPushButton("Export raw data to origin")
        export_to_origin_button.clicked.connect(self.exportToOrigin)
        
        layout = QVBoxLayout()
        layout.addWidget(edit_timeline_button)
        layout.addWidget(edit_collumns_button)
        layout.addWidget(edit_axis_button)
        layout.addStretch()
        layout.addWidget(export_to_origin_button)
        self.setLayout(layout)
        
        
    def exportToOrigin(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(
            None, "Save File", "", "Origin Notebook (*.opju)", options=options
        )
        if fileName:
            try:
                bh.OriginLoader(self.beamtime).initNotebook(self.datapath,fileName,visible=True)
            except:
                QMessageBox.critical(
                    self,
                    "Error exporting to origin",
                    "Make sure you installed originpro correctly using \n \"pip install --upgrade originpro\"",
                    buttons=QMessageBox.Cancel,
                    #defaultButton=QMessageBox.Cancel,
                )

    def edit_collumns(self):
        dlg = QMessageBox()
        dlg.setWindowTitle("Warning!")
        dlg.setText("This action will delete the current timeline!")
        dlg.setStandardButtons(QMessageBox.Ignore | QMessageBox.Ok)
        dlg.setIcon(QMessageBox.Warning)
        button = dlg.exec()
        
        if button == QMessageBox.Ok:
            self.table_header = TableHeader(self.beamtime)
            self.table_header.closed.connect(self.reload.emit)
            self.table_header.show()

    
    def edit_timeline(self):
        file=self.datapath+'/config/timeline.csv'
        if sys.platform in ('linux','linux2'):
            subprocess.call(["xdg-open", file])
        elif ('win' in sys.platform):
            os.startfile(file)
            
    def edit_axis(self):
        file=self.datapath+'/config/axis.csv'
        if sys.platform in ('linux','linux2'):
            subprocess.call(["xdg-open", file])
        elif ('win' in sys.platform):
            os.startfile(file)

class TableHeader(QWidget):
    closed = pyqtSignal()
    def __init__(self, beamtime):
        super().__init__()
        self.label_layout = QHBoxLayout()
        self.list_of_labels = []
        self.beamtime = beamtime
        self.motors = beamtime.get_all_motors()
        self.motors.append("Mask")
        self.motors.append("Data_Points")
        default=["Measurement",
                "Date",
                "Time",
                "Filename",
                "#scan",
                "Command",
                "Sampletype",
                "Sample"
                ]
        for name in default:
            self.list_of_labels.append(HeaderChoice(self.motors,text=name,editable=False))
        self.list_of_labels.append(HeaderChoice(self.motors))
        self.list_of_labels[-1].activated.connect(self.update)
        for widget in self.list_of_labels:
            self.label_layout.addWidget(widget)
            
        self.layout= QVBoxLayout()
        self.layout.addLayout(self.label_layout)
        
        accept_button=QPushButton("Save and exit")
        accept_button.clicked.connect(self.save_and_exit)
        
        self.layout.addWidget(accept_button)
        self.setLayout(self.layout)
            
    def update(self):
        if self.list_of_labels[-1].currentText()!="":
            self.list_of_labels.append(HeaderChoice(self.motors))
            self.list_of_labels[-1].activated.connect(self.update)
            self.label_layout.addWidget(self.list_of_labels[-1])
        elif self.list_of_labels[-1].currentText()==self.list_of_labels[-2].currentText()=="":
            self.label_layout.removeWidget(self.list_of_labels[-1])
            self.list_of_labels[-1].deleteLater()
            self.list_of_labels.pop(-1)
    
    def save_and_exit(self):
        list_of_collumns=[]
        for widget in self.list_of_labels:
            if widget.currentText()!="":
                list_of_collumns.append(widget.currentText())
        list_of_collumns.append("Shift")
        list_of_collumns.append("Group")
        self.beamtime.config.make(list_of_collumns,force=True)
        self.closed.emit()
        self.close()
        
class HeaderChoice(QComboBox):
    def __init__(self,motors,text="",editable=True):
        super().__init__()
        self.setEditable(editable)
        self.setInsertPolicy(QComboBox.NoInsert)
        if text:
            self.addItem(text)
            self.setCurrentText(text)
            self.setEnabled(False)
        else:
            self.addItems(np.append([""],motors))
            self.setCurrentText(text)