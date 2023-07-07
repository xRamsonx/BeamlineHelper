#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 10:23:57 2023

@author: kai
"""
from setuptools import setup

setup(
    name='BeamlineHelper',
    version='0.1.0',    
    description='A example Python package',
    url='https://github.com/xRamsonx/BeamlineHelper',
    author='Kai Arnold',
    author_email='kai.arnold@design4webs.de',
    license='MIT License',
    packages=['BeamlineHelper'],
    include_package_data=True,
    package_data={'':['gui/*','gui/icons/*']},
    install_requires=['matplotlib',
                      'numpy',
                      'python-dateutil',
                      'pandas',
                      'PyQt5'
                      ],
    entry_points={
        'gui_scripts': [
            'BeamlineHelper = BeamlineHelper.gui.main:run',
        ],
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: MIT License',  
        'Operating System :: POSIX :: Linux/Windows',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
