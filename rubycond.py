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
import os, sys, platform
from datetime import datetime
from time import sleep 
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


script = os.path.abspath(__file__)
script_dir = os.path.dirname(script)
sys.path.append(script_dir)

from PyQt5 import QtWidgets, QtCore, QtGui

from my_models.model_core import my_model as model
from my_models.model_FIT import fit 

from my_view.file_controls import controls
from my_view.Frame_1_graph import Frame_1_graph

from my_view.pop_up import pop_up_error, pop_up_simple
from my_view.calib_controls import calib_controls
from my_view.about import about

from my_drivers.spectrometer import spectrometer
from my_drivers.spectrometer_thread import spectrometer_thread_get_intensities

from rubycond_OF.rubycond_OF import open_file
from rubycond_CB.rubycond_CB import calibrator
from rubycond_calc.rubycond_calc import rubycond_calc
from rubycond_calc.view import Equations_RubySam_Scale as RS

class Window(QtWidgets.QMainWindow):
    
    work_requested = QtCore.pyqtSignal()
    
    signal_thread_A_read_data = QtCore.pyqtSignal()
    signal_thread_B_read_temperature = QtCore.pyqtSignal()
    
    signal_calibrator_selected_data = QtCore.pyqtSignal(np.ndarray, np.ndarray, str)
    
    def __init__(self, debug = True):
        
        super().__init__()
        
        
        self.__name__ = 'Rubycond'
        self.__version__ = '0.2.0' 
        self.__release__ = '260301'
        
        self.about = about(self.__name__, self.__version__, self.__release__)
        self.pop_up_info = pop_up_simple()
        
        self.script = os.path.abspath(__file__)
        self.script_dir = os.path.dirname(self.script)

        #config section
        
        # 'QWERTY' or 'AZERTY' for Shortucts settings

        self.keyboard = 'QWERTY'#uncomment to select
        #self.keyboard = 'AZERTY' #uncomment to select
        
        
        self.spectrometer_model = "OceanOptics" 
        #self.spectrometer_model = "Andor"   
        
        
        config_spec_autoconnect = True
        self.init_calib_settings()
        
        self.controls_minimum_width = 500
        self.debug = debug
        
        
        self.version = '0.0.251104'
        self.window_Title = script_name#'Rubycond ' + self.version
        self.setWindowTitle(self.window_Title)
        self.model = model(self.debug)
        self.fit = fit(self.debug)
        
        self.spec = spectrometer(self.fit, self.debug) 
        
        
        #self.spectrometer_model = "Andor"
        self.init_target_cooler_temperature = -60  #cooler initial target temperature
        
        self.timestamp_now = datetime.now().timestamp()
        
        self.rubycond_open_file = open_file()
        self.rubycond_calibrator = calibrator()
        self.rubycond_calculator = rubycond_calc()
        
        self.calib_controls = calib_controls(main_dir = self.script_dir)
        
        self.report_window = pop_up_simple()
        
        self.data_from_file_x = None  #Used as a reference if working on file condition
        
        self.thread_reading = False
        self.gaugetabRuby_checkb_cont_value = False
        self.gaugetabSam_checkb_cont_value = False
        
        self.font_size = 15
        self.font_style = ''
        #self.update_font()
        
        self.controls = controls(font_size= self.font_size, debug = debug)
        
        
        self.graph_1 = Frame_1_graph(debug = debug)
        
        
        #Shortcuts
        
        shortcut = QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_I)
        shortcut = QtWidgets.QShortcut(shortcut, self)
        shortcut.activated.connect(self.script_info) 
        
        
        if self.keyboard == 'QWERTY':
            shortcuts = {
                 'Set Fit:Min as cursor' : (self.set_control_fit_min, QtCore.Qt.CTRL + QtCore.Qt.Key_Z),
                 'Set Fit:Max as cursor' : (self.set_control_fit_max, QtCore.Qt.CTRL + QtCore.Qt.Key_X),
                 'Zoom to fit' : (self.graph_1.Rescale_to_fit, QtCore.Qt.CTRL + QtCore.Qt.Key_C ),
                 'Rescale to full scale' : (self.graph_1.autoscale_ax, QtCore.Qt.CTRL + QtCore.Qt.Key_Q),
                 'Fit snap' : (self.command_fit_button_snap, QtCore.Qt.CTRL + QtCore.Qt.Key_F),
                 'Fit continuous ' : (self.shortcut_control_fit_cont, QtCore.Qt.CTRL + QtCore.Qt.Key_G),
                 'Open file' : (self.command_file_open_file, QtCore.Qt.CTRL + QtCore.Qt.Key_O),
                 'Save File' : (self.command_file_save_data, QtCore.Qt.CTRL + QtCore.Qt.Key_S)
                 }
        elif self.keyboard == 'AZERTY':
            shortcuts = {
                 'Set Fit:Min as cursor' : (self.set_control_fit_min, QtCore.Qt.CTRL + QtCore.Qt.Key_W),
                 'Set Fit:Max as cursor' : (self.set_control_fit_max, QtCore.Qt.CTRL + QtCore.Qt.Key_X),
                 'Zoom to fit' : (self.graph_1.Rescale_to_fit, QtCore.Qt.CTRL + QtCore.Qt.Key_C ),
                 'Rescale to full scale' : (self.graph_1.autoscale_ax, QtCore.Qt.CTRL + QtCore.Qt.Key_Q),
                 'Fit snap' : (self.command_fit_button_snap, QtCore.Qt.CTRL + QtCore.Qt.Key_F),
                 'Fit continuous ' : (self.shortcut_control_fit_cont, QtCore.Qt.CTRL + QtCore.Qt.Key_G),
                 'Open file' : (self.command_file_open_file, QtCore.Qt.CTRL + QtCore.Qt.Key_O),
                 'Save File' : (self.command_file_save_data, QtCore.Qt.CTRL + QtCore.Qt.Key_S)
                 }
        
        shortcuts_text = '\n'*3 + f"   Available shortcuts, '{self.keyboard}' keyboard" + '\n'*3
        
        for key, value in shortcuts.items():
            
            shortcuts_text+= '   '
            shortcuts_text+= QtGui.QKeySequence(value[1]).toString()
            shortcuts_text+= ' = '
            shortcuts_text+= key + '\n'
            print('Shortcut ', QtGui.QKeySequence(value[1]).toString(), key)
            shortcut = QtGui.QKeySequence(value[1])
            shortcut = QtWidgets.QShortcut(shortcut, self)
            shortcut.activated.connect(value[0])
        
        label = QtWidgets.QLabel(shortcuts_text, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        
        #MainTabs
        self.main_tabs = QtWidgets.QTabWidget()
        #tabs.setTabPosition(QtWidgets.QTabWidget.West)
        #tabs.addTab(self.Tab_Neon_Data, "Neon Lines")
        self.main_tabs.addTab(self.graph_1, "PRL")
        self.main_tabs.addTab(self.rubycond_calculator, "Calculator")
        self.main_tabs.addTab(label, "Shortcuts")
        self.main_layout = QtWidgets.QHBoxLayout()
        
        #No splitter
        
        self.main_layout.addWidget(self.controls)
        self.main_layout.addWidget(self.main_tabs)
        
        
        # #Yes splitter
        # self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal) #Horizontal
        
        # #self.controls.setMinimumWidth(self.controls_minimum_width)
        # #self.controls.sizeHint().setWidth(self.controls_minimum_width)
        # self.splitter.addWidget(self.controls)
        # #self.controls.sizeHint().setWidth(self.controls_minimum_width)
        # self.splitter.addWidget(self.main_tabs)
        
        # # initial_widths = [200, 1] 
        # # self.splitter.setSizes(initial_widths)
        
        # self.main_layout.addWidget(self.splitter)
        
        # #Add vertival expanding to splitter
        # self.splitter.setSizePolicy(
        #     QtWidgets.QSizePolicy.Preferred ,
        #     QtWidgets.QSizePolicy.Expanding)
        
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
        
        
        #self.controls.setMinimumWidth(self.controls_minimum_width)
        #self.controls.sizeHint().setWidth(self.controls_minimum_width)
        # No splitter
        self.controls.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding) #Fixed
        
        #Fixed
        
        # self.graph_1.setSizePolicy(
        #     QtWidgets.QSizePolicy.Expanding,
        #     QtWidgets.QSizePolicy.Expanding)
        
        self.mainWidget = QtWidgets.QFrame()
        self.mainWidget.setLayout(self.main_layout)
        
        #Signal slot connection
        #self.rubycond_open_file.commands.signal_selected_data_all.connect(self.method_file_open_file_all) #Not used
        self.rubycond_open_file.commands.signal_selected_data_xy.connect(self.method_file_open_file_xy)
        self.rubycond_calibrator.signal_update_calibration_pars.connect(self.method_update_calib_cn) 
        self.calib_controls.signal_update_calibration_pars.connect(self.method_update_calib_cn)
        self.signal_calibrator_selected_data.connect(self.rubycond_calibrator.open_file_command_xy)
        
        
        
        
        self.init_Menu()
        self.init_disabled()
        self.init_controls()
        
        self.setCentralWidget(self.mainWidget)
        self.init_logger()
        
        self.update_control_fit_function("Double Voigt")
        self.update_control_fit_iterLim(150)

        #self.controls.group_meas.setVisible(False)
        self.controls.group_measTemp.setVisible(False)  #Andor cooling controls
        self.menu_measTemp.menuAction().setVisible(False)
        # command_fit_button_min
        
        shortcut = QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_Y)
        shortcut = QtWidgets.QShortcut(shortcut, self)
        shortcut.activated.connect(self.yiuri_debug) 

        self.init_gauge()

    
        self.model.statusbar_message('Done Init')
        
        self.save_data_format_txt = True
        self.save_data_format_csv = True
        self.save_data_format_npy = True
        
        self.create_debug_info_message()
        #self.splitter.sizeHint().setWidth(self.controls_minimum_width)
        
        if config_spec_autoconnect:
            self.command_spec_button_connect()
            if self.spectrometer_model == "Andor":
                self.command_measTemp_checkb_cool(True)

    def create_debug_info_message(self):
        script = os.path.abspath(__file__)
        script_dir = os.path.dirname(script)
        script_name = os.path.basename(script)
        now = datetime.now()
        date = now.isoformat(sep = ' ', timespec = 'seconds') #example = '2024-03-27 18:04:46'
        date_short = date[2:].replace('-','').replace(' ','_').replace(':','') #example = '240327_180446'
        message = ''
        message+= '\n'
        message+= '_/‾\\'*20 + '\n'
        message+= '\n'
        message+= 'System Info' + '\n'
        message+= '\n'
        message+= '_/‾\\'*20 + '\n'
        message+= '\n'
        message+= "File folder = " + script_dir + '\n'
        message+= "File name = " + script_name + '\n'
        message+= "Current working directory (AKA Called from ...) = " + os.getcwd() + '\n'
        message+= "Python version = " + sys.version + '\n'
        message+= "Python folder = " + sys.executable + '\n'
        message+= '\n'
        message+= "Started @ " + date +' AKA ' + date_short + '\n'
        message+= '\n'
        message+= '_/‾\\'*20 + '\n'
        message+= '\n'
        self.debug_info_message = message
        
    def yiuri_debug(self):
        print(self.debug_info_message)
        #self.graph_1.erase_fit_plot()
        #self.graph_1.remove_red_lines()

        
    def init_calib_settings(self):
        #calib file
        
        filename = Path(self.script_dir) / 'Default_calib.ini'

        config = cp.ConfigParser()
        config.read(filename)
        self.calib_cn = [0, 0, 0, 0]
        try:
            #Read file
            self.calib_cn[0] = float(config['Calib']['c0'])
            self.calib_cn[1] = float(config['Calib']['c1'])
            self.calib_cn[2] = float(config['Calib']['c2'])
            self.calib_cn[3] = float(config['Calib']['c3'])
        except:
            #Create default file
            self.calib_cn = [1, 1, 0, 0]
            try:
                config['Calib']
            except:
                config.add_section('Calib')
            
            config['Calib']['c0'] = str(self.calib_cn[0])
            config['Calib']['c1'] = str(self.calib_cn[1])
            config['Calib']['c2'] = str(self.calib_cn[2])
            config['Calib']['c3'] = str(self.calib_cn[3])
            
            with open(filename, 'w') as configfile:    # save
                config.write(configfile)
                print()
                print(f'Saved {filename}')
                print()
        
        
    def init_logger(self):
        self.update_log_button_delta(60)
        self.update_log_button_threshold(1000)
        script = os.path.abspath(__file__)
        script_dir = os.path.dirname(script)
        self.update_log_button_folder(script_dir)
    
    #Save section
        
    def create_header(self):
        #yyy
        try:
            now = datetime.now()
            current_time = now.strftime("%A %d %B %Y %H:%M:%S")
            header = '\n' + current_time + '\n\n'
            header+= self.gauge_title_text + '\n'
            
            last = self.last_gauge_selected #'Sam' 'Ruby' 'None'
            
            if last == 'Ruby':
                header+= 'Ruby λ₀ (nm) = ' + str(self.ruby_lambda_zero) + '\n'
                #T(λ) and T(λ₀) already in the title

            elif last == 'Sam':
                header+= 'Sam λ₀ (nm) = ' + str(self.sam_lambda_zero) + '\n'
                

            if self.data_from_file_x is not None:
                #working on file
                header+= f'Filename = {Path(self.opened_filename)}\n'
            else:
                header+= f'Spectrometer = {self.spectrometer_model} sn {self.spec.SN}\n'
                if self.controls.spec_checkb_calib.isChecked():
                #if self.calib.get():
                    header+= f'User Calibration = {self.calib_controls.calib_cn}\n'
                else:
                    header+= 'Used No Calibration\n'
                #header+= f'Electronic Dark = {self.dark.get()}\n'
                if self.controls.spec_checkb_bkgUse.isChecked():
                    header+= 'Background Subtracted\n'
            
                header+= 'Int Time (s) = ' + self.controls.meas_button_intTime.text() + '\n'
                header+= 'Accumulation = ' + self.controls.meas_button_acc.text() + '\n'
            
            #print(header)
            return header
            
        except:
            pop_up_error(traceback.format_exc(), 'create_header Error')
            return ''
    
    #Gauge section
    
    def calc_all_ruby_pressures(self):
        # See Gauge_eq_Ruby
        #print('Ruby L selected')
        self.last_ruby_selected = 'Ruby L selected'
        L0 = self.ruby_lambda_zero
        T0 = self.ruby_T_lambda_zero
        #print(self.rubycond_calculator.controls)
        lambda_value = self.rubycond_calculator.controls.ruby_lambda 
        #print(lambda_value)
        T_value = self.ruby_T_lambda 

            #self.Ruby_calc_T_value.set('298')
            #T_value = 298

        temperature_gauge = str(self.controls.gaugetabRuby_combob_Tcalib.currentText())
        # pressure_gauge_m = self.controls.gaugetabRuby_combob_gauge.currentText()
        # pressure_gauge_i = self.controls.gaugetabRuby_combob_gauge.currentIndex()
        #print(self.Ruby_calc_all_P_gauges[pressure_gauge_i])
        
        header = 'Ruby λ selected\n'
        header+= f'λ = {lambda_value} nm, '
        
        if temperature_gauge == "Datchi 2004":
            f = RS.Ruby_Datchi_T
            P = [g(f(T_value,lambda_value),f(T0,L0)) for g in self.Ruby_calc_all_P_gauges]
            header+= f'T(λ) = {T_value}, Datchi 2004 \n'
            header+= f'λ₀ = {L0} nm, T(λ₀) = {T0} \n\n'
        else:
            P = [g(lambda_value,L0) for g in self.Ruby_calc_all_P_gauges]
            header+= 'T(λ) Not Used \n'
            header+= f'λ₀ = {L0} nm, T(λ₀) Not Used \n\n'
        
        #nice_output = self.ruby_format_output_str(P)
        
        P= [lambda_value, L0, T_value, T_value - 273.15] + P

        #print(P)
    
    def eee(self):
        fit = self.fit.fit_function
        if fit[:6] == 'Double':
            print('Double')
            center = self.fit.out.params["pk_1_center"].value
        else:
            print('Single')
            center = self.fit.out.params["pk_1_center"].value
        print(center)
    
    def command_gaugetabSam_button_snap(self):
        #print('command_gaugetabRuby_button_snap')
        if self.fit.out is not None:
            title = self.sam_figure_title()
            self.graph_1.set_title(title)
            self.gauge_title_text = title
            self.last_gauge_selected = 'Sam'  #'Sam' 'Ruby'
            
            self.graph_1.fig.tight_layout()
            self.graph_1.canvas.draw()
            
    def command_gaugetabRuby_button_snap(self):
        #print('command_gaugetabRuby_button_snap')
        if self.fit.out is not None:
            title = self.ruby_figure_title()
            self.graph_1.set_title(title)
            self.gauge_title_text = title
            self.last_gauge_selected = 'Ruby'  #'Sam' 'Ruby' 'None'
            
            self.graph_1.fig.tight_layout()
            self.graph_1.canvas.draw()
    
    def command_gaugetab_button_clean(self):
        title = ''
        self.graph_1.set_title(title)
        self.gauge_title_text = title
        self.last_gauge_selected = 'None'  #'Sam' 'Ruby' 'None'
        
        self.graph_1.fig.tight_layout()
        self.graph_1.canvas.draw()
        
    def sam_figure_title(self):
        header = ''
        fit = self.fit.fit_function
        if fit[:6] == 'Double':
            #print('Double')
            lambda_cm1 = self.fit.out.params["pk_1_center"].value
            sigma_cm1 = self.fit.out.params["pk_1_gamma"].value
        else:
            #print('Single')
            lambda_cm1 = self.fit.out.params["pk_1_center"].value
            sigma_cm1 = self.fit.out.params["pk_1_sigma"].value
            
        lambda_value_nm = 1e7/lambda_cm1
        sigma_value_nm = 1e7/(lambda_cm1-sigma_cm1) - 1e7/(lambda_cm1+sigma_cm1)
        self.header_lambda_value_nm = lambda_value_nm
        self.header_sigma_value_nm = sigma_value_nm
        
        L0 = self.sam_lambda_zero 


        pressure_gauge_m = self.controls.gaugetabSam_combob_gauge.currentText()
        pressure_gauge_i = self.controls.gaugetabSam_combob_gauge.currentIndex()
        

        g = self.Sam_calc_all_P_gauges[pressure_gauge_i]
        
        P = g(lambda_value_nm,L0) 
        
        self.header_pressure = P
        
        header+= f"P '{pressure_gauge_m}' "
        header+= f'P = {P:.2f} GPa \n'
        header+= f'Sam λ = {lambda_value_nm:.2f} σ {sigma_value_nm:.2f} nm'
        
        return header
    
    def ruby_figure_title(self):
        header = ''
        fit = self.fit.fit_function
        if fit[:6] == 'Double':
            #print('Double')
            lambda_cm1 = self.fit.out.params["pk_1_center"].value
            sigma_cm1 = self.fit.out.params["pk_1_gamma"].value
        else:
            #print('Single')
            lambda_cm1 = self.fit.out.params["pk_1_center"].value
            sigma_cm1 = self.fit.out.params["pk_1_sigma"].value
            
        lambda_value_nm = 1e7/lambda_cm1
        sigma_value_nm = 1e7/(lambda_cm1-sigma_cm1) - 1e7/(lambda_cm1+sigma_cm1)
        self.header_lambda_value_nm = lambda_value_nm
        self.header_sigma_value_nm = sigma_value_nm
        
        L0 = self.ruby_lambda_zero
        T0 = self.ruby_T_lambda_zero
        #print(self.rubycond_calculator.controls)
        
        
        #print(lambda_value)
        T_value = self.ruby_T_lambda 

        temperature_gauge = str(self.controls.gaugetabRuby_combob_Tcalib.currentText())
        pressure_gauge_m = self.controls.gaugetabRuby_combob_gauge.currentText()
        pressure_gauge_i = self.controls.gaugetabRuby_combob_gauge.currentIndex()
        #print(self.Ruby_calc_all_P_gauges[pressure_gauge_i])
        
        
        
        g = self.Ruby_calc_all_P_gauges[pressure_gauge_i]
        
        if temperature_gauge == "Datchi 2004":
            f = RS.Ruby_Datchi_T
            
            P = g(f(T_value,lambda_value_nm),f(T0,L0)) 

        else:
            P = g(lambda_value_nm,L0) 
            
        self.header_pressure = P
        
        header+= f"P '{pressure_gauge_m}' "
        header+= f'P = {P:.2f} GPa \n'
        if temperature_gauge == "Datchi 2004":
            header+= f"T 'Datchi 2004' T(λ) = {T_value:.2f} T(λ₀) = {T0:.2f} K\n"
        header+= f'Ruby R1 λ = {lambda_value_nm:.2f} σ {sigma_value_nm:.2f} nm'
        
        
        return header
    
    def ruby_format_output_str(self, pres):
        ruby_output = ''
        
        for val, i in enumerate(self.ruby_pressure_gauge):
            #ruby_output+= f'{val:.2f} Gpa {i:<30} \n'
            ruby_output+= f'{pres[val]:.2f} GPa {i} \n'
        return ruby_output
    
    def init_gauge(self):
        #Ruby
        fixed_tab_width = 150
        self.gauge_title_text = ''
        self.last_gauge_selected = 'None' #'Sam' 'Ruby' 'None'
        
        self.ruby_pressure_gauge = self.rubycond_calculator.controls.ruby_pressure_gauge
        self.controls.gaugetabRuby_combob_gauge.setFixedWidth(fixed_tab_width)
        self.controls.gaugetabRuby_combob_gauge.addItems(self.ruby_pressure_gauge)
        
        
        self.temperature_gauge = self.rubycond_calculator.controls.temperature_gauge
        self.controls.gaugetabRuby_combob_Tcalib.addItems(self.temperature_gauge)
        
        self.sam_pressure_gauge = self.rubycond_calculator.controls.sam_pressure_gauge
        self.controls.gaugetabSam_combob_gauge.setFixedWidth(fixed_tab_width)
        self.controls.gaugetabSam_combob_gauge.addItems(self.sam_pressure_gauge)
        
        self.Ruby_calc_all_P_gauges = self.rubycond_calculator.controls.Ruby_calc_all_P_gauges
        self.Sam_calc_all_P_gauges = self.rubycond_calculator.controls.Sam_calc_all_P_gauges
        
        

        self.action_gaugetabRuby_combob_gauge = self.ActionCombo(self.menu_ruby_combob_Pcalib, self.ruby_pressure_gauge, self.command_gaugetabRuby_combob_gauge)                             #WIPDONE
        self.controls.gaugetabRuby_combob_gauge.activated.connect(self.command_gaugetabRuby_combob_gauge)
        
        self.action_gaugetabSam_combob_gauge = self.ActionCombo(self.menu_sam_combob_Pcalib, self.sam_pressure_gauge, self.command_gaugetabSam_combob_gauge)                             #WIPDONE
        self.controls.gaugetabSam_combob_gauge.activated.connect(self.command_gaugetabSam_combob_gauge)
        
        self.action_gaugetabRuby_combob_Tcalib = self.ActionCombo(self.menu_ruby_combob_Tcalib, self.temperature_gauge, self.command_gaugetabRuby_combob_Tcalib)                             #WIPDONE
        self.controls.gaugetabRuby_combob_Tcalib.activated.connect(self.command_gaugetabRuby_combob_Tcalib)
        
        
        #Init values 
        
        self.update_ruby_lambda_zero(694.25)        #set self.ruby_lambda_zero
        self.update_ruby_T_lambda(273.15+20)        #set self.ruby_T_lambda
        self.update_ruby_T_lambda_zero(273.15+20)   #set self.ruby_T_lambda_zero
        
        self.update_control_gaugetabRuby_combob_gauge(self.ruby_pressure_gauge[0])
        self.update_control_gaugetabRuby_combob_Tcalib(self.temperature_gauge[0])
        
        self.update_sam_lambda_zero(685.51)
        
        #self.sam_pressure_gauge = self.rubycond_calculator.controls.sam_pressure_gauge
    
    def calc_Sam_pressures(self):
        print('calc_Sam_pressures')
    
    def command_log_checkb_ONOFF(self, value):
        self.model.statusbar_message('Not yet implemented')
        # #value = checkbox value
        # self.action_log_checkb_ONOFF.setChecked(value)
        # self.controls.log_checkb_ONOFF.setChecked(value)
        # if value:
        #     self.model.statusbar_message('Logger is ON')
        # else:
        #     self.model.statusbar_message('Logger is OFF')
        
    def command_gaugetabSam_checkb_cont(self, value):

        #value = checkbox value
        self.action_gaugetabSam_checkb_cont.setChecked(value)
        self.controls.gaugetabSam_checkb_cont.setChecked(value)
        
        self.gaugetabSam_checkb_cont_value = value 
        self.controls.tabs_gauge.setTabEnabled(0, not value)    #Disable Ruby tab
        self.menu_gaugetabRuby.setEnabled(not value)    #Disable Ruby menu
        
        if value:
            self.model.statusbar_message('Gauge Samarium continuous  is ON')
        else:
            self.model.statusbar_message('Gauge Samarium continuous  is OFF')
            
    def command_gaugetabRuby_checkb_cont(self, value):

        #value = checkbox value
        self.action_gaugetabRuby_checkb_cont.setChecked(value)
        self.controls.gaugetabRuby_checkb_cont.setChecked(value)
        #self.main_tabs.setTabEnabled(1, value)
        
        self.gaugetabRuby_checkb_cont_value = value
        self.controls.tabs_gauge.setTabEnabled(1, not value)    #Disable Samarium tab
        self.menu_gaugetabSam.setEnabled(not value)    #Disable Samarium menu
        
        if value:
            self.model.statusbar_message('Gauge Ruby continuous  is ON')
        else:
            self.model.statusbar_message('Gauge Ruby continuous  is OFF')
            
        
    
    def command_gaugetabSam_combob_gauge(self):
        ''' only sync labels'''
        sender = self.sender()
        
        if type(sender) == QtWidgets.QComboBox:
            value = self.sender().currentText()
        if type(sender) == QtWidgets.QAction:   
            value = self.sender().text()
        
        self.update_control_gaugetabSam_combob_gauge(value)
    
    def update_control_gaugetabSam_combob_gauge(self, value):
        self.SPG = value
        self.controls.gaugetabSam_combob_gauge.setCurrentText(value)
        #self.controls.fit_combob_func.setCurrentText(value)
        for action in self.action_gaugetabSam_combob_gauge:
            if action.text() == value:
                action.setChecked(True)
        self.model.statusbar_message('Samarium P Gauge = ' + value)
        
        

    
    def command_gaugetabRuby_combob_Tcalib(self):
        ''' only sync labels'''
        sender = self.sender()
        
        if type(sender) == QtWidgets.QComboBox:
            value = self.sender().currentText()
        if type(sender) == QtWidgets.QAction:   
            value = self.sender().text()
        
        self.update_control_gaugetabRuby_combob_Tcalib(value)
    
    def update_control_gaugetabRuby_combob_Tcalib(self, value):
        
        self.controls.gaugetabRuby_combob_Tcalib.setCurrentText(value)
        #self.controls.fit_combob_func.setCurrentText(value)
        for action in self.action_gaugetabRuby_combob_Tcalib:
            if action.text() == value:
                action.setChecked(True)
        self.RTG = value
        self.model.statusbar_message('Ruby T Calib = ' + value)
        
    def command_gaugetabRuby_combob_gauge(self):
        ''' only sync labels'''
        sender = self.sender()
        
        if type(sender) == QtWidgets.QComboBox:
            value = self.sender().currentText()
        if type(sender) == QtWidgets.QAction:   
            value = self.sender().text()
        
        self.update_control_gaugetabRuby_combob_gauge(value)
        
        
    def update_control_gaugetabRuby_combob_gauge(self, value):
        
        self.controls.gaugetabRuby_combob_gauge.setCurrentText(value)
        #self.controls.fit_combob_func.setCurrentText(value)
        for action in self.action_gaugetabRuby_combob_gauge:
            if action.text() == value:
                action.setChecked(True)
        self.RPG = value
        self.model.statusbar_message('Ruby P Gauge = ' + value)
        
        
    def update_ruby_T_lambda(self, value):
        self.ruby_T_lambda = value
        message = f"{self.ruby_T_lambda:.2f} K / {self.ruby_T_lambda - 273.15:.2f} °C "
        self.controls.gaugetabRuby_button_Tlambda.setText(message)
        self.action_gaugetabRuby_button_Tlambda.setText(message)
        self.model.statusbar_message("T(λ) = " + message)
        
    def command_gaugetabRuby_button_Tlambda(self):
        title = 'Change Value'
        label = 'Enter new T(λ) value in K'
        value = self.ruby_T_lambda
        minvalue = -1
        maxvalue = 10000
        new_value, ok = QtWidgets.QInputDialog.getDouble(self, title, label , value, minvalue, maxvalue, decimals=2)
        if ok:
            if new_value <=0:
                self.update_ruby_T_lambda(273.15+20)
            else:
                self.update_ruby_T_lambda(new_value)

    def update_ruby_T_lambda_zero(self, value):
        self.ruby_T_lambda_zero = value
        message = f"{self.ruby_T_lambda_zero:.2f} K / {self.ruby_T_lambda_zero - 273.15:.2f} °C "
        self.controls.gaugetabRuby_button_Tlambda0.setText(message)
        self.action_gaugetabRuby_button_Tlambda0.setText(message)
        self.model.statusbar_message("T(λ₀) = " + message)
        
    def command_gaugetabRuby_button_Tlambda0(self):
        title = 'Change Value'
        label = 'Enter new T(λ₀) value in K'
        value = self.ruby_T_lambda_zero
        minvalue = 0
        maxvalue = 10000
        new_value, ok = QtWidgets.QInputDialog.getDouble(self, title, label , value, minvalue, maxvalue, decimals=2)
        if ok:
            if new_value <=0:
                self.update_ruby_T_lambda_zero(273.15+20)
            else:
                self.update_ruby_T_lambda_zero(new_value)
    
    def update_sam_lambda_zero(self, value):
        self.sam_lambda_zero = value
        self.controls.gaugetabSam_button_lambda0.setText(f"{self.sam_lambda_zero:.2f} nm") 
        self.action_gaugetabSam_button_lambda0.setText(f"{self.sam_lambda_zero:.2f} nm")
        self.model.statusbar_message(f"Samarium λ₀ = {self.sam_lambda_zero:.2f} nm")
        
    def command_gaugetabSam_button_lambda0(self): #change_ruby_lambda(self):
        title = 'Change Value'
        label = 'Enter new λ₀ value in nm'
        value = self.sam_lambda_zero
        minvalue = 0
        maxvalue = 10000
        new_value, ok = QtWidgets.QInputDialog.getDouble(self, title, label , value, minvalue, maxvalue, decimals=2)
        if ok:
            self.update_sam_lambda_zero(new_value)
            
    def update_ruby_lambda_zero(self, value):
        self.ruby_lambda_zero = value
        self.controls.gaugetabRuby_button_lambda0.setText(f"{self.ruby_lambda_zero:.2f} nm") 
        self.action_gaugetabRuby_button_lambda0.setText(f"{self.ruby_lambda_zero:.2f} nm")
        self.model.statusbar_message(f"Ruby λ₀ = {self.ruby_lambda_zero:.2f} nm")
        
    def command_gaugetabRuby_button_lambda0(self): #change_ruby_lambda(self):
        title = 'Change Value'
        label = 'Enter new λ₀ value in nm'
        value = self.ruby_lambda_zero
        minvalue = 0
        maxvalue = 10000
        new_value, ok = QtWidgets.QInputDialog.getDouble(self, title, label , value, minvalue, maxvalue, decimals=2)
        if ok:
            self.update_ruby_lambda_zero(new_value)
            

            
    def init_thread_B_read_temperature(self):
        #Thread B Read temperature from spectrometer
        #2 import from Driver_Andor
        from my_drivers.Driver_Andor import spectrometer_thread_get_temperature
        
        self.thread_B_read_temperature = spectrometer_thread_get_temperature(self.spec)             #Thread_1B) Create Thread
        self.thread_B_read_temperature.signal_temperature.connect(self.method_update_temperature)   #Thread_2B) Connect Thread Status Signal to action in main (i.e. update status bar)
        
        
        self.signal_thread_B_read_temperature.connect(self.thread_B_read_temperature.start)         #Thread_3B) Connect main launcher signal (i.e. in start button) to Thread Start process 

        self.thread_B_read_temperature.moveToThread(self.main_thread_B)                       #Thread_4B) Move every Thread to Main Thread
        
    def init_thread_A_read_data(self):
        #Thread A Read data from spectrometer
        self.thread_A_read_data = spectrometer_thread_get_intensities(self.spec)            #Thread_1A) Create Thread
        self.thread_A_read_data.signal_status.connect(self.method_update_status)            #Thread_2A) Connect Thread Status Signal to action in main (i.e. update status bar)
        self.thread_A_read_data.signal_done.connect(self.method_update_done) 
        self.thread_A_read_data.signal_fit_done.connect(self.method_update_fit_plot) 
        self.signal_thread_A_read_data.connect(self.thread_A_read_data.start)               #Thread_3A) Connect main launcher signal (i.e. in start button) to Thread Start process 

        self.thread_A_read_data.moveToThread(self.main_thread_A)                              #Thread_4A) Move every Thread to Main Thread

        
    def test_status(self, data):
        print('Status ', datetime.now().strftime("%H:%M:%S"))
        print(data)
    
    def method_update_done(self):
        if self.spec.abort:
            self.spec.abort = False
            self.spec.thread_accumulation_i = 1
        self.thread_reading = False
        #print('Done ', datetime.now().strftime("%H:%M:%S"))
        
    #Spectrometer section
    
    def command_spec_button_connect(self):

        try:
            #try to  import the drivers
            
            if self.spectrometer_model == "OceanOptics":
                from my_drivers.Driver_OO import spectrometer
                
                
            elif self.spectrometer_model == "Andor":
                #2 import from Driver_Andor
                from my_drivers.Driver_Andor import spectrometer
                
            self.spec = spectrometer(self.fit, self.debug)
            
            
            self.model.statusbar_message(self.spectrometer_model + " model selected")
            
            if self.spec.connect_first():
                
                self.main_thread_A = QtCore.QThread()                                                 #Thread_0) Create main Thread, only 1 Time
                
                
                self.init_thread_A_read_data()                                                      #Thread_A) thread_A_read_data
                self.main_thread_A.start()  
                if self.spectrometer_model == "Andor":
                    self.main_thread_B = QtCore.QThread()
                    self.init_thread_B_read_temperature()                                           #Thread_B) thread_B_read_temperature
                    self.main_thread_B.start() 
                    self.controls.group_measTemp.setVisible(True)       #Andor cooling controls
                    self.menu_measTemp.menuAction().setVisible(True)    #Thread_5) Start Main Thread, only 1 Time
                    self.update_measTemp_button_target(self.init_target_cooler_temperature)
                
                
                #self.action_spec_button_group_measTemp.setDisabled(True)
                
                self.controls.spec_button_connect.setDisabled(True)
                self.controls.spec_label_connect.setText(self.spec.SN[:13])  #Max 13 characters (= 'Substract bkg)
                
                self.controls.spec_button_calibPar.setDisabled(False)
                self.action_spec_button_calibPar.setDisabled(False)
                
                self.controls.spec_button_calibrator.setDisabled(False)
                self.action_spec_button_calibrator.setDisabled(False)
                
                self.controls.spec_checkb_calib.setDisabled(False)
                self.action_spec_checkb_calib.setDisabled(False)
                
                self.controls.spec_button_bkgTake.setDisabled(False)
                self.action_spec_button_bkgTake.setDisabled(False)
                
                self.controls.spec_checkb_bkgUse.setDisabled(False)
                self.action_spec_checkb_bkgUse.setDisabled(False)
                
                self.controls.group_meas.setDisabled(False)
                self.menu_meas.setDisabled(False)
                
                self.controls.group_fit.setDisabled(False)
                self.menu_fit.setDisabled(False)
                
                self.controls.group_gauge.setDisabled(False)
                
                #self.controls.group_log.setDisabled(False)
                #self.menu_log.setDisabled(False)
                
                #Init Fit
    
                self.fit.wavelengths_units = 'nm'
                self.fit.fit_set_x(self.spec.wavelengths)
                self.fit.intensities = np.zeros_like(self.fit.wavelengths)
                
                self.graph_1.data_x = self.spec.wavelengths
                self.graph_1.plot_reset()  #reset graph if switch open file / connect
                
                print('\n', self.graph_1.data_x.shape, '\n')
                #Init Spectro
                
                self.spec.set_integration_time(0.1) #0.1 S
                #self.update_control_meas_intTime(self.spec.integration_time_value_microsec/1e6)
                self.update_control_meas_intTime(self.spec.integration_time_value)
                self.update_control_meas_acc(self.spec.accumulations_n)
                
                
                self.model.statusbar_message('Connected Spectrometer ' + self.spec.SN)
                self.data_from_file_x = None  #Used as a reference if working on file condition
                
                #correct x_label
                self.update_graph_xlabel()
                self.graph_1.canvas.draw()
                
                self.command_spec_checkb_calib(True)
                
            else:
                self.model.statusbar_message(self.spectrometer_model + ' spectrometer Connection Error')
                pop_up_error(self.spectrometer_model + " spectrometer not found", 'Connection Error')
                
        except:
            self.model.statusbar_message(self.spectrometer_model + ' spectrometer Connection Error')
            pop_up_error(traceback.format_exc(), 'Driver Error')    
        
            
            
    
    def method_update_calib_cn(self, calib_cn : list):
        self.calib_cn = calib_cn
        
        #If Use calib checked update values
        if self.controls.spec_checkb_calib.isChecked():
            
            self.command_spec_checkb_calib(True)
            print('Update')
        #print(self.calib_cn)
        
        # if self.action_spec_checkb_calib.isChecked():
        #     #using calib, update value
        #     x = np.arange(len(self.graph_1.data_x))
        #     new_x = self.calib_cn[0] + self.calib_cn[1]*x + self.calib_cn[2]*x**2 + self.calib_cn[3]*x**3 
            
        #     #print((new_x == 0).sum())
        #     error = (new_x == 0).sum()
        #     if error :
        #         message = 'Error, there is a 0 value in the X array'
        #         self.model.statusbar_message(message)
        #         pop_up_error(message, 'Data Error')
        #         self.action_spec_checkb_calib.setChecked(False)
        #         self.controls.spec_checkb_calib.setChecked(False)
    
        #     else:
        #         message = 'New scale ' + str(self.calib_cn)
        #         self.model.statusbar_message(message)
                
        #         self.graph_1.data_x = new_x
                
        #         if self.graph_1.data_plot_ref is not None:
        #             self.graph_1.data_plot_ref.set_xdata(new_x)
        #         self.fit.fit_set_x(new_x)
        #         self.graph_1.erase_fit_plot()
        #         self.graph_1.autoscale_ax()
                
            
    def command_spec_checkb_calib(self, value):
        
        self.graph_1.erase_fit_plot()
        
        self.action_spec_checkb_calib.setChecked(value)
        self.controls.spec_checkb_calib.setChecked(value)

        if value:
            #Use calib
            x = np.arange(len(self.graph_1.data_x))
            new_x = self.calib_cn[0] + self.calib_cn[1]*x + self.calib_cn[2]*x**2 + self.calib_cn[3]*x**3 
            
        else:
            #back to original data
            if self.data_from_file_x is not None:
                #working on file
                new_x = self.data_from_file_x
            else:
                new_x = self.spec.wavelengths
    
        
        # if (new_x == 0).sum() :
        #     message = 'Error, there is a 0 value in the X array'
        #     self.model.statusbar_message(message)
        #     pop_up_error(message, 'Data Error')
        #     self.action_spec_checkb_calib.setChecked(not value)
        #     self.controls.spec_checkb_calib.setChecked(not value)

        # else:
        self.graph_1.data_x = new_x
        
        if self.graph_1.data_plot_ref is not None:
            self.graph_1.data_plot_ref.set_xdata(new_x)
        
        condition = ((new_x == 0).sum() == 0) #No zero in X
        
        # print(self.calib_cn)
        # print(new_x)
        # print((new_x == 0).sum())
        # print(condition)
        
        if condition:
            self.controls.group_fit.setDisabled(False)
            self.menu_fit.setDisabled(False)
            
            self.fit.fit_set_x(new_x)
            print(new_x.min())
            self.set_control_fit_min(new_x.min())
            self.set_control_fit_max(new_x.max())
        else:
            self.controls.group_fit.setDisabled(True)
            self.menu_fit.setDisabled(True)
            
            self.graph_1.remove_red_lines()
        
        self.graph_1.erase_fit_plot()
        self.graph_1.autoscale_ax()
        
        self.update_graph_xlabel()
            
        self.graph_1.canvas.draw()
        
    def update_graph_xlabel(self):
        
        value = self.controls.spec_checkb_calib.isChecked()

        if self.data_from_file_x is not None:
            #working on file
            if value:
                self.graph_1.ax_1.set_xlabel('Wavelength (nm)')
            else:
                self.graph_1.ax_1.set_xlabel('Wavelength (file data)')
        else:
            #spectrometer data
            if value:
                if self.spectrometer_model == "OceanOptics":
                    self.graph_1.ax_1.set_xlabel('Wavelength (calib nm)')
                elif self.spectrometer_model == "Andor":
                    self.graph_1.ax_1.set_xlabel('Wavelength (nm)')
            else:
                if self.spectrometer_model == "OceanOptics":
                    self.graph_1.ax_1.set_xlabel('Wavelength (OO nm)')
                elif self.spectrometer_model == "Andor":
                    self.graph_1.ax_1.set_xlabel('Wavelength (pixel)')
        
    def method_update_status(self, data, thread_accumulation_i):
        
        if self.fit.bkg:
            if len(data) == len(self.fit.intensities_bkg):
                data = data - self.fit.intensities_bkg
            else:
                pop_up_error('The background in memory and the current measurement have different lengths')
                self.action_spec_checkb_bkgUse.setChecked(False)
                self.controls.spec_checkb_bkgUse.setChecked(False)
                self.fit.bkg = False
        
        if self.gaugetabRuby_checkb_cont_value:
            if self.fit.out is not None:
                title = self.ruby_figure_title()
                self.graph_1.set_title(title)
                self.gauge_title_text = title
                #self.graph_1.canvas.draw()  Already in plot_data
        
        if self.gaugetabSam_checkb_cont_value:
            if self.fit.out is not None:
                title = self.sam_figure_title()
                self.graph_1.set_title(title)
                self.gauge_title_text = title
                #self.graph_1.canvas.draw()  Already in plot_data
        
        self.graph_1.fig.tight_layout()
        self.graph_1.plot_data(data)
        

        
        
        # if self.spec.thread_continuous == False:
        #     self.graph_1.autoscale_ax()
        #print(thread_accumulation_i, self.spec.accumulations_n)
        self.controls.meas_pbar.setValue(int((thread_accumulation_i)/self.spec.accumulations_n*100))
        now = datetime.now().timestamp()
        dt =  now - self.timestamp_now
        
        text = f'Update {thread_accumulation_i}/{self.spec.accumulations_n} dt {dt:.2f}'#' sec @{now} {self.timestamp_now}'
        self.timestamp_now = now
        self.model.statusbar_message(text)
    
    def open_input_dialog_float(self, title, label, value, minvalue, maxvalue):
        ''' 
        Scientific notation not allowed in QInputDialog.getDouble
        Return float, OK
        '''
        newvalue, ok = QtWidgets.QInputDialog.getText(self, title, label, text = str(value))
        # print('newvalue = ', newvalue)
        # print('OK = ', ok)
        if ok and newvalue:
            try:
                newvalue = float(newvalue)
                if (newvalue > minvalue) & (newvalue < maxvalue):
                    return newvalue, 1
                else:
                    return None, 0
            except:
                return None, 0
        else:
            return None, 0
    
    #File section
    
    def method_file_open_file_all(self, data, filename):
        self.opened_filename = filename
        self.model.statusbar_message('Loaded data from ' + self.opened_filename)
        
    def method_file_open_file_xy(self, data_x, data_y, filename):
        
        
        
        self.graph_1.erase_fit_plot()
        self.graph_1.remove_red_lines()
        
        if self.thread_reading:
            self.model.statusbar_message('Stopping meas ...')
            self.spec.abort = True
            self.spec.set_integration_time(0.1)
            self.update_control_meas_intTime(0.1)
            self.model.statusbar_message('Meas Stopped')
            
            self.controls.meas_checkb_acq.setChecked(False)
            self.action_meas_checkb_acq.setChecked(False)
        
        
        self.opened_filename = filename
        self.model.statusbar_message('Loaded data from ' + self.opened_filename)
        
        self.data_from_file_x = data_x
        self.data_from_file_y = data_y
        
        self.fit.fit_set_x(self.data_from_file_x)
        self.graph_1.data_x = self.data_from_file_x
        
        
        

        self.graph_1.plot_reset()  #reset graph if switch open file / connect
        self.graph_1.plot_data(self.data_from_file_y)   #update y value
        
        
        #self.controls.spec_button_connect.setDisabled(False)
        condition = ((data_x == 0).sum() == 0) #No zero in X

        if condition:
            self.controls.group_fit.setDisabled(False)
            self.menu_fit.setDisabled(False)
        
        self.controls.spec_button_calibPar.setDisabled(False)
        self.action_spec_button_calibPar.setDisabled(False)
        
        self.controls.spec_button_calibrator.setDisabled(False)
        self.action_spec_button_calibrator.setDisabled(False)
        
        self.controls.spec_checkb_calib.setDisabled(False)
        self.action_spec_checkb_calib.setDisabled(False)
        
        self.controls.spec_button_bkgTake.setDisabled(False)
        self.action_spec_button_bkgTake.setDisabled(False)
        
        self.controls.spec_checkb_bkgUse.setDisabled(False)
        self.action_spec_checkb_bkgUse.setDisabled(False)
    
        self.controls.group_meas.setDisabled(True)
        self.menu_meas.setDisabled(True)
        
        #self.controls.group_log.setDisabled(True)
        #self.menu_log.setDisabled(True)
        
        if self.spec.connected:
            self.spec.close()
        self.controls.spec_button_connect.setDisabled(False)
        self.controls.spec_label_connect.setText('')  #Max 13 characters (= 'Substract bkg)
        
        self.command_spec_checkb_calib(False)
        
        self.graph_1.autoscale_ax()
        
    def command_file_open_file(self):
        
        #self.action_spec_button_connect.setDisabled(True)
        #self.controls.spec_button_connect.setDisabled(True)
        
        self.rubycond_open_file.tab_data.clear()
        self.rubycond_open_file.tab_fig.reset()
        self.rubycond_open_file.tab_fig.canvas.draw()
        self.rubycond_open_file.show()
        
    def command_file_save_data(self):
        
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self,"Select File", datetime.now().strftime("%y%m%d_%H%M%S"))
        
        if filename != '':
            filename = Path(filename)
            #self.save_data(Path(filename))
            
            self.save_fig(filename)
            self.save_data(filename)
            self.save_header(filename)
            self.save_header_fit_report(filename)
            
            self.model.statusbar_message('Data Saved')
        else:
            self.model.statusbar_message('Data Save Cancelled')
    
    def save_logger(self):
        filename = self.logger_folder / datetime.now().strftime("%y%m%d_%H%M%S")
        self.save_fig(filename)
        self.save_data(filename)
        self.save_header(filename)
        self.save_header_fit_report(filename)
        
    def save_header(self, filename : Path):
        #Save header
        filename = filename.with_name(filename.stem + '_header.rtf')
        filename.write_text(self.create_header(), encoding="utf-8") 
    
    def save_header_fit_report(self, filename : Path):
        #Save header
        filename = filename.with_name(filename.stem + '_header.rtf')
        filename.write_text(self.create_header() +  '\n    Fit Report\n\n' + self.fit.fit_report, encoding="utf-8")
        
    def save_fig(self, filename : Path):
        #Save figure
        f = filename.with_name(filename.stem + '_img.png')
        self.graph_1.fig.savefig(f, dpi=300, format='png')
        
    def save_data(self, filename : Path):
        try:
            if self.controls.spec_checkb_bkgUse.isChecked():
                data = np.c_[self.spec.wavelengths, self.spec.average_intensities, self.fit.intensities_bkg]
                csv_header = ('wavelengths, average_intensities, background')
            else:
                data = np.c_[self.spec.wavelengths, self.spec.average_intensities]
                csv_header = ('wavelengths, average_intensities')

            if debug: print(filename)
            if debug: print(self.spec.average_intensities)
            if debug: print(data.shape)
            
            f = filename.with_name(filename.stem + '_data.txt')
            
            if self.save_data_format_txt : np.savetxt(f.with_suffix('.txt'), data, fmt='%s')
            if self.save_data_format_csv : np.savetxt(f.with_suffix('.csv'), data, fmt='%s', delimiter = ",", header = csv_header)#, header = 'seconds, temperature, pressure, timestamp, date')
            if self.save_data_format_npy : np.save(f.with_suffix('.npy'), data)
            
            if self.spec.accumulations_n > 1:
                #data = np.c_[self.spec.wavelengths,self.spec.average_intensities, self.thread_accumulation_data]
                data = self.spec.thread_accumulation_data
                f = filename.with_name(filename.stem + '_data_All.txt')
                
                
                if self.save_data_format_txt : np.savetxt(f.with_suffix('.txt'), data, fmt='%s')
                if self.save_data_format_csv : np.savetxt(f.with_suffix('.csv'), data, fmt='%s', delimiter = ",")#, header = 'seconds, temperature, pressure, timestamp, date')
                if self.save_data_format_npy : np.save(f.with_suffix('.npy'), data)
                
        except:
            pop_up_error(traceback.format_exc(), 'Pythony Error')
            self.model.statusbar_message('Data Save Error')
            
    #FIT section
    

    
    
            
            
    def command_fit_button_report(self):
        time = datetime.now().strftime("%H:%M:%S")
        self.report_window.setWindowTitle('Report ' + time)
        self.report_window.label.setText(self.fit.fit_report)
        print(self.report_window.isVisible())
        
        self.report_window.show()
        
        #self.report_window('Report Window ' + time, message).show()
        
    def command_fit_button_iterLim(self):
        pass
    
        minvalue = 1
        maxvalue = 100000
        value = self.fit.max_nfev

        title = 'Maximum number of function evaluations'
        label = f'min {minvalue} max {maxvalue}'
        new_value, ok = QtWidgets.QInputDialog.getInt(self, title, label , value, minvalue, maxvalue)
        
        if ok:
            self.update_control_fit_iterLim(new_value)
        else:
            self.model.statusbar_message(f'Error: Maximum number of function evaluations = {value}')
    
    def command_fit_button_bkgDeg(self):
        self.spec.thread_fit_lock = True #Prevent fit in thread before re-initializing
    
        minvalue = 1
        maxvalue = 7
        value = self.fit.polynomial_degree

        title = 'Backgound polynomial degree'
        label = f'min {minvalue} max {maxvalue}'
        new_value, ok = QtWidgets.QInputDialog.getInt(self, title, label , value, minvalue, maxvalue)
        
        if ok:
            self.update_control_fit_bkgDeg(new_value)
        else:
            self.model.statusbar_message(f'Error: Backgound polynomial degree = {value}')
        
        self.spec.thread_fit_lock = False #Prevent fit in thread before re-initializing
    
    def command_fit_button_min(self):
        
        self.spec.thread_fit_lock = True #Prevent fit in thread before re-initializing
        
        minvalue = self.fit.wavelengths.min()
        maxvalue = self.fit.wavelengths.max()
        
        
        # minvalue = self.graph_1.data_x.min()
        # maxvalue = self.graph_1.data_x.max()
        
        value = self.fit.wavelengths_min
        
        if value is None:
            value = minvalue
            
        #print(value, minvalue, maxvalue)
        
        title = 'Fit Min limit'
        label = f'min {minvalue:.1f} max {maxvalue:.1f} actual value {value:.1f}'
        
        if self.graph_1.click is not None:
            value = self.graph_1.click[3]
        
        new_value, ok = QtWidgets.QInputDialog.getDouble(self, title, label , value, minvalue, maxvalue)

        if ok:
            self.set_control_fit_min(new_value)
        else:
            self.model.statusbar_message(f'Error: Min Value = {value:.1f}')
            self.spec.thread_fit_lock = False #Prevent fit in thread before re-initializing

    def set_control_fit_min(self, new_value = None):
        if self.controls.group_fit.isEnabled():
            self.spec.thread_fit_lock = True #Prevent fit in thread before re-initializing
                
            max_range = self.fit.wavelengths_max
            maxvalue = self.fit.wavelengths.max()
            
            #For shortcut new_value = None
            if new_value is None:
                if self.graph_1.click is not None:
                    new_value = self.graph_1.click[3]
                else:
                    new_value = maxvalue
                    
            if max_range is None:
                max_range = maxvalue
                
            if new_value < max_range:
                self.update_control_fit_min(new_value)
                
                # #Plot red line ref
                # refline = self.graph_1.Fit_range_min_line
                # if refline == None:
                #     self.graph_1.Fit_range_min_line = self.graph_1.ax_1.axvline(new_value, color = 'red', linestyle = '--')
                # else:
                #     refline.set_xdata([new_value,new_value])
                # self.graph_1.canvas.draw()
                self.graph_1.plot_red_min(new_value)
                
            else:
                self.model.statusbar_message(f'Error: value bigger than Max lim {max_range:.1f}')
            
            self.spec.thread_fit_lock = False #Prevent fit in thread before re-initializing
        else:
            pop_up_error('Fit not enabled, select data (the X-axis must not contain values ​​equal to zero)','Command Set Min')

    def command_fit_button_max(self):
        
        self.spec.thread_fit_lock = True #Prevent fit in thread before re-initializing
        
        minvalue = self.fit.wavelengths.min()
        maxvalue = self.fit.wavelengths.max()
        
        # minvalue = self.graph_1.data_x.min()
        # maxvalue = self.graph_1.data_x.max()
        
        value = self.fit.wavelengths_max
        
        if value is None:
            value = maxvalue
            
        #print(value, minvalue, maxvalue)
        
        title = 'Fit Max limit'
        label = f'min {minvalue:.1f} max {maxvalue:.1f} actual value {value:.1f}'
        
        if self.graph_1.click is not None:
            value = self.graph_1.click[3]
        
        new_value, ok = QtWidgets.QInputDialog.getDouble(self, title, label , value, minvalue, maxvalue)

        if ok:
            self.set_control_fit_max(new_value)
        else:
            self.model.statusbar_message(f'Error: Max Value = {value:.1f}')
            self.spec.thread_fit_lock = False #Prevent fit in thread before re-initializing
    
    def set_control_fit_max(self, new_value = None):
        
        if self.controls.group_fit.isEnabled():
            
            self.spec.thread_fit_lock = True #Prevent fit in thread before re-initializing
            
            min_range = self.fit.wavelengths_min
            minvalue = self.fit.wavelengths.min()
            
            #For shortcut new_value = None
            if new_value is None:
                if self.graph_1.click is not None:
                    new_value = self.graph_1.click[3]
                else:
                    new_value = minvalue
                    
            if min_range is None:
                min_range = minvalue
                
            if new_value > min_range:
                self.update_control_fit_max(new_value)
                
                # #Plot red line ref
                # refline = self.graph_1.Fit_range_max_line
                # if refline == None:
                #     self.graph_1.Fit_range_max_line = self.graph_1.ax_1.axvline(new_value, color = 'red', linestyle = '--')
                # else:
                #     refline.set_xdata([new_value,new_value])
                # self.graph_1.canvas.draw()
                
                self.graph_1.plot_red_max(new_value)
                
            else:
                self.model.statusbar_message(f'Error: value smaller than Min lim {min_range:.1f}')
            
            self.spec.thread_fit_lock = False #Prevent fit in thread before re-initializing
            
        else:
            pop_up_error('Fit not enabled, select data (the X-axis must not contain values ​​equal to zero)','Command Set Max')
            
    def command_fit_combob_func(self):
        self.spec.thread_fit_lock = True #Prevent fit in thread before re-initializing
        
        self.graph_1.erase_fit_plot()
        
        sender = self.sender()
        
        if type(sender) == QtWidgets.QComboBox:
            value = self.sender().currentText()
        if type(sender) == QtWidgets.QAction:   
            value = self.sender().text()
        
        self.update_control_fit_function(value)
        
        self.spec.thread_fit_lock = False #Prevent fit in thread before re-initializing
        
    def command_fit_button_snap(self):
        # self.spec.thread_fit_snap = True
        # self.signal_thread_A_read_data.emit()
        # print(str(self.spec.thread_continuous)*50)
        
        
        if self.controls.group_fit.isEnabled():
            if (self.fit.x_fit is not None) and ((self.fit.x_fit == 0).sum() == 0): #No zero in X
            #no zero in x
                if self.data_from_file_x is not None:
                    #Fitting data from file
                    self.fit.fit_set_y(self.graph_1.data_y) #set_x in method_file_open_file or set_lim crash
                    self.fit.fit_run()
                    self.fit.fit_eval_comp()
                    self.fit.fit_update_report()
                    self.method_update_fit_plot()
                    
                else:
                    if self.spec.average_intensities is not None:
                        #fitting data from spectrometer
                        
                        self.spec.fit.fit_set_y(self.spec.average_intensities)
                        # error = self.spec.fit.fit_run()
                        self.spec.fit.fit_eval_comp()
                        self.fit.fit_update_report()
                        #self.signal_fit_done.emit()
                        self.method_update_fit_plot()
                    else:
                        self.model.statusbar_message('Error: no data to fit')
                        
                if self.report_window.isVisible():
                    time = datetime.now().strftime("%H:%M:%S")
                    self.report_window.setWindowTitle('Report ' + time)
                    self.report_window.label.setText(self.fit.fit_report)
            else:
                pop_up_error('Fit not enabled, select data (the X-axis must not contain values ​​equal to zero)','Command Fit Snap')
        else:
            pop_up_error('Fit not enabled, select data (the X-axis must not contain values ​​equal to zero)','Command Fit Continuous')
    
    def method_update_fit_plot(self):
        fit = self.fit.fit_function
        
        if fit == "Double Voigt" or fit == "Double Lorentz" or fit == "Double Gauss":
            comps_x, full, P1, P2, bkg = self.fit.eval_comps_x, self.fit.eval_full, self.fit.eval_P1, self.fit.eval_P2, self.fit.eval_bkg

            comps_x = 1e7/comps_x
            self.graph_1.plot_fit_full(comps_x, full)
            self.graph_1.plot_fit_P1(comps_x, P1)
            self.graph_1.plot_fit_P2(comps_x, P2)
            self.graph_1.plot_fit_bkg(comps_x, bkg)
            self.graph_1.canvas.draw()
        else:
            comps_x, full, P1, bkg = self.fit.eval_comps_x, self.fit.eval_full, self.fit.eval_P1, self.fit.eval_bkg

            comps_x = 1e7/comps_x
            self.graph_1.plot_fit_full(comps_x, full)

            self.graph_1.plot_fit_bkg(comps_x, bkg)
            self.graph_1.canvas.draw()
        
        self.update_control_fit_label_iterLim()
        
        if self.report_window.isVisible():
            time = datetime.now().strftime("%H:%M:%S")
            self.report_window.setWindowTitle('Report ' + time)
            self.report_window.label.setText(self.fit.fit_report)
    
    def update_control_fit_label_iterLim(self):
        nfev = self.fit.out_dictionary['function evals']
        self.controls.fit_label_iterLim.setText(f'Iter Lim {nfev}/')
    
    def shortcut_control_fit_cont(self):
        if self.controls.group_fit.isEnabled():
            value = not self.spec.thread_fit_continuous 
            
            self.update_control_fit_cont(value)
        else:
            pop_up_error('Fit not enabled, select data (the X-axis must not contain values ​​equal to zero)','Command Fit Continuous')
        
    def update_control_fit_cont(self, value):
        self.spec.thread_fit_continuous  = value
        #value = checkbox value
        self.action_fit_checkb_cont.setChecked(value)
        self.controls.fit_checkb_cont.setChecked(value)
        
    
    def update_control_fit_auto(self, value):
        #value = checkbox value
        self.fit.autoupdate = value
        self.action_fit_checkb_auto.setChecked(value)
        self.controls.fit_checkb_auto.setChecked(value)
        
        #if in Autoupdate prevet fit function and fit background change
        for i in self.action_fit_combob_func:
            i.setDisabled(value)
        self.controls.fit_combob_func.setDisabled(value)    
        self.action_fit_button_bkgDeg.setDisabled(value)
        self.controls.fit_button_bkgDeg.setDisabled(value) 
        
        #if in Autoupdate prevent background 
        self.action_spec_button_bkgTake.setDisabled(value)            
        self.controls.spec_button_bkgTake.setDisabled(value)
        
        self.action_spec_checkb_bkgUse.setDisabled(value)            
        self.controls.spec_checkb_bkgUse.setDisabled(value) 

    #Spectrometer section
    
    def command_spec_button_calibPar(self):
        self.calib_controls.calib_cn = self.calib_cn.copy()
        self.calib_controls.update_labels()
        self.calib_controls.show()
        
        
    def command_spec_button_calibrator(self):
        #send data to calibrator and open it
        # data = np.c_[self.spec.wavelengths, self.spec.average_intensities] #Option 1: send original data from spectrometer connection
        
        #data = np.c_[self.graph_1.data_x, self.spec.average_intensities] #Option 2: send data from screen (i.e. with last calibration)
        
        #data = np.c_[self.graph_1.data_x, self.graph_1.data_y]
        
        if self.graph_1.data_y is not None:
            self.signal_calibrator_selected_data.emit(self.graph_1.data_x,self.graph_1.data_y, "None")
        else:
            fake_x = np.arange(10)
            fake_y = np.zeros(10)
            self.signal_calibrator_selected_data.emit(fake_x,fake_y, "None")
            
        self.rubycond_calibrator.show()
        
    def command_spec_button_bkgTake(self):
        #save background data in mem
        if self.data_from_file_x is not None:
            #working on file
            self.fit.intensities_bkg = np.copy(self.graph_1.data_y)
        else:
            self.fit.intensities_bkg = np.copy(self.spec.average_intensities)
        self.model.statusbar_message('Background saved')

    
    def command_spec_checkb_bkgUse(self, value):
        #value = checkbox value
        
        if self.data_from_file_x is not None:
            #working on file
            if value:
                #substract bkg
                if len(self.data_from_file_y) == len(self.fit.intensities_bkg):
                    self.graph_1.plot_data(self.data_from_file_y - self.fit.intensities_bkg)
                    self.model.statusbar_message('Background substracted')
                else:
                    value = False
                    pop_up_error('The background in memory and the current measurement have different lengths')
                    self.model.statusbar_message('Background incompatible')
            else:
                #restore original
                self.graph_1.plot_data(self.data_from_file_y)
        else:
            #working on measurements
            #case = self.fit.intensities_bkg is not None and value
            
            if self.fit.intensities_bkg is not None:
                #value = checkbox value
                
                self.action_spec_checkb_bkgUse.setChecked(value)
                self.controls.spec_checkb_bkgUse.setChecked(value)
                self.fit.bkg = value
            else:
                self.action_spec_checkb_bkgUse.setChecked(False)
                self.controls.spec_checkb_bkgUse.setChecked(False)
                self.fit.bkg = False
            
    #Measurements section
    
    def command_meas_checkb_acq(self, value):
        #value = checkbox value
        self.action_meas_checkb_acq.setChecked(value)
        self.controls.meas_checkb_acq.setChecked(value)
        
        #Cooler ON/OFF not available on continuous  acquisition
        
        self.action_measTemp_checkb_cool.setDisabled(value)
        self.controls.measTemp_checkb_cool.setDisabled(value)
        
        #Cooler button_target not available on continuous  acquisition
        
        self.action_measTemp_button_target.setDisabled(value)
        self.controls.measTemp_button_target.setDisabled(value)
            
        if self.thread_reading == False:
            #Thread Not running
            if value:
                #checkbox checked = start
                self.thread_reading = True
                self.spec.thread_continuous = True
                self.signal_thread_A_read_data.emit()  #Thread_3A) start

                self.controls.meas_button_acc.setDisabled(True)
                self.action_meas_button_acc.setDisabled(True)
            else:
                #checkbox unchecked = stop
                self.model.statusbar_message('Meas Already Stopped')
        else:
            #Thread running
            if value:
                #checkbox checked = start
                self.model.statusbar_message('Meas Already Running')
            else:
                #checkbox unchecked = stop
                self.model.statusbar_message('Stopping meas ...')
                self.spec.abort = True
                self.model.statusbar_message('Meas Stopped')
                
                self.controls.meas_button_acc.setDisabled(False)
                self.action_meas_button_acc.setDisabled(False)
                
                self.spec.thread_continuous = False

        
    def command_meas_button_snap(self):
        if self.thread_reading == False:
            self.thread_reading = True
            self.spec.thread_continuous = False
            self.graph_1.erase_fit_plot()
            self.signal_thread_A_read_data.emit()  #Thread_3A) start
        else:
            self.model.statusbar_message('Error: Thread Busy')
    
    
    def command_meas_acc(self):
        minvalue = 1
        maxvalue = 10000
        value = self.spec.accumulations_n

        title = 'Accumulation'
        label = f'min {minvalue} max {maxvalue}'
        new_value, ok = QtWidgets.QInputDialog.getInt(self, title, label , value, minvalue, maxvalue)
        
        if ok:
            self.update_control_meas_acc(new_value)
        else:
            self.model.statusbar_message(f'Error: Accumulation = {value}')
    

        
    
    
    def command_meas_intTime(self):
        minvalue, maxvalue = self.spec.integration_time_limits
        minvalue = minvalue
        maxvalue = maxvalue
        value = self.spec.integration_time_value

        title = 'Integration time in sec'
        label = f'min {minvalue:.2e} max {maxvalue:.2e}'
        value_str = f'{value:.2e}'
        new_value, ok = self.open_input_dialog_float(title, label , value_str, minvalue, maxvalue)
        
        if ok:
            self.update_control_meas_intTime(new_value)
        else:
            self.model.statusbar_message(f'Error: Integration time {value:.2e} sec')
            
    def update_control_fit_iterLim(self, value):
        self.fit.max_nfev = value
        self.model.statusbar_message(f'Maximum number of function evaluations = {value}')
        text = f'{value}'
        self.controls.fit_button_iterLim.setText(text)
        self.action_fit_button_iterLim.setText(text) 
        
    def update_control_fit_bkgDeg(self, value):
        self.fit.polynomial_degree = value
        self.model.statusbar_message(f'Backgound polynomial degree = {value}')
        text = f'{value}'
        self.controls.fit_button_bkgDeg.setText(text)
        self.action_fit_button_bkgDeg.setText(text) 
        self.fit.fit_init_model() # Re-initializing
        
    def update_control_fit_min(self, value):
        self.fit.wavelengths_min = value
        self.fit.fit_update_mask()
        self.model.statusbar_message(f'Fit Range Min Value = {value:.1f}')
        text = f'{value:.1f}'
        self.controls.fit_button_min.setText(text)
        self.action_fit_button_min.setText(text)  
        

    def update_control_fit_max(self, value):
        self.fit.wavelengths_max = value
        self.fit.fit_update_mask()
        self.model.statusbar_message(f'Fit Range Max Value = {value:.1f}')
        text = f'{value:.1f}'
        self.controls.fit_button_max.setText(text)
        self.action_fit_button_max.setText(text)  
        
    
    def update_control_fit_function(self, value):
        self.fit.fit_function = value
        self.model.statusbar_message('Fit function = ' + value)
        self.controls.fit_combob_func.setCurrentText(value)
        for action in self.action_fit_combob_func:
            if action.text() == value:
                action.setChecked(True)
        self.fit.fit_init_model()
                
    def update_control_meas_acc(self, value):
        self.spec.accumulations_n = value
        self.model.statusbar_message(f'Accumulation = {value}')
        text = f'{value}'
        self.controls.meas_button_acc.setText(text)
        self.action_meas_button_acc.setText(text)  

    def update_control_meas_intTime(self, value):
        self.spec.set_integration_time(value)
        self.model.statusbar_message(f'Integration time {value:.2e} sec')
        text = f'{value:.2e}'
        self.controls.meas_button_intTime.setText(text)
        self.action_meas_button_intTime.setText(text)
        
    
        
    def command_meas_abort(self):
        if self.thread_reading:
            self.model.statusbar_message('Stopping meas ...')
            self.spec.abort = True
            self.spec.set_integration_time(0.1)
            self.update_control_meas_intTime(0.1)
            self.model.statusbar_message('Meas Stopped')
            
            self.controls.meas_checkb_acq.setChecked(False)
            self.action_meas_checkb_acq.setChecked(False)
            
            self.controls.meas_button_acc.setDisabled(False)
            self.action_meas_button_acc.setDisabled(False)
        else:
            self.model.statusbar_message('No running measure, nothing to do')
    
    #Cooler Section group_measTemp menu_measTemp
    
    def command_measTemp_checkb_cool(self, value):
        #value = checkbox value
        self.action_measTemp_checkb_cool.setChecked(value)
        self.controls.measTemp_checkb_cool.setChecked(value)
        #self.action_meas_checkb_acq.setChecked(value)
        #self.controls.meas_checkb_acq.setChecked(value)
        if value:
            #start cooling and reading
            self.spec.read_temperature = True
            self.spec.turn_cooler_ON()
            self.signal_thread_B_read_temperature.emit()
            self.model.statusbar_message('Cooler ON')
        else:
            
            self.spec.turn_cooler_OFF()
            self.model.statusbar_message('Cooler OFF')
    
    def decode_ret_Andor(self, ret):
        #print(ret)
        if ret == 20037 :
            #20037 DRV_TEMP_NOT_REACHED Temperature has not reached set point.
            out = 'Cooling'
        elif ret == 20034: 
            #20034 DRV_TEMP_OFF Temperature is OFF.
            out = 'OFF'
        elif ret == 20036 :
            #20036 DRV_TEMP_STABILIZED Temperature has stabilized at set point.
            out = 'Stable'
        elif ret == 20072 :
            #20072 DRV_ACQUIRING Acquisition in progress.
            out = 'ERROR'
        elif ret == 20013 :
            #20013 DRV_ERROR_ACK Unable to communicate with card.
            out = 'ERROR'
        elif ret == 20035 :
            #20035 DRV_TEMP_NOT_STABILIZED Temperature reached but not stabilized
            out = 'Unstable'
        else:
            out = 'UNK'
        return out 
    
    def method_update_temperature(self, temperature, TargetTemp, ret):
        #self.measTemp_label_temp = QtWidgets.QLabel("Temperature = -- °C")
        now_str = datetime.now().strftime("%H:%M:%S")
        status = self.decode_ret_Andor(ret)
        text = f"{temperature:.2f}/{TargetTemp:.2f} °C: " + now_str +' | '+status
        text_menu = f"T = {temperature:.2f} °C: " + now_str
        self.controls.measTemp_label_temp.setText(text)
        self.action_measTemp_label_temp.setText(text_menu)
    
    def update_measTemp_button_target(self, value):
        try:
            self.spec.sdk.AbortAcquisition() #acquisition must be stopped to send command spectrometer_thread_get_temperature
            self.spec.set_temperature(int(value))
            self.spec.Andor_t_target = value
            
            text = f"Target {self.spec.Andor_t_target} °C"
            
            self.action_measTemp_button_target.setText(text)
            self.controls.measTemp_button_target.setText(text)
            self.model.statusbar_message(text)
        except:
            print(traceback.format_exc())
            
    def command_measTemp_button_target(self):
        try:
            minvalue, maxvalue = self.spec.Andor_tmin, self.spec.Andor_tmax 
    
            value = self.spec.Andor_t_target
            #print(value, minvalue, maxvalue)
            title = 'Set the desired temperature of the detector'
            label = f'min {minvalue} max {maxvalue}'
            #value_str = f'{value}'
            new_value, ok = QtWidgets.QInputDialog.getInt(self, title, label , value, minvalue, maxvalue)
            
            if ok:

                self.update_measTemp_button_target(new_value)
            else:
                self.model.statusbar_message(f'Error: Target temperature {self.spec.Andor_t_target } C')
            
        except:
            print(traceback.format_exc())
        
    #Init section
    
    def init_controls(self):
        self.controls.fit_combob_func.addItems(self.fit.fit_functions)
        
    def init_disabled(self):
        
        #controls. => action_
        self.controls.spec_button_calibPar.setDisabled(True)
        self.controls.spec_button_calibrator.setDisabled(True)
        self.controls.spec_checkb_calib.setDisabled(True)
        self.controls.spec_button_bkgTake.setDisabled(True)
        self.controls.spec_checkb_bkgUse.setDisabled(True)

        self.action_spec_button_calibPar.setDisabled(True)
        self.action_spec_button_calibrator.setDisabled(True)
        self.action_spec_checkb_calib.setDisabled(True)
        self.action_spec_button_bkgTake.setDisabled(True)
        self.action_spec_checkb_bkgUse.setDisabled(True)
        
        #self.controls.group_ => self.menu_
        
        self.controls.group_meas.setDisabled(True)
        self.controls.group_fit.setDisabled(True)
        self.controls.group_gauge.setDisabled(True)
        self.controls.group_log.setDisabled(True)
        
        self.menu_meas.setDisabled(True)
        self.menu_fit.setDisabled(True)
        #self.menu_gauge.menu_gaugetabRuby(True)
        #self.menu_gauge.gaugetabSam(True)
        self.menu_log.setDisabled(True)

        

    
    def test_sender(self):
        sender = self.sender()
        if type(sender) == QtWidgets.QComboBox:
            value = self.sender().currentText()
        if type(sender) == QtWidgets.QAction:   
            value = self.sender().text()
        
        self.update_control_fit_function(value)
    
    def ActionCombo(self, menu, value_list, command):
        group = QtWidgets.QActionGroup(self)
        
        actions_list = []
        for value in value_list:
            action = QtWidgets.QAction(self)
            action.setText(value)
            action.setCheckable(True)
            action.triggered.connect(command)
            menu.addAction(action)
            group.addAction(action)
            actions_list.append(action)
        return actions_list
            
    def init_Menu(self):
        menu_Bar = QtWidgets.QMenuBar()
        
        menu_file = QtWidgets.QMenu("File", menu_Bar)
        menu_spec = QtWidgets.QMenu("Spectrometer", menu_Bar)
        menu_meas = QtWidgets.QMenu("Measurements", menu_Bar)
        menu_measTemp = QtWidgets.QMenu("Cooler", menu_Bar)  #Optional Menu
        menu_gaugetabRuby  = QtWidgets.QMenu("Gauge Ruby", menu_Bar)
        menu_gaugetabSam  = QtWidgets.QMenu("Gauge Sam", menu_Bar)
        menu_fit = QtWidgets.QMenu("Fit", menu_Bar)
        menu_log = QtWidgets.QMenu("Logger", menu_Bar)
        menu_Help = QtWidgets.QMenu('&Help', menu_Bar)
        
        menu_file.setTearOffEnabled(True)
        menu_spec.setTearOffEnabled(True)
        menu_meas.setTearOffEnabled(True)
        menu_measTemp.setTearOffEnabled(True)
        menu_gaugetabRuby.setTearOffEnabled(True)
        menu_gaugetabSam.setTearOffEnabled(True)
        menu_fit.setTearOffEnabled(True)
        menu_log.setTearOffEnabled(True)
        menu_Help.setTearOffEnabled(True)
        
        
        
        
        
        menu_Bar.addMenu(menu_file)
        menu_Bar.addMenu(menu_spec)
        menu_Bar.addMenu(menu_meas)
        menu_Bar.addMenu(menu_measTemp)
        menu_Bar.addMenu(menu_fit)
        menu_Bar.addMenu(menu_gaugetabRuby)
        menu_Bar.addMenu(menu_gaugetabSam )
        menu_Bar.addMenu(menu_log)
        menu_Bar.addMenu(menu_Help)
        
        
        
        self.action_file_button_saveData = QtWidgets.QAction()
        self.action_file_button_saveData.setText('save Data')
        
        #self.action_file_button_saveData.setShortcut('Ctrl+O')
        self.action_file_button_saveData.triggered.connect(self.command_file_save_data)
        self.controls.file_button_saveData.clicked.connect(self.command_file_save_data)                             #WIPDONE
        menu_file.addAction(self.action_file_button_saveData)
        
        self.action_file_button_saveFit = QtWidgets.QAction()
        self.action_file_button_saveFit.setText('saveFit')
        #self.action_file_button_saveFit.setShortcut('Ctrl+O')
        #self.action_file_button_saveFit.triggered.connect(self.event_file_button_saveFit)
        menu_file.addAction(self.action_file_button_saveFit)
        
        self.action_file_button_openFile = QtWidgets.QAction()
        self.action_file_button_openFile.setText('open File')
        #self.action_file_button_openFile.setShortcut('Ctrl+O')
        self.action_file_button_openFile.triggered.connect(self.command_file_open_file)
        self.controls.file_button_openFile.clicked.connect(self.command_file_open_file)
        menu_file.addAction(self.action_file_button_openFile)
        
        self.action_file_button_quit = QtWidgets.QAction()
        self.action_file_button_quit.setText('quit')
        #self.action_file_button_quit.setShortcut('Ctrl+O')
        self.action_file_button_quit.triggered.connect(self.command_quit)
        self.controls.file_button_quit.clicked.connect(self.command_quit)                             #WIPDONE
        menu_file.addAction(self.action_file_button_quit)
        
        self.controls.file_button_quit.setToolTip('See you next time !')
        
        self.action_spec_button_connect = QtWidgets.QAction()
        self.action_spec_button_connect.setText('Connect')
        #self.action_spec_button_connect.setShortcut('Ctrl+O')
        self.action_spec_button_connect.triggered.connect(self.command_spec_button_connect)            #WIPDONE
        self.controls.spec_button_connect.clicked.connect(self.command_spec_button_connect)
        
        menu_spec.addAction(self.action_spec_button_connect)
        
        self.action_spec_button_calibPar = QtWidgets.QAction()
        self.action_spec_button_calibPar.setText('Calib Pars')
        #self.action_spec_button_calib.setShortcut('Ctrl+O')
        self.action_spec_button_calibPar.triggered.connect(self.command_spec_button_calibPar)
        self.controls.spec_button_calibPar.clicked.connect(self.command_spec_button_calibPar)
        menu_spec.addAction(self.action_spec_button_calibPar)
        
        
        self.action_spec_button_calibrator = QtWidgets.QAction()
        self.action_spec_button_calibrator.setText('Calibrator')
        #self.action_spec_button_calib.setShortcut('Ctrl+O')
        self.action_spec_button_calibrator.triggered.connect(self.command_spec_button_calibrator)
        self.controls.spec_button_calibrator.clicked.connect(self.command_spec_button_calibrator)
        menu_spec.addAction(self.action_spec_button_calibrator)
        
        self.action_spec_checkb_calib = QtWidgets.QAction()
        self.action_spec_checkb_calib.setText('User Calib')
        #self.action_spec_button_calib.setShortcut('Ctrl+O')
        self.action_spec_checkb_calib.triggered.connect(self.command_spec_checkb_calib)
        self.controls.spec_checkb_calib.clicked.connect(self.command_spec_checkb_calib)
        menu_spec.addAction(self.action_spec_checkb_calib)
        
        self.action_spec_button_bkgTake = QtWidgets.QAction()
        self.action_spec_button_bkgTake.setText('Take bkg')
        #self.action_spec_button_bkgTake.setShortcut('Ctrl+O')
        self.action_spec_button_bkgTake.triggered.connect(self.command_spec_button_bkgTake)             #WIPDONE
        self.controls.spec_button_bkgTake.clicked.connect(self.command_spec_button_bkgTake)
        self.controls.spec_button_bkgTake.setToolTip("Not available if 'Auto update' activated")
        menu_spec.addAction(self.action_spec_button_bkgTake)

        self.action_spec_checkb_bkgUse = QtWidgets.QAction()
        self.action_spec_checkb_bkgUse.setText('Substract bkg')
        self.action_spec_checkb_bkgUse.setCheckable(True)
        #self.action_spec_button_bkgTake.setShortcut('Ctrl+O')
        self.action_spec_checkb_bkgUse.triggered.connect(self.command_spec_checkb_bkgUse)             #WIPDONE
        self.controls.spec_checkb_bkgUse.clicked.connect(self.command_spec_checkb_bkgUse)
        self.controls.spec_checkb_bkgUse.setToolTip("Not available if 'Auto update' activated")
        menu_spec.addAction(self.action_spec_checkb_bkgUse)

        self.action_meas_button_snap = QtWidgets.QAction()
        self.action_meas_button_snap.setText('Snap')
        #self.action_meas_button_snap.setShortcut('Ctrl+O')
        self.action_meas_button_snap.triggered.connect(self.command_meas_button_snap)                               #WIPDONE
        self.controls.meas_button_snap.clicked.connect(self.command_meas_button_snap)
        menu_meas.addAction(self.action_meas_button_snap)
        
        self.action_meas_checkb_acq = QtWidgets.QAction()
        self.action_meas_checkb_acq.setText('Acquire')
        self.action_meas_checkb_acq.setCheckable(True)
        #self.action_meas_checkb_acq.setShortcut('Ctrl+O')
        self.action_meas_checkb_acq.triggered.connect(self.command_meas_checkb_acq)                               #WIPDONE
        self.controls.meas_checkb_acq.clicked.connect(self.command_meas_checkb_acq)
        menu_meas.addAction(self.action_meas_checkb_acq)
        
        menu_intTime = menu_meas.addMenu('Int Time (s)')
        
        self.action_meas_button_intTime = QtWidgets.QAction()
        self.action_meas_button_intTime.setText('1')
        #self.action_meas_button_intTime.setShortcut('Ctrl+O')
        self.action_meas_button_intTime.triggered.connect(self.command_meas_intTime)                        #WIPDONE
        self.controls.meas_button_intTime.clicked.connect(self.command_meas_intTime)
        menu_intTime.addAction(self.action_meas_button_intTime) 
        #command_int_time
        
        menu_acc = menu_meas.addMenu('Accumulation')
        
        self.action_meas_button_acc = QtWidgets.QAction()
        self.action_meas_button_acc.setText('1')
        #self.action_meas_button_acc.setShortcut('Ctrl+O')
        self.action_meas_button_acc.triggered.connect(self.command_meas_acc)                                #WIPDONE
        self.controls.meas_button_acc.clicked.connect(self.command_meas_acc)
        menu_acc.addAction(self.action_meas_button_acc)
        
        self.action_meas_button_abort = QtWidgets.QAction()
        self.action_meas_button_abort.setText('Abort')
        #self.action_meas_button_abort.setShortcut('Ctrl+O')
        self.action_meas_button_abort.triggered.connect(self.command_meas_abort)                             #WIPDONE
        self.controls.meas_button_abort.clicked.connect(self.command_meas_abort)
        menu_meas.addAction(self.action_meas_button_abort)
        
        #
        #command_measTemp_button_target
        
        self.action_measTemp_label_temp = QtWidgets.QAction()
        self.action_measTemp_label_temp.setText('T = --- °C')
        #self.action_measTemp_button_target.setShortcut('Ctrl+O')
        # self.action_measTemp_button_target.triggered.connect(self.command_measTemp_button_target)            #WIPDONE
        # self.controls.measTemp_button_target.clicked.connect(self.command_measTemp_button_target)
        menu_measTemp.addAction(self.action_measTemp_label_temp)
        
        self.action_measTemp_button_target = QtWidgets.QAction()
        self.action_measTemp_button_target.setText('Target --- °C')
        #self.action_measTemp_button_target.setShortcut('Ctrl+O')
        self.action_measTemp_button_target.triggered.connect(self.command_measTemp_button_target)            #WIPDONE
        self.controls.measTemp_button_target.clicked.connect(self.command_measTemp_button_target)
        menu_measTemp.addAction(self.action_measTemp_button_target)
        
        self.action_measTemp_checkb_cool  = QtWidgets.QAction()
        self.action_measTemp_checkb_cool.setText('Cooling')
        self.action_measTemp_checkb_cool.setCheckable(True)
        #self.action_meas_checkb_acq.setShortcut('Ctrl+O')
        self.action_measTemp_checkb_cool.triggered.connect(self.command_measTemp_checkb_cool)                               #WIPDONE
        self.controls.measTemp_checkb_cool.clicked.connect(self.command_measTemp_checkb_cool)
        menu_measTemp.addAction(self.action_measTemp_checkb_cool)
        
        #Gauge section Ruby
        #menu_gaugetabRuby
        
        self.action_gaugetab_button_clean = QtWidgets.QAction()
        self.action_gaugetab_button_clean.setText('Clean Title')
        #self.action_fit_button_snap.setShortcut('Ctrl+O')
        self.action_gaugetab_button_clean.triggered.connect(self.command_gaugetab_button_clean)                 #WIPDONE
        self.controls.gaugetab_button_clean.clicked.connect(self.command_gaugetab_button_clean)
        menu_gaugetabRuby.addAction(self.action_gaugetab_button_clean)
        
        self.action_gaugetabRuby_button_snap = QtWidgets.QAction()
        self.action_gaugetabRuby_button_snap.setText('Snap')
        #self.action_fit_button_snap.setShortcut('Ctrl+O')
        self.action_gaugetabRuby_button_snap.triggered.connect(self.command_gaugetabRuby_button_snap)                 #WIPDONE
        self.controls.gaugetabRuby_button_snap.clicked.connect(self.command_gaugetabRuby_button_snap)
        menu_gaugetabRuby.addAction(self.action_gaugetabRuby_button_snap)
        
        
        self.action_gaugetabRuby_checkb_cont = QtWidgets.QAction()
        self.action_gaugetabRuby_checkb_cont.setText('continuous ')
        self.action_gaugetabRuby_checkb_cont.setCheckable(True)
        #self.action_fit_button_cont.setShortcut('Ctrl+O')
        self.action_gaugetabRuby_checkb_cont.triggered.connect(self.command_gaugetabRuby_checkb_cont)        #WIPDONE
        self.controls.gaugetabRuby_checkb_cont.clicked.connect(self.command_gaugetabRuby_checkb_cont)
        menu_gaugetabRuby.addAction(self.action_gaugetabRuby_checkb_cont)
        
        menu_ruby_lambda0 = menu_gaugetabRuby.addMenu('λ₀')
        
        self.action_gaugetabRuby_button_lambda0 = QtWidgets.QAction()
        self.action_gaugetabRuby_button_lambda0.setText('--- ')
        #self.gaugetabRuby_button_lambda0.setShortcut('Ctrl+O')
        self.action_gaugetabRuby_button_lambda0.triggered.connect(self.command_gaugetabRuby_button_lambda0)
        self.controls.gaugetabRuby_button_lambda0.clicked.connect(self.command_gaugetabRuby_button_lambda0)                      #WIPDONE
        menu_ruby_lambda0.addAction(self.action_gaugetabRuby_button_lambda0)
        
        
        self.menu_ruby_combob_Pcalib = menu_gaugetabRuby.addMenu('P Calibration')  #Defined in init_gauge()
        
        # self.action_gaugetabRuby_combob_gauge = QtWidgets.QAction()
        # self.action_gaugetabRuby_combob_gauge.setText('P Calibration')
        # #self.action_gaugetabRuby_combob_gauge.setShortcut('Ctrl+O')
        # #self.action_gaugetabRuby_combob_gauge.triggered.connect(self.event_gaugetabRuby_combob_gauge)
        # menu_gaugetabRuby.addAction(self.action_gaugetabRuby_combob_gauge)
        
        # self.action_fit_combob_func = self.ActionCombo(menu_ruby_combob_Pcalib, self.fit.fit_functions, self.command_fit_combob_func)                             #WIPDONE
        # self.controls.fit_combob_func.activated.connect(self.command_fit_combob_func)
        
        menu_ruby_Tlambda0 = menu_gaugetabRuby.addMenu('T(λ₀)')
        
        self.action_gaugetabRuby_button_Tlambda0 = QtWidgets.QAction()
        self.action_gaugetabRuby_button_Tlambda0.setText('---')
        #self.action_gaugetabRuby_button_Tlambda0.setShortcut('Ctrl+O')
        self.action_gaugetabRuby_button_Tlambda0.triggered.connect(self.command_gaugetabRuby_button_Tlambda0)                      #WIPDONE
        self.controls.gaugetabRuby_button_Tlambda0.clicked.connect(self.command_gaugetabRuby_button_Tlambda0)
        menu_ruby_Tlambda0.addAction(self.action_gaugetabRuby_button_Tlambda0)
        
        menu_ruby_Tlambda = menu_gaugetabRuby.addMenu('T(λ)')
        
        self.action_gaugetabRuby_button_Tlambda = QtWidgets.QAction()
        self.action_gaugetabRuby_button_Tlambda.setText('---')
        #self.action_gaugetabRuby_button_Tlambda.setShortcut('Ctrl+O')
        self.action_gaugetabRuby_button_Tlambda.triggered.connect(self.command_gaugetabRuby_button_Tlambda)                      #WIPDONE
        self.controls.gaugetabRuby_button_Tlambda.clicked.connect(self.command_gaugetabRuby_button_Tlambda)
        menu_ruby_Tlambda.addAction(self.action_gaugetabRuby_button_Tlambda)
        
        self.menu_ruby_combob_Tcalib = menu_gaugetabRuby.addMenu('T Calibration')  #Defined in init_gauge()
        
        # self.action_gaugetabRuby_combob_Tcalib = QtWidgets.QAction()
        # self.action_gaugetabRuby_combob_Tcalib.setText('T calibration')
        # #self.action_gaugetabRuby_combob_Tcalib.setShortcut('Ctrl+O')
        # #self.action_gaugetabRuby_combob_Tcalib.triggered.connect(self.event_gaugetabRuby_combob_Tcalib)
        # menu_gaugetabRuby.addAction(self.action_gaugetabRuby_combob_Tcalib)
        
        
        #menu_gaugetabSam #Gauge section Samarium
        
        
        
        self.action_gaugetabSam_button_snap = QtWidgets.QAction()
        self.action_gaugetabSam_button_snap.setText('Snap')
        #self.action_fit_button_snap.setShortcut('Ctrl+O')
        self.action_gaugetabSam_button_snap.triggered.connect(self.command_gaugetabSam_button_snap)                 #WIPDONE
        self.controls.gaugetabSam_button_snap.clicked.connect(self.command_gaugetabSam_button_snap)
        menu_gaugetabSam.addAction(self.action_gaugetabSam_button_snap)
        
        self.action_gaugetabSam_checkb_cont = QtWidgets.QAction()
        self.action_gaugetabSam_checkb_cont.setText('continuous ')
        self.action_gaugetabSam_checkb_cont.setCheckable(True)
        #self.action_fit_button_cont.setShortcut('Ctrl+O')
        self.action_gaugetabSam_checkb_cont.triggered.connect(self.command_gaugetabSam_checkb_cont)        #WIPDONE
        self.controls.gaugetabSam_checkb_cont.clicked.connect(self.command_gaugetabSam_checkb_cont)
        menu_gaugetabSam.addAction(self.action_gaugetabSam_checkb_cont)
        
        
        menu_samy_lambda0 = menu_gaugetabSam.addMenu('λ₀')
        
        self.action_gaugetabSam_button_lambda0 = QtWidgets.QAction()
        self.action_gaugetabSam_button_lambda0.setText(' --- ')
        #self.action_gaugetabSam_button_acq.setShortcut('Ctrl+O')
        self.action_gaugetabSam_button_lambda0.triggered.connect(self.command_gaugetabSam_button_lambda0)
        self.controls.gaugetabSam_button_lambda0.clicked.connect(self.command_gaugetabSam_button_lambda0)   
        menu_samy_lambda0.addAction(self.action_gaugetabSam_button_lambda0)
        
        

        
        
        self.menu_sam_combob_Pcalib = menu_gaugetabSam.addMenu('P Calibration')  #Defined in init_gauge()
        
        # self.action_gaugetabSam_combob_gauge = QtWidgets.QAction()
        # self.action_gaugetabSam_combob_gauge.setText('P Calibration')
        # #self.action_gaugetabRuby_combob_gauge.setShortcut('Ctrl+O')
        # #self.action_gaugetabRuby_combob_gauge.triggered.connect(self.event_gaugetabRuby_combob_gauge)
        # menu_gaugetabSam.addAction(self.action_gaugetabSam_combob_gauge)
        
        #menu_fit
        
        self.action_fit_button_snap = QtWidgets.QAction()
        self.action_fit_button_snap.setText('Snap')
        #self.action_fit_button_snap.setShortcut('Ctrl+O')
        self.action_fit_button_snap.triggered.connect(self.command_fit_button_snap)                 #MEMOTMP
        self.controls.fit_button_snap.clicked.connect(self.command_fit_button_snap)
        menu_fit.addAction(self.action_fit_button_snap)
        
        
        self.action_fit_checkb_cont = QtWidgets.QAction()
        self.action_fit_checkb_cont.setText('continuous ')
        self.action_fit_checkb_cont.setCheckable(True)
        #self.action_fit_button_cont.setShortcut('Ctrl+O')
        self.action_fit_checkb_cont.triggered.connect(self.update_control_fit_cont)
        self.controls.fit_checkb_cont.clicked.connect(self.update_control_fit_cont)
        menu_fit.addAction(self.action_fit_checkb_cont)
        
        menu_fit_combob_func = menu_fit.addMenu('Fit Functions')
        
        # self.action_fit_combob_func = QtWidgets.QAction()
        # self.action_fit_combob_func.setText(self.fit.functions)
        # #self.action_fit_combob_func.setShortcut('Ctrl+O')
        # self.action_fit_combob_func.triggered.connect(self.command_fit_label_func)               
        # menu_fit_combob_func.addAction(self.action_fit_combob_func)
        
        self.action_fit_combob_func = self.ActionCombo(menu_fit_combob_func, self.fit.fit_functions, self.command_fit_combob_func)                             #WIPDONE
        self.controls.fit_combob_func.activated.connect(self.command_fit_combob_func)
        self.controls.fit_combob_func.setToolTip("Not available if 'Auto update' activated")
        
        menu_fit_bkgDeg = menu_fit.addMenu('Bkg poly degree')
        
        self.action_fit_button_bkgDeg = QtWidgets.QAction()
        self.action_fit_button_bkgDeg.setText('1')
        #self.action_fit_button_bkgDeg.setShortcut('Ctrl+O')
        self.action_fit_button_bkgDeg.triggered.connect(self.command_fit_button_bkgDeg)                             #WIPDONE
        self.controls.fit_button_bkgDeg.clicked.connect(self.command_fit_button_bkgDeg)
        self.controls.fit_button_bkgDeg.setToolTip("Not available if 'Auto update' activated")
        menu_fit_bkgDeg.addAction(self.action_fit_button_bkgDeg)
        
        menu_fit_min = menu_fit.addMenu('Min lim')
        
        self.action_fit_button_min = QtWidgets.QAction()
        self.action_fit_button_min.setText('NaN')
        #self.action_fit_button_min.setShortcut('Ctrl+O')
        self.action_fit_button_min.triggered.connect(self.command_fit_button_min)                             #WIPDONE
        self.controls.fit_button_min.clicked.connect(self.command_fit_button_min)
        menu_fit_min.addAction(self.action_fit_button_min)
        
        menu_fit_max = menu_fit.addMenu('Max lim')
        
        self.action_fit_button_max = QtWidgets.QAction()
        self.action_fit_button_max.setText('NaN')
        #self.action_fit_button_max.setShortcut('Ctrl+O')
        self.action_fit_button_max.triggered.connect(self.command_fit_button_max)                      #WIPDONE
        self.controls.fit_button_max.clicked.connect(self.command_fit_button_max)
        menu_fit_max.addAction(self.action_fit_button_max)
        
        menu_fit_iterLim = menu_fit.addMenu('Iter Lim')
        
        self.action_fit_button_iterLim = QtWidgets.QAction()
        self.action_fit_button_iterLim.setText('NaN')
        #self.action_fit_button_max.setShortcut('Ctrl+O')
        self.action_fit_button_iterLim.triggered.connect(self.command_fit_button_iterLim)                      #WIPDONE
        self.controls.fit_button_iterLim.clicked.connect(self.command_fit_button_iterLim)
        self.controls.fit_button_iterLim.setToolTip("Maximum number of iteration during the fitting procedure")
        menu_fit_iterLim.addAction(self.action_fit_button_iterLim)
        
        self.action_fit_checkb_auto = QtWidgets.QAction()
        self.action_fit_checkb_auto.setText('Auto update')
        self.action_fit_checkb_auto.setCheckable(True)
        #self.action_fit_button_cont.setShortcut('Ctrl+O')
        self.action_fit_checkb_auto.triggered.connect(self.update_control_fit_auto)
        self.controls.fit_checkb_auto.clicked.connect(self.update_control_fit_auto)
        menu_fit.addAction(self.action_fit_checkb_auto)
        
        self.action_fit_button_report = QtWidgets.QAction()
        self.action_fit_button_report.setText('Report')
        #self.action_fit_button_max.setShortcut('Ctrl+O')
        self.action_fit_button_report.triggered.connect(self.command_fit_button_report)                      #WIPDONE
        self.controls.fit_button_report.clicked.connect(self.command_fit_button_report)
        self.controls.fit_button_report.setToolTip("Shows a detailed fit report in a new windows")
        menu_fit.addAction(self.action_fit_button_report)
        
        #menu_log
        
        self.action_log_checkb_ONOFF = QtWidgets.QAction()
        self.action_log_checkb_ONOFF.setText('Active')
        self.action_log_checkb_ONOFF.setCheckable(True)
        #self.action_fit_button_cont.setShortcut('Ctrl+O')
        self.action_log_checkb_ONOFF.triggered.connect(self.command_log_checkb_ONOFF)
        self.controls.log_checkb_ONOFF.clicked.connect(self.command_log_checkb_ONOFF)
        menu_log.addAction(self.action_log_checkb_ONOFF)
        
        menu_log_logTime = menu_log.addMenu('Log Time')
        
        self.action_log_button_delta = QtWidgets.QAction()
        self.action_log_button_delta.setText(' --- ')
        #self.action_log_button_delta.setShortcut('Ctrl+O')
        self.action_log_button_delta.triggered.connect(self.command_log_button_delta)
        self.controls.log_button_delta.clicked.connect(self.command_log_button_delta)
        menu_log_logTime.addAction(self.action_log_button_delta)
        
        menu_log_threshold = menu_log.addMenu('Threshold')
        
        self.action_log_button_threshold = QtWidgets.QAction()
        self.action_log_button_threshold.setText(' --- ')
        #self.action_log_button_threshold.setShortcut('Ctrl+O')
        self.action_log_button_threshold.triggered.connect(self.command_log_button_threshold)
        self.controls.log_button_threshold.clicked.connect(self.command_log_button_threshold)
        menu_log_threshold.addAction(self.action_log_button_threshold)
        
        menu_log_folder = menu_log.addMenu('Folder')
        
        self.action_log_button_folder = QtWidgets.QAction()
        self.action_log_button_folder.setText(' --- ')
        #self.action_log_button_folder.setShortcut('Ctrl+O')
        self.action_log_button_folder.triggered.connect(self.command_log_button_folder)
        self.controls.log_button_folder.clicked.connect(self.command_log_button_folder)
        menu_log_folder.addAction(self.action_log_button_folder)
        
        
        
        #Manual actions
        
        self.action_help_setStyleFile = QtWidgets.QAction()
        self.action_help_setStyleFile.setText('Set style file')
        #self.action_log_button_folder.setShortcut('Ctrl+O')
        self.action_help_setStyleFile.triggered.connect(self.get_font_style)
        menu_Help.addAction(self.action_help_setStyleFile)
        
        # self.action_help_setFontsSize = QtWidgets.QAction()
        # self.action_help_setStyleFile.setText('Set Fonts Size')
        # #self.action_log_button_folder.setShortcut('Ctrl+O')
        # self.action_help_setStyleFile.triggered.connect(self.set_font_size)
        # menu_Help.addAction(self.action_help_setStyleFile)
        
        self.action_help_setFontsSize = QtWidgets.QAction()
        self.action_help_setFontsSize.setText(f'Font Size {int(self.font_size)}')
        #self.action_Open_image.setShortcut('Ctrl+O')
        self.action_help_setFontsSize.triggered.connect(self.get_font_size)
        menu_Help.addAction(self.action_help_setFontsSize)
        
        self.action_help_resetFontsSize = QtWidgets.QAction()
        self.action_help_resetFontsSize.setText('Reset Font Size')
        #self.action_Open_image.setShortcut('Ctrl+O')
        self.action_help_resetFontsSize.triggered.connect(self.reset_font_style_and_size)
        menu_Help.addAction(self.action_help_resetFontsSize)
        
        
        
        self.action_help_resetFontsSize = QtWidgets.QAction()
        self.action_help_resetFontsSize.setText('Reset Font Size')
        #self.action_Open_image.setShortcut('Ctrl+O')
        self.action_help_resetFontsSize.triggered.connect(self.reset_font_style_and_size)
        menu_Help.addAction(self.action_help_resetFontsSize)
        
        menu_Help.addSeparator()
        
        
        
        menu_Help_visible = menu_Help.addMenu('Visible')
        
        #Visible section
        
        self.action_help_visible_all = QtWidgets.QAction()
        self.action_help_visible_all.setText('all')
        #self.action_Open_image.setShortcut('Ctrl+O')
        self.action_help_visible_all.setCheckable(True)
        self.action_help_visible_all.setChecked(True)
        self.action_help_visible_all.triggered.connect(self.command_help_visible_all)
        menu_Help_visible.addAction(self.action_help_visible_all)
        
        menu_Help_visible.addSeparator()
        
        self.action_help_visible_file = QtWidgets.QAction()
        self.action_help_visible_file.setText('File')
        #self.action_Open_image.setShortcut('Ctrl+O')
        self.action_help_visible_file.setCheckable(True)
        self.action_help_visible_file.setChecked(True)
        self.action_help_visible_file.triggered.connect(self.command_help_visible_file)
        menu_Help_visible.addAction(self.action_help_visible_file)
        
        self.action_help_visible_spec = QtWidgets.QAction()
        self.action_help_visible_spec.setText('Spectrometer')
        #self.action_Open_image.setShortcut('Ctrl+O')
        self.action_help_visible_spec.setCheckable(True)
        self.action_help_visible_spec.setChecked(True)
        self.action_help_visible_spec.triggered.connect(self.command_help_visible_spec)
        menu_Help_visible.addAction(self.action_help_visible_spec)
        
        self.action_help_visible_meas = QtWidgets.QAction()
        self.action_help_visible_meas.setText('Measurements')
        #self.action_Open_image.setShortcut('Ctrl+O')
        self.action_help_visible_meas.setCheckable(True)
        self.action_help_visible_meas.setChecked(True)
        self.action_help_visible_meas.triggered.connect(self.command_help_visible_meas)
        menu_Help_visible.addAction(self.action_help_visible_meas)
        
        self.action_help_visible_tabs_gauge = QtWidgets.QAction()
        self.action_help_visible_tabs_gauge.setText('Gauge')
        #self.action_Open_image.setShortcut('Ctrl+O')
        self.action_help_visible_tabs_gauge.setCheckable(True)
        self.action_help_visible_tabs_gauge.setChecked(True)
        self.action_help_visible_tabs_gauge.triggered.connect(self.command_help_visible_tabs_gauge)
        menu_Help_visible.addAction(self.action_help_visible_tabs_gauge)
        
        self.action_help_visible_fit = QtWidgets.QAction()
        self.action_help_visible_fit.setText('Fit')
        #self.action_Open_image.setShortcut('Ctrl+O')
        self.action_help_visible_fit.setCheckable(True)
        self.action_help_visible_fit.setChecked(True)
        self.action_help_visible_fit.triggered.connect(self.command_help_visible_fit)
        menu_Help_visible.addAction(self.action_help_visible_fit)
        
        self.action_help_visible_log = QtWidgets.QAction()
        self.action_help_visible_log.setText('Logger')
        #self.action_Open_image.setShortcut('Ctrl+O')
        self.action_help_visible_log.setCheckable(True)
        self.action_help_visible_log.setChecked(True)
        self.action_help_visible_log.triggered.connect(self.command_help_visible_log)
        menu_Help_visible.addAction(self.action_help_visible_log)
        
        self.action_help_button_about = QtWidgets.QAction()
        self.action_help_button_about.setText('About')
        self.action_help_button_about.setShortcut('Ctrl+H')
        self.action_help_button_about.triggered.connect(self.open_about)
        menu_Help.addAction(self.action_help_button_about)
        
        self.menu_meas = menu_meas
        self.menu_measTemp = menu_measTemp
        self.menu_gaugetabRuby = menu_gaugetabRuby
        self.menu_gaugetabSam = menu_gaugetabSam
        self.menu_fit = menu_fit
        self.menu_log = menu_log
        self.menu_Help = menu_Help
        
        #self.menu_measTemp.menuAction().setVisible(False)
        
        self.setMenuBar(menu_Bar)
        self.init_Statusbar()
        self.model.statusbar_message('Done Menu')
    
    def script_info(self):
        script = os.path.abspath(__file__)
        script_dir = os.path.dirname(script)
        script_name = os.path.basename(script)
        now = datetime.now()
        date = now.isoformat(sep = ' ', timespec = 'seconds') #example = '2024-03-27 18:04:46'
        
        print()
        print('_/‾\\'*20)
        print()
        print(date)
        print()
        print("File folder = " + script_dir)
        print("File name = " + script_name)
        print("Current working directory (AKA Called from ...) = " + os.getcwd())
        print("Python version = " + sys.version)
        print("Python folder = " + sys.executable)
        print()
        print('_/‾\\'*20)
        print()
        
        time = datetime.now().strftime("%d %B %Y %H:%M:%S")
        message = '\n'
        message+= f'Program name = {self.__name__}\n'
        message+= f'Version {self.__version__} | Release {self.__release__}\n'
        message+= '\n'
        message+= "Sys Info:\n"
        message+= '\n'
        message+= f"OS: {platform.system()} {platform.release()}\n"
        message+= f"Architecture: {platform.machine()}\n"
        message+= '\n'
        message+= 'Script Info:\n'
        message+= '\n'
        message+= f"File folder = {script_dir}\n"
        message+= f"File name = {script_name}\n"
        message+= f"Current working directory = {os.getcwd()}\n"
        message+= f"Python version = {sys.version}\n"
        message+= f"Python folder = {sys.executable}\n"
        message+= '\n'
        self.pop_up_info.setWindowTitle('Info ' + time)
        self.pop_up_info.label.setText(message)
        self.pop_up_info.show()
        
    def open_about(self):
        self.about.show()
        
    def command_help_button_debug(self):
        #print(self.spec.sdk.GetTemperatureStatus())
        print()
        print('_/‾\\'*20)
        print()
        if self.spectrometer_model == "Andor":
            self.spec.helper.print_all()
        self.eee()
        
        print()
        print('_/‾\\'*20)
        print()
        
    #Logger section
    
    def command_log_button_folder(self):
        
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose the folder where the log files will be saved")
        
        if folder != '':
            self.update_log_button_folder(folder)
        
    def update_log_button_folder(self, value):
        
        self.logger_folder = Path(value)
        message = str(self.logger_folder)
        max_l = 30
        if len(message)>max_l:
            short_message = message[0:max_l] + '...'
        else:
            short_message = message
        self.controls.log_label_folder.setText(short_message)
        self.action_log_button_folder.setText(message)
        self.model.statusbar_message('Logger Path = ' + message)
        
    def command_log_button_threshold(self):
        title = 'Change Value'
        label = 'Enter new threshold in Intensity a.u.'
        value = self.log_threshold
        minvalue = 1
        new_value, ok = QtWidgets.QInputDialog.getInt(self, title, label , value, minvalue)
    
        
        if ok:
            self.update_log_button_threshold(new_value)
            
    def update_log_button_threshold(self, value):
        
        self.log_threshold= value
        message = f'{self.log_threshold} a.u.'
        self.action_log_button_threshold.setText(message)
        self.controls.log_button_threshold.setText(message)
        self.model.statusbar_message('Logger threshold = ' + message)
        
    def command_log_button_delta(self):
        title = 'Change Value'
        label = 'Enter new log time in seconds'
        value = self.log_delta
        minvalue = 1
        maxvalue = 10000
        new_value, ok = QtWidgets.QInputDialog.getInt(self, title, label , value, minvalue, maxvalue)
    
        
        if ok:
            self.update_log_button_delta(new_value)
            
    def update_log_button_delta(self, value):
        
        self.log_delta = value
        message = f'{self.log_delta} sec'
        self.action_log_button_delta.setText(message)
        self.controls.log_button_delta.setText(message)
        self.model.statusbar_message('Logger time = ' + message)
     
    #Menu visibility section
        
    def command_help_visible_all(self, value):
        
        self.controls.setVisible(value)
        
        self.action_help_visible_file.setChecked(value)
        self.action_help_visible_spec.setChecked(value)
        self.action_help_visible_meas.setChecked(value)
        self.action_help_visible_tabs_gauge.setChecked(value)
        self.action_help_visible_fit.setChecked(value)
        self.action_help_visible_log.setChecked(value)

        self.controls.group_gauge.setVisible(value)
        self.controls.group_log.setVisible(value)
        self.controls.group_fit.setVisible(value)
        self.controls.group_meas.setVisible(value)
        self.controls.group_spec.setVisible(value)
        self.controls.group_file.setVisible(value)

    
    def command_help_visible_tabs_gauge(self, value):
        #self.controls.group_tabs_gauge.hide()
        self.controls.group_gauge.setVisible(value)
        if value:
            self.controls.setVisible(value)
            
    def command_help_visible_log(self, value):
        #self.controls.group_logger.hide()
        self.controls.group_log.setVisible(value)
        if value:
            self.controls.setVisible(value)
        
    def command_help_visible_fit(self, value):
        #self.controls.group_fit.hide()
        self.controls.group_fit.setVisible(value)
        if value:
            self.controls.setVisible(value)
        
    def command_help_visible_meas(self, value):
        #self.controls.group_meas.hide()
        self.controls.group_meas.setVisible(value)
        if value:
            self.controls.setVisible(value)
        
    def command_help_visible_spec(self, value):
        #self.controls.group_spec.hide()
        self.controls.group_spec.setVisible(value)
        if value:
            self.controls.setVisible(value)
        
    def command_help_visible_file(self, value):
        #self.controls.group_file.hide()
        self.controls.group_file.setVisible(value)
        if value:
            self.controls.setVisible(value)
        
    def init_Statusbar(self):
        self.statusbar = QtWidgets.QStatusBar()
        #self.statusbar.addPermanentWidget(QtWidgets.QLabel("Welcome !"))
        #self.statusbar.addWidget(QtWidgets.QLineEdit())
        self.setStatusBar(self.statusbar)
        #self.statusbar.showMessage('Init 2')
        self.model.statusbar_message_add(self.statusbar.showMessage)
    
    def get_font_size(self):
        size, ok = QtWidgets.QInputDialog.getInt(self, 'Font Size', 'Enter size (min 10):', self.font_size, 10)
        if ok:
            self.font_size = size
            self.action_help_setFontsSize.setText(f'Font Size {int(self.font_size)}')
            self.model.statusbar_message(f'Font Size {int(self.font_size)}')
            self.update_font()
    
    def get_font_style(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self,"Select .qss File", '', "QSS files (*.qss)")
        if filename != '':
            style = Path(filename).read_text()
            self.font_style = style
            self.model.statusbar_message(f'Font Style {Path(filename).name}')
            self.update_font()
    
    def reset_font_style_and_size(self):
        self.font_style = ''
        self.font_size = 15
        self.action_help_setFontsSize.setText(f'Font Size {int(self.font_size)}')
        self.update_font()
        self.model.statusbar_message(f'Default Style, Font Size {int(self.font_size)}')
        
    def update_font(self):
        style = self.font_style + """
                      * {
                          font-size: """ + str(int(self.font_size)) + """px;
                    }
                      """
        QtWidgets.qApp.setStyleSheet(style)
        self.controls.force_style_update(self.font_size)
        
        # self.adjustSize()
        # current_size = self.size()
        # self.resize(current_size.width() + 1, current_size.height())
        # self.resize(current_size)
        # self.repaint()
        
        
        # if self.mainWidget.layout():
        #     self.mainWidget.layout().invalidate() 
        # for child_widget in self.mainWidget.findChildren(QtWidgets.QWidget):
        #     child_widget.updateGeometry()
        # self.setWidget(self.mainWidget)
        # self.frame.adjustSize()
        # self.adjustSize()
        # self.update()
        
    def command_quit(self):
        
        self.close() #Call closeEvent()
    
    def closeEvent(self, event):
        
        self.command_meas_abort()
        choice = QtWidgets.QMessageBox.question(self, "Quit", f"Do you want to Quit {self.window_Title} ?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        QtWidgets.QMessageBox()
        if choice == QtWidgets.QMessageBox.Yes:
            self.model.statusbar_message('Quitting, please wait ...')
            if self.spec.connected:
                self.spec.close()
                self.main_thread_A.quit() #Thread_7) Close Main Thread at the end
                if self.spectrometer_model == "Andor":
                    self.main_thread_B.quit() #Thread_7) Close Main Thread at the end
            sleep(1)
            self.report_window.close()
            
            event.accept()
        else:
            event.ignore()
            
def main():
    #Entry point in poetry pyproject.toml
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_DontShowIconsInMenus) 
    app.setStyleSheet("""
                      * {
                          font-size: 15px;
                    }
                      QGroupBox { font-weight: bold;  color : blueviolet; } 
                      """)
    window = Window(False) 
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

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

