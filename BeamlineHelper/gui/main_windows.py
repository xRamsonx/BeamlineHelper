#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 18:24:21 2023

@author: kai
"""
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTabWidget, QSplitter
from PyQt5.QtCore import Qt

import BeamlineHelper as bh
from BeamlineHelper.gui.widgets import DragAndDropLabelwithButton
from BeamlineHelper.gui.timeline import TimelineViewer
from BeamlineHelper.gui.editor import Editor
from BeamlineHelper.gui.plot_window import MainPlotWindow
from BeamlineHelper.gui.analyzer import Analyzer

class StartWindow(QMainWindow):
    def __init__(self,app_icon):
        super().__init__()
        self.app_icon = app_icon
        
        self.setWindowIcon(app_icon)
        self.setAcceptDrops(True)
        self.setGeometry(800, 600, 600, 300)
        self.setWindowTitle('Drag and Drop Folder')
        
        self.drag_and_drop = DragAndDropLabelwithButton("the folder of your Beamtime")
        self.drag_and_drop.fileDropped.connect(self.open_beamtime_viewer)
        layout = QVBoxLayout()
        layout.addWidget(self.drag_and_drop)
        widget = QWidget()
        widget.setStyleSheet(" font-size: 12pt; ")
        widget.setLayout(layout)
        
        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)
            
    def open_beamtime_viewer(self,path):
            self.BeamtimeViewer=BeamtimeViewer(path,self.app_icon)
            self.BeamtimeViewer.setWindowTitle("BeamlineHelper")
            self.BeamtimeViewer.setGeometry(100,100,1600,800)
            self.BeamtimeViewer.show()
            self.hide()     
    
class BeamtimeViewer(QWidget):
    def __init__(self, datapath,app_icon):   
        super().__init__()
        self.setWindowIcon(app_icon)
        list_of_collums=["Measurement",
                        "Date",
                        "Time",
                        "Filename",
                        "#scan",
                        "Command",
                        "Sampletype",
                        "Sample",
                        "Data_Points",
                        "Shift",
                        "Group"
                        ]
        self.beamtime=bh.Beamtime(datapath,list_of_collums)
        
        self.currentSelection={}
        self.scan_plot_list={}
        
        self.main_plot = MainPlotWindow(self.beamtime)
        
        self.timeline = TimelineViewer(self.beamtime)
        self.timeline.scan_list_updated.connect(self.update)
        
        self.analyzer = Analyzer(self.beamtime)
        
        self.editor=Editor(datapath=datapath,beamtime=self.beamtime)
        self.editor.reload.connect(self.reload_timeline)
        
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        tabs.setMovable(True)
        tabs.addTab(self.timeline,'Timeline')
        tabs.addTab(self.analyzer,'Analyze')
        tabs.addTab(self.editor,'Edit')
        
        #Add a splitter in between to make the window adjustable
        main = QSplitter(Qt.Horizontal)
        main.addWidget(self.main_plot)
        main.addWidget(tabs)
        
        main_layout=QHBoxLayout()
        main_layout.addWidget(main)
        self.setLayout(main_layout)
    
    def reload_timeline(self):
        self.beamtime.config.reload()
        self.timeline.loadData(self.beamtime)
        self.timeline.scan_list_updated.connect(self.update)
    
    def update(self,current_scan,scan_dict):
        self.main_plot.update_plot(current_scan,scan_dict)
        self.analyzer.update(current_scan)
        
