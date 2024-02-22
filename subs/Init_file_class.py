# -*- coding: utf-8 -*-
"""

Init_file_class

This file is part of Rubycond

Rubycond: Pressure by Ruby Luminescence (PRL) software to determine pressure in diamond anvil cell experiments.

Version 0.1.0
Release 240222

Author:

Yiuri Garino:
     yiuri.garino@cnrs.fr   

Copyright (c) 2023-2024 Yiuri Garino

Download: https://github.com/CelluleProjet/Rubycond

License: GPLv3

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

"""

def reset():
    import sys
    
    if hasattr(sys, 'ps1'):
        #clean Console and Memory
        from IPython import get_ipython
        get_ipython().run_line_magic('clear','/')
        get_ipython().run_line_magic('reset','-sf')
        print("Running interactively")
        print()
        terminal = False
    else:
        print("Running in terminal")
        print()
        terminal = True

if __name__ == '__main__':
    reset()

import configparser as cp
from pathlib import Path
import datetime
import sys
import os 
from tkinter import messagebox

class init:
    def __init__(self, folder = None, filename = None):
        if (filename == None) or (folder == None): 
            filename = Path(sys.argv[0])
            filename = filename.stem+'_init'
            filename = (Path(filename)).with_suffix('.txt')
        else:
            filename = folder + os.path.sep + filename + '_init.txt'
            filename = Path(filename)
        self.filename = filename
        
        #Sections in initialization file
        sections = ['Settings', 'Spectrometer']

        #Keys in initialization file
        #If initialization file not found or corrupted default values
        # are used to create a new initialization file
        section_1_keys = ['stand_alone']
        section_1_keys_default = ['False']

        section_2_keys = ['calibration_i','calibration_c1','calibration_c2', 'calibration_c3', 'sigma_vary', 'sigma (cm-1)']
        section_2_keys_default = ['1', '1', '0', '0', 'False', '0.637']


        section_keys = [section_1_keys,section_2_keys]
        section_keys_default = [section_1_keys_default,section_2_keys_default]
        
        self.init_var = {}
        
        try:
            self.init_create = False
            
            self.config = cp.ConfigParser()
            self.config.read(filename)
            
            for i, sec in enumerate(sections):
                init_var_nested = {}
                for j, key in enumerate(section_keys[i]):
                    init_var_nested[f'{key}'] = self.config[sec][key]
                self.init_var[sec] = init_var_nested
            print()
            print(f"Loaded initialization file '{filename}'")
            print()
            print(f'location: {filename.resolve()}')
            print()
        
        except:
            self.init_create = True
            
            if filename.is_file():
                print()
                print(f"Corrupted initialization file '{filename}'")
                print()
                print(f'location: {filename.resolve()}')
                print()
                
                backup = filename.stem+'_old_'+ datetime.now().strftime("%y%m%d_%H%M%S") +filename.suffix
                filename.rename(backup)
                
                print(f'Corrupted file renamed in {backup}')
                print()
            else:
                print()
                print(f"Initialization file not found, '{filename}' created")
                print()
                print(f'location: {filename.resolve()}')
                print()

            self.config = cp.ConfigParser()
            self.config.read(filename)
            
            
            for i, sec in enumerate(sections):
                self.config.add_section(sec)
                init_var_nested = {}
                for j, key in enumerate(section_keys[i]):
                    self.config[sec][key] = section_keys_default[i][j]
                    init_var_nested[f'{key}'] = self.config[sec][key]
                self.init_var[sec] = init_var_nested
            
            with open(filename, 'w') as configfile:    # save
                self.config.write(configfile)
    
    def save(self):
        """
        save self.init_var to self.filename
        all self.init_var must be string

        """
        try:
        
            self.config = cp.ConfigParser()
            self.config.read(self.filename)
            
            for section in self.init_var.keys():
                for key in self.init_var[section].keys():
                    print(section,key)
                    self.config[section][key] = self.init_var[section][key]
                    
            with open(self.filename, 'w') as configfile:    # save
                self.config.write(configfile)
        except Exception as e:
            messagebox.showerror(title = 'Open File Error', message = e)
            
    def __repr__(self):
        repr = str('\n')
        for i in self.init_var.keys():
            repr+= f'\nSection : [{i}]\n'
            for j in self.init_var[i].keys():
                repr+= f"   Key '{j}' value '{self.init_var[i][j]}'\n"
        return repr

    def __str__(self):
        repr = str('\n')
        for i in self.init_var.keys():
            repr+= f'\nSection : [{i}]\n'
            for j in self.init_var[i].keys():
                repr+= f"   Key '{j}' value '{self.init_var[i][j]}'\n"
        return repr

