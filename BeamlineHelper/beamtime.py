#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 10:35:33 2023

@author: kai
"""
from matplotlib import cm
import os

from BeamlineHelper.config import Config
from BeamlineHelper.datafile import DataFile

class Beamtime:
    def __init__(
        self,
        datapath,
        list_of_collumns=[
            "Measurement",
            "Date",
            "Time",
            "Filename",
            "#scan",
            "Command",
            "Sampletype",
            "Sample",
            "Mask",
            "Data_Points",
            "Shift",
            "Group",
        ],
    ):
        self.datapath = datapath
        if list_of_collumns:
            self.config = Config(datapath, list_of_collumns)
        else:
            self.config = Config(datapath)
        self.files=set(line['Filename'] for line in self.config.timeline)

    def plot(
        self,
        axis,
        scan_list,
        cmaplist=[
            "summer",
            "winter",
            "spring_r",
            "copper_r",
            "pink",
            "winter_r",
            "Wistia",
            "cool",
            "bone",
            "spring",
        ],
    ):
        """
        Append plots of scans to a matplotlib plot axis for a list of scans

        Parameters
        ----------
        axis : matplotlib.pyplot.axis object
            Axis on which to append the plots

        scan_list : list
            List of scans to be plotted

        cmaplist : list, optional
            List of colormaps used to highlight similar plots

        Returns
        -------
        axis : matplotlib.pyplot.axis object
            Axis with appended plots of the scans
        """
        print("Plot " + str(len(scan_list)) + " scans")
        scan_list.sort(key=lambda item: item.sample)
        samplelist = {}
        # Count the number of scans per sample to choose the color
        for scan in scan_list:
            if not scan.sample in samplelist.keys():
                samplelist[scan.sample] = 1
            else:
                samplelist[scan.sample] += 1
        # distribute the color and plot the scans
        i = -1
        j = -1

        last_sample = ""
        plot_only_2d = len(scan_list) != 1
        for scan in scan_list:
            j += 1
            if scan.sample != last_sample:
                j = 0
                i += 1
            # If the number of scans is too large, only name one scan for each Sample
            if len(scan_list) > 14:
                if scan.sample != last_sample:
                    label = scan.sample
                else:
                    label = ""
            else:
                label = scan.sample + "_" + str(j)

            if scan.sampletype == "Ref":
                color = cm.get_cmap("autumn")(j / samplelist[scan.sample] / 2)
            else:
                color = cm.get_cmap(cmaplist[i])(j / samplelist[scan.sample] / 2)
            last_sample = scan.sample

            axis = scan.plot(
                self.config,
                axis=axis,
                color=color,
                label=label,
                plot_only_2d=plot_only_2d,
            )
        axis.legend()
        return axis

    def read_data(
        self, measurement=["All"], command=["All"], sampletype=["All"], sample=["All"]
    ):
        """
        Reads in all datafiles included in the timeline.csv and exchanges their entries
        with the ones defined in the timeline.csv file of the current datapath

        Parameters
        ----------
        Measurement : str, optional
            Measurement to be read in (Default 'All')

        Group : str, optional
            Group to be read in (Default 'All')

        Sampletype : str, optional
            Sampletype to be read in (Default 'All')

        Sample : str, optional
            Sample to be read in (Default 'All')

        Returns
        -------
        list
            Ordered list of all the datasets listet in the timeline.csv file
        """
        path = self.datapath + "/config"
        if not os.path.exists(path + "/timeline.csv"):
            raise Exception(
                "No timeline.csv available.\n Use make_conf first and edit the timeline.csv file"
            )
        self.config.clean()
        all_data = []
        for point in self.config.timeline:
            if (
                ('All' in measurement or point["Measurement"] in measurement)
                and ('All' in command or point["Command"] in command) 
                and ('All' in sample or point["Sample"] in sample)
                and ('All' in sampletype or point["Sampletype"] in sampletype)
            ):
                current = DataFile(self.datapath, point["Filename"]).read(self.config)
                data = current[int(point["#scan"]) - 1]
                all_data.append(data)
        return all_data

    def read_file(self, file):
        """Reads a specific datafile included in the timeline.csv and exchanges
        their entries with the ones defined in the timeline.csv file of the current datapath

        Parameters
        ----------
        File : str
            Name of the file tp be read in

        Returns
        -------
        list
            Ordered list of all the datasets from the specified file
        """
        self.config.clean()
        for point in self.config.timeline:
            if file == point["Filename"]:
                data = DataFile(self.datapath, point["Filename"]).read(self.config)
        return data

    def get_all_motors(self):
        motors = []
        all_data = self.read_data()
        for scan in all_data:
            for motor in scan.motor_position.keys():
                if not motor in motors:
                    motors.append(motor)
        return motors