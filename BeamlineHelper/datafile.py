#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 10:41:10 2023

@author: kai
"""
import warnings

from BeamlineHelper.scan import Scan

class DataFile:
    """
    Class to manage spec datafiles

    Attributes
    ----------
        datapath
            absolute path to the file storing the measurement data
        filename
            name of the file
    """

    def __init__(self, datapath, filename):
        self.datapath = datapath
        self.filename = filename

    def seperate_datafile(self):
        measurement_number = -1
        fileheader = []
        datsets = []
        with open(
            self.datapath + "/" + self.filename, "r", encoding="UTF-8"
        ) as datafile:
            # Reading
            for line in datafile:
                line = line.strip()
                if line:
                    if line[0] == "#":
                        if line[1] == "S":
                            datsets.append({"header": [], "data": []})
                            measurement_number += 1
                        if measurement_number == -1:
                            fileheader.append(line)
                        else:
                            datsets[measurement_number]["header"].append(line)
                    else:
                        datsets[measurement_number]["data"].append(line)
        return fileheader, datsets

    def process_header(self, header):
        fileheader = {}
        for line in header:
            key = line.split()[0]
            data = line.replace(key, "").strip()
            fileheader[key] = data
        return fileheader

    def read_raw(self):
        """
        Reads in the datafile to generate usable scan classes

        Parameters
        ----------
        None
            None

        Returns
        -------
        list
            A list with a dictionary for each measurement in the file
            containing all the relevant informations of the measurement
        """
        measurements = []
        # Seperate the file into headers and measurement data
        try:
            fileheader_raw, datsets_raw = self.seperate_datafile()
            # Restructure the fileheader into a dictionary
            fileheader = self.process_header(fileheader_raw)
            # For each dataset structure the important informations into dictionarys
            for data in datsets_raw:
                header = self.process_header(data["header"])
                measurements.append(
                    Scan(self.filename, fileheader, header, data["data"])
                )
            return measurements
        except:
            warnings.warn(
                "File " + self.filename + " does not contain data or is corrupt"
            )
            return []

    def read(self, config):
        """
        Reads in the datafile and updates it with the information in the timeline.csv
        to generate usable scan classes


        Parameters
        ----------
        filename : str
            The file location of the dataset relative to the datapath

        Returns
        -------
        list
            A list with a dictionary for each measurement in the file
            containing all the relevant informations of the measurement
        """
        measurement = self.read_raw()
        for scan in measurement:
            scan.update(config)
        return measurement