#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 10:44:15 2023

@author: kai
"""

import sys
from time import sleep
import originpro as op


class OriginLoader():
    def __init__(self,beamtime):
        self.beamtime=beamtime
        
    def origin_shutdown_exception_hook(self, exctype, value, traceback):
        op.exit()
        sys.__excepthook__(exctype, value, traceback)
        
    def initOrigin(self,visible=False):
        """Initiates a Origin instance 

        Parameters
        ----------
        visible : boolean, optional
            Toogles if a visible instance of origin is opened or not
            
        Returns
        -------
        None
        """
        if op and op.oext:
            sys.excepthook = self.origin_shutdown_exception_hook
        if visible:
            if op.oext:
                op.set_show(True)

    def initNotebook(self,savepath,visible=False):
        """Saves the raw data as specified in the conf.csv file into a new origin notebook in the subfolder origin 

        Parameters
        ----------
        savepath : str
            Datapath where you want to save the origin file
            
        visible : boolean, optional
            Toogles if a visible instance of origin is opened or not
            
        Returns
        -------
        None
        """
        self.initOrigin(visible=visible)
        op.new()
        groupNumbers=[]
        filenames=[]
        firstdata=True
        firstfolder=True
        j=1
        AllData=self.beamtime.read_data()
        for scan in AllData:
            if firstdata:
                firstdata=False
            op.pe.cd('/UNTITLED')
            Group=scan.measurement
            if not Group in groupNumbers:
                if firstfolder:
                    firstfolder=False
                    op.pe.cd('Folder1')
                    op.pe.active_folder().name=f'Dataset {Group}'
                    currentBook=op.find_book()
                    currentBook.lname=scan.filename
                else: 
                    op.pe.mkdir(f'Dataset {Group}')
                    op.pe.cd(f'Dataset {Group}')
                    currentBook=op.new_book('w',scan.filename)
                currentBook.name=scan.sampletype+str(j)
                j+=1
                current=currentBook[0]
                current.name=scan.scannumber
                groupNumbers.append(Group)
                filenames.append(scan.filename)
            else:
                op.pe.cd(f'Dataset {Group}')
                if not scan.filename in filenames:
                    currentBook=op.new_book('w',scan.filename)
                    currentBook.name=scan.filename+str(j)
                    j+=1
                    current=currentBook[0]
                    current.name=scan.scannumber
                    filenames.append(scan.filename)
                else:
                    currentBook=op.find_sheet('w', '['+scan.filename+']1').get_book()
                    current=currentBook.add_sheet(scan.scannumber)
            i=0
            for name in scan.longnames:
                if(i==0):
                    current.from_list(i, scan.data[name], lname=name, comments = scan.command, axis = 'X')
                elif(i==1):
                    current.from_list(i, scan.data[name], lname=name, comments = 'Shift:'+str(scan.shift), axis = 'X')
                else:
                    current.from_list(i,scan.data[name], lname=name, axis = 'X')
                i+=1
        savepath = savepath.replace("/","\\")
        print("Saving to "+savepath)
        op.save(savepath)
        sleep(3)
        if op.oext:
            op.exit()


