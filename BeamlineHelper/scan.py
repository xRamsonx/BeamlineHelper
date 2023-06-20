#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 10:42:34 2023

@author: kai
"""
import numpy as np
from dateutil import parser

from BeamlineHelper.misc import Commands
from BeamlineHelper.plot import Plot

class Scan:
    """
    Class to cache and manage a single scan from an spec dataset

    Attributes
    ----------
        filename, str
            name of the file

        longnames, list
            list of all the longnames stored in the scan

        data, dict
            dictionary of all datasets stored in the scan
            with the longnames as keys

        shift, float
            energy shift of the measurement

        motor_position, dict
            dictionary of all initial motorpositions stored
            in the scan with the motors as keys

        command, str
            command used to create the scan

        measurement, str
            indicator cached from the filename,
            which states the kind of measurement e.g. (XanesL3 or RixsM4...)

        sampletype, str
            type of sample (Ref or Sa)

        sample, str
            name of sample (UF6, Ba3UO6...)

        scannumber, str
            number of this scan in the file

        date, datetime
            date of the beginning of the measurement

    """

    def __init__(self, filename, fileheader, header, data):
        # Add data
        self.filename = filename
        self.longnames = header["#L"].split()
        self.data = self.get_data(data)
        self.shift = 0
        # Add motorpositions
        self.motor_position = self.get_motorpositions(fileheader, header)
        # Getting experiment type from filename
        (
            self.command,
            self.measurement,
            self.sampletype,
            self.sample,
            self.mask,
            self.slits
        ) = self.get_experiment(header)
        self.scannumber = header["#S"].split()[0]
        self.date = parser.parse(header["#D"])

    def get_data(self, data):
        """
        Grab the datasets from the data collumns of the spec file

        Parameters
        ----------
        data : str
            respective data collumns of the spec file

        Returns
        -------
        dict
            dictionary of all datasets stored in the scan
            with the longnames as keys
        """
        dataset = {}
        for name in self.longnames:
            dataset[name] = np.array([])
        points = []
        for line in data:
            points.append(np.array(line.split(), dtype=float))
        points = np.array(points).T
        for i in range(0, len(self.longnames)):
            dataset[self.longnames[i]] = points[i]
        return dataset

    def get_motorpositions(self, fileheader, header):
        """
        Grab the initial motorpositions from the headers of the spec file

        Parameters
        ----------
        fileheader : str
            main header of the entire spec file

        header : str
            header of the scan

        Returns
        -------
        dict
            dictionary of all initial motorpositions stored
            in the scan with the motors as keys
        """
        motors = []
        positions = []
        motorpositions = {}
        for key in fileheader.keys():
            if key[:2] == "#O":
                for motor in fileheader[key].split():
                    motors.append(motor)
        for key in header.keys():
            if key[:2] == "#P":
                for position in header[key].split():
                    positions.append(position)
        for i in range(0, len(motors)):
            motorpositions[motors[i]] = positions[i]
        return motorpositions

    def get_experiment(self, header):
        """
        Grab important information from the filename

        Parameters
        ----------
        fileheader : str
            main header of the entire spec file

        header : str
            header of the scan

        Returns
        -------
        dict
            dictionary of all initial motorpositions stored
            in the scan with the motors as keys
        """
        command = " ".join(header["#S"].split()[1:])
        namedata = self.filename.replace("-", " ")
        namedata = namedata.replace("_", " ").split()
        if "-Sa-" in self.filename:
            sampletype = "Sa"
            measurement = namedata[namedata.index("Sa") - 1]
            sample = namedata[namedata.index("Sa") + 1]
        elif "-Ref-" in self.filename:
            sampletype = "Ref"
            measurement = namedata[namedata.index("Ref") -1]
            sample = namedata[namedata.index("Ref") + 1]
        else:
            sampletype = "None"
            measurement = namedata[1]
            sample = "None"
        if "Mask" in self.filename:
            mask="Yes"
        else:
            mask="None"
        if "Slit" in self.filename:
            slits="Yes"
        else:
            slits="None"
        return command, measurement, sampletype, sample, mask, slits

    def update(self, config):
        """
        Grab important information from the

        Parameters
        ----------
        fileheader : str
            main header of the entire spec file

        header : str
            header of the scan

        Returns
        -------
        dict
            dictionary of all initial motorpositions stored
            in the scan with the motors as keys
        """
        for i in range(0, len(config.timeline)):
            if (
                config.timeline[i]["Filename"] == self.filename
                and config.timeline[i]["#scan"] == self.scannumber
            ):
                break
        config_data = config.timeline[i]
        self.measurement = config_data["Measurement"]
        self.command = config_data["Command"]
        self.sampletype = config_data["Sampletype"]
        self.sample = config_data["Sample"]
        self.shift = float(config_data["Shift"])

    def plot(self, config, axis, label="", color="", plot_only_2d=False):
        scan_axis_command = Commands(self.command).minimize()
        if not any(scan_axis_command == key for key in config.axis.keys()):
            raise Exception(
                f"Error occured {scan_axis_command} is not included in axis.csv"
            )

        plot_data = {}
        axislabel = {}
        for key in config.axis[scan_axis_command].keys():
            if not config.axis[scan_axis_command][key] in ("None", ""):
                plot_data[key] = self.data[config.axis[scan_axis_command][key]]
                axislabel[key] = config.axis[scan_axis_command][key]
        plot_data["Shift"] = self.shift
        if not "x1" in plot_data.keys():
            plot_data["x1"] = list(self.data.values())[1]
            axislabel["x1"] = list(self.data.keys())[1]
        if not "y" in plot_data.keys():
            plot_data["y"] = list(self.data.values())[2]
            axislabel["y"] = list(self.data.keys())[2]
        if plot_only_2d and ("x2" in plot_data.keys()):
            return axis

        return Plot(axis, plot_data, axislabel, label, color).axis
