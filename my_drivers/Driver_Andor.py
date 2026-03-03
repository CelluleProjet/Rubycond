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




from PyQt5 import QtWidgets, QtCore
import time 

from pyAndorSDK2 import atmcd, atmcd_codes, atmcd_errors, CameraCapabilities
# sdk = atmcd()  # Load the atmcd library
# codes = atmcd_codes


class spectrometer():
    
    def __init__(self, fit = None, debug = False):
        self.fit = fit
        self.debug = debug
        
        #Andor SDK examples from: C:\Program Files\Andor SDK\Python\pyAndorSDK2\examples
        
        from pyAndorSDK2 import atmcd, atmcd_codes, atmcd_errors
        
        self.atmcd = atmcd
        self.codes = atmcd_codes
        self.errors = atmcd_errors
        
        self.connected = False
        
        self.read_temperature = False
        self.read_temperature_freq = 1 #reading frequency in seconds
        self.Andor_tmin = None
        self.Andor_tmax = None
        
        self.xpixels = None
        self.ypixels = None

        #get_rates
        self.HSSpeeds = None
        self.VSSpeeds = None
        self.amp_modes = None
        
        #get_timings
        self.Exposure = None 
        self.Accumulate = None
        self.Kinetic = None
        
        self.integration_time_value = 1/20 #seconds
        
        self.accumulations_n = 1 #number of accumulations, used in spectrometer_thread_get_intensities
        self.average_intensities = None
        self.thread_fit_snap = False #used in spectrometer_thread_get_intensities
        self.thread_fit_lock = False #used in spectrometer_thread_get_intensities
        self.thread_max_speed_ms = 100 #min delta time to update the main program in ms
        self.thread_continuous = False
        self.thread_fit_continuous = False
        self.thread_reading_temperature = False #used in spectrometer_thread_get_intensities
        self.thread_reading_data = False
        
    def __str__(self):
        #what is returned by print
        #return str(self.__doc__)
        if self.connected:
            string = 'Andor connected\n'
            string+= 'SN = ' + self.SN + '\n'
            string+= 'pixels = ' + str(self.pixels) + '\n'
            self.get_integration_time_limits()
            string+= 'Int Time Lim microsec = ' + str(self.integration_time_micros_limits) + '\n'
            return string
        else:
            return 'No spectrometer Connected'
    
    def init_cooler(self):
        ''' 
        Called by the .connect_ methods
        '''
        self.get_temperature_range()
        self.Andor_t_target = max(self.Andor_tmin, -60)
        
    def init(self):
        ''' 
        Called by the .connect_ methods
        '''
        (ret, iSerialNumber) = self.sdk.GetCameraSerialNumber()
        self.SN = str(iSerialNumber)
        (ret, self.xpixels, self.ypixels) = self.sdk.GetDetector()
        if self.debug: print("Function GetDetector returned {} xpixels = {} ypixels = {}".format(
            ret, self.xpixels, self.ypixels))
        self.pixels = self.xpixels
        self.wavelengths = np.arange(0, self.pixels)
        
        self.connected = True
        self.get_integration_time() 
        self.get_integration_time_limits()
        self.thread_accumulation_data = None #used in spectrometer_thread_get_intensities #np.zeros((self.spec.pixels, self.accumulations))
        self.thread_accumulation_i = 1 #pointer of accumulations, used in spectrometer_thread_get_intensities
        self.abort = False
        print('Connected ', self.SN)
        
    def connect_first(self):
        
        self.sdk = self.atmcd()
        ret = self.sdk.Initialize("")
        
        if self.debug: print(f'OK Code = {atmcd_errors.Error_Codes.DRV_SUCCESS}')

        if atmcd_errors.Error_Codes.DRV_SUCCESS == ret:
            
            from pyAndorSDK2 import CameraCapabilities
            self.helper = CameraCapabilities.CapabilityHelper(self.sdk)
            
            if self.debug:
                
                self.helper.print_all()
                
            ret = self.sdk.SetAcquisitionMode(self.codes.Acquisition_Mode.SINGLE_SCAN)
            if self.debug: print("Function SetAcquisitionMode returned {} mode = Single Scan".format(ret))

            ret = self.sdk.SetReadMode(self.codes.Read_Mode.FULL_VERTICAL_BINNING)
            if self.debug: print("Function SetReadMode returned {} mode = FVB".format(ret))

            ret = self.sdk.SetTriggerMode(self.codes.Trigger_Mode.INTERNAL)
            if self.debug: print("Function SetTriggerMode returned {} mode = Internal".format(ret))
            
            self.init()
            self.init_cooler()
            return 1
        else:
            print(f'Connection Error, Error code = {ret}')
            return 0 
        
    def set_temperature(self, value):
        'Set the desired detector temperature in C'
        ''
        if self.connected:
            try:
                ret = self.sdk.SetTemperature(int(value))
                print(atmcd_errors.Error_Codes(ret).name, self.sdk.GetTemperatureStatus())
                if self.debug: print(atmcd_errors.Error_Codes(ret).name)
            except:
                print(traceback.format_exc())
    
    def get_temperature_range(self):
        '''returns the valid minimum temperature in centigrade to which the detector can be cooled
        self.Andor_tmin self.Andor_tmax'''
        if self.connected:
            ret, t_min, t_max  = self.sdk.GetTemperatureRange()
            status  = atmcd_errors.Error_Codes(ret).name
            self.Andor_tmin = t_min
            self.Andor_tmax = t_max
            out = status
            print(status)
            
        else:
            out = None
        return out
    
    def get_temperature(self):
        '''Get the detector temperature in C
        (22, 'DRV_TEMPERATURE_OFF')
        '''
        if self.connected:
            ret, temperature = self.sdk.GetTemperature()
            status  = atmcd_errors.Error_Codes(ret).name
            out = (temperature, status)
            print(status)
        else:
            out = None
        return out
    
    def turn_cooler_ON(self):
        if self.connected:
            ret = self.sdk.CoolerON()
            print(atmcd_errors.Error_Codes(ret).name)
            if self.debug: print(atmcd_errors.Error_Codes(ret).name)
            
    def turn_cooler_OFF(self):
        if self.connected:
            ret = self.sdk.CoolerOFF()
            print(atmcd_errors.Error_Codes(ret).name)
            if self.debug: print(atmcd_errors.Error_Codes(ret).name)
            
    def get_rates(self):
        #Andor SDK example ReadOutRates.py
        HSSpeeds = []
        VSSpeeds = []
        amp_modes = []

        (ret, ADchannel) = self.sdk.GetNumberADChannels()
        print("Function GetNumberADChannels returned {} number of available channels {}".format(
            ret, ADchannel))
        for channel in range(0, ADchannel):
            (ret, speed) = self.sdk.GetNumberHSSpeeds(channel, 0)
            print("Function GetNumberHSSpeeds {} number of available speeds {}".format(
                ret, speed))
            for x in range(0, speed):
                (ret, speed) = self.sdk.GetHSSpeed(channel, 0, x)
                HSSpeeds.append(speed)

            print("Available HSSpeeds in MHz {} ".format(HSSpeeds))

            (ret, speed) = self.sdk.GetNumberVSSpeeds()
            print("Function GetNumberVSSpeeds {} number of available speeds {}".format(
                ret, speed))
            for x in range(0, speed):
                (ret, speed) = self.sdk.GetVSSpeed(x)
                VSSpeeds.append(speed)
            print("Available VSSpeeds in us {}".format(VSSpeeds))

            (ret, index, speed) = self.sdk.GetFastestRecommendedVSSpeed()
            print("Recommended VSSpeed {} index {}".format(speed, index))

            (ret, amps) = self.sdk.GetNumberAmp()
            print("Function GetNumberAmp returned {} number of amplifiers {}".format(ret, amps))
            for x in range(0, amps):
                (ret, name) = self.sdk.GetAmpDesc(x, 21)
                amp_modes.append(name)

            print("Available amplifier modes {}".format(amp_modes))
            
            self.HSSpeeds = HSSpeeds
            self.VSSpeeds = VSSpeeds
            self.amp_modes = amp_modes
            
    def set_integration_time(self, sec):
        if self.connected:
            ret = self.sdk.SetExposureTime(sec)
            if self.debug: print(atmcd_errors.Error_Codes(ret).name)
            self.get_integration_time()
            
            # lim_min, lim_max = self.integration_time_micros_limits
            # if (micros > lim_min) & (micros < lim_max):
            #     self.spec.integration_time_micros(micros)
            #     self.integration_time_value_microsec = micros
            # else:
            #     print('Int time out of limits')
    
    def get_integration_time(self):
        self.get_timings()
        print(f"Int time {self.Exposure} sec")
        self.integration_time_value = self.Exposure
        
    def get_integration_time_limits(self):
        ''' get max, min unknown
        use get_timings
        '''
        if self.connected:
            ret,  value = self.sdk.GetMaximumExposure()
            self.integration_time_limits = 0, value
            if self.debug: print(atmcd_errors.Error_Codes(ret).name)
            
    def get_timings(self):
        ''' Update self.Exposure, self.Accumulate, self.Kinetic
        in seconds 
        '''
        if self.connected:
            (ret, self.Exposure, self.Accumulate, self.Kinetic) = self.sdk.GetAcquisitionTimings()
            self.integration_time_value = self.Exposure
            if self.debug: print("Function GetAcquisitionTimings returned {} exposure = {} accumulate = {} kinetic = {}".format(
                ret, self.Exposure, self.Accumulate, self.Kinetic))
    
    #Acquisition Section
    def get_intensities(self):
        self.start_acquisition()
        self.wait_acquisition()  #GetStatus alternative bus re
        (ret, arr, validfirst, validlast) = self.get_acquisition()
        self.intensities = arr
        return self.intensities
    
    def prepare_acquisition(self):
        ret = self.sdk.PrepareAcquisition()
        if self.debug: 
            print(atmcd_errors.Error_Codes(ret).name)
            print("Function PrepareAcquisition returned {}".format(ret)) 
    
    def start_acquisition(self):
        ret = self.sdk.StartAcquisition()
        if self.debug: 
            print(atmcd_errors.Error_Codes(ret).name)
            print("Function StartAcquisition returned {}".format(ret)) 
            
    def wait_acquisition(self):
        ret = self.sdk.WaitForAcquisition()
        if self.debug: 
            print(ret)
            print(atmcd_errors.Error_Codes(ret).name)
            print(atmcd_errors.Error_Codes(ret).value)
            print("Function WaitForAcquisition returned {}".format(ret)) 
    
    
    def get_acquisition(self, n_traks = 1):
        self.imageSize = self.xpixels*n_traks
        (ret, arr, validfirst, validlast) = self.sdk.GetImages(1, 1, self.imageSize)
        if self.debug: print("Function GetImages returned {} first pixel = {} size = {}".format(
                ret, arr[0], self.imageSize))
        return (ret, arr, validfirst, validlast)
    
    # imageSize = xpixels
    # (ret, arr, validfirst, validlast) = sdk.GetImages16(1, 1, imageSize)
    # print("Function GetImages16 returned {} first pixel = {} size = {}".format(
    #     ret, arr[0], imageSize))
    
    def close(self):
        ''' When closing down the program via ShutDown you must ensure that the temperature of the
detector is above -20ºC, otherwise calling ShutDown while the detector is still cooled will
cause the temperature to rise faster than certified. '''
        status, temperature = self.get_temperature()
        print(f'Temp = {temperature} {status}' )
        if self.debug: print(f'Temp = {temperature} {status}' )
        self.read_temperature = False
        time.sleep(self.read_temperature_freq) #give time to close to spectrometer_thread_get_temperature
        self.sdk.AbortAcquisition()
        self.sdk.CancelWait()
        self.sdk.ShutDown()
        self.connected = False
        
        # if temperature is not None:
        #     if temperature > -20 and self.connected:
        #         self.sdk.AbortAcquisition()
        #         self.sdk.CancelWait()
        #         self.sdk.ShutDown()
        #         self.connected = False
        #     else:
        #         print(''' When closing down the program via ShutDown you must ensure that the temperature of the
        # detector is above -20ºC, otherwise calling ShutDown while the detector is still cooled will
        # cause the temperature to rise faster than certified. ''')


