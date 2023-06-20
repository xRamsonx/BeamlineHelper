#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 10:38:23 2023

@author: kai
"""
import os
import numpy as np
import warnings

from BeamlineHelper.datafile import DataFile
from BeamlineHelper.misc import Commands

class Config:
    """
    Class to create and manage a cache of important data from the beamtime.
    It creates 3 datafiles in datapath/config
    containing information about plotting, scans and edge data.

    Attributes
    ----------
        datapath
            absolute path to the file storing the measurement data
    """

    def __init__(self, datapath, list_of_collumns):
        self.datapath = datapath
        self.make(list_of_collumns)

        self.axis = self.axis_read()
        self.edges = self.csv_read("edges.csv", 6)
        self.timeline = self.csv_read("timeline.csv", 11)

    def reload(self):
        """
        reload the csv files
        ----------
        None
            None

        Returns
        -------
        None
            None
        """

        self.axis = self.axis_read()
        self.edges = self.csv_read("edges.csv", 6)
        self.timeline = self.csv_read("timeline.csv", 11)

    def make(self, list_of_collumns, ignore=[], force=False):
        """
        Creates the timeline.csv, axis.csv and edges.csv files of the current datapath
        if they don't exist yet or force is specified.
        Parameters
        ----------
        ignore : list, optional
            List containing all the substrings of the datafiles you want to
            completely ignore, e.g. 'align' or 'test' (Default is [])
            shutil.copyfile('src/edges.csv', path +'edges.csv')
        force : boolean, optional
            True if you want to overwrite all the .csv files (Default is False)
        readable : boolean, optional
            True if you want to have spaces between different files for better
            readability (Default is False)

        Returns
        -------
        None
            None
        """
        if not os.path.exists(self.datapath + "/config"):
            os.mkdir(self.datapath + "/config")

        if not os.path.exists(self.datapath + "/config/timeline.csv") or force:
            self.make_timeline(list_of_collumns=list_of_collumns, ignore=ignore)
        if not os.path.exists(self.datapath + "/config/axis.csv") or force:
            self.make_axis(ignore=ignore)
        if not os.path.exists(self.datapath + "/config/edges.csv") or force:
            self.make_edge()
        else:
            self.clean()
            print("Config already exists. To overwrite it, use the argument force=True")

    def clean(self):
        """
        Cleans the timeline.csv of the current datapath by removing anything
        written between the lines

        Parameters
        ----------
        None
            None

        Returns
        -------
        None
            None
        """
        lines = []
        first = True
        path = self.datapath + "/config"
        if not os.path.exists(path + "/timeline.csv"):
            raise Exception(
                "No timeline.csv available.\n Use make_conf first and edit the timeline.csv file"
            )
        with open(path + "/timeline.csv", encoding="UTF-8") as datafile:
            for line in datafile:
                content = line.replace(",", " ")
                content = content.replace(";", " ")
                content = content.strip()
                if first:
                    first = False
                    length = len(line.split())
                if len(content.split()) < length:
                    lines.append(length * ";" + "\n")
                else:
                    newline = line.replace(",", ";")
                    lines.append(newline)
        with open(path + "timeline.csv", "w", encoding="UTF-8") as datafile:
            for line in lines:
                datafile.write(line)

    def make_axis(self, ignore):
        """
        Creates an axis.csv file containing the information about
        which commands correspond to which axis to plot

        Parameters
        ----------
        None
            None

        Returns
        -------
        None
            None
        """
        path = self.datapath + "/config"
        data = self.read_all_raw(ignore=ignore)
        commands = []

        out = [["Command", "x1", "x2", "y", "ymon"]]
        for scan in data:
            command = Commands(scan.command)
            if not command.minimize() in commands:
                commands.append(command.minimize())
                out.append([command.minimize(), "", "", "", ""])
                motorlist = command.get_motors(scan.longnames)
                for i, motor in enumerate(motorlist):
                    out[-1][i + 1] = motor
                if "APD" in scan.longnames:
                    out[-1][3] = "APD"
                elif "Detector" in scan.longnames:
                    out[-1][3] = "Detector"
        np.savetxt(path + "/axis.csv", out, delimiter=";", fmt="%s")

    def make_edge(self):
        """
        Creates an edges.csv file containing the information about
        important spectral edges

        Parameters
        ----------
        None
            None

        Returns
        -------
        None
            None
        """
        print("Making edge.csv")
        path = self.datapath + "/config"
        out = [["Sample", "Edge", "Energy"], ["LaOx", "xasLaL2", "5.89060"]]
        np.savetxt(path + "/edges.csv", out, delimiter=";", fmt="%s")

    def make_timeline(self, list_of_collumns, ignore, readable=True):
        """
        Creates an timeline.csv file containing the information
        about the measurements

        Parameters
        ----------
        None
            None

        Returns
        -------
        None
            None
        """
        print("Making timeline.csv")
        all_data = self.read_all_raw(ignore=ignore)
        all_data.sort(key=lambda item: item.date)
        out = []
        out.append(list_of_collumns)
        empty = []
        for name in list_of_collumns:
            empty.append("")
        last_file = all_data[0].filename
        last_measurement = ""
        group_list = {}
        for scan in all_data:
            if readable and last_file != scan.filename:
                out.append(empty)
                if last_measurement != scan.measurement:
                    out.append(empty)
            if not scan.measurement in group_list.keys():
                group_list[scan.measurement] = 1
            if last_measurement not in (scan.measurement, ""):
                group_list[last_measurement] += 1

            alias = {
                "Measurement": scan.measurement,
                "Date": scan.date.strftime("%d-%m-%Y"),
                "Time": scan.date.strftime("%H:%M:%S"),
                "Filename": scan.filename,
                "#scan": scan.scannumber,
                "Command": scan.command,
                "Sampletype": scan.sampletype,
                "Sample": scan.sample,
                "Mask": scan.mask,
                "Slits": scan.slits,
                "Data_Points": str(len(scan.data[scan.longnames[0]])),
                "Shift": "0",
                "Group": group_list[scan.measurement],
            }
            row = []
            for name in list_of_collumns:
                if name == "slits":
                    if "slit_small1" in scan.motor_position.keys():
                        if (
                            float(scan.motor_position["slit_small1"]) < 1
                            or float(scan.motor_position["slit_small2"]) < 1
                        ):
                            slits = "no"
                        else:
                            slits = "yes"
                    else:
                        slits = "?"
                        warnings.warn("Warning:" + scan.filename + ":No Slit data")
                    row.append(slits)
                elif name in alias.keys():
                    row.append(alias[name])
                elif name in scan.motor_position.keys():
                    row.append(scan.motor_position[name])
                else:
                    row.append("")
            out.append(row)
            last_measurement = scan.measurement
            last_file = scan.filename
        np.savetxt(self.datapath + "/config/timeline.csv", out, delimiter=";", fmt="%s")

    def read_all_raw(self, ignore=["Nothing"]):
        """
        Reads in all datafiles from the datapath
        Parameters
        ----------
        ignore : list
            List containing all the substrings of the datafiles you want
            to completely ignore, e.g. 'align' or 'test'.
        Returns
        -------
        list
            A list containing all the dictionaries for each datafile
        """
        all_data = []
        for root, directories, files in os.walk(self.datapath):
            for file in files:
                if (
                    root == self.datapath
                    and not ("." in file)
                    and not any([name in file for name in ignore])
                ):
                    data = DataFile(self.datapath, file).read_raw()
                    if data:
                        for point in data:
                            all_data.append(point)
        return all_data

    def write(self, conf_data):
        """
        Uses the input config-data to overwrite the current timeline.csv file
        of the current datapath  with the new data
        Parameters
        ----------
        ignore : list
            List containing the config-data in the format of read_conf()
        Returns
        -------
        None
            None
        """
        i = 0
        first = True
        lines = []
        path = self.datapath + "/config"
        with open(self.datapath + "/config/timeline.csv", encoding="UTF-8") as datafile:
            for line in datafile:
                content = line.replace('"', "").strip()
                if first:
                    content = line.replace(" ", "")
                    delimiter = content[11]
                    # cover for empty fields
                for i in range(0, 10):
                    content = content.replace(
                        2 * delimiter, delimiter + "None" + delimiter
                    )

                # set up the split
                content = content.replace(delimiter, " ")
                content = content.strip()
                if first:
                    first = False
                    header = content.split()
                    length = len(header)
                    newline = line.replace(",", ";")
                    lines.append(newline)
                elif len(content.split()) < length:
                    lines.append(length * ";" + "\n")
                else:
                    newline = ""
                    for name in header:
                        newline = newline + conf_data[i][name] + ";"
                    newline += "\n"
                    lines.append(newline)
                    i += 1
        with open(path + "timeline.csv", "w", encoding="UTF-8") as datafile:
            for line in lines:
                datafile.write(line)

    def csv_read(self, filename, delimiter_position):
        """
        Reads in the timeline.csv file and structures it into a list

        Parameters
        ----------
        ignore : list
            List containing the config-data in the format of read_conf()

        Returns
        -------
        list
            A list containing a dictionary with elements for each collumn
        """
        out = []
        first = True
        with open(self.datapath + "/config/" + filename, encoding="UTF-8") as datafile:
            for line in datafile:
                content = line.replace('"', "").strip()
                if first:
                    content = content.replace(" ", "")
                    delimiter = content[delimiter_position]

                content = content.replace(" ", "[space]").strip()
                # cover for empty fields
                for i in range(0, 10):
                    content = content.replace(
                        2 * delimiter, delimiter + "None" + delimiter
                    )
                if content[-1] == delimiter:
                    content += "None"
                content = content.replace(delimiter, " ")
                content = content.strip()

                if first:
                    names = content.split()
                    first = False
                elif content.replace("None", "") != "":
                    data = content.split()
                    current = {}
                    if len(names) == len(data):
                        for i, name in enumerate(names):
                            point = data[i].strip()
                            point = point.replace("[space]", " ")
                            current[name] = point
                        out.append(current)
        return out

    def edit_axis(self, commands):
        """
        Edits the axis.csv and overwrites the axis of the commands specified,
        while leaving the rest

        Parameters
        ----------
        commands : dict
            Dict of dict containing the axis data whereby the first key
            is the command and the second is the axis

        Returns
        -------
        None
            None
        """
        self.reload()
        for command in commands.keys():
            if command in self.axis:
                self.axis[command] = commands[command]
        out = [["Command", "x1", "x2", "y", "ymon"]]
        for command in self.axis.keys():
            axi = self.axis[command]
            out.append([command, axi["x1"], axi["x2"], axi["y"], axi["ymon"]])
        np.savetxt(self.datapath + "/config/axis.csv", out, delimiter=";", fmt="%s")

    def axis_read(self):
        axis = {}
        data = self.csv_read("axis.csv", 7)
        for point in data:
            axis[point["Command"]] = {}
            for key in point.keys():
                if key != "Command":
                    axis[point["Command"]][key] = point[key]
        return axis

    def get_list(self, keys, restrictions=False):
        out = {}
        self.reload()
        for key in keys:
            out[key] = []
        for data in self.timeline:
            for key in keys:
                if not data[key] in out[key]:
                    if restrictions:
                        if all(item in data.values() for item in restrictions):
                            out[key].append(data[key])
                    else:
                        out[key].append(data[key])
        return out

    def set_shift(self):
        """
        Uses the shift of the references of each group to calulate a mean shift
        and adds this shift to the samples in the timeline.csv file of the current datapath

        Parameters
        ----------
        None
            None

        Returns
        -------
        None
            None
        """
        self.clean()
        measurement_group_list = {}
        new_conf_data = []
        for data in self.timeline:
            measurement_group = data["Measurement"] + "_" + data["Group"]
            if not measurement_group in measurement_group_list.keys():
                measurement_group_list[measurement_group] = []
            measurement_group_list[measurement_group].append(data)
        for measurement_group in measurement_group_list.keys():
            group = measurement_group_list[measurement_group]
            shift_total = 0
            shifts = []
            for data in group:
                if data["Sampletype"] == "Ref":
                    if data["Shift"] != "0":
                        shifts.append(float(data["Shift"]))
            if shifts:
                shift_total = np.sum(shifts) / len(shifts)
            for data in group:
                if data["Sampletype"] == "Sa":
                    data["Shift"] = str(shift_total)
                new_conf_data.append(data)
        self.timeline = new_conf_data
        self.write(self.timeline)
