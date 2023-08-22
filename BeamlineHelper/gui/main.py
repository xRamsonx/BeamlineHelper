#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 11:51:56 2023

@author: kai
"""

import os
import sys
import argparse

from pyshortcuts import make_shortcut
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, QCoreApplication, Qt
from PyQt5.QtWidgets import QApplication

from BeamlineHelper.gui.main_windows import StartWindow

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def init_app():
    myappid = "bh_gui"  # arbitrary string
    try:
        from ctypes import windll
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except:
        pass
    
    import BeamlineHelper
    package_dir = os.path.abspath(os.path.join(os.path.dirname(BeamlineHelper.__file__)))

    icon_path = os.path.join(
        package_dir,  # Package name/folder
        'icons'
    )
    icon1=os.path.join(
        icon_path,
        '48.ico'
    )   
    icon2=os.path.join(
        icon_path,
        '256.ico'
    )   
    #set fontsize:
    # Get the default font
    # defaultFont = QtWidgets.QApplication.font()
    
    # # Define a scaling factor for the font size (adjust as needed)
    # scalingFactor = 1.2
    
    # # Calculate the scaled font size
    # scaledFontSize = defaultFont.pointSizeF() * scalingFactor
    
    # # Create a font with the scaled font size
    # scaledFont = defaultFont
    # scaledFont.setPointSizeF(scaledFontSize)
    
    # # Set the scaled font as the application font
    # QtWidgets.QApplication.setFont(scaledFont)
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # Enable high DPI scaling
    app = QApplication(sys.argv)
    app_icon = QIcon()
    app_icon.addFile(icon1, QSize(48, 48))
    app_icon.addFile(icon2, QSize(256, 256))
    window = StartWindow(app_icon)
    window.show()
    app.exec_()
    
def generate_shortcut():
    import BeamlineHelper
    package_dir = os.path.abspath(os.path.join(os.path.dirname(BeamlineHelper.__file__)))

    main_script_path = os.path.join(package_dir,'gui', 'main.py')
    icon_path = os.path.join(
        package_dir,
        'icons',  # Package name/folder
        'icon.ico'
    )

    # Create a desktop shortcut
    make_shortcut(
        main_script_path,  # Path to your main script
        name='BeamlineHelper',  # Shortcut name
        description='Organizer of your beamtime',
        icon=icon_path,  # Path to your application icon
        terminal=False,  # Set this to True if your application needs a terminal
    )
    
def run():
    # Instantiate the parser
    parser = argparse.ArgumentParser(description='Optional app description')
    parser.add_argument('-s','--shortcut', action='store_true',
                    help='creates a shortcut on your desktop')
    args = parser.parse_args()
    if args.shortcut:
        generate_shortcut()
    else:
        init_app()
        
if __name__ == "__main__":
    run()
    