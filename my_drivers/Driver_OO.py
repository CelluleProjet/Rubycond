# -*- coding: utf-8 -*-
"""

Title: Rubycond: Python software to determine pressure in diamond anvil cell experiments by Ruby and Samarium luminescence.

Version 0.2.0
Release 260301

Author:

Yiuri Garino:

Copyright (c) 2023-2026 Yiuri Garino

Download: 
    https://github.com/CelluleProjet/Rubycond

Contacts:

Yiuri Garino
    yiuri.garino@cnrs.fr

Silvia Boccato
    silvia.boccato@cnrs.fr

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
    else:
        print("Running in terminal")
        print()


if __name__ == '__main__':
    reset()

import configparser as cp
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import os, sys
from datetime import datetime
import traceback


debug = True

if debug:
    script = os.path.abspath(__file__)
    script_dir = os.path.dirname(script)
    script_name = os.path.basename(script)
    now = datetime.now()
    date = now.isoformat(sep = ' ', timespec = 'seconds') #example = '2024-03-27 18:04:46'
    date_short = date[2:].replace('-','').replace(' ','_').replace(':','') #example = '240327_180446'
    print("File folder = " + script_dir)
    print("File name = " + script_name)
    print("Current working directory (AKA Called from ...) = " + os.getcwd())
    print("Python version = " + sys.version)
    print("Python folder = " + sys.executable)
    print()
    print("Started @ " + date +' AKA ' + date_short) #example = 'Started @ 2024-03-27 18:04:46 AKA 240327_180446'
    print()
    print('_/‾\\'*20)
    print()

import seabreeze 
seabreeze.use('pyseabreeze')

class spectrometer():
    
    def __init__(self, fit, debug = False):

        
        #https://pypi.org/project/seabreeze/
        #https://python-seabreeze.readthedocs.io/en/latest/
        self.fit = fit
        self.debug = debug
        self.correct_dark_counts = True
        self.connected = False
        self.list_devices = None
        self.thread_reading = False
        self.thread_max_speed_ms = 100 #min delta time to update the main program in ms
        self.thread_continuous = False
        self.thread_accumulation_data_flag = False
        self.thread_fit_continuous = False
        self.thread_fit_snap = False #used in spectrometer_thread_get_intensities
        self.thread_fit_lock = False #used in spectrometer_thread_get_intensities
        
        self.thread_reading_temperature = False #Used in others drivers :-D
        
        self.accumulations_n = 1 #number of accumulations, used in spectrometer_thread_get_intensities
        #self.integration_time_value_microsec = 1e6/20 #microsec
        self.integration_time_value = 1/20 #seconds
        self.abort = False
        self.average_intensities = None
        
    def __str__(self):
        #what is returned by print
        #return str(self.__doc__)
        if self.connected:
            string = 'Model ' + self.SN + ' connected\n'
            string+= 'SN = ' + self.SN + '\n'
            string+= 'pixels = ' + str(self.pixels) + '\n'
            #string+= 'Int Time Lim microsec = ' + str(self.integration_time_micros_limits) + '\n'
            string+= 'Int Time Lim = ' + str(self.integration_time_limits) + '\n'
            return string
        else:
            return 'No spectrometer Connected'

    def init(self):
        ''' 
        Called by the .connect_ methods
        '''
        self.SN = self.spec.serial_number #2/353
        self.pixels = self.spec.pixels #3/353
        self.wavelengths = self.spec.wavelengths()
        
        #self.integration_time_micros_limits = self.spec.integration_time_micros_limits #7/363
        l_min, l_max = self.spec.integration_time_micros_limits#7/363
        self.integration_time_limits = (l_min/1e6, l_max/1e6)
        self.connected = True
        self.thread_accumulation_data = None #used in spectrometer_thread_get_intensities #np.zeros((self.spec.pixels, self.accumulations))
        self.thread_accumulation_i = 1 #pointer of accumulations, used in spectrometer_thread_get_intensities
        
        
        self.spec.integration_time_micros(int(self.integration_time_value*1e6))
        print('Connected ', self.SN)
        
    def connect_first(self):
        ''' 
        Open first available spectrometer
        '''
        try:
            
            from seabreeze.spectrometers import Spectrometer
            self.spec = Spectrometer.from_first_available()
            self.init()
            
            
            print('Model ', self.SN, ' connected')
            return 1
        except:
            print(traceback.format_exc())
            return 0 
        
    def connect_device_n(self, n):
        ''' 
        Open n spectrometer in .list_devices
        '''
        if self.list_devices is None:
            self.get_all_devices()
        try:
            from seabreeze.spectrometers import Spectrometer
            self.spec = Spectrometer(self.list_devices[n])
            self.init()
        except:
            print(traceback.format_exc()) 

    def connect_SN(self, SN):
        ''' 
        Open the spectrometer matching the provided serial number SN
        '''
        try:
            from seabreeze.spectrometers import Spectrometer
            self.spec = Spectrometer.from_serial_number(SN)
            self.init()
        except:
            print(traceback.format_exc())
            
    def get_all_devices(self):
        self.list_devices = seabreeze.spectrometers.list_devices()
        print(self.list_devices)
        
    def get_wavelengths(self):
        if self.connected:
            self.wavelengths = self.spec.wavelengths()
    
    def get_intensities(self):
       if self.connected:
           self.intensities = self.spec.intensities(correct_dark_counts=self.correct_dark_counts)
           return self.intensities
    
    def set_integration_time(self, sec):
        if self.connected:
            micros = int(sec * 1e6)
            lim_min, lim_max = self.integration_time_limits
            lim_min, lim_max = lim_min*1e6, lim_max*1e6
            if (micros > lim_min) & (micros < lim_max):
                self.spec.integration_time_micros(micros)
                self.integration_time_value = micros/1e6
            else:
                print('Int time out of limits')
    
    # def set_integration_time(self, sec):
    #     if self.connected:
    #         micros = int(sec * 1e6)
    #         lim_min, lim_max = self.integration_time_micros_limits
    #         if (micros > lim_min) & (micros < lim_max):
    #             self.spec.integration_time_micros(micros)
    #             self.integration_time_value_microsec = micros
    #         else:
    #             print('Int time out of limits')
                
    def close(self):
        if self.connected:
            self.spec.close()
            self.connected = False


    
                
'''           
            
if __name__ == '__main__':
    try:
    
        import seabreeze 
        #https://pypi.org/project/seabreeze/
        #https://python-seabreeze.readthedocs.io/en/latest/
        seabreeze.use('pyseabreeze')
        # from seabreeze.spectrometers import Spectrometer
        # spec = Spectrometer.from_first_available()
        SN = 'HR4C1307'
        test = spectrometer()
        test.connect_SN(SN)
        test.get_wavelengths()
        x = test.wavelengths
        y = test.get_intensities()
        plt.plot(x,y)
        plt.show()
        
    except:
        print(traceback.format_exc())


    #%%
    import time
    
    x = test.wavelengths
    int_times = np.linspace(0.1,1,10)
    all_data = np.zeros((len(int_times), test.pixels))
    
    for i, int_time in enumerate(int_times):
        test.set_integration_time(int_time)
        #time.sleep(0.1)
        y = test.get_intensities()
        plt.plot(x, y, label = f'{int_time:.1f}')
        all_data[i,:] = y
        print(f'Int time = {int_time:.1f}')
    plt.grid()
    plt.legend()
    plt.show()
    
    #%%
    #%matplotlib auto 
    
    for int_time, y in zip(int_times, all_data):
        plt.plot(x, y, label = f'{int_time:.1f}')
    plt.grid()
    
    plt.legend()
    plt.show()
'''
if debug:
    now_end = datetime.now()
    date_end = now_end.isoformat(sep = ' ', timespec = 'seconds') #example = '2024-03-27 18:04:46'
    date_short_end = date_end[2:].replace('-','').replace(' ','_').replace(':','') #example = '240327_180446'
    timedelta = (datetime.now() - now)
    print()
    print('_/‾\\'*20)
    print()
    print()
    print("Done @ " + date_end +' AKA ' + date_short_end) #example = 'Started @ 2024-03-27 18:04:46 AKA 240327_180446'
    print()
    print(f"Elapsed time {timedelta} ({timedelta.seconds + round(timedelta.microseconds/1000)/1000})" )