class spectrometer_thread_get_temperature(QtCore.QObject):
    
    signal_temperature = QtCore.pyqtSignal(float, float, int)

    
    #Thread B Read temperature from spectrometer
    def __init__(self, spectrometer : spectrometer):
        super().__init__()
        self.spec = spectrometer
    
    @QtCore.pyqtSlot()
    def start(self):
        #Thread_2A) Create temperature Start method
        #print(datetime.now().strftime("%H:%M:%S") +' Thread_2A started '+ str(self.spec.abort) +f' {self.spec.thread_accumulation_i}')
        if self.spec.connected:
            while self.spec.read_temperature == True:
                #Main Loop
                #Wait to read temperature until reading data is finished:
                    
                if not self.spec.thread_reading_data: 
                     
                    self.spec.thread_reading_temperature = True
                    self.spec.sdk.AbortAcquisition()
                    ret_temp, temperature = self.spec.sdk.GetTemperature()
                    ret, temperature, TargetTemp, AmbientTemp, CoolerVolts = self.spec.sdk.GetTemperatureStatus()
                    self.signal_temperature.emit(temperature, TargetTemp, ret_temp)
                    #print(datetime.now(), ' t = ', temperature, '  ' , ret, ))
                    if self.spec.debug:
                        print(datetime.now(), ' t = ', temperature)
                    self.spec.thread_reading_temperature = False
                    
                    #Sleep until next reading
                    time.sleep(self.spec.read_temperature_freq)
                
                # else:
                #     #Wait to read temperature until reading data is finished:
                #     #Minimum delay
                #     time.sleep(0.01)
                
                    
                
