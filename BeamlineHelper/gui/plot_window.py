#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 18:35:17 2023

@author: kai
"""
import numpy as np

from PyQt5.QtWidgets import QVBoxLayout, QWidget, QTableView, QHeaderView
from PyQt5.QtCore import pyqtSignal, Qt, QModelIndex, QRect
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas)

import BeamlineHelper as bh

class ChannelEditor(QStandardItemModel):
    checkboxStateChanged = pyqtSignal(dict)
    def __init__(self, header, preset):
        super(ChannelEditor, self).__init__()
        self._header = header
        self.plot_settings=preset
        for row in range(3): #4
            checked=preset[["x1","y","ymon"][row]] #x2 removed
            for col in range(len(header)):
                item = QStandardItem()
                item.setCheckable(True)
                if checked==header[col]:
                    item.setCheckState(Qt.Checked)
                self.setItem(row, col, item)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return None
        elif role == Qt.CheckStateRole:
            item = self.itemFromIndex(self.index(index.row(), index.column()))
            return item.checkState()
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        else:
            return super(ChannelEditor, self).data(index, role)

    def setData(self, index, value, role):
        # Set the check state of the checkbox
        item = self.itemFromIndex(self.index(index.row(), index.column()))
        if item not in [None,""] and item.isCheckable():
            item.setCheckState(value)
            self.dataChanged.emit(index, index)
            column = self._header[index.column()]
            row = ["x1","y","ymon"][index.row()] #"x2" removed
            checked = item.checkState() == Qt.Checked
            if checked:
                self.plot_settings[row]=column
            else:
                self.plot_settings[row]="None"
            self.checkboxStateChanged.emit(self.plot_settings)
            for j in range(0,self.columnCount()):
                if j!=index.column():
                    self.itemFromIndex(self.index(index.row(),j)).setCheckState(Qt.Unchecked)
                    
            print("klick")
            return True

    def rowCount(self, index=QModelIndex()):
        return 3 #4

    def columnCount(self, index=QModelIndex()):
        return len(self._header)

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole :
            if orientation == Qt.Horizontal:
                return str(self._header[section])
            if orientation == Qt.Vertical:
                out=["x1","y","ymon"] #x2 removed
                return out[section]

    def flags(self, index):  
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.AlignCenter

class RotatedHeaderView(QHeaderView):
    def __init__(self, orientation, parent=None ):
        super(RotatedHeaderView, self).__init__(orientation, parent)
        self.setMinimumSectionSize(20)

    def paintSection(self, painter, rect, logicalIndex ):
        painter.save()
        # translate the painter such that rotate will rotate around the correct point
        painter.translate(rect.x()+rect.width(), rect.y())
        painter.rotate(90)
        # and have parent code paint at this location
        newrect = QRect(0,0,rect.height(),rect.width())
        super(RotatedHeaderView, self).paintSection(painter, newrect, logicalIndex)
        painter.restore()

    def minimumSizeHint(self):
        size = super(RotatedHeaderView, self).minimumSizeHint()
        size.transpose()
        return size

    def sectionSizeFromContents(self, logicalIndex):
        size = super(RotatedHeaderView, self).sectionSizeFromContents(logicalIndex)
        size.transpose()
        return size

class MainPlotWindow(QWidget):
    def __init__(self, beamtime):
        super().__init__()
        self.beamtime = beamtime
        self.scan_list={}
        self.current_scan=None
        
        self.canvas = FigureCanvas(Figure())
        self.axis=self.canvas.figure.add_subplot()
        self.w=np.linspace(0,7,200)
        
        self.plot_setter = QTableView()
        self.plot_setter.setFixedHeight(240)
        empty = np.repeat(['                     '],17,axis=0)
        preset= {'x1':'empty','x2':'empty','y':'empty','ymon':'empty'}
        empty_model = ChannelEditor(empty,preset)
        self.plot_setter.setModel(empty_model)
        headerView = RotatedHeaderView(Qt.Horizontal)
        self.plot_setter.setHorizontalHeader(headerView)
        self.plot_setter.resizeColumnsToContents()
        
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas,stretch=1)
        layout.addWidget(self.plot_setter)
        self.setLayout(layout)
        
    def update_settings(self,plot_settings):
        # Drop off the first y element, append a new one.right_layout
        if self.current_scan:   
            command = bh.Commands(self.current_scan.command).minimize()
            commands={}
            commands[command]=plot_settings
            self.beamtime.config.edit_axis(commands)
            self.update_plot(self.current_scan,self.scan_list)
            
    def update_plot(self,current_scan,scan_list):
        # Drop off the first y element, append a new one.right_layou
        self.current_scan= current_scan
        self.scan_list=scan_list
        if self.current_scan: 
            preset = self.beamtime.config.axis_read()[bh.Commands(current_scan.command).minimize()]
            model = ChannelEditor(current_scan.longnames, preset)
            model.checkboxStateChanged.connect(self.update_settings)
            self.plot_setter.setModel(model)
            self.plot_setter.resizeColumnsToContents()
        else:
            empty = np.repeat(['                     '],17,axis=0)
            preset= {'x1':'empty','x2':'empty','y':'empty','ymon':'empty'}
            empty_model = ChannelEditor(empty,preset)
            self.plot_setter.setModel(empty_model)
            self.plot_setter.resizeColumnsToContents()
        
        self.axis.cla()
        self.axis = self.beamtime.plot(self.axis,list(scan_list.values()))
        self.canvas.draw()