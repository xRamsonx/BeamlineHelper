#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 10:44:15 2023

@author: kai
"""
import numpy as np

class Plot:
    """
    Plots a the data (dictionary type) with respect to the command as
    defined in the Config class of the current datapath

    Parameters
    ----------
    data : dict
        Data as readed in from readData()

    shift : float, optional
        x-shift of the plot, if not defined it will take the value from data['Shift']

    label : str, optional
        Label of the graph in the legend

    color : str, optional
        Color of the graph,
        see https://matplotlib.org/stable/gallery/color/named_colors.html for more information

    Returns
    -------
    None
        None
    """

    def __init__(self, axis, data, axislabel, label, color):
        self.shift = data["Shift"]
        self.label = label
        self.axis = axis
        self.color = color
        self.data = data
        self.axislabel = axislabel
        self.roundn = 3
        if not "ymon" in data.keys():
            self.data["ymon"] = 1
        if not "x2" in data.keys():
            self.axis = self.plot_2d(self.axis)
        else:
            print("3d")
            self.axis = self.plot_3d(self.axis)

    def plot_2d(self, axis):
        axis.plot(
            self.data["x1"] - self.shift,
            self.data["y"]
            / self.data["ymon"]
            / np.max(self.data["y"] / self.data["ymon"]),
            label=self.label,
            color=self.color,
        )
        axis.set_xlim(
            min(self.data["x1"] - self.shift), max(self.data["x1"] - self.shift)
        )
        axis.set_ylim(-0.1, 1.1)
        axis.set_xlabel(self.axislabel["x1"])
        if not isinstance(self.data["ymon"], int):
            axis.set_ylabel(
                "$\\frac{"
                + self.axislabel["y"]
                + "}{"
                + self.axislabel["ymon"]
                + "} (Normalised)$"
            )
        else:
            axis.set_ylabel("$" + self.axislabel["y"] + "(Normalised)$")
        return axis

    def plot_3d(self, axis):
        """Plots a heatmap with the given x1, x2 and y data, e.g. rixs
        Parameters
        ----------
        x1 : list
            x1 data
        x2 : list
            x2 data
        y : list
            y data
        roundn : int
            number of floatingpoints to be displayed
        Returns
        -------
        None
            None
        """

        x_1 = self.data["x1"]
        x_2 = self.data["x2"]
        y = (
            self.data["y"]
            / self.data["ymon"]
            / np.max(self.data["y"] / self.data["ymon"])
        )
        # Setting up the correct axislabels
        yplot = [[]]
        x1label = []
        for i in x_1:
            if i not in x1label:
                x1label.append(i)
        x2label = []
        for i in x_2:
            if i not in x2label:
                x2label.append(i)

        x1label = np.round(np.array(x1label), self.roundn)
        x2label = np.round(np.array(x2label), self.roundn)
        i = 0
        x1ticks = []
        while i < len(x1label):
            x1ticks.append(i)
            i += 10
        i = 0
        x2ticks = []
        while i < len(x2label):
            x2ticks.append(i)
            i += 10
        axis.set_xticks(x1ticks)
        axis.set_xticklabels(x1label[x1ticks])
        axis.set_yticks(x2ticks)
        axis.set_yticklabels(x2label[x2ticks])
        # Bringing the data into the right format to use imshow
        j = 0
        for i in range(len(x_1)):
            if i != 0 and (x_1[i] != x_1[i - 1] and x_2[i] != x_2[i - 1]):
                yplot.append([])
                j += 1
            yplot[j].append(y[i])
        yplot = np.array(yplot).T
        # Plotting it with a correct aspect ratio
        axis.imshow(yplot, aspect=(max(x_2) - min(x_2)) / (max(x_1) - min(x_1)))

        axis.set_xlabel(self.axislabel["x1"])
        axis.set_ylabel(self.axislabel["x2"])

        if not self.axislabel["ymon"] in ("None", ""):
            axis.colorbar(
                label="$\\frac{"
                + self.axislabel["y"]
                + "}{"
                + self.axislabel["ymon"]
                + "} (Normalised)$"
            )
        else:
            axis.colorbar(
                label="$\\frac{"
                + self.axislabel["y"]
                + "}{"
                + self.axislabel["ymon"]
                + "} (Normalised)$"
            )
        return axis