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
from PyQt5 import QtWidgets, QtCore
import time 

# try: 
#     from . Driver_OO_23 import spectrometer
#     #https://peps.python.org/pep-0328/
#     #Spyder: ImportError: attempted relative import with no known parent package
# except:
#     from Driver_OO_23 import spectrometer
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




class spectrometer_thread_get_intensities(QtCore.QObject):
    
    signal_status = QtCore.pyqtSignal(np.ndarray, int)
    signal_done = QtCore.pyqtSignal()
    signal_fit_done = QtCore.pyqtSignal()
    
    #Thread A Read data from spectrometer
    def __init__(self, spectrometer):
        super().__init__()
        self.spec = spectrometer
    
    @QtCore.pyqtSlot()
    def start(self):
        #Thread_2A) Create Thread Start method
        #print(datetime.now().strftime("%H:%M:%S") +' Thread_2A started '+ str(self.spec.abort) +f' {self.spec.thread_accumulation_i}')
        self.spec.thread_accumulation_data_flag = False
        self.safe = True
        

        self.spec.thread_accumulation_data = np.zeros((self.spec.pixels, self.spec.accumulations_n))
        
        emit_t0 = datetime.now().timestamp()
        while True:
            error = 0
            #Main Loop
            #Wait to read data until reading temperature is finished:
            if not self.spec.thread_reading_temperature:
                
                if not self.spec.abort: 
                    
                    #print(datetime.now().strftime("%H:%M:%S") +' '+ str(self.spec.abort) +f' {self.spec.thread_accumulation_i}')
                        #print(f"Driver Reading {self.spec.thread_accumulation_i} / {self.spec.accumulations_n}")
                        
            
                    if self.spec.debug: print(f' Acc set {self.spec.thread_accumulation_i} / {self.spec.accumulations_n}')
                    
                    #blocking request
                    self.spec.thread_reading_data = True
                    self.spec.thread_accumulation_data[:,self.spec.thread_accumulation_i-1] = self.spec.get_intensities() 
                    self.spec.thread_reading_data = False
                    
                    if self.spec.thread_accumulation_data_flag == True:
                        
                        #continuous with all data in mem
                        
                        if self.spec.debug: print("All in mem")
                        self.spec.average_intensities = self.spec.thread_accumulation_data.mean( axis=1 )
                    else:
                        
                        #Snap or accumulating data in mem
                        
                        if self.spec.debug: print("Proportional in mem")
                        self.spec.average_intensities = self.spec.thread_accumulation_data[:,:self.spec.thread_accumulation_i].mean( axis=1 )
                    
                    
                    delta_time = datetime.now().timestamp() - emit_t0 > self.spec.thread_max_speed_ms/1000
    
                
                    # previous Emit = not (self.spec.thread_continuous and not delta_time) #Problem: in snap when a lot of accumulation too many Emit
                    # Actual Emit:
                    # Snap: after dt OR Last 
                    # continuous only after dt
                    # => dt or L and not C
                    
                    Last = self.spec.thread_accumulation_i >= self.spec.accumulations_n
                    Emit = delta_time or Last and not self.spec.thread_continuous
                    #print("Emit data = ", Emit)
                    
                    if Emit:
                        
                        #emit and update main prog if: 
                        #1) more than thread_max_speed_ms (timestamp is in sec) 
                        
                        
                        Fit = self.spec.thread_fit_continuous and not self.spec.thread_fit_lock
                        if Fit:
                            #Fit data 
                            self.spec.thread_fit_snap = False
                            self.spec.fit.fit_set_y(self.spec.average_intensities)
                            error = self.spec.fit.fit_run()
                        
                        self.signal_status.emit(self.spec.average_intensities, self.spec.thread_accumulation_i)
                        
                        #print("continuous = ", self.spec.thread_fit_continuous , "Fit = ", Fit ,"Error = ",error,  "Emit Fit = ", Fit and not error)
                        
                        if Fit and not error:
                            #Emit Fit 
                            self.spec.fit.fit_eval_comp()
                            self.spec.fit.fit_update_report()
                            self.signal_fit_done.emit()
                        
                        emit_t0 = datetime.now().timestamp()
                        
                    self.spec.thread_reading = False
                    
                    if Last:
                        #self.signal_status.emit(self.spec.average_intensities, self.spec.thread_accumulation_i)
                        self.spec.thread_accumulation_i = 1
                        self.spec.thread_accumulation_data_flag = True #Mem for continuous ready
                        if self.spec.thread_continuous == False:
                            #Snap case
                            self.signal_done.emit()
                            break
                    else:
                        self.spec.thread_accumulation_i = self.spec.thread_accumulation_i + 1
                    
                else:
                    #Abort case
                    self.signal_done.emit()
                    
                    break
            else:
                #Wait to read data until reading temperature is finished
                #Minimum delay
                time.sleep(0.1)












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