#%%
'''
if __name__ == '__main__':
    spec = spectrometer(debug = True)
    spec.connect_first()
    print()
    print('_/‾\\'*5)
    print()
    ret = spec.turn_cooler_OFF()
   
    ret = spec.set_temperature(10)
    
    temperature, status = spec.get_temperature()
    print(f'temperature = {temperature}')
    print(f'status = {status}')
    
    #%%
    spec.set_integration_time(5)
    spec.get_timings()
    t0 = datetime.now().timestamp()
    spec.prepare_acquisition()
    spec.start_acquisition()
    spec.wait_acquisition()  #GetStatus alternative bus re
    (ret, arr, validfirst, validlast) = spec.get_acquisition()
    delta = datetime.now().timestamp() -t0
    print(f'Elapsed = {delta}')
    plt.plot(spec.wavelengths, arr)
    plt.show()
    
    #%%
    
    spec.sdk.SetReadMode(spec.codes.Read_Mode.IMAGE)
    #sdk.SetImage(1, 1, 1, self.xpixels, 1, self.ypixels)
    
    spec.set_integration_time(1)
    spec.get_timings()
    
    t0 = datetime.now().timestamp()
    spec.prepare_acquisition()
    spec.start_acquisition()
    spec.wait_acquisition()  #GetStatus alternative bus re
    (ret, arr, validfirst, validlast) = spec.get_acquisition(spec.ypixels)
    delta = datetime.now().timestamp() -t0
    arr.resize(spec.ypixels, spec.xpixels)
    plt.imshow(arr)
    plt.show()
    #self.data.resize(self.ypixels, self.xpixels)
    
    #GetMostRecentImage
#%%
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

'''