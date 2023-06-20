#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 18:37:11 2023

@author: kai
"""
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QTableView, QAction, QMenu
from PyQt5.QtCore import pyqtSignal, Qt, QModelIndex
from PyQt5.QtGui import QStandardItem, QStandardItemModel

class TimelineViewer(QWidget):
    scan_list_updated = pyqtSignal(object, dict)
    def __init__(self,beamtime):
        super(TimelineViewer, self).__init__()
        self.tableWidget = QTableView()
        layout = QVBoxLayout() 
        layout.addWidget(self.tableWidget)
        self.setLayout(layout)
        self.beamtime = beamtime
        self.loadData(self.beamtime)
        
        # Set the context menu policy to CustomContextMenu
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        # Connect the customContextMenuRequested signal to a slot
        self.tableWidget.customContextMenuRequested.connect(self.showContextMenu)
        self.tableWidget.clicked.connect(self.rowClicked)
        
    def loadData(self, beamtime):
        self.beamtime = beamtime
        
        data=[]
        lastFile=''
        self.row_to_scan=[]
        self.scan_plot_list={}
        
        for i,scan in enumerate(self.beamtime.config.timeline):
            if lastFile!=scan['Filename'] and lastFile:
                data.append(np.repeat([''],len(scan.values())))
                self.row_to_scan.append(-1)
            data.append(scan.values())
            self.row_to_scan.append(i)
            lastFile=scan['Filename'] 
        dataframe=pd.DataFrame(data,columns=self.beamtime.config.timeline[0].keys())
        
        model = TimelineModel(dataframe)
        model.checkboxStateChanged.connect(self.update)
        self.tableWidget.setModel(model)
        self.tableWidget.resizeColumnsToContents()
        
    def update(self, row, checked):
        if self.row_to_scan[row]!=-1:
            config=self.beamtime.config.timeline[self.row_to_scan[row]]
            scan=self.beamtime.read_file(config['Filename'])[int(config["#scan"])-1]
            scan.update(self.beamtime.config)
            if checked:
                #set current scan and update plot setter
                self.scan_plot_list[config['Filename']+'_'+config["#scan"]]=scan
                current_scan = scan
            else:
                #set current scan to None and reset plot setter
                self.scan_plot_list.pop(config['Filename']+'_'+config["#scan"])
                current_scan = None
            self.scan_list_updated.emit(current_scan,self.scan_plot_list)
            
    def getTextFromCell(self, index):
        model = self.tableWidget.model()
        if isinstance(model, QStandardItemModel):
            item = model.itemFromIndex(index)
            if item is not None:
                if item.isCheckable():
                    # Retrieve the check state of the cell
                    checkState = item.checkState()
                    return str(checkState)
        else:
            if index.isValid():
                # Retrieve the data from the cell using the model
                data = model.data(index, Qt.DisplayRole)
                if data is not None:
                    return str(data)
        return ""
    
    def setModel(self, model):
        self.tableWidget.setModel(model)
        self.tableWidget.resizeColumnsToContents()
    
    def showContextMenu(self, position):
        index = self.tableWidget.indexAt(position)
        row = index.row()
        if self.row_to_scan[row]!=-1:
            # Create the context menu
            contextMenu = QMenu(self)
            # Get the index of the selected cell
            
            # Add actions to the context menu
            change_file = QAction("Change file of scan", self)
            change_filename = QAction("Change filename", self)
            # Connect the actions to their respective slots
            change_file.triggered.connect(lambda: self.action1Clicked(index))
            
            # Add the actions to the context menu
            contextMenu.addAction(change_file)
            contextMenu.addAction(change_filename)
            # Show the context menu at the given position
            contextMenu.exec_(self.tableWidget.mapToGlobal(position))
    
    def action1Clicked(self, index):
        row = index.row()
        if self.row_to_scan[row]!=-1:
            print("Change file of scan in",row)

    def rowClicked(self, index):
        row = index.row()
        if self.row_to_scan[row]!=-1:
            print("Row", row, "clicked")
            item =self.tableWidget.model().itemFromIndex(self.tableWidget.model().index(row,0))
            checked = item.checkState() == Qt.Checked
            if checked:
                item.setCheckState(Qt.Unchecked)
            else:
                item.setCheckState(Qt.Checked)
            
            self.update(row, not checked)

class TimelineModel(QStandardItemModel):
    checkboxStateChanged = pyqtSignal(int, str, bool)
    def __init__(self, data):
        super(TimelineModel, self).__init__()
        self._data = data
        for row in range(data.shape[0]):
            if any(data.iloc[row] != ""):
                # Add a checkbox to the first column of this row
                item = QStandardItem()
                item.setCheckable(True)
                item.setEditable(False)
                self.setItem(row, 0, item)
                # Set the rest of the data in the row
                for col in range(1,data.shape[1]+1):
                    item = QStandardItem(str(data.iloc[row, col-1]))
                    self.setItem(row, col, item)

    def setData(self, index, value, role):
        #print('setData',time.perf_counter())
        if role == Qt.CheckStateRole and index.column() == 0:
            # Set the check state of the checkbox
            item = self.itemFromIndex(self.index(index.row(), 0))
            if item not in [None,""] and item.isCheckable():
                return True
        elif role == Qt.EditRole:
            self._data.iloc[index.row(), index.column()-1] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def rowCount(self, index=QModelIndex()):
        return self._data.shape[0]

    def columnCount(self, index=QModelIndex()):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole :
            if orientation == Qt.Horizontal:
                if section != 0:
                    return str(self._data.columns[section-1])
                else:
                    return str("Plot")

    def flags(self, index):
        if any(self._data.iloc[index.row()] != ""):
            if index.column() == 0:
                # Make the checkbox editable
                return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
            else:
                return Qt.ItemIsEnabled
        else:
            # Make the cell not selectable, editable or checkable
            return Qt.NoItemFlags