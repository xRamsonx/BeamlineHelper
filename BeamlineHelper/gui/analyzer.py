# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 16:39:11 2023

@author: kai.arnold@design4webs.de
"""
import numpy as np
#from scipy.optimize import curve_fit

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QAbstractSpinBox, QDoubleSpinBox, QFormLayout
from PyQt5.QtCore import pyqtSignal

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg 
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas)
import BeamlineHelper as bh

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
        
class SpinBox(QDoubleSpinBox):
    def __init__(self):
        super(SpinBox,self).__init__()
        self.setMaximum(9999.99)
        self.setMinimum(0.01)
        self.setDecimals(2)
        self.setValue(1)

class SignalToNoiseIndicator(QHBoxLayout):
    itemChanged = pyqtSignal(float,float,float,float)
    
    def __init__(self):
        super().__init__()
        self.datapoints = 0
        
        self.s2n = SpinBox()
        self.s2n.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.s2n.setReadOnly(True)
        
        self.integration = SpinBox()
        self.integration.editingFinished.connect(self.changed)
        
        self.estimated_s2n = SpinBox()
        self.estimated_s2n.editingFinished.connect(self.changed)
        
        self.estimated_integration = SpinBox()
        self.estimated_integration.editingFinished.connect(self.changed)
        
        self.measurement_time = SpinBox()
        self.measurement_time.editingFinished.connect(self.changed)
        
        self.motor_time = SpinBox()
        self.motor_time.setReadOnly(True)
        self.motor_time.setButtonSymbols(QAbstractSpinBox.NoButtons)
        
        self.expected_time = SpinBox()
        self.expected_time.setReadOnly(True)
        self.expected_time.setButtonSymbols(QAbstractSpinBox.NoButtons)
        
        
        left_layout=QFormLayout()
        left_layout.addRow("Current signal to noise:",self.s2n)
        left_layout.addRow("Integration time:",self.integration)
        left_layout.addRow("Wanted signal to noise:",self.estimated_s2n)
        left_layout.addRow("Estimated integration time:",self.estimated_integration)
        
        right_layout=QFormLayout()
        right_layout.addRow("Total measuring time [min]:",self.measurement_time)
        right_layout.addRow("Motor time [min]:",self.motor_time)
        right_layout.addRow("Expected measure time [min]:",self.expected_time)
        
        self.values=[1,1,1,1]
        self.update()
        self.addLayout(left_layout)
        self.addLayout(right_layout)
    
    
    def estimate(self,parameters):
        #calculate
        for i,value in enumerate(parameters):
            if value != self.values[i]:
                self.values[i] = value
                #only fetch one datapoint from the set values to calculate the rest
                if i!=0:
                    break
        #if not integration time changed then calculate it from the other values
        if i != 3:
            self.values[3] = self.values[1]/self.values[0] * self.values[2]
        else: # calculate the estimatet signal to noise ratio
            self.values[2] = self.values[0]/self.values[1] * self.values[3]
        self.update()
    
    def update(self):
        self.s2n.setValue(self.values[0])
        self.integration.setValue(self.values[1])
        self.estimated_s2n.setValue(self.values[2])
        self.estimated_integration.setValue(self.values[3])
    
    def changed(self):
        parameters = [self.s2n.value(),self.integration.value(),self.estimated_s2n.value(),self.estimated_integration.value()]
        self.estimate(parameters)
        self.calculate_time()
        self.itemChanged.emit(*self.values)
        
    def calculate_time(self):
        measure_time=self.integration.value() * self.datapoints / 60
        motor_time=self.measurement_time.value() - measure_time
        self.motor_time.setValue(motor_time)
        expected_measure_time=self.estimated_integration.value() * self.datapoints / 60 + motor_time 
        self.expected_time.setValue(expected_measure_time)


class SelectionPlot(QWidget):
    points_selected = pyqtSignal(list)
    def __init__(self, beamtime,scan=None):
        super(SelectionPlot, self).__init__()
        self.canvas = FigureCanvas(Figure())
        self.axis = self.canvas.figure.subplots()
        self.beamtime = beamtime
        self.scan = scan
        
        self.entered = False
        self.points = []

        self.update()

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        self.setLayout(layout)
        self.canvas.mpl_connect("axes_enter_event", self.mouse_enter)
        self.canvas.mpl_connect("axes_leave_event", self.mouse_leave)
        self.canvas.mpl_connect("button_press_event", self.mouse_click)

    def mouse_click(self, event):
        if self.entered and self.scan:
            x = event.xdata
            if all(
                np.abs(x - point) > .01
                for point in self.points
            ):
                self.points.append(x)
                if len(self.points) > 2:
                    self.points.pop(0)
                if len(self.points) == 2:
                    self.points_selected.emit(self.points)
                self.update()
            else:
                points = np.array(self.points)
                distances = np.abs(points - x)
                self.points.pop(int(np.where(distances == min(distances))[0]))
                self.update()

    def mouse_enter(self, event):
        self.entered = True

    def mouse_leave(self, event):
        self.entered = False

    def update(self):
        self.axis.cla()
        if self.scan:
            self.axis = self.beamtime.plot(self.axis,[self.scan])
            for point in self.points:
                self.axis.vlines(point, 0, 1000, "r")
            self.canvas.draw()  

class ExamplePlot(QWidget):
    def __init__(self,s2n):
        super().__init__()
        self.s2n=s2n
        self.canvas = MplCanvas(self, width=5, height=2, dpi=100)
        self.update()
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    def update(self):
        self.canvas.axes.cla()
        signal=self.noise_example(self.s2n)
        self.canvas.axes.plot(*signal)
        self.canvas.draw()
        
    def lorentz(self,w,A,w0,gamma):
        return A/((w**2-w0**2)**2+(gamma*w)**2)
        
    def noise_example(self,signal2noise):
        w= np.linspace(0,7,200)
        signal=self.lorentz(7-w,10,2,0.5) + self.lorentz(7-w,1,1.2,0.6)
        signal=signal/np.max(signal)
        count=np.random.normal(signal,1/signal2noise)
        return w,count/np.max(count)

class Analyzer(QWidget):
    def __init__(self,beamtime):
        super().__init__()
        self.status = QLabel("No scan selected")
        self.beamtime = beamtime
        self.signal_to_noise = SignalToNoiseIndicator()
        self.signal_to_noise.itemChanged.connect(self.update_s2n)
        
        self.canvas = SelectionPlot(self.beamtime)
        self.canvas.points_selected.connect(self.calculate_signal_to_noise)
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Current signal to noise"))
        header_layout.addWidget(QLabel("Estimated signal to noise"))
        
        self.current_s2n_plot = ExamplePlot(1)
        self.estimated_s2n_plot = ExamplePlot(1)
        
        example_layout = QHBoxLayout()
        example_layout.addWidget(self.current_s2n_plot)
        example_layout.addWidget(self.estimated_s2n_plot)
        
        subheader_layout = QHBoxLayout()
        subheader_layout.addWidget(QLabel("Signal to noise calculation"))
        subheader_layout.addWidget(QLabel("Measure time estimation"))
       
        layout = QVBoxLayout()
        layout.addWidget(self.status,2)
        layout.addWidget(self.canvas,30)
        layout.addLayout(header_layout,1)
        layout.addLayout(example_layout,20)
        layout.addLayout(subheader_layout,1)
        layout.addLayout(self.signal_to_noise,20)
        layout.addStretch()
        self.setLayout(layout)
    
    def update_s2n(self,s2n,integration,estimated_s2n,estimated_integration):
        self.current_s2n_plot.s2n = s2n
        self.current_s2n_plot.update()
        self.estimated_s2n_plot.s2n = estimated_s2n
        self.estimated_s2n_plot.update()
    
    def update(self,scan):
        if scan:
            self.signal_to_noise.datapoints=len(list(scan.data.values())[0])
            self.status.setText(scan.filename+":"+str(scan.scannumber)+" selected. Select the background.")
            self.canvas.scan = scan
            self.canvas.points=[]
            self.canvas.update()
        else:
            self.status = QLabel("No scan selected")
             
    def calculate_signal_to_noise(self,points):
        self.status.setText("Background selected.")
        
        boundaries = self.canvas.points
        command = bh.Commands(self.canvas.scan.command).minimize()
        x = self.canvas.scan.data[self.beamtime.config.axis[command]['x1']]
        y = self.canvas.scan.data[self.beamtime.config.axis[command]['y']]

        noise=np.std(y[(min(boundaries)<x) & (x<max(boundaries))])**2
        signal = max(y)
        #linear fit
        # def linear(x,a,b):
        #     return x*a+b
        # w_opt, w_cov = curve_fit(linear,x[(min(boundaries)<x) & (x<max(boundaries))],y[(min(boundaries)<x) & (x<max(boundaries))])
        # noise2=(w_cov[0,0]+w_cov[1,1])**0.5
        s2n = np.round(signal/noise,2)
        self.signal_to_noise.estimate([s2n,1,s2n,1])
        self.update_s2n(s2n, 1, s2n, 1)
