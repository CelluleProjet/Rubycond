# -*- coding: utf-8 -*-
"""

Rubycond: Pressure by Ruby Luminescence (PRL) software to determine pressure in diamond anvil cell experiments.

Version 0.1.2
Release 240227

Author:

Yiuri Garino:

Copyright (c) 2023-2024 Yiuri Garino

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

Ocean Optics Drivers: python-seabreeze

https://python-seabreeze.readthedocs.io/en/latest/

conda install -c conda-forge seabreeze

to configure seabreeze run the command:
    
seabreeze_os_setup
 
"""

import sys

if hasattr(sys, 'ps1'):
    #clean Console and Memory
    from IPython import get_ipython
    get_ipython().run_line_magic('clear','/')
    get_ipython().run_line_magic('reset','-sf')
    import sys
    print("Running interactively")
    print()
    terminal = False
else:
    print("Running in terminal")
    print()
    terminal = True


import threading
import numpy as np
import tkinter as tk
from tkinter import font
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from datetime import datetime
from time import sleep
from lmfit.models import LorentzianModel, GaussianModel, VoigtModel, PolynomialModel


try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from PIL import Image, ImageTk
from pathlib import Path
from scipy.special import wofz
from lmfit import Parameters, minimize
import os 

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)

try:
    from subs.rubycond_calibrator import Main as R_C_Main
except:
    #https://docs.python.org/3/library/importlib.metadata.html
    import importlib
    if sys.version_info < (3, 10):
        from importlib_metadata import entry_points
    else:
        from importlib.metadata import entry_points
    eps = entry_points()

    
    scripts = eps.select(group='console_scripts')  
    rubycond_calibrator = scripts['rubycond_calibrator_call']
    #Entry point in rubycond_calibrator poetry pyproject.toml
    R_C_Main = rubycond_calibrator.load()



from subs import Equations_RubySam_Scale as RS
from subs import Init_file_class as Init
from subs import Logger_class as Logger
debug = False
resize = True

if debug:
    print(os.path.basename(__file__))
    print('starting ')
    print('')
    print('__file__')
    print(__file__)
    print('')
    print('os.getcwd()')
    print(os.getcwd())
    print('')
    print('sys.path')
    [print(i) for i in sys.path]
    print('')

padx = 10
pady = 10

class Main:
    def __init__(self, root, init, spec = None):
        self.Init = init
        
        
        
        
        self.logger = Logger.Logger(parameters = self.log_parameters , methods = [self.Save_log], debug = False)
        self.init_log_par()
        #Fot Size
        #Font main application
        self.defaultFont = font.nametofont("TkDefaultFont") #ref_fontsize
        self.defaultFont.configure(size=14) 
        #Text in Fit Window
        self.Fit_window_font_size = ("", 14)
        
        #Text in Menu (in Windwos the 1st line is Windows system settings, not Tk)
        self.default_menu_Font = ("",14)
        
        self.default_entry_Font = ("",14)
        
        res_x = int(448/2) # Image in About
        res_y = int(300/2) # Image in About
        ratio = 1
        self.figsize = (10*ratio,6*ratio)
        try:
            file_IMPMC = Path("subs/logo_IMPMC.jpg")
            path_IMPMC = Path(__file__).parent.resolve() / file_IMPMC
            file_CP = Path("subs/logo_CP.jpg")
            path_CP = Path(__file__).parent.resolve() / file_CP
        except:
            path_IMPMC = file_IMPMC
            path_CP = file_CP
        self.photo_IMPMC = ImageTk.PhotoImage(Image.open(path_IMPMC).resize((res_x, res_y)))
        self.photo_CP = ImageTk.PhotoImage(Image.open(path_CP).resize((res_x, res_y)))
        self.im_IMPMC = Image.open(path_IMPMC)
        self.im_CP = Image.open(path_CP)
        self.About = """

Rubycond: Pressure by Ruby Luminescence (PRL) software to determine pressure in diamond anvil cell experiments.

Version 0.1.2
Release 240227

Author:

Yiuri Garino:

Copyright (c) 2023-2024 Yiuri Garino

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

Ocean Optics Drivers: python-seabreeze

https://python-seabreeze.readthedocs.io/en/latest/

conda install -c conda-forge seabreeze

to configure seabreeze run the command:
    
seabreeze_os_setup
 
"""
        self.Shortcuts = """
ctrl + # = Select the # Tab

ctrl + z = Set Fit:Min as cursor
ctrl + x = Set Fit:Max as cursor
ctrl + c = Zoom to fit
ctrl + q = Rescale to full scale
ctrl + f = Fit snap
ctrl + g = Fit continuos

ctrl + r = Read file
ctrl + s = Save image
ctrl + v = Save fit
"""

        if spec == None:
            self.stand_alone = "True"
        else:
            self.stand_alone = init.init_var['Settings']['stand_alone'] 
        
        I = float(init.init_var['Spectrometer']['calibration_i'])
        C1 = float(init.init_var['Spectrometer']['calibration_c1'])
        C2 = float(init.init_var['Spectrometer']['calibration_c2'])
        C3 = float(init.init_var['Spectrometer']['calibration_c3'])
        
        self.calib_par = np.array((I, C1, C2, C3))
        self.new_calib_par = np.copy(self.calib_par)
        
        if debug: print(f'Calibration parameters = {self.calib_par}')
        
        self.click = [ float("NaN"), float("NaN"),float("NaN"),float("NaN"),float("NaN") ]
        self.center_pk = 0.
        
        self.sigma = float(init.init_var['Spectrometer']['sigma (cm-1)']) #sigma of the Gaussian profile, defined by the spectrometer resolution
        self.sigma_vary = eval(init.init_var['Spectrometer']['sigma_vary']) #Voigt Gaussian component, Vary if sigma spectrometer is unknown
        if debug: print(f'sigma_vary = {self.sigma_vary}')
        
        self.ruby_ref = 694.25 #nm
        self.ruby_ref_TL0 = 298
        self.ruby_ref_TL = 298 
        
        
        self.SrB4O7_ref = 685.51 #nm
        
        self.Gauge_eq = None
        
        self.Main_title = 'No Gauge Selected'
        
        self.Fit_report = 'No Fit Performed'
        
        #https://www.w3.org/TR/xml-entity-names/025.html
        #https://en.wikipedia.org/wiki/Unicode_subscripts_and_superscripts
        self.menu_sel = '\u25C9'
        
        #tk Variables
        self.dark = tk.BooleanVar()
        self.dark.set(True)
        
        self.bkg = tk.BooleanVar()
        self.bkg.set(False)
        
        self.calib = tk.BooleanVar()
        self.calib.set(True)
        
        self.autoupdate = tk.BooleanVar()
        self.autoupdate.set(False)
        
        self.acquire_continuos_status = tk.BooleanVar() #Set in Stand Alone
        
        self.acquire_snap_status = tk.BooleanVar()

        
        self.fit_snap_flag = False
        
        self.fit = tk.BooleanVar()
        self.fit.set(False)
        
        self.x_axis_units = tk.BooleanVar()
        self.x_axis_units.set(False) #False = nm
        
        self.Integration_time = tk.DoubleVar()
        self.Integration_time.set(.1)
        self.log_integration_time = .1 
        
        self.Logger_time = tk.DoubleVar()
        self.Logger_time.set(1)
        #self.logger.logger_time = 1
        
        self.Logger_Directory = tk.StringVar()
        self.Logger_Directory.set(self.logger.logger_folder)

        self.logging = tk.BooleanVar()
        self.logging.set(False)
        
        self.Fit_function = tk.StringVar()
        self.Fit_function.set("Voigt") #"Lorentz", "Gauss", "Voigt"
        
        self.Ruby_P_gauge = tk.StringVar()
        self.Ruby_P_gauge.set("None") 
        
        self.calc_Ruby_P_gauge = tk.StringVar()
        self.calc_Ruby_P_gauge.set("Shen 2020")
        
        self.calc_Sam_P_gauge = tk.StringVar()
        self.calc_Sam_P_gauge.set("Rashchenko 2015")
        
        self.calc_Ruby_T_gauge = tk.StringVar()
        self.calc_Ruby_T_gauge.set("Datchi 2004")
        
        self.Ruby_name = 'Cr\u00B3\u207A:Al\u2082O\u2083'
        self.Ruby_T_gauge = tk.StringVar()
        self.Ruby_T_gauge.set("None") 
        
        self.Sam_Name = 'Sm\u00B2\u207A:SrB\u2084O\u2087'
        self.Sam_gauge = tk.StringVar()
        self.Sam_gauge.set("None") 
        
        self.Polynomial_degree = tk.IntVar()
        self.Polynomial_degree.set(1)
        
        self.Accumulation_n = tk.IntVar()
        self.Accumulation_n.set(1)
        self.log_accumulation = 1 
        
        self.Accumulation_i = tk.IntVar()
        self.Accumulation_i.set(1)
        
        self.pointer_line = None
        
        self.root = root
        self.filename = 'No File'
        
        self.interval = 150 #TK after delay in ms
        self.Running_thread = False
        
        if self.stand_alone == "False":
            #Spectrometer Initialization
            self.acquire_continuos_status.set(True)
            self.spec = spec
            if debug: print("Int time = ", self.Integration_time.get()*1e6)
            self.spec.integration_time_micros(self.Integration_time.get()*1e6)
            if debug: 
                print()
                print(f'Found {self.spec}')
                print()
                print(f"SN {self.spec.serial_number}, {self.spec.pixels} pixels")
            self.wavelengths = self.spec.wavelengths()
            
            self.intensities = self.spec.intensities(correct_dark_counts=self.dark.get())
            self.intensities_bkg = np.zeros_like(self.intensities)
            self.Accumulation_data = np.zeros((self.spec.pixels,self.Accumulation_n.get()))
            self.Accumulation_data_flag = False
            if debug: print(f"Mem array size = {self.Accumulation_data.shape}")
            #Todo https://github.com/ap--/python-seabreeze/issues/88
            self.black_pixels = [6,18]
            self.int_limits = self.spec.integration_time_micros_limits
            if debug: print(self.int_limits)
        else:
            #Stand Alone, read file
            self.acquire_continuos_status.set(False)
            # self.wavelengths = None
            # self.intensities = None
            self.Init_file()
        # print(self.wavelengths[0])
        # print(self.wavelengths[-1])
        # print(self.wavelengths)
        # self.QuitMain()
        
        self.Fit_to_save = np.zeros_like(self.wavelengths)
        self.pk1_to_save = np.zeros_like(self.wavelengths)
        self.pk2_to_save = np.zeros_like(self.wavelengths)
        
        self.Fit_range_min = tk.DoubleVar()
        self.Fit_range_min.set(self.wavelengths.min())
        self.fit_x_min = self.wavelengths.min()
        
        self.Fit_range_min_idx = self.wavelengths.argmin()
        
        if debug: print(f'Min wavelengths = {self.wavelengths.min()}')
        self.Fit_range_max = tk.DoubleVar()
        self.Fit_range_max.set(self.wavelengths.max())
        self.fit_x_max = self.wavelengths.max()
        
        self.Fit_range_max_idx = self.wavelengths.argmax()
        
        if debug: print(f'x id range {self.Fit_range_min_idx} {self.Fit_range_max_idx}')
        
        self.Fit_iter_lim = tk.IntVar()
        self.Fit_iter_lim.set(150)
        
        self.Update_fit()
        
        self.W_range_min = self.Fit_range_min.get()
        self.W_range_max = self.Fit_range_max.get()
        
        if debug: print(f'Max wavelengths = {self.wavelengths.max()}')
        
        self.Fit_window_active = False
        
        root.protocol("WM_DELETE_WINDOW", self.QuitMain) #Intercept the close button
        root.title("Rubycond")
        root.configure(background='DimGray')
        self.tabControl = ttk.Notebook(root)
        
        if resize:
            root.grid_columnconfigure(0, weight=1)
            root.grid_rowconfigure(0, weight=1)
            
        self.tab1 = ttk.Frame(self.tabControl, borderwidth=5, relief="sunken")
        self.tab2 = ttk.Frame(self.tabControl, borderwidth=5, relief="sunken")
        self.tab3 = ttk.Frame(self.tabControl, borderwidth=5, relief="sunken")
        self.tab4 = ttk.Frame(self.tabControl, borderwidth=5, relief="sunken", width = res_x*2, height = res_y*2)
        if resize:
            self.tab1.grid_columnconfigure(0, weight=1)
            self.tab1.grid_rowconfigure(0, weight=1)
            
        self.tabControl.add(self.tab1, text ='PRL')
        self.tabControl.add(self.tab2, text ='Shortcuts')
        self.tabControl.add(self.tab3, text ='Calc')
        self.tabControl.add(self.tab4, text ='About')
        
        label_Shortcuts = tk.Label(self.tab2, text = self.Shortcuts, anchor = 'e', justify = "left", padx = padx, pady = pady)

                               
        label_Shortcuts.grid(row = 1, column = 0, columnspan = 2, sticky = tk.NSEW)
        
        label_CP = tk.Label(self.tab4, image = self.photo_CP, padx = padx, pady = pady)
        label_CP.grid(row = 0, column = 0, sticky = tk.NSEW)

        label_IMPMC = tk.Label(self.tab4, image = self.photo_IMPMC, padx = padx, pady = pady)
        label_IMPMC.grid(row = 0, column = 1, sticky = tk.NSEW)

        #label_About = tk.Label(self.tab4, text = self.About, anchor = 'e', justify = "left", padx = padx, pady = pady, wraplength=2*res_x)

        label_About = tk.Text(self.tab4, borderwidth=0, font = self.Fit_window_font_size) #ref_fontsize
        label_About.insert(1.0, self.About)
        label_About.grid(row = 1, column = 0, columnspan = 2, sticky = tk.NSEW)
        
        self.calc()
        

        self.tabControl.pack(expand = True, fill ="both")
          
        self.Init_figure()
        
        #Menu
        
        menu = tk.Menu(root)
        root.config(menu=menu)
        
        # File Menu
        
        fileMenu = tk.Menu(menu, font = self.default_menu_Font)
        if self.stand_alone == "False":
            fileMenu.add_command(label="Save", command=self.Save_file, font = self.default_menu_Font, underline = 0) #ToDo, font = self.menu_font) NOT WORKING in add_cascade menu_font = None #("", 50)
        fileMenu.add_command(label="Save Fit", command=self.Save_fit, font = self.default_menu_Font, underline = 1)
        fileMenu.add_command(label="Open File", command=self.Read_file, font = self.default_menu_Font, underline = 0)#ToDo, accelerator = 'Control + r')
        fileMenu.add_command(label="Quit", command=self.QuitMain, font = self.default_menu_Font, underline = 0)
        menu.add_cascade(label="File", menu=fileMenu, font = self.default_menu_Font, underline = 0)
        
        # Graph Menu
        
        graphMenu = tk.Menu(menu, font = self.default_menu_Font)
        graphMenu.add_command(label='Rescale Y', command=self.Rescale_y, font = self.default_menu_Font, underline = 8)
        graphMenu.add_command(label='Rescale X', command=self.Rescale_x, font = self.default_menu_Font, underline = 8)
        graphMenu.add_command(label='Rescale XY', command=self.Rescale_xy, font = self.default_menu_Font, underline = 1)
        graphMenu.add_command(label='Rescale to Fit', command=self.Rescale_to_fit, font = self.default_menu_Font, underline = 0)
        #X_axis_units sub menu / Graph Menu
        
        x_axisMenu = tk.Menu(menu, tearoff = 0, font = self.default_menu_Font)
        x_axisMenu.add_radiobutton(label='nm', variable = self.x_axis_units, value=False, command = self.Change_x_axis_units, font = self.default_menu_Font, underline = 0) #False = nm
        x_axisMenu.add_radiobutton(label='cm\u207B\u00B9', variable = self.x_axis_units, value=True, command = self.Change_x_axis_units, font = self.default_menu_Font, underline = 0)
        graphMenu.add_cascade(label="X axis units", menu=x_axisMenu, font = self.default_menu_Font, underline = 2) #unicode ref https://groups.google.com/g/comp.lang.tcl/c/9uQXrnfbt8c
        
        menu.add_cascade(label="Graph", menu=graphMenu, font = self.default_menu_Font, underline = 0)
        
        # Spectrometer Menu
        # Not Available if Stand Alone
        
        if self.stand_alone == "False":
            specMenu = tk.Menu(menu, font = self.default_menu_Font)

            menu.add_cascade(label="Spectrometer", menu=specMenu, font = self.default_menu_Font)
            
            modelMenu = tk.Menu(menu, tearoff = 0, font = self.default_menu_Font)
            modelMenu.add_command(label=f'{self.spec}', font = self.default_menu_Font)
            
            specMenu.add_cascade(label='Model', menu = modelMenu, font = self.default_menu_Font)
            specMenu.add_checkbutton(label='User Calibration', onvalue=1, offvalue=0, variable=self.calib, command = self.Set_calib, font = self.default_menu_Font, underline = 0)
            specMenu.add_checkbutton(label='Electronic Dark', onvalue=1, offvalue=0, variable=self.dark, command = self.reset_bkg, font = self.default_menu_Font, underline = 0) 
            specMenu.add_command(label='Take Background', command=self.memorize_bkg, font = self.default_menu_Font, underline = 0)
            specMenu.add_checkbutton(label='Subtract Background', onvalue=1, offvalue=0, variable=self.bkg, font = self.default_menu_Font, underline = 0)
            specMenu.add_command(label='Calibrate', command=self.calibrate, font = self.default_menu_Font, underline = 0)

        # Measurement Menu
        # Not Available if Stand Alone
        
        if self.stand_alone == "False":
            self.measMenu = tk.Menu(menu, font = self.default_menu_Font)
            menu.add_cascade(label="Measurement", menu=self.measMenu, font = self.default_menu_Font, underline = 0)

            #self.measMenu.add_command(label='Snap', command=self.acquire_snap)
            self.measMenu.add_checkbutton(label='Snap', onvalue=1, offvalue=0, variable=self.acquire_snap_status, command=self.acquire_snap, font = self.default_menu_Font, underline = 0)
            
            if self.acquire_continuos_status.get():
                self.measMenu.entryconfig(1, state=tk.DISABLED)
                self.acquire_snap_status.set(False)
            else:
                self.measMenu.entryconfig(1, state=tk.NORMAL)
                
            self.measMenu.add_checkbutton(label='Acquire', onvalue=1, offvalue=0, variable=self.acquire_continuos_status, command = self.acquire_continuos, font = self.default_menu_Font, underline = 0)
            self.measMenu.add_separator()
            
            self.intMenu = tk.Menu(menu, tearoff = 0, font = self.default_menu_Font)
            self.measMenu.add_cascade(label='Int Time (s)', menu = self.intMenu, font = self.default_menu_Font)
            self.intMenu.add_command(label=self.Integration_time.get(), command=self.Int_time, font = self.default_menu_Font)
            
            self.accMenu = tk.Menu(menu, tearoff = 0, font = self.default_menu_Font)
            self.measMenu.add_cascade(label='Accumulation', menu = self.accMenu, font = self.default_menu_Font)
            self.accMenu.add_command(label=self.Accumulation_n.get(), command=self.Acc_n, font = self.default_menu_Font, underline = 1)
        
        #Pressure Gauge Menu
        
        self.presMenu = tk.Menu(menu, font = self.default_menu_Font)
        
        #Lambda zero Ruby
        
        self.presMenu.add_separator()
        self.presMenu.add_command(label='Ruby', font = self.default_menu_Font) 
        self.presMenu.add_command(label=f'    \u03BB\u2080 (nm) = {self.ruby_ref:.2f}', command=self.set_ruby_ref, font = self.default_menu_Font) 
        
        #Ruby sub menu / Pressure Gauge Menu
        
        rubyMenu = tk.Menu(menu, tearoff = 0, font = self.default_menu_Font)
        rubyMenu.add_checkbutton(label='Shen 2020', onvalue="Shen 2020", offvalue='None', variable = self.Ruby_P_gauge, command = self.Update_Ruby_P_Gauge, font = self.default_menu_Font, underline = 0)
        rubyMenu.add_checkbutton(label='Mao hydro 1986', onvalue="Mao hydro 1986", offvalue='None', variable = self.Ruby_P_gauge, command = self.Update_Ruby_P_Gauge, font = self.default_menu_Font, underline = 4)
        rubyMenu.add_checkbutton(label='Mao non hydro 1986', onvalue="Mao non hydro 1986", offvalue='None', variable = self.Ruby_P_gauge, command = self.Update_Ruby_P_Gauge, font = self.default_menu_Font, underline = 4)
        rubyMenu.add_checkbutton(label='Dewaele 2008', onvalue="Dewaele 2008", offvalue='None', variable = self.Ruby_P_gauge, command = self.Update_Ruby_P_Gauge, font = self.default_menu_Font, underline = 1)
        rubyMenu.add_checkbutton(label='Dorogokupets and Oganov 2007', onvalue="Dorogokupets and Oganov 2007", offvalue='None', variable = self.Ruby_P_gauge, command = self.Update_Ruby_P_Gauge, font = self.default_menu_Font, underline = 1)
        self.presMenu.add_cascade(label="    P Calibration", menu=rubyMenu, font = self.default_menu_Font, underline = 4) #✔ \u2714
        
        #T(Lambda zero) Ruby
        
        self.presMenu.add_command(label=f'    T(\u03BB\u2080) (K) = {self.ruby_ref_TL0:.2f}', command=self.set_ruby_ref_TL0, font = self.default_menu_Font) 
        self.presMenu.add_command(label=f'    T(\u03BB) (K) = {self.ruby_ref_TL:.2f}', command=self.set_ruby_ref_TL, font = self.default_menu_Font) 
        
        #Ruby Temperature sub menu / Pressure Gauge Menu
        
        rubyTMenu = tk.Menu(menu, tearoff = 0, font = self.default_menu_Font)
        rubyTMenu.add_checkbutton(label='Datchi 2004', onvalue="Datchi 2004", offvalue='None', variable=self.Ruby_T_gauge, command = self.Update_Ruby_T_Gauge, font = self.default_menu_Font, underline = 0)
        self.presMenu.add_cascade(label="    T Calibration", menu=rubyTMenu, font = self.default_menu_Font, underline = 4)
        self.presMenu.add_separator()
        
        #Lambda zero SrB4O7

        self.presMenu.add_command(label=self.Sam_Name, font = self.default_menu_Font) 
        self.presMenu.add_command(label=f'    \u03BB\u2080 (nm) = {self.SrB4O7_ref:.2f}', command=self.set_SrB4O7_ref, font = self.default_menu_Font)
        
        #Samarium sub menu / Pressure Gauge Menu
        
        samMenu = tk.Menu(menu, tearoff = 0, font = self.default_menu_Font)
        samMenu.add_checkbutton(label='Rashchenko 2015', onvalue='Rashchenko 2015', offvalue='None', variable = self.Sam_gauge, command = self.Update_Sam_Gauge, font = self.default_menu_Font, underline = 0)
        samMenu.add_checkbutton(label='Datchi 1997', onvalue='Datchi 1997', offvalue='None', variable = self.Sam_gauge, command = self.Update_Sam_Gauge, font = self.default_menu_Font, underline = 0)
        self.presMenu.add_cascade(label="    P Calibration", menu=samMenu, font = self.default_menu_Font, underline = 4)
        
        menu.add_cascade(label="Gauge", menu=self.presMenu, font = self.default_menu_Font, underline = 1)
        #Fit Menu
        
        self.fitMenu = tk.Menu(menu, font = self.default_menu_Font)
        menu.add_cascade(label="Fit", menu=self.fitMenu, font = self.default_menu_Font, underline = 1)
        
        self.fitMenu.add_command(label='Snap', command = self.Fit_snap, font = self.default_menu_Font, underline = 0)
        self.fitMenu.add_checkbutton(label='Continous', onvalue=1, offvalue=0, variable=self.fit, command = self.Fit_acquire, font = self.default_menu_Font, underline = 0)
 
        self.fitMenu.add_separator()
        
        #Function sub menu / Fit Menu
        
        eqMenu = tk.Menu(menu)
        eqMenu.add_radiobutton(label='Voigt', variable = self.Fit_function, value="Voigt", command = self.Update_fit, font = self.default_menu_Font, underline = 0)
        eqMenu.add_radiobutton(label='Gauss', variable = self.Fit_function, value="Gauss", command = self.Update_fit, font = self.default_menu_Font, underline = 0)
        eqMenu.add_radiobutton(label='Lorentz', variable = self.Fit_function, value="Lorentz", command = self.Update_fit, font = self.default_menu_Font, underline = 0)
        eqMenu.add_radiobutton(label='Double Voigt', variable = self.Fit_function, value="Double Voigt", command = self.Update_fit, font = self.default_menu_Font, underline = 11)
        eqMenu.add_radiobutton(label='Double Gauss', variable = self.Fit_function, value="Double Gauss", command = self.Update_fit, font = self.default_menu_Font, underline = 11)
        eqMenu.add_radiobutton(label='Double Lorentz', variable = self.Fit_function, value="Double Lorentz", command = self.Update_fit, font = self.default_menu_Font, underline = 13)
        self.fitMenu.add_cascade(label="Function", menu=eqMenu, font = self.default_menu_Font, underline = 0)
        
        self.polMenu = tk.Menu(menu, tearoff = 0, font = self.default_menu_Font)
        self.polMenu.add_command(label=self.Polynomial_degree.get(), command=self.Poly_degree, font = self.default_menu_Font)
        
        self.minMenu = tk.Menu(menu, tearoff = 0, font = self.default_menu_Font)
        self.minMenu.add_command(label='Enter Value', command=self.F_r_min, font = self.default_menu_Font)
        self.minMenu.add_command(label=f'Set {self.click[3]:.2f}', command=self.F_r_min_set_click, font = self.default_menu_Font)
        
        self.maxMenu = tk.Menu(menu, tearoff = 0, font = self.default_menu_Font)
        self.maxMenu.add_command(label='Enter Value', command=self.F_r_max, font = self.default_menu_Font)
        self.maxMenu.add_command(label=f'Set {self.click[3]:.2f}', command=self.F_r_max_set_click, font = self.default_menu_Font)
        
        self.iterMenu = tk.Menu(menu, tearoff = 0, font = self.default_menu_Font)
        self.iterMenu.add_command(label=self.Fit_iter_lim.get(), command=self.Iter_lim, font = self.default_menu_Font)
        
        self.fitMenu.add_cascade(label='Poly Degree', menu = self.polMenu, font = self.default_menu_Font, underline = 0)
        self.fitMenu.add_cascade(label=f'Min {self.Fit_range_min.get():.2f}', menu = self.minMenu, font = self.default_menu_Font)
        self.fitMenu.add_cascade(label=f'Max {self.Fit_range_max.get():.2f}', menu = self.maxMenu, font = self.default_menu_Font)
        self.fitMenu.add_cascade(label='Iter Lim', menu = self.iterMenu, font = self.default_menu_Font, underline = 0)
        self.fitMenu.add_checkbutton(label='Autoupdate', variable=self.autoupdate, font = self.default_menu_Font, underline = 0)
        
        self.fitMenu.add_separator()
        
        
        self.fitMenu.add_command(label='Clean Graph', command = self.Reset_fit_figure, font = self.default_menu_Font, underline = 1)
        
        #Logger Menu
        # Not Available if Stand Alone
        
        if self.stand_alone == "False":
            self.logMenu = tk.Menu(menu, font = self.default_menu_Font)
            menu.add_cascade(label="Logger", menu=self.logMenu, font = self.default_menu_Font, underline = 1)
            
            self.logMenu.add_checkbutton(label='Logger (OFF)', onvalue=1, offvalue=0, variable=self.logging, command = self.logger_on_off, font = self.default_menu_Font, underline = 0)
            
            self.logTMenu = tk.Menu(menu, tearoff = 0, font = self.default_menu_Font)
            self.logMenu.add_cascade(label='Log Time (s)', menu = self.logTMenu, font = self.default_menu_Font)
            self.logTMenu.add_command(label=self.Logger_time.get(), command=self.log_time, font = self.default_menu_Font)
            
            self.logDirMenu = tk.Menu(menu, tearoff = 0, font = self.default_menu_Font)
            self.logMenu.add_cascade(label='Log Directory', menu = self.logDirMenu, font = self.default_menu_Font)
            self.logDirMenu.add_command(label=self.Logger_Directory.get(), command=self.log_directory, font = self.default_menu_Font)
        #todo
        
        #Bindings o Shortcuts
        
        self.root.bind_all('<Control-z>', self.F_r_min_set_click)
        self.root.bind_all('<Control-x>', self.F_r_max_set_click) 
        self.root.bind_all('<Control-c>', self.Rescale_to_fit)
        self.root.bind_all('<Control-r>', self.Read_file)
        self.root.bind_all('<Control-v>', self.Save_fit)
        self.root.bind_all('<Control-f>', self.Fit_snap)
        self.root.bind_all('<Control-g>', self.Fit_acquire_ctrl)
        self.root.bind_all('<Control-q>', self.Rescale_xy)
        #self.root.bind_all('a', self.print_time)
        self.root.bind_all('<Control-Key-1>', lambda event:self.tabControl.select(self.tab1))
        self.root.bind_all('<Control-Key-2>', lambda event:self.tabControl.select(self.tab2))
        self.root.bind_all('<Control-Key-3>', lambda event:self.tabControl.select(self.tab3))
        self.root.bind_all('<Control-Key-4>', lambda event:self.tabControl.select(self.tab4))

        #self.root.bind_all("<<CalibDone>>", self.print_time) # see line 367 in calibrator self.root.event_generate("<<CalibDone>>")
        
        if self.stand_alone == "False":
            sleep(2) #wait a moment to start HR4000
            if self.calib.get():
                self.Set_calib()
            
        self.Update_spectra()
        if self.stand_alone == "True":
            self.Fit_snap()
        
        if debug: print('Done Init')
    
    def logger_on_off(self):
        command = self.logging.get()
        if command:
            self.Update_menu(1, self.logMenu, 'Logger (ON)')
            self.logger.logger_start()
        else:
            self.Update_menu(1, self.logMenu, 'Logger (OFF)')
            self.logger.logger_stop()
        
    def log_directory(self):
        filename = tk.filedialog.askdirectory(title = 'Change logging folder')
        if filename == '': #cancel & esc button
            return
        if filename is None:  
            return
        try:
            filename = Path(filename)
            self.logger.logger_folder = filename
            self.Logger_Directory.set(self.logger.logger_folder)
            self.Update_menu(1, self.logDirMenu, self.Logger_Directory.get())
        except:
            print('Folder error')
    
    def log_time(self):
        entry = tk.simpledialog.askinteger(f"Logger time = {self.Logger_time.get()} seconds", "Enter new Logger time in seconds",
                                           parent=self.root, minvalue=.1)
        if entry is None: #cancel button
            return
        
        self.Logger_time.set(entry)
        self.logger.logger_time = entry
        self.Update_menu(1, self.logTMenu, self.Logger_time.get())
        if debug: print(f'Logger time = {self.Logger_time.get()}')
    
    def init_log_par(self):
        #parameters for logger
        self.log_filename = 0
        self.log_integration_time = 0
        self.log_accumulation = 0
        self.R1_center = 0
        self.R1_gamma = 0
        self.R1_fwhm = 0
        self.R2_center = 0
        self.R2_gamma = 0
        self.R2_fwhm = 0
        self.fit_x_min = 0
        self.fit_x_max = 0
        self.log_pressure_gauge = 'None'
        self.log_temperature_gauge = 'None'
        self.log_pressure = 0
        self.log_temperature = 0
        
        
        
    def log_parameters(self):
        #wrapper to pass parameters reference
        return [#self.log_filename,
        self.log_integration_time,
        self.log_accumulation,
        self.R1_center,
        self.R1_gamma,
        self.R1_fwhm,
        self.R2_center,
        self.R2_gamma,
        self.R2_fwhm,
        self.fit_x_min,
        self.fit_x_max,
        self.log_pressure_gauge,
        self.log_temperature_gauge,
        self.log_pressure,
        self.log_temperature,
        ]
    
    def calibrate(self):
        win = tk.Toplevel()
        win.title('Rubycond Calibrator')
        
        if self.x_axis_units.get():
            #True = cm-1
            _x = 1e7/self.wavelengths
        else:
            _x = self.wavelengths
        

        R_C_Main(win, self.Init, _x, self.intensities, self.new_calib_par)
        
        win.wait_window(win)
        
        if debug: print(f'Done Init, New pars = {self.new_calib_par}')
        
        if not (self.new_calib_par == self.calib_par).all():
            #Calib change, reload calib if necessary
            self.calib_par = np.copy(self.new_calib_par)
            if self.calib.get():
                self.Set_calib()

        
        
    def calc(self):

        #self.calc_w_unit = tk.IntVar()
        self.calc_t_unit = tk.IntVar()
        self.calc_t_unit.set(1)
        
        
        #Ruby calc section
        self.calc_frame_Ruby = ttk.Frame(self.tab3, borderwidth=5, relief="sunken")
        self.calc_frame_Ruby.pack(anchor=tk.W, side = tk.TOP)
        
        calc_frame_Ruby_title = tk.Label(self.calc_frame_Ruby, text = "Ruby " + self.Ruby_name, anchor = 'w')
        calc_frame_Ruby_title.grid(row=0, column=0,sticky='NSEW', padx = padx, pady = pady) #self.Ruby_name
        calc_frame_Ruby_title.configure(font='Helvetica 18 bold')
                
        ttk.Button(self.calc_frame_Ruby, text = "Calc", command = self.calc_Ruby).grid(row=0, column=1,sticky='NSEW', padx = padx, pady = pady)
        
        #tk.Label(self.calc_frame_Ruby, text = f"\u03BB\u2080 = {self.ruby_ref:.2f} nm").grid(row=1, column=0,sticky='NSEW', padx = padx, pady = pady)
        self.Ruby_lambda_zero_calc_label = tk.Label(self.calc_frame_Ruby, text = f"\u03BB\u2080 = {self.ruby_ref:.2f} nm", anchor="w")
        self.Ruby_lambda_zero_calc_label.grid(row=1, column=0,sticky='NSEW', padx = padx, pady = pady)
        
        #tk.Label(self.calc_frame_Ruby, text = "T(\u03BB\u2080) = ").grid(row=1, column=2,sticky='NSEW', padx = padx, pady = pady)
        self.Ruby_T_lambda_zero_calc_label = tk.Label(self.calc_frame_Ruby, text = f"T(\u03BB\u2080) = {self.ruby_ref_TL0:.2f} K", anchor="w")
        self.Ruby_T_lambda_zero_calc_label.grid(row=1, column=1,sticky='NSEW', padx = padx, pady = pady)
        
        self.Ruby_calc_L_P = tk.IntVar()
        self.Ruby_calc_L_P.set(1)
        
        self.calc_T = tk.BooleanVar()
        self.calc_T.set(0)
        
        ttk.Radiobutton(self.calc_frame_Ruby, text = "\u03BB ( nm )", var = self.Ruby_calc_L_P, value = 1, command = self.Ruby_calc_L_P_selection).grid(row=2, column=0,sticky='NSEW', padx = padx, pady = pady)
        
        _P_frame = ttk.Frame(self.calc_frame_Ruby)
        _P_frame.grid(row=2, column=1, sticky='NSEW', padx = padx, pady = pady)
        
        ttk.Radiobutton(_P_frame, text = "P ( GPa ) ", var = self.Ruby_calc_L_P, value = 2, command = self.Ruby_calc_L_P_selection).grid(row=0, column=0,sticky='NSEW', padx = padx, pady = pady)
        
        
        available_P_gauges = ('Shen 2020', 'Mao hydro 1986', 'Mao non hydro 1986', 'Dewaele 2008', "Dorogokupets and Oganov 2007")
        
        self.Ruby_calc_P_gauge = ttk.Combobox(_P_frame, textvariable = self.calc_Ruby_P_gauge )
        self.Ruby_calc_P_gauge["values"] = available_P_gauges
        self.Ruby_calc_P_gauge.state(["readonly"]) #User restricted to list, no modification possible
        self.Ruby_calc_P_gauge.grid(row=0, column=1,sticky='NSEW', padx = padx, pady = pady)
        
        
        _T_frame = ttk.Frame(self.calc_frame_Ruby)
        _T_frame.grid(row=2, column=2, sticky='NSEW', padx = padx, pady = pady)
        
        self.calc_T_checkbutton  = ttk.Checkbutton(_T_frame, text = "T ( K ) ", var = self.calc_T)
        self.calc_T_checkbutton.grid(row=0, column=0,sticky='NSEW', padx = padx, pady = pady)
        
        available_T_gauges = ('Datchi 2004',)
        
        self.calc_T_gauge = ttk.Combobox(_T_frame, textvariable = self.calc_Ruby_T_gauge )
        self.calc_T_gauge["values"] = available_T_gauges
        self.calc_T_gauge.state(["readonly"]) #User restricted to list, no modification possible
        self.calc_T_gauge.grid(row=0, column=1, sticky='NSEW', padx = padx, pady = pady)
        
        self.Ruby_calc_L_value = tk.StringVar()
        self.Ruby_calc_P_value = tk.StringVar()
        self.Ruby_calc_T_value = tk.StringVar()
        self.Ruby_calc_T_value.set(str(self.ruby_ref_TL))
        
        ttk.Entry(self.calc_frame_Ruby, textvariable= self.Ruby_calc_L_value, font = self.default_entry_Font).grid(row=3, column=0, sticky='NSEW', padx = padx, pady = pady)
        ttk.Entry(self.calc_frame_Ruby, textvariable= self.Ruby_calc_P_value, font = self.default_entry_Font).grid(row=3, column=1, sticky='NSEW', padx = padx, pady = pady)
        ttk.Entry(self.calc_frame_Ruby, textvariable= self.Ruby_calc_T_value, font = self.default_entry_Font).grid(row=3, column=2, sticky='NSEW', padx = padx, pady = pady)
        
        #Ruby Output Table
        
        self.calc_frame_Ruby_output_table = ttk.Frame(self.calc_frame_Ruby, borderwidth=5, relief="sunken")
        self.calc_frame_Ruby_output_table.grid(row=4, column=0, rowspan=2, columnspan=11, sticky='NSEW', padx = padx, pady = pady) #
        
        self.Ruby_calc_all_P_gauges = (RS.Ruby_Shen, RS.Ruby_hydro, RS.Ruby_non_hydro, RS.Ruby_Dewaele, RS.Ruby_Dorogokupets_forDatchiT)
        

        
        self.Ruby_calc_labels = ["\u03BB (nm)", "\u03BB\u2080 (nm)", "T (K) ", "T (°C)", 
                  "Shen 20 (GPa)", "Mao hydro 86 (GPa)", "Mao non hydro 86 (GPa)", "Dewaele 08 (GPa)", "Dorogokupets 07 (GPa)"]
        
        
        
        #Sam calc section
        self.calc_frame_Sam = ttk.Frame(self.tab3, borderwidth=5, relief="sunken")
        self.calc_frame_Sam.pack(anchor=tk.W, side = tk.TOP)
        
        calc_frame_Sam_title = tk.Label(self.calc_frame_Sam, text = "Samarium " + self.Sam_Name, anchor = 'w')
        calc_frame_Sam_title.grid(row=0, column=0,sticky='NSEW', padx = padx, pady = pady) 
        calc_frame_Sam_title.configure(font='Helvetica 18 bold')
        
        ttk.Button(self.calc_frame_Sam, text = "Calc", command = self.calc_Sam).grid(row=0, column=1,sticky='NSEW', padx = padx, pady = pady)
        
        self.Sam_lambda_zero_calc_label = tk.Label(self.calc_frame_Sam, text = f"\u03BB\u2080 = {self.SrB4O7_ref:.2f} nm", anchor="w")
        self.Sam_lambda_zero_calc_label.grid(row=1, column=0,sticky='NSEW', padx = padx, pady = pady)
        
        self.Sam_calc_L_P = tk.IntVar()
        self.Sam_calc_L_P.set(1)
        
        ttk.Radiobutton(self.calc_frame_Sam, text = "\u03BB ( nm )", var = self.Sam_calc_L_P, value = 1).grid(row=2, column=0,sticky='NSEW', padx = padx, pady = pady)
        
        _P_frame = ttk.Frame(self.calc_frame_Sam)
        _P_frame.grid(row=2, column=1, sticky='NSEW', padx = padx, pady = pady)
        
        ttk.Radiobutton(_P_frame, text = "P ( GPa ) ", var = self.Sam_calc_L_P, value = 2).grid(row=0, column=0,sticky='NSEW', padx = padx, pady = pady)
        
        available_P_gauges = ('Rashchenko 2015', 'Datchi 1997')
        
        self.Sam_calc_P_gauge = ttk.Combobox(_P_frame, textvariable = self.calc_Sam_P_gauge )
        self.Sam_calc_P_gauge["values"] = available_P_gauges
        self.Sam_calc_P_gauge.state(["readonly"]) #User restricted to list, no modification possible
        self.Sam_calc_P_gauge.grid(row=0, column=1,sticky='NSEW', padx = padx, pady = pady)
        
        self.Sam_calc_L_value = tk.StringVar()
        self.Sam_calc_P_value = tk.StringVar()
        
        ttk.Entry(self.calc_frame_Sam, textvariable= self.Sam_calc_L_value, font = self.default_entry_Font).grid(row=3, column=0, sticky='NSEW', padx = padx, pady = pady)
        ttk.Entry(self.calc_frame_Sam, textvariable= self.Sam_calc_P_value, font = self.default_entry_Font).grid(row=3, column=1, sticky='NSEW', padx = padx, pady = pady)
        
        #Sam Output Table
        
        self.calc_frame_Sam_output_table = ttk.Frame(self.calc_frame_Sam, borderwidth=5, relief="sunken")
        self.calc_frame_Sam_output_table.grid(row=4, column=0, rowspan=2, columnspan=11, sticky='NSEW', padx = padx, pady = pady) #
        
        self.Sam_calc_all_P_gauges = (RS.Sam_Rashchenko, RS.Sam_Datchi)
        
        
        self.Sam_calc_labels = ["\u03BB (nm)", "\u03BB\u2080 (nm)", 
                  "Rashchenko 15 (GPa)", "Datchi 97 (GPa)"]
        
    def calc_Sam(self):
        print('Click Sam')
        print(self.Sam_calc_L_P.get())
        if self.Sam_calc_L_P.get() == 1:
            print('Sam L selected')
            Error = False
            try: 
                L_value = float(self.Sam_calc_L_value.get())
            except:
                print('Error')
                self.Sam_reset_table()
                self.Sam_calc_L_value.set('NaN Input')
                Error = True
            if not Error:
                L0 = self.SrB4O7_ref 

                P = [g(L_value,L0) for g in self.Sam_calc_all_P_gauges]
                #P= [lambda_value, 1e7/lambda_value, L0, 1e7/L0, T_value, T_value - 273.15] + P
                P= [L_value, L0] + P
                print(P)
                
        if self.Sam_calc_L_P.get() == 2:
            print('Sam P selected')
            Error = False
            try: 
                P_value = float(self.Sam_calc_P_value.get())
            except:
                print('Error')
                self.Sam_reset_table()
                self.Sam_calc_P_value.set('NaN Input')
                Error = True
            if not Error:
                RSrB = self.calc_Sam_P_gauge.get()
                L0 = self.SrB4O7_ref 
                
                if RSrB == 'Rashchenko 2015':
                    g = RS.Sam_Rashchenko
                elif RSrB == 'Datchi 1997':
                    g = RS.Sam_Datchi
                
                def residual(p):
                    v = p.valuesdict()
                    return abs(g(v['L'], v['L0']) - v['P'])


                params = Parameters()
                params.add('L', value = L0+10, min = L0)
                params.add('L0', value = L0, vary = False)
                params.add('P', value = P_value, vary = False)

                mi = minimize(residual, params, method='nelder', nan_policy='omit')

                print()
                print(mi.params.pretty_print())
                print()

                res_L = mi.params['L'].value
                P = [g(res_L,L0) for g in self.Sam_calc_all_P_gauges]
                #P= [lambda_value, 1e7/lambda_value, L0, 1e7/L0, T_value, T_value - 273.15] + P
                P= [res_L, L0] + P
                print(P)
                
        
        if not Error:
            for col, val in enumerate(self.Sam_calc_labels):
                frameGrid = tk.Frame(master=self.calc_frame_Sam_output_table,relief=tk.RAISED,borderwidth=4)
                frameGrid.grid(row=0, column=col, sticky='NSEW')
                labelGrid = tk.Label(master=frameGrid, text=val)
                labelGrid.pack()
                frameGrid = tk.Frame(master=self.calc_frame_Sam_output_table,relief=tk.RAISED,borderwidth=4)
                frameGrid.grid(row=1, column=col, sticky='NSEW')
                labelGrid = tk.Label(master=frameGrid, text=f'{P[col]:.2f}')
                labelGrid.pack()
                
    def Ruby_calc_L_P_selection(self):
        if self.Ruby_calc_L_P.get() ==1:
            #Lambda case
            #self.calc_T.set(0)
            self.calc_T_checkbutton.configure(state= "normal")
        if self.Ruby_calc_L_P.get() ==2:
            #P case
            self.calc_T.set(0)
            self.Ruby_calc_T_value.set('298')
            self.calc_T_checkbutton.configure(state= "disabled")
        
    def calc_Ruby(self):
        print('/////')
        print(self.Ruby_calc_L_P.get())
        print(self.calc_Ruby_P_gauge.get())
        print(self.calc_T.get())
        print(self.calc_Ruby_T_gauge.get())
        
        print(self.Ruby_calc_L_value.get())
        print(self.Ruby_calc_P_value.get())
        print(self.Ruby_calc_T_value.get())
        print('/////')
        
        if self.Ruby_calc_L_P.get() == 2:
            print('Ruby P selected')
            L0 = self.ruby_ref
            T_value = 298
            Error = False
            try: 
                P_value = float(self.Ruby_calc_P_value.get())
            except:
                print('Error')
                self.Ruby_reset_table()
                self.Ruby_calc_P_value.set('NaN Input')
                Error = True
                
            if not Error:
                RPG = self.calc_Ruby_P_gauge.get()
                print(RPG)
                if RPG == "Shen 2020":
                    g = RS.Ruby_Shen
                elif RPG == "Mao hydro 1986":
                    g = RS.Ruby_hydro
                elif RPG == "Mao non hydro 1986":
                    g = RS.Ruby_non_hydro
                elif RPG == "Dewaele 2008":
                    g = RS.Ruby_Dewaele
                elif RPG == "Dorogokupets and Oganov 2007":
                    g = RS.Ruby_Dorogokupets_forDatchiT
                
                def residual(p):
                    v = p.valuesdict()
                    return abs(g(v['L'], v['L0']) - v['P'])


                params = Parameters()
                params.add('L', value = L0+10, min = L0)
                params.add('L0', value = L0, vary = False)
                params.add('P', value = P_value, vary = False)

                mi = minimize(residual, params, method='nelder', nan_policy='omit')

                print()
                print(mi.params.pretty_print())
                print()

                res_L = mi.params['L'].value
                P = [g(res_L,L0) for g in self.Ruby_calc_all_P_gauges]
                #P= [lambda_value, 1e7/lambda_value, L0, 1e7/L0, T_value, T_value - 273.15] + P
                P= [res_L, L0, T_value, T_value - 273.15] + P
                print(P)
                
                
        if self.Ruby_calc_L_P.get() == 1:
            # See Gauge_eq_Ruby
            print('Ruby L selected')
            L0 = self.ruby_ref
            T0 = self.ruby_ref_TL0
            Error = False
            try: 
                lambda_value = float(self.Ruby_calc_L_value.get())
            except:
                print('Error')
                self.Ruby_reset_table()
                self.Ruby_calc_L_value.set('NaN Input')
                Error = True
            if self.calc_T.get():
                try: 
                    T_value = float(self.Ruby_calc_T_value.get())
                except:
                    print('Error')
                    self.Ruby_reset_table()
                    self.Ruby_calc_T_value.set('NaN Input')
                    Error = True
            else:
                self.Ruby_calc_T_value.set('298')
                T_value = 298
            if not Error:
                print(lambda_value)
                print(T_value)
                if self.calc_T.get():
                    if self.calc_Ruby_T_gauge.get() == "Datchi 2004":
                        T0 = self.ruby_ref_TL0
                        f = RS.Ruby_Datchi_T
                    P = [g(f(T_value,lambda_value),f(T0,L0)) for g in self.Ruby_calc_all_P_gauges]
                    
                else:
                    P = [g(lambda_value,L0) for g in self.Ruby_calc_all_P_gauges]
                #P= [lambda_value, 1e7/lambda_value, L0, 1e7/L0, T_value, T_value - 273.15] + P
                P= [lambda_value, L0, T_value, T_value - 273.15] + P
                print(P)
        
        if not Error:
            for col, val in enumerate(self.Ruby_calc_labels):
                frameGrid = tk.Frame(master=self.calc_frame_Ruby_output_table,relief=tk.RAISED,borderwidth=4)
                frameGrid.grid(row=0, column=col, sticky='NSEW')
                labelGrid = tk.Label(master=frameGrid, text=val)
                labelGrid.pack()
                frameGrid = tk.Frame(master=self.calc_frame_Ruby_output_table,relief=tk.RAISED,borderwidth=4)
                frameGrid.grid(row=1, column=col, sticky='NSEW')
                labelGrid = tk.Label(master=frameGrid, text=f'{P[col]:.2f}')
                labelGrid.pack()
    def Sam_reset_table(self):
        for col, val in enumerate(self.Sam_calc_labels):
            frameGrid = tk.Frame(master=self.calc_frame_Sam_output_table,relief=tk.RAISED,borderwidth=4)
            frameGrid.grid(row=1, column=col, sticky='NSEW')
            labelGrid = tk.Label(master=frameGrid, text="   ")
            labelGrid.pack()
            
    def Ruby_reset_table(self):
        for col, val in enumerate(self.Ruby_calc_labels):
            # frameGrid = tk.Frame(master=self.calc_frame_Ruby_output_table,relief=tk.RAISED,borderwidth=4)
            # frameGrid.grid(row=0, column=col, sticky='NSEW')
            # labelGrid = tk.Label(master=frameGrid, text=val)
            # labelGrid.pack()
            frameGrid = tk.Frame(master=self.calc_frame_Ruby_output_table,relief=tk.RAISED,borderwidth=4)
            frameGrid.grid(row=1, column=col, sticky='NSEW')
            labelGrid = tk.Label(master=frameGrid, text="   ")
            labelGrid.pack()
        
    def select_X_units(self, filename):
        with open(filename) as f:
            s = f.read().replace(',','.')
            lines = (line for line in StringIO(s) if line.strip() != "" and line.strip()[0].isdigit()) 
            FH = np.loadtxt(lines)
        _min = FH[:,0].min()
        _max = FH[:,0].max()
        def Button1():
            message.set(f'Select file X units, nm or cm\u207B\u00B9\n Data in file from {_min:.1f} to {_max:.1f}\n\nNow selected nm')
            #True = cm-1 
            self.x_axis_units.set(False)
            if debug: print(f' Units = cm-1 {self.x_axis_units.get()}')
            self.ax_Spectro.set_xlabel('Wavelengths (nm)')
        def Button2():
            message.set(f'Select file X units, nm or cm\u207B\u00B9\n Data in file from {_min:.1f} to {_max:.1f}\n\nNow selected cm\u207B\u00B9')
            self.x_axis_units.set(True)
            if debug: print(f' Units = cm-1 {self.x_axis_units.get()}')
            self.ax_Spectro.set_xlabel('Wavelengths (cm\u207B\u00B9)')
        win = tk.Toplevel()
        win.title('warning')
        message = tk.StringVar()
        message.set(f"Select file X units, nm or cm\u207B\u00B9\n Data in file from {_min:.1f} to {_max:.1f}")
        tk.Label(win, textvariable = message).grid(row=0, column=0, columnspan=2, padx = padx, pady = pady)
        tk.Button(win, text='nm', command=Button1).grid(row=1, column=0,sticky='NSEW', padx = padx, pady = pady)
        tk.Button(win, text='cm', command=Button2).grid(row=1, column=1,sticky='NSEW', padx = padx, pady = pady)
        tk.Button(win, text='Accept', command=win.destroy).grid(row=2, column=0,columnspan=2, sticky='NSEW', padx = padx, pady = pady)
        win.wait_window()
        return FH
    
    def update_fit_log_par(self):
        self.R1_center = self.out.params['pk_center'].value
        self.R1_fwhm = self.out.params['pk_fwhm'].value
        
        fit = self.Fit_function.get()
        
        if fit == "Voigt" or fit == "Double Voigt":
            self.R1_gamma = self.out.params["pk_gamma"].value
        else:
            self.R1_gamma = self.out.params["pk_sigma"].value
        
        
        if fit == "Double Voigt" or fit == "Double Lorentz" or fit == "Double Gauss":
            self.R2_center = self.out.params['pk_2_center'].value
            self.R2_fwhm = self.out.params['pk_2_fwhm'].value
            
            if fit == "Double Voigt":
                self.R2_gamma = self.out.params["pk_2_gamma"].value
            else:
                self.R2_gamma = self.out.params["pk_2_sigma"].value
                
    def Update_spectra(self):
        
        if self.acquire_continuos_status.get() or self.acquire_snap_status.get():
            self.Start_thread()
        
        if (self.Fit_window_active == True) & (self.fit.get() or self.fit_snap_flag):
            # Performing Fit
            # Fit Options : method='nelder'
            if self.x_axis_units.get():
                #True = cm-1
                mask = slice(self.Fit_range_max_idx, self.Fit_range_min_idx)
                x = self.wavelengths[mask]
                x_fit_lmfit = np.linspace(self.wavelengths[mask].min(),self.wavelengths[mask].max(),200) #self.wavelengths[mask]
                x_fit_plot = x_fit_lmfit
            else:
                mask = slice(self.Fit_range_min_idx,self.Fit_range_max_idx)
                x = 1e7/self.wavelengths[mask]
                x_fit_lmfit = 1e7/np.linspace(self.wavelengths[mask].min(),self.wavelengths[mask].max(),200)
                x_fit_plot = 1e7/x_fit_lmfit
            if debug: print(f'mask = {mask}')
            try:
                #max_nfev ref https://github.com/lmfit/lmfit-py/pull/610
                if self.bkg.get():
                    y_fit = (self.intensities - self.intensities_bkg)[mask]
                else:
                    y_fit = self.intensities[mask]
                    
                self.out = self.model.fit(y_fit, self.pars, x = x, max_nfev = self.Fit_iter_lim.get()) 
                self.update_fit_log_par()
                if self.autoupdate.get(): self.Autoupdate()
                self.center_pk = self.out.params['pk_center'].value
                
                self.Update_Fit_window()
                
                
                comps = self.out.eval_components(x = x_fit_lmfit)
                Background = comps['bkg_']
                
                #Fit = self.out.best_fit #self.model.eval(self.out.params, x = x_fit_plot) # 
                Fit = self.model.eval(self.out.params, x = x_fit_lmfit)
                
                
                
                
                    
                    
                self.ax_Spectro_fit.set_xdata(x_fit_plot)
                self.ax_Spectro_fit.set_ydata(Fit)
                
                fit = self.Fit_function.get()
                if fit == "Double Voigt" or fit == "Double Lorentz" or fit == "Double Gauss":
                    
                    # self.bkg_to_save = comps['bkg_']
                    # self.pk1_to_save = comps['pk_'] + comps['bkg_']
                    # self.pk2_to_save = comps['pk_2_'] + comps['bkg_']
                    
                    P1 = comps['pk_'] + comps['bkg_']
                    P2 = comps['pk_2_'] + comps['bkg_']
                    
                    self.ax_Spectro_P1.set_xdata(x_fit_plot)
                    self.ax_Spectro_P1.set_ydata(P1)
                    self.ax_Spectro_P2.set_xdata(x_fit_plot)
                    self.ax_Spectro_P2.set_ydata(P2)
                else:
                    self.ax_Spectro_P1.set_xdata(x_fit_plot)
                    self.ax_Spectro_P1.set_ydata(Background)
                    self.ax_Spectro_P2.set_xdata(x_fit_plot)
                    self.ax_Spectro_P2.set_ydata(Background)
                    
                self.ax_Spectro_bkg.set_xdata(x_fit_plot)
                self.ax_Spectro_bkg.set_ydata(Background)
                if debug: print('Fit OK')
            except Exception as e:
                self.Fit_window_active == False
                self.fit.set(False)
                self.fitMenu.entryconfig(1, state=tk.NORMAL)
                messagebox.showerror(title = 'LMFIT Error', message = e)
            if self.fit_snap_flag: self.fit_snap_flag = False
        RPG = self.Ruby_P_gauge.get() != 'None'
        RTG = self.Ruby_T_gauge.get() != 'None'
        RSrB = self.Sam_gauge.get() != 'None'
        try:
            
            
            
            if RPG or RSrB:
                
                
                Title = ''
                if RPG:
                    if debug: print(f'RPG = {self.Ruby_P_gauge.get()}')
                    P = self.Gauge_eq_Ruby(1e7/self.center_pk, RPG = self.Ruby_P_gauge.get(), RTG = self.Ruby_T_gauge.get())
                    self.log_pressure = P
                    self.log_temperature = self.ruby_ref_TL
                    self.log_pressure_gauge = self.Ruby_P_gauge.get()
                    self.log_temperature_gauge = self.Ruby_T_gauge.get()
                    
                    # RPG = self.Ruby_P_gauge.get()
                    # RTG = self.Ruby_T_gauge.get()
                    Title += f"P '{self.Ruby_P_gauge.get()}' "
                    if RTG: 
                        Title += f" T '{self.Ruby_T_gauge.get()}' "
                        Title += f'@ T(\u03BB) = {self.ruby_ref_TL:.2f} K '
                elif RSrB:
                    if debug: print(f'RSrB = {self.Sam_gauge.get()}')
                    P = self.Gauge_eq_Sam(1e7/self.center_pk)
                    self.log_pressure = P
                    self.log_temperature = 0 
                    self.log_pressure_gauge = self.Sam_gauge.get()
                    self.log_temperature_gauge = 'None'
                    
                    Title += f"P '{self.Sam_gauge.get()}'"
                    
                Title += f'P = {P:.2f} GPa \n'
                
                
                if RPG: 
                    Title += f"Ruby R1 \u03BB = {1e7/self.center_pk:.2f} "
                    
                    
                    fit = self.Fit_function.get()
                    if fit == "Voigt" or fit == "Double Voigt":
                        
                        gamma = self.out.params["pk_gamma"].value
                        center = self.center_pk
                        gammanm = 1e7/(center-gamma) - 1e7/(center+gamma)

                        
                        Title += f"\u03C3 {gammanm:.2f}"  #Unicode sigma \u03C3 +/- \u00B1
                        if fit == "Double Voigt":
                            gamma = self.out.params["pk_2_gamma"].value
                            center = self.out.params['pk_2_center'].value
                            gammanm = 1e7/(center-gamma) - 1e7/(center+gamma)


                            Title += f" R2 \u03BB = {1e7/center:.2f} \u03C3 {gammanm:.2f}"  #Unicode sigma \u03C3 +/- \u00B1
                    Title += " nm " 
                if RSrB: Title += self.Sam_Name +f" \u03BB {1e7/self.center_pk:.2f} nm" # cm-1 => "  {self.center_pk:.1f} cm\u207B\u00B9 "
                
                if debug: print(f'center = {1e7/self.center_pk:.2f} nm {self.center_pk:.1f} cm\u207B\u00B9 P = {P:.2f} GPa')
                self.Main_title = Title
                self.ax_Spectro.set_title(Title)

            else:
                self.Main_title = 'No Gauge Selected'
                # try:
                #     self.Main_title = f'Last center = {1e7/self.center_pk:.2f} nm'
                # except:
                #     self.Main_title = 'No Gauge Selected'
                    
                self.ax_Spectro.set_title(self.Main_title)
        except Exception as e:
            messagebox.showerror(title = 'Gauge Error', message = e)
            if debug: print('Gauge Error, resetting')
            self.Ruby_T_gauge.set('None')
            self.Ruby_P_gauge.set('None')
            self.Sam_gauge.set('None')
            self.Update_Ruby_P_Gauge()
            self.Update_Ruby_T_Gauge()
            self.Update_Sam_Gauge()  
        self.canvas1.draw()   
        self.root.after(self.interval, self.Update_spectra)
        
    def reset_bkg(self):
        self.intensities_bkg[:] = 0 
        self.bkg.set(False)
        if debug : print('Reset bkg')

    def set_ruby_ref(self):
        entry = tk.simpledialog.askfloat("Ruby \u03BB\u2080", "Enter new value in nm", parent=self.root, minvalue=1, maxvalue=1000, initialvalue = self.ruby_ref)
        if entry is None: #cancel button
            return
        self.ruby_ref = entry
        self.Update_menu(3, self.presMenu, f'    \u03BB\u2080 (nm) = {self.ruby_ref:.2f}') #Lambda zero Ruby
        self.Ruby_lambda_zero_calc_label.config(text = f"\u03BB\u2080 = {self.ruby_ref:.2f} nm")
        if debug: print(f'Ruby \u03BB\u2080 = {self.ruby_ref}')
    
    def set_ruby_ref_TL0(self):
        entry = tk.simpledialog.askfloat("Ruby T(\u03BB\u2080)", "Enter new value in K", parent=self.root, minvalue=1, maxvalue=2000, initialvalue = self.ruby_ref_TL0)
        if entry is None: #cancel button
            return
        self.ruby_ref_TL0 = entry
        self.Update_menu(5, self.presMenu, f'    T(\u03BB\u2080) (K) = {self.ruby_ref_TL0:.2f}') #T(Lambda zero) Ruby
        self.Ruby_T_lambda_zero_calc_label.config(text = f"T(\u03BB\u2080) = {self.ruby_ref_TL0:.2f} K")
        if debug: print(f'Ruby T(\u03BB\u2080) = {self.ruby_ref_TL0}')
    
    def set_ruby_ref_TL(self):
        entry = tk.simpledialog.askfloat("Ruby T(\u03BB)", "Enter new value in K", parent=self.root, minvalue=1, maxvalue=2000, initialvalue = self.ruby_ref_TL)
        if entry is None: #cancel button
            return
        self.ruby_ref_TL = entry
        self.Update_menu(6, self.presMenu, f'    T(\u03BB) (K) = {self.ruby_ref_TL:.2f}') #T(Lambda) Ruby
        if debug: print(f'Ruby T(\u03BB) = {self.ruby_ref_TL}')
        
    def set_SrB4O7_ref(self):
        entry = tk.simpledialog.askfloat(self.Sam_Name + " \u03BB\u2080", "Enter new value in nm", parent=self.root, minvalue=1, maxvalue=1000, initialvalue = self.SrB4O7_ref)
        if entry is None: #cancel button
            return
        self.SrB4O7_ref = entry
        self.Update_menu(10, self.presMenu, f'    \u03BB\u2080 (nm) = {self.SrB4O7_ref:.2f}') #Lambda zero SrB4O7
        self.Sam_lambda_zero_calc_label.config(text = f"\u03BB\u2080 = {self.SrB4O7_ref:.2f} nm")
        if debug: print(self.Sam_Name + f' \u03BB\u2080 = {self.SrB4O7_ref}')
        
    def Fit_snap(self, event = None):
        self.fit_snap_flag = True
        self.Fit_window()
    
    def Fit_acquire_ctrl(self, event = None):
        #opposite of Fit_acquire(self)
        if self.fit.get() == 0:
            self.fit.set(1)
            self.fitMenu.entryconfig(1, state=tk.DISABLED)
        else:
            self.fit.set(0)
            self.fitMenu.entryconfig(1, state=tk.NORMAL)
        self.Fit_window()
        
    def Fit_acquire(self):
        if self.fit.get() == 1:
            self.fitMenu.entryconfig(1, state=tk.DISABLED)
        else:
            self.fitMenu.entryconfig(1, state=tk.NORMAL)
        self.Fit_window()
        
    def Update_Ruby_P_Gauge(self):
        if debug: print(f'Ruby P Gauge {self.Ruby_P_gauge.get()}')
        if self.Ruby_P_gauge.get() == 'None':
            self.Update_menu(4, self.presMenu, "    P Calibration")
        else:
            self.Update_menu(4, self.presMenu, self.menu_sel + " P Calibration")
            self.Sam_gauge.set('None')
            self.Update_Sam_Gauge()
        
        #Reset Title
        
        RPG = self.Ruby_P_gauge.get() != 'None'
        RSrB = self.Sam_gauge.get() != 'None'
        if not (RPG or RSrB):
            self.ax_Spectro.set_title(self.Main_title)
                
    def Update_Ruby_T_Gauge(self):
        if debug: print(f'Ruby T Gauge {self.Ruby_T_gauge.get()}')
        if self.Ruby_T_gauge.get() == 'None':
            self.Update_menu(7, self.presMenu, "    T Calibration")
        else:
            self.Update_menu(7, self.presMenu, self.menu_sel + " T Calibration")
            self.Sam_gauge.set('None')
            self.Update_Sam_Gauge()
        
    def Update_Sam_Gauge(self):
        if debug: print(f'Sam Gauge {self.Sam_gauge.get()}')
        if self.Sam_gauge.get() == 'None':
            self.Update_menu(11, self.presMenu,"    P Calibration")
        else:
            self.Update_menu(11, self.presMenu, self.menu_sel + " P Calibration")
            self.Ruby_P_gauge.set('None')
            self.Ruby_T_gauge.set('None')
            self.Update_Ruby_P_Gauge()
            self.Update_Ruby_T_Gauge()
            
        #Reset Title
        
        RPG = self.Ruby_P_gauge.get() != 'None'
        RSrB = self.Sam_gauge.get() != 'None'
        if not (RPG or RSrB):
            self.ax_Spectro.set_title(self.Main_title)
        
    def Gauge_eq_Ruby(self, L, RPG, RTG):
        #Ruby
        L0 = self.ruby_ref
        
        # RPG = self.Ruby_P_gauge.get()
        # RTG = self.Ruby_T_gauge.get()
        
        if RPG != 'None':
            if RPG == "Shen 2020":
                g = RS.Ruby_Shen
            elif RPG == "Mao hydro 1986":
                g = RS.Ruby_hydro
            elif RPG == "Mao non hydro 1986":
                g = RS.Ruby_non_hydro
            elif RPG == "Dewaele 2008":
                g = RS.Ruby_Dewaele
            elif RPG == "Dorogokupets and Oganov 2007":
                g = RS.Ruby_Dorogokupets_forDatchiT

            if RTG != 'None':
                if RTG == "Datchi 2004":
                    T = self.ruby_ref_TL
                    T0 = self.ruby_ref_TL0
                    f = RS.Ruby_Datchi_T
                    
                if debug: print(f'Ruby P {RPG}, T {RTG}')
                return g(f(T,L),f(T0,L0))
            return g(L,L0)
        
        if debug: print(f'Ruby P {RPG}, T {RTG}')
        
            
    
    def Gauge_eq_Sam(self, L):
        #SrB4O7
        RSrB = self.Sam_gauge.get()
        if RSrB != 'None':
            if RSrB == 'Rashchenko 2015':
                g = RS.Sam_Rashchenko
            elif RSrB == 'Datchi 1997':
                g = RS.Sam_Datchi
        if debug: print(RSrB)
        L0 = self.SrB4O7_ref 
        return g(L,L0)
        
    def Reset_fit_figure(self):
        self.ax_Spectro_fit.set_data(self.wavelengths, np.zeros_like(self.intensities))
        self.ax_Spectro_bkg.set_data(self.wavelengths, np.zeros_like(self.intensities))
        self.ax_Spectro_P1.set_data(self.wavelengths, np.zeros_like(self.intensities))
        self.ax_Spectro_P2.set_data(self.wavelengths, np.zeros_like(self.intensities))
        
    def Init_figure(self):
        #fig_Spectro, ax_Spectro = plt.subplots(figsize=self.figsize)
        fig_Spectro, ax_Spectro = plt.subplots()
        self.fig_Spectro = fig_Spectro
        self.ax_Spectro = ax_Spectro
        
        
        image_width = 0.1
        
        logo_ax_IMPMC = self.fig_Spectro.add_axes([0, 0.01, image_width, image_width]) #[left, bottom, width, height], anchor='SE', anchor='SE'
        logo_ax_CP = self.fig_Spectro.add_axes([1 - image_width, 0.01, image_width, image_width])
        
        
        logo_ax_IMPMC.imshow(self.im_IMPMC)
        
        # Hide X and Y axes label marks
        logo_ax_IMPMC.xaxis.set_tick_params(labelbottom=False)
        logo_ax_IMPMC.yaxis.set_tick_params(labelleft=False)
        
        # Hide X and Y axes tick marks
        logo_ax_IMPMC.set_xticks([])
        logo_ax_IMPMC.set_yticks([])
        
        logo_ax_CP.imshow(self.im_CP)
        
        # Hide X and Y axes label marks
        logo_ax_CP.xaxis.set_tick_params(labelbottom=False)
        logo_ax_CP.yaxis.set_tick_params(labelleft=False)
        
        # Hide X and Y axes tick marks
        logo_ax_CP.set_xticks([])
        logo_ax_CP.set_yticks([])
        
        self.ax_Spectro_data, = ax_Spectro.plot(self.wavelengths,self.intensities,'ko', markersize = 3, label = 'Data')
        if debug: print(f' data xy len {len(self.wavelengths)} {len(self.intensities)}')
        self.ax_Spectro_fit, = ax_Spectro.plot(self.wavelengths,np.zeros_like(self.intensities),'r', linewidth= 2, label = 'Fit')
        self.ax_Spectro_bkg, = ax_Spectro.plot(self.wavelengths,np.zeros_like(self.intensities),'--k', label = 'Bkg')
        self.Fit_range_min_line = self.ax_Spectro.axvline(self.W_range_min, color = 'red', linestyle = '--')
        self.Fit_range_max_line = self.ax_Spectro.axvline(self.W_range_max, color = 'red', linestyle = '--')
        self.ax_Spectro_P1, = ax_Spectro.plot(self.wavelengths,np.zeros_like(self.intensities),'--g')
        self.ax_Spectro_P2, = ax_Spectro.plot(self.wavelengths,np.zeros_like(self.intensities),'--g')
        
        leg = ax_Spectro.legend()
        leg.set_draggable(True) 
        ax_Spectro.grid()
        ax_Spectro.set_xlabel('Wavelengths (nm)')
        ax_Spectro.set_ylabel('Intensity (a.u.)')
        ax_Spectro.set_title(self.Main_title)
        
        self.canvas1 = FigureCanvasTkAgg(fig_Spectro, master = self.tab1)
        #self.canvas1.get_tk_widget().grid(row=0, column=0, padx = padx, pady = pady)
        self.canvas1.get_tk_widget().pack(side="top",fill='both',expand=True)
        #self.canvas1.pack(side="top",fill='both',expand=True)
       
        self.canvas1.draw()
        self.canvas1.mpl_connect('button_press_event', self.onclick)
        
        toolbar_frame1=tk.Frame(self.tab1)
        #toolbar_frame1.grid(row=1, column=0, sticky='NESW', padx = padx, pady = pady)
        toolbar_frame1.pack(side="bottom",fill='both',expand=False)
        
        toolbar1 = NavigationToolbar2Tk(self.canvas1,toolbar_frame1)
        toolbar1.grid(row=1,column=0, sticky='NESW')

        
    
    def acquire_snap(self):
        self.Accumulation_data = np.zeros((self.spec.pixels,self.Accumulation_n.get()))
        self.Accumulation_data_flag = False
        self.Accumulation_i.set(1)

    def memorize_bkg(self):
        self.intensities_bkg = np.copy(self.intensities)
        if debug : print("Memorized bkg")
        
    def acquire_continuos(self):
        self.Accumulation_data = np.zeros((self.spec.pixels,self.Accumulation_n.get()))
        if self.acquire_continuos_status.get():
            self.measMenu.entryconfig(1, state=tk.DISABLED)
            self.acquire_snap_status.set(False)
        else:
            self.measMenu.entryconfig(1, state=tk.NORMAL)

        self.Accumulation_data_flag = False
        self.Accumulation_i.set(1)
            
    def Read_HR4000(self):
        self.Running_thread = True
        
        if self.Accumulation_n.get() > 1:
            self.ax_Spectro.set_ylabel(f'Intensity (a.u.) Acc {self.Accumulation_i.get()} / {self.Accumulation_n.get()}')
        if debug: print(f' Acc set {self.Accumulation_i.get()} / {self.Accumulation_n.get()}')
        self.Accumulation_data[:,self.Accumulation_i.get()-1] = self.spec.intensities(correct_dark_counts=self.dark.get())
        
        if self.Accumulation_data_flag == True:
            
            #Continuos with all data in mem
            
            if debug: print("All in mem")
            self.intensities = self.Accumulation_data.mean( axis=1 )
        else:
            
            #Snap or accumulating data in mem
            
            if debug: print("Proportional in mem")
            self.intensities = self.Accumulation_data[:,:self.Accumulation_i.get()].mean( axis=1 )
     
        if not self.bkg.get() : 
            self.ax_Spectro_data.set_ydata(self.intensities)
            if debug: print('No bkg')
        else:
            self.ax_Spectro_data.set_ydata(self.intensities - self.intensities_bkg)
            
        if debug: print(f' data xy len {len(self.wavelengths)} {len(self.intensities)}')
        if debug: print(f' Acc {self.Accumulation_i.get()} / {self.Accumulation_n.get()}')
        if debug: print(self.Accumulation_data[:,:self.Accumulation_i.get()].shape)
        
        
        if self.Accumulation_i.get() == self.Accumulation_n.get():
            self.Accumulation_i.set(1)
            self.acquire_snap_status.set(False) #Snap Done
            self.Accumulation_data_flag = True #Mem for Continuos ready
        else:
            self.Accumulation_i.set(self.Accumulation_i.get() + 1)
        self.Running_thread = False
        
    def Start_thread(self):
        if not self.Running_thread:
            self.thread = threading.Thread(target=self.Read_HR4000)
            self.thread.start()

    def Quit_Fit_Window(self):
        self.Fit_window_active = False
        self.fit.set(False)
        self.fitMenu.entryconfig(1, state=tk.NORMAL)
        self.Fit_window_child.destroy()
                
    def Fit_report_update(self):
        # now = datetime.now()
        # current_time = now.strftime("%A %d %B %Y %H:%M:%S")
        # self.Fit_report = current_time + '\n\n'
        try:
            fit = self.Fit_function.get()
            
            center = self.out.params["pk_center"].value
            self.Fit_report = f'Peak center = {center:.2f} cm\u207B\u00B9 {1e7/center:.2f} nm\n'
            
            if fit == "Voigt" or fit == "Double Voigt":
                gamma = self.out.params["pk_gamma"].value
                gammanm = 1e7/(center-gamma) - 1e7/(center+gamma)
                self.Fit_report+= f'Peak gamma = {gamma:.2f} cm\u207B\u00B9 {gammanm:.2f} nm\n'
            else:
                sigma = self.out.params["pk_sigma"].value
                sigmanm = 1e7/(center-sigma) - 1e7/(center+sigma)
                self.Fit_report+= f'Peak sigma = {sigma:.2f} cm\u207B\u00B9 {sigmanm:.2f} nm\n'
                
            if fit == "Double Lorentz" or fit == "Double Gauss" or fit == "Double Voigt" :
                self.Fit_report+= '\n'
                center = self.out.params["pk_2_center"].value
                self.Fit_report+= f'Peak 2 center = {center:.2f} cm\u207B\u00B9 {1e7/center:.2f} nm\n'
                if fit == "Double Lorentz" or fit == "Double Gauss":
                    sigma = self.out.params["pk_2_sigma"].value
                    sigmanm = 1e7/(center-sigma) - 1e7/(center+sigma)
                    self.Fit_report+= f'Peak 2 sigma = {sigma:.2f} cm\u207B\u00B9 {sigmanm:.2f} nm\n'
                else:
                    gamma = self.out.params["pk_2_gamma"].value
                    gammanm = 1e7/(center-gamma) - 1e7/(center+gamma)
                    self.Fit_report+= f'Peak 2 gamma = {gamma:.2f} cm\u207B\u00B9 {gammanm:.2f} nm\n'
            self.Fit_report+= '\n'
        except:
            pass 
        self.Fit_report+= f"Model = {self.Fit_function.get()} + Poly Degree {self.Polynomial_degree.get()}\n"
        if self.x_axis_units.get():
            #True = cm-1
            self.Fit_report+= f"Fit Range {self.Fit_range_min.get():.2f} to {self.Fit_range_max.get():.2f} cm\u207B\u00B9\n"
        else:
            self.Fit_report+= f"Fit Range {1e7/self.Fit_range_min.get():.2f} to {1e7/self.Fit_range_max.get():.2f} cm\u207B\u00B9\n"
            self.Fit_report+= f"Fit Range {self.Fit_range_min.get():.2f} to {self.Fit_range_max.get():.2f} nm\n"
        self.Fit_report+= f"Maximum number of function evaluations = {self.Fit_iter_lim.get()}\n\n"
        try:
            self.Fit_report+= self.out.fit_report()
        except:
            pass    
    
    def Fit_window(self):
        
        if debug: print(f'Open Fit Windows = {self.fit.get()}')

        if self.Fit_window_active == False:
            #Open Fit Windows
            self.Fit_window_child = tk.Toplevel(self.root)
            self.Fit_window_child.protocol("WM_DELETE_WINDOW", self.Quit_Fit_Window)
            
            
            menu = tk.Menu(self.Fit_window_child, font = self.default_menu_Font)
            self.Fit_window_child.config(menu=menu)

            fileMenu = tk.Menu(menu, font = self.default_menu_Font)
            fileMenu.add_command(label="Save Fit & Data", command=self.Save_fit, font = self.default_menu_Font)
            menu.add_cascade(label="File", menu=fileMenu, font = self.default_menu_Font)
            
            self.Fit_window_child.wm_title("Fit Settings and Results")
            self.Fit_report_update()
            text=self.Fit_report
            self.Fit_window_text = tk.Text(self.Fit_window_child, borderwidth=0, font = self.Fit_window_font_size) #ref_fontsize
            self.Fit_window_text.insert(1.0, text)
            self.Fit_window_text.pack(side="top", fill="both", expand=True, padx=10, pady=10)
            self.Fit_window_active = True
 
    def onclick(self, event):
        button = event.button
        if event.xdata != None:
            x = event.x
            y = event.y
            xdata = event.xdata
            ydata = event.ydata
            self.click = [button, x, y, xdata, ydata]
            if debug: print(f'button = {button}, x = {x}, y = {y}, xdata = {xdata}, ydata = {ydata}')
            if event.button == 1:
                
                if self.pointer_line:
                    if debug: print('update pointer')
                    self.pointer_line.set_xdata([xdata,xdata])
                else:
                    if debug: print('new line')
                    self.pointer_line = self.ax_Spectro.axvline(xdata, color = 'black', linestyle = ':')
            if event.button == 3:
                self.pointer_line.remove()
                self.pointer_line = None
            self.canvas1.draw()
            self.Update_menu(2, self.minMenu, f'Set {self.click[3]:.2f}')
            self.Update_menu(2, self.maxMenu, f'Set {self.click[3]:.2f}')
        else:
            if debug: print('Click out of graph')
    
    def Set_calib(self):
        if self.calib.get():
            if self.x_axis_units.get():
                #True = cm-1
                x = np.arange(0,float(len(self.wavelengths)) ) #pixelm
                self.wavelengths = 1e7 / (self.calib_par[0] + self.calib_par[1] * x + self.calib_par[2] * x**2 + self.calib_par[3] * x**3)
            else:
                print(self.wavelengths[0],self.wavelengths[-1])
                x = np.arange(0,float(len(self.wavelengths)) ) #pixel
                self.wavelengths = (self.calib_par[0] + self.calib_par[1] * x + self.calib_par[2] * x**2 + self.calib_par[3] * x**3)
                print(self.wavelengths[0],self.wavelengths[-1])
        else:
            #Reload HR4000
            x = self.spec.wavelengths()
            if self.x_axis_units.get():
                #True = cm-1
                self.wavelengths = 1e7/x
            else:
                self.wavelengths = x
        self.Update_x_axis_units()
        
    def Change_x_axis_units(self):
        actual = self.ax_Spectro.get_xlabel()
        if self.x_axis_units.get():
            #True = cm-1
            new = 'Wavelengths (cm\u207B\u00B9)'
        else:
            new = 'Wavelengths (nm)'
        if actual is not new:
            self.ax_Spectro.set_xlabel(new)
            self.wavelengths = 1e7/self.wavelengths
            self.Update_x_axis_units()
        
    def Update_x_axis_units(self):
        
        self.click = [ float("NaN"), float("NaN"),float("NaN"),float("NaN"),float("NaN") ]
        self.Update_menu(2, self.minMenu, f'Set {self.click[3]:.2f}')
        self.Update_menu(2, self.maxMenu, f'Set {self.click[3]:.2f}')

        self.fit.set(False) 
        self.fitMenu.entryconfig(1, state=tk.NORMAL)
        
        entry = self.wavelengths.min()
        self.Fit_range_min.set(entry)
        self.fit_x_min = entry
        
        self.Update_menu(6, self.fitMenu, f'Min {self.Fit_range_min.get():.2f}')
        self.Fit_range_min_line.set_xdata([entry,entry])
        self.Fit_range_min_idx = abs(self.wavelengths-entry).argmin()
        
        entry = self.wavelengths.max()
        self.Fit_range_max.set(entry)
        self.fit_x_max = entry 
        
        self.Update_menu(7, self.fitMenu, f'Max {self.Fit_range_max.get():.2f}')
        self.Fit_range_max_line.set_xdata([entry,entry])
        self.Fit_range_max_idx = abs(self.wavelengths-entry).argmin()
        
        if debug: print(f'x range = {int(self.wavelengths.min())} to {int(self.wavelengths.max())}')
        if debug: print(f'x Fit range = {self.Fit_range_min.get()} {self.Fit_range_max.get()}')
        if debug: print(f'x id range {self.Fit_range_min_idx} {self.Fit_range_max_idx}')

        self.ax_Spectro_data.set_xdata(self.wavelengths)
        if debug: print(f' data xy len {len(self.wavelengths)} {len(self.intensities)}')
        self.Reset_fit_figure()
        self.canvas1.draw()
        self.Rescale_x()
        
        self.W_range_min = self.Fit_range_min.get()
        self.W_range_max = self.Fit_range_max.get()
        self.Update_fit()
        
    def Update_fit(self):
        
        fit = self.Fit_function.get()
        #"Lorentz", "Gauss", "Voigt"
        if debug: print(f'Selected fit = {fit}')
        if fit == "Lorentz":
            peak = LorentzianModel(prefix='pk_')
        elif fit == "Gauss":
            peak = GaussianModel(prefix='pk_')
        elif fit == "Voigt":
            peak = VoigtModel(prefix='pk_')
        elif fit == "Double Lorentz":
            peak = LorentzianModel(prefix='pk_') + LorentzianModel(prefix='pk_2_')
        elif fit == "Double Gauss":
            peak = GaussianModel(prefix='pk_') + GaussianModel(prefix='pk_2_')
        elif fit == "Double Voigt":
            peak = VoigtModel(prefix='pk_') + VoigtModel(prefix='pk_2_')
            
        if self.x_axis_units.get():
            #True = cm-1
            mask = slice(self.Fit_range_max_idx, self.Fit_range_min_idx)
            min_idx = self.Fit_range_max_idx
            max_idx = self.Fit_range_min_idx
            x = self.wavelengths
        else:
            mask = slice(self.Fit_range_min_idx,self.Fit_range_max_idx)
            min_idx = self.Fit_range_min_idx
            max_idx = self.Fit_range_max_idx
            x = 1e7/self.wavelengths
        
        if self.bkg.get():
            y0 = (self.intensities - self.intensities_bkg)[min_idx]
            y1 = (self.intensities - self.intensities_bkg)[max_idx]
        else:
            y0 = self.intensities[min_idx]
            y1 = self.intensities[max_idx]
        
        x0 = x[min_idx]
        x1 = x[max_idx]
        
        if debug:
            print()
            print(f'Fit Range = {self.Fit_range_min_idx} to  {self.Fit_range_max_idx}')
            print()
            print()
            print(f'Fit Range = {x0:.2f} to  {x1:.2f}')
            print()
        try:
            slope = (y0-y1)/(x0-x1)
        except:
            slope = 0
                
        intercept = y0-slope*x0
        
        if debug: print(f'Mask = {mask}')
        
        if self.bkg.get():
            y_fit = (self.intensities - self.intensities_bkg)[mask]
        else:
            y_fit = self.intensities[mask]
            
        center = x[y_fit.argmax() + min_idx]

        if debug: print(f'Center = {center}')
        
        y_max_rel = y_fit.max() - (intercept+slope*center)
                      
        bkg_n = self.Polynomial_degree.get()
        background = PolynomialModel(bkg_n,prefix='bkg_')
        
        if bkg_n == 0:
            self.pars = background.make_params(c0=intercept)
        elif bkg_n == 1:
            self.pars = background.make_params(c0=intercept, c1=slope)
        elif bkg_n == 2:
            self.pars = background.make_params(c0=intercept, c1=slope, c2=0)
        elif bkg_n == 3:
            self.pars = background.make_params(c0=intercept, c1=slope, c2=0, c3=0)
        elif bkg_n == 4:
            self.pars = background.make_params(c0=intercept, c1=slope, c2=0, c3=0, c4=0)
        elif bkg_n == 5:
            self.pars = background.make_params(c0=intercept, c1=slope, c2=0, c3=0, c4=0, c5=0)
        elif bkg_n == 6:
            self.pars = background.make_params(c0=intercept, c1=slope, c2=0, c3=0, c4=0, c5=0, c6=0)
        elif bkg_n == 7:
            self.pars = background.make_params(c0=intercept, c1=slope, c2=0, c3=0, c4=0, c5=0, c6=0, c7=0)
                
        self.pars += peak.make_params()
        self.model = peak + background

        self.pars['pk_center'].max = x0
        self.pars['pk_center'].min = x1
        self.pars['pk_center'].value = center

        if fit == "Lorentz" or fit == "Gauss":
            
            sigma_init = 10
            amplitude = y_max_rel*sigma_init*np.sqrt(2*np.pi)
            
            self.pars['pk_amplitude'].min = 1
            self.pars['pk_amplitude'].value = amplitude
            
            self.pars['pk_sigma'].vary = True
            self.pars['pk_sigma'].value = sigma_init
        
        elif fit == "Voigt":
            
            gamma_init = 10
            amplitude = self.Voigt_Amplitude(y_max_rel, gamma_init, self.sigma)
            
            self.pars['pk_amplitude'].min = .0001
            self.pars['pk_amplitude'].value = amplitude

            self.pars['pk_gamma'].set(vary=True, expr='')
            self.pars['pk_gamma'].vary = True
            self.pars['pk_gamma'].expr = None
            self.pars['pk_gamma'].value = gamma_init
            self.pars['pk_gamma'].min = 0.0001
            
            self.pars['pk_sigma'].vary = self.sigma_vary
            self.pars['pk_sigma'].value = self.sigma
        
        elif fit == "Double Lorentz" or fit == "Double Gauss":
            sigma_init = 10
            amplitude = y_max_rel*sigma_init*np.sqrt(2*np.pi)
            
            self.pars['pk_amplitude'].min = 1
            self.pars['pk_amplitude'].value = amplitude
            
            self.pars['pk_sigma'].vary = True
            self.pars['pk_sigma'].value = sigma_init
            
            delta =  14450.8 - 14421.8 #Syassen Table 4
            
            self.pars['pk_2_center'].value = center + delta
            self.pars['pk_2_center'].max = x0
            self.pars['pk_2_center'].min = x1
            
            self.pars['pk_2_amplitude'].min = 1
            self.pars['pk_2_amplitude'].value = amplitude
            
            self.pars['pk_2_sigma'].vary = True
            self.pars['pk_2_sigma'].value = sigma_init

        elif fit == "Double Voigt":
            gamma_init = 10
            amplitude = self.Voigt_Amplitude(y_max_rel, gamma_init, self.sigma)
            self.pars['pk_amplitude'].value = amplitude/2
            self.pars['pk_amplitude'].min = .0001
            
            self.pars['pk_2_amplitude'].value = amplitude/2
            self.pars['pk_2_amplitude'].min = .0001
            
            delta =  14450.8 - 14421.8 #Syassen Table 4
            
            self.pars.add('delta', value=delta,  vary=True, min=1)
            
            self.pars['pk_2_center'].expr = 'pk_center + delta'
            # self.pars['pk_2_center'].value = center + delta
            # self.pars['pk_2_center'].max = x0
            # self.pars['pk_2_center'].min = x1
            
            
            
            self.pars['pk_gamma'].set(vary=True, expr='')
            self.pars['pk_gamma'].vary = True
            self.pars['pk_gamma'].expr = None
            self.pars['pk_gamma'].value = gamma_init
            self.pars['pk_gamma'].min = 0.0001
            
            self.pars['pk_sigma'].vary = self.sigma_vary
            self.pars['pk_sigma'].value = self.sigma
            
            self.pars['pk_2_gamma'].set(vary=True, expr='')
            self.pars['pk_2_gamma'].vary = True
            self.pars['pk_2_gamma'].expr = None
            self.pars['pk_2_gamma'].value =gamma_init
            self.pars['pk_2_gamma'].min = 0.0001
            self.pars['pk_2_sigma'].value = self.sigma
            self.pars['pk_2_sigma'].vary = self.sigma_vary
 
        if debug: print(self.model)
        if debug: print(self.sigma_vary)
        if debug: print(self.pars.pretty_print())
    
    def Voigt_Amplitude(self, height, gamma, sigma):
        # height = (pk_amplitude/(max(1e-15, pk_sigma*sqrt(2*pi))))*wofz((1j*pk_gamma)/(max(1e-15, pk_sigma*sqrt(2)))).real
        return height*(sigma*np.sqrt(2*np.pi))/wofz((1j*gamma)/(sigma*np.sqrt(2))).real
    
    
    def Update_menu(self, n, menu, label):
        menu.entryconfigure(n, label=label)
    
    def Poly_degree(self):
        entry = tk.simpledialog.askinteger(f"Baseline Polynomial degree {self.Polynomial_degree.get()}", "Enter new Polynomial degree \
from 0 to 7", parent=self.root, minvalue=0, maxvalue=7)
        if entry is None: #cancel button
            return
        self.Polynomial_degree.set(entry)
        #self.interval = entry
        self.Update_menu(1, self.polMenu, self.Polynomial_degree.get())
        self.Update_fit()
        if debug: print(f'Poly Degree = {self.Polynomial_degree.get()}')
        
        
    def F_r_min(self):
        self.fit.set(False)
        title = f"Fit Range min value {self.Fit_range_min.get():.2f}"
        prompt = f"Enter new value from {int(self.W_range_min):.2f} to {int(self.W_range_max):.2f}"
        if self.pointer_line:
            entry = tk.simpledialog.askfloat(title, prompt, parent=self.root, minvalue=self.W_range_min, maxvalue=self.W_range_max,
                                               initialvalue = self.click[3])
        else:
            entry = tk.simpledialog.askfloat(title, prompt , parent=self.root, minvalue=self.W_range_min, maxvalue=self.W_range_max)
        if entry is None: #cancel button
            return
        if entry > self.Fit_range_max.get():
            messagebox.showinfo('Error','xmin must be smaller than xmax')
            return
        self.F_r_min_set(entry)
    
        
    def F_r_min_set(self, entry):
        self.Fit_range_min.set(entry)
        self.fit_x_min = entry 
        
        #self.interval = entry
        self.Update_menu(6, self.fitMenu, f'Min {self.Fit_range_min.get():.2f}')
        self.Fit_range_min_line.set_xdata([entry,entry])
        self.Fit_range_min_idx = abs(self.wavelengths-entry).argmin()
        if debug: print(f'Min Range = {self.Fit_range_min.get()}, real id = {self.Fit_range_min_idx}, value = {self.wavelengths[self.Fit_range_min_idx]}')
        self.Update_fit()
        self.Reset_fit_figure()
        
    def F_r_min_set_click(self, event = None):
        entry = self.click[3]
        if entry > self.Fit_range_max.get():
            messagebox.showinfo('Error','xmin must be smaller than xmax')
            return
        self.F_r_min_set(entry)
        
    def F_r_max(self):
        self.fit.set(False)
        title = f"Fit Range max value {self.Fit_range_max.get():.2f}"
        prompt = f"Enter new value from {int(self.W_range_min):.2f} to {int(self.W_range_max):.2f}"
        if self.pointer_line:
            entry = tk.simpledialog.askfloat(title, prompt, parent=self.root, minvalue=self.W_range_min, maxvalue=self.W_range_max,
                                               initialvalue = self.click[3])
        else:
            entry = tk.simpledialog.askfloat(title, prompt, parent=self.root, minvalue=self.W_range_min, maxvalue=self.W_range_max) 
        if entry is None: #cancel button
            return
        if entry < self.Fit_range_min.get():
            messagebox.showinfo('Error','xmax must be bigger than xmin')
            return
        self.F_r_max_set(entry)
    
    def F_r_max_set(self, entry):
        self.Fit_range_max.set(entry)
        self.fit_x_max = entry 
        
        #self.interval = entry
        self.Update_menu(7, self.fitMenu, f'Max {self.Fit_range_max.get():.2f}')
        self.Fit_range_max_line.set_xdata([entry,entry])
        self.Fit_range_max_idx = abs(self.wavelengths-entry).argmin()
        if debug: print(f'Max Range = {self.Fit_range_max.get()}, real id = {self.Fit_range_max_idx}, value = {self.wavelengths[self.Fit_range_max_idx]}')
        self.Update_fit()
        self.Reset_fit_figure()
        
    def F_r_max_set_click(self, event = None):
        entry = self.click[3]
        if entry < self.Fit_range_min.get():
            messagebox.showinfo('Error','xmax must be bigger than xmin')
            return
        self.F_r_max_set(entry)
            
    def Int_time(self):
        entry = tk.simpledialog.askfloat(f"Integration time = {self.Integration_time.get()} seconds", f"Enter new Integration time in seconds \
from {self.int_limits[0]} μs to {self.int_limits[1]/1e6} s", parent=self.root, minvalue=self.int_limits[0]/1e6, maxvalue=self.int_limits[1]/1e6)
        if entry is None: #cancel button
            return        
        self.Integration_time.set(entry)
        self.log_integration_time = entry
        self.reset_bkg()
        if debug: print(entry, self.int_limits[0]/1e6, self.int_limits[1]/1e6)
        if debug: print("Int time = ", self.Integration_time.get()*1e6)
        self.spec.integration_time_micros(self.Integration_time.get()*1e6)
        self.Update_menu(1, self.intMenu, self.Integration_time.get())
        if debug: print(f'Integration time = {self.Integration_time.get()} seconds')
    
    def Acc_n(self):
        entry = tk.simpledialog.askinteger(f"Number of accumulation = {self.Accumulation_n.get()}", "Enter new value",
                                           parent=self.root, minvalue=1)
        if entry is None: #cancel button
            return
        self.reset_bkg()
        self.acquire_snap_status.set(False)
        self.measMenu.entryconfig(1, state=tk.NORMAL)
        self.acquire_continuos_status.set(False)
        
        self.Accumulation_n.set(entry)
        self.log_accumulation = entry
        
        if entry == 1:
            self.ax_Spectro.set_ylabel('Intensity (a.u.)')

        self.Update_menu(1, self.accMenu, self.Accumulation_n.get())
        self.Accumulation_data = np.zeros((self.spec.pixels,self.Accumulation_n.get()))

        if debug: print(f'Number of accumulation = {self.Accumulation_n.get()}')
        if debug: print(f"Mem array size = {self.Accumulation_data.shape}")
        
    def Iter_lim(self):
        entry = tk.simpledialog.askinteger(f"Maximum number of function evaluations = {self.Fit_iter_lim.get()}", "Enter new limit",
                                           parent=self.root, minvalue=1)
        if entry is None: #cancel button
            return
        self.Fit_iter_lim.set(entry)
        self.Update_menu(1, self.iterMenu, self.Fit_iter_lim.get())
        if debug: print(f'Maximum number of function evaluations = {self.Fit_iter_lim.get()}')
        
    def Save_fig(self, filename : Path):
        #Save figure
        filename = filename.with_name(filename.stem + '_img.png')
        self.fig_Spectro.savefig(filename, dpi=300, format='png')
    
    def Save_log_fig(self, filename : Path):
        #Save figure
        filename = filename.with_name(filename.stem + '_img.png')
        #self.fig_Spectro.savefig(filename, dpi=300, format='png')
        self.fig_Spectro.savefig(filename, format='png') #Changing DPI cause slow blinking in main Tab
        
        
    def Save_header(self, filename : Path):
        #Save figure
        filename = filename.with_name(filename.stem + '_header.rtf')
        filename.write_text(self.create_header(), encoding="utf-8") 
    
    def Save_header_fit_report(self, filename : Path):
        #Save figure
        filename = filename.with_name(filename.stem + '_header.rtf')
        filename.write_text(self.create_header() +  '\n    Fit Report\n\n' + str(self.Fit_report), encoding="utf-8")
    
    def Save_data(self, filename: Path):
        if self.Accumulation_n.get() > 1:
            data = np.c_[self.wavelengths,self.intensities, self.Accumulation_data]
        else:
            data = np.c_[self.wavelengths,self.intensities]
        if debug: print(self.wavelengths.shape)
        if debug: print(self.intensities.shape)
        if debug: print(data.shape)
        
        filename = filename.with_name(filename.stem + '_data.txt')
        np.savetxt(filename, data)
    
    def Save_data_fit(self, filename: Path):
        if self.x_axis_units.get():
            #True = cm-1
            self.Fit_to_save = self.model.eval(self.out.params, x = self.wavelengths)
        else:
            self.Fit_to_save = self.model.eval(self.out.params, x = 1e7/self.wavelengths)
        
        
        #'Save_data' with fit data
        fit = self.Fit_function.get()
        if fit == "Double Voigt" or fit == "Double Lorentz" or fit == "Double Gauss":
            
            #adding also the 2 separate peaks
            if self.x_axis_units.get():
                #True = cm-1
                _comps = self.out.eval_components(x = self.wavelengths)
            else:
                _comps = self.out.eval_components(x = 1e7/self.wavelengths)
                
            self.bkg_to_save = _comps['bkg_']
            self.pk1_to_save = _comps['pk_'] + _comps['bkg_']
            self.pk2_to_save = _comps['pk_2_'] + _comps['bkg_']
            
            if self.Accumulation_n.get() > 1:
                data = np.c_[self.wavelengths,self.intensities,self.Fit_to_save, self.pk1_to_save, self.pk2_to_save, self.bkg_to_save, self.Accumulation_data]
            else:
                data = np.c_[self.wavelengths,self.intensities,self.Fit_to_save, self.pk1_to_save, self.pk2_to_save, self.bkg_to_save]
        else:
            if self.Accumulation_n.get() > 1:
                data = np.c_[self.wavelengths,self.intensities,self.Fit_to_save, self.Accumulation_data]
            else:
                data = np.c_[self.wavelengths,self.intensities,self.Fit_to_save]
        if debug: print(self.wavelengths.shape)
        if debug: print(self.intensities.shape)
        if debug: print(data.shape)
        
        filename = filename.with_name(filename.stem + '_data.txt')
        np.savetxt(filename, data)
        
    def Save_file(self):
        #Save Figure + Header + Data 
        
        now = datetime.now()
        #filename = tk.filedialog.asksaveasfile(mode='w', defaultextension=".txt", initialfile = now.strftime("%y%m%d_%H%M%S"))
        
        filename = tk.filedialog.asksaveasfilename(initialfile = now.strftime("%y%m%d_%H%M%S"))
        
        if filename is None: #cancel button
            return
        
        filename = Path(filename)
        if debug: print(filename)
        
        self.Save_fig(filename)

        self.Save_header(filename)

        self.Save_data(filename)

    
    
    def Save_fit(self, event = None):
        #Save Figure + Fit Report + Header + Data 
        try:
            now = datetime.now()
            #filename = tk.filedialog.asksaveasfile(mode='w', defaultextension=".txt", initialfile = now.strftime("%y%m%d_%H%M%S"))
            filename = tk.filedialog.asksaveasfilename(initialfile = now.strftime("%y%m%d_%H%M%S"))
            
            if filename is None: #cancel button
                return
            
            filename = Path(filename)
            if debug: print(filename)
            
            self.Save_fig(filename)
            
            self.Save_header_fit_report(filename)
            
            self.Save_data_fit(filename)
            
        except Exception as e:
            messagebox.showerror(title = 'Save Fit Error', message = e)
            return
    
    
    def Save_log(self, filename):
        
        if self.fit.get() :
            
            self.Save_header_fit_report(filename)
            
            self.Save_data_fit(filename)
        else:
            
            self.Save_header(filename)
    
            self.Save_data(filename)
        
        self.Save_log_fig(filename)
        
    def create_header(self):
        now = datetime.now()
        current_time = now.strftime("%A %d %B %Y %H:%M:%S")
        header = '\n' + current_time + '\n\n'
        header+= self.Main_title + '\n'
        
        if not (self.Ruby_P_gauge.get() == 'None'):
            header+= 'Ruby \u03BB\u2080 (nm) = ' + str(self.ruby_ref) + '\n'
            header+= 'Ruby T(\u03BB\u2080) (K) = ' + str(self.ruby_ref_TL0) + '\n\n'
        if not (self.Sam_gauge.get() == 'None'):
            header+= 'Sam \u03BB\u2080 (nm) = ' + str(self.SrB4O7_ref) + '\n'
            
        if self.x_axis_units.get():
            #True = cm-1
            header+= 'X axis units =  cm\u207B\u00B9\n'
        else:
            header+= 'X axis units =  nm\n'
        if self.stand_alone == "False":
            header+= f'Spectrometer = {self.spec}\n'
            if self.calib.get():
                header+= f'User Calibration = {self.calib_par}\n'
            else:
                header+= 'Used No Calibration\n'
            header+= f'Electronic Dark = {self.dark.get()}\n'
            header+= f'Subtract Background = {self.bkg.get()}\n'
        
            header+= f'Int Time (s) = {self.Integration_time.get()}\n'
            header+= f'Accumulation = {self.Accumulation_n.get()}\n'
        else:
            header+= f'Filename = {self.filename}\n'
        return header
                
    def Init_file(self):
        sim_sigma = 50
        sim_amplitude = 1000 #Min 1 in Fit
        self.wavelengths = np.arange(500,500 + 1025)
        x = 1e7/self.wavelengths
        sim_center = (x[0]+x[-1])/2
        y = sim_amplitude/(sim_sigma * np.sqrt(2 * np.pi)) * np.exp( - (x - (sim_center))**2 / (2 * sim_sigma**2))
        self.intensities = y
        if debug: 
            print()
            print(f'Simulated Gaussian data => center = {sim_center} amplitude = {sim_amplitude} sigma = {sim_sigma}')
            print()
            print(self.wavelengths.shape)
            print(self.intensities.shape)
            print()
        
        
    def Read_file(self, event = None):
        if self.stand_alone == "False":
            #Stop Acquisition
            self.acquire_snap_status.set(False)
            self.measMenu.entryconfig(1, state=tk.NORMAL)
            self.acquire_continuos_status.set(False)
        
        filename = tk.filedialog.askopenfilename(defaultextension=".txt")
        if filename == '': #cancel & esc button
            return
        if filename is None:  
            return
        try:
            data = self.select_X_units(filename)
        except Exception as e:
            messagebox.showerror(title = 'Open File Error', message = e)
            return
        tmp_x = data[:,0]
        tmp_y = data[:,1]
        self.filename = filename
        if self.x_axis_units.get():
            #True = cm-1
            self.wavelengths = tmp_x[tmp_x.argsort()[::-1]]
            self.intensities = tmp_y[tmp_x.argsort()[::-1]]
            if debug: print('File in cm-1')
        else:
            self.wavelengths = tmp_x[tmp_x.argsort()]
            self.intensities = tmp_y[tmp_x.argsort()]
            if debug: print('File in nm')
        
        # self.wavelengths = data[:,0]
        # self.intensities = data[:,1]
        self.ax_Spectro_data.set_data(self.wavelengths, self.intensities)
        if debug: print(f' data xy len {len(self.wavelengths)} {len(self.intensities)}')
        
        self.Reset_fit_figure()
        self.Rescale_y()
        self.Rescale_x()
        self.canvas1.draw()
        self.Update_x_axis_units()
        if debug: print(filename)
        if debug: print(data.shape)
        if debug: print(self.wavelengths.shape)
        if debug: print(self.intensities.shape)

    def Rescale_y(self):
        y_min = self.intensities.min()
        y_max = self.intensities.max()
        y_range = (y_max -y_min)*0.05*np.array((-1,1))+np.array((y_min,y_max))
        self.ax_Spectro.set_ylim(y_range)
        if debug: print('Rescale y')
    
    def Rescale_xy(self, event = None):
        x_min = self.wavelengths.min()
        x_max = self.wavelengths.max()
        x_range = (x_max -x_min)*0.05*np.array((-1,1))+np.array((x_min,x_max))
        self.ax_Spectro.set_xlim(x_range)
        if debug: print('Rescale x')
        y_min = self.intensities.min()
        y_max = self.intensities.max()
        y_range = (y_max -y_min)*0.05*np.array((-1,1))+np.array((y_min,y_max))
        self.ax_Spectro.set_ylim(y_range)
        if debug: print('Rescale y')
        
    def Rescale_x(self):
        x_min = self.wavelengths.min()
        x_max = self.wavelengths.max()
        x_range = (x_max -x_min)*0.05*np.array((-1,1))+np.array((x_min,x_max))
        self.ax_Spectro.set_xlim(x_range)
        if debug: print('Rescale x')
    
    def Rescale_to_fit(self, event = None):
        x_min = self.Fit_range_min.get()
        x_max = self.Fit_range_max.get()
        x_range = (x_max -x_min)*0.05*np.array((-1,1))+np.array((x_min,x_max))
        self.ax_Spectro.set_xlim(x_range)
        _x = self.wavelengths
        mask = (_x > x_min) & (_x < x_max)
        y_min = self.intensities[mask].min()
        y_max = self.intensities[mask].max()
        y_range = (y_max -y_min)*0.05*np.array((-1,1))+np.array((y_min,y_max))
        self.ax_Spectro.set_ylim(y_range)
        if debug: print('Rescale x & y to fit')
        
    def Autoupdate(self):
        fit = self.Fit_function.get()
        if fit == "Lorentz" or fit == "Gauss":
            pars_auto = ['pk_center','pk_amplitude','pk_sigma']
            
        elif fit == "Voigt" :
            pars_auto = ['pk_center','pk_amplitude','pk_gamma']
            
        if fit == "Double Lorentz" or fit == "Double Gauss":
            pars_auto = ['pk_center','pk_amplitude','pk_sigma','pk_2_center', 'pk_2_amplitude' , 'pk_2_sigma']
            
        elif fit == "Double Voigt" :
            pars_auto = ['pk_center','pk_amplitude','pk_gamma','delta','pk_2_amplitude','pk_2_gamma']  
        
        for i in pars_auto:
            self.pars[i].value = self.out.params[i].value
        
        pars_auto = ['bkg_c'+str(i) for i in range(self.Polynomial_degree.get() + 1)]
        
        for i in pars_auto:
            self.pars[i].value = self.out.params[i].value

    def Update_Fit_window(self):
        now = datetime.now()
        current_time = now.strftime("%A %d %B %Y %H:%M:%S") + '\n\n'

        self.Fit_report_update()
        text=current_time + self.Fit_report 
        self.Fit_window_text.delete('1.0', 'end')
        self.Fit_window_text.insert(1.0, text)
        
        
    def QuitMain(self, event = None):
        self.acquire_snap_status.set(False)
        self.acquire_continuos_status.set(False)
        MsgBox = messagebox.askquestion ('Quitting ...','Are you sure you want to quit ?',icon = 'warning')
        if MsgBox == 'yes':
            command = self.logging.get()

            if command:
                #Logging ON, stopping
                self.logger.logger_stop()
                
            if debug: print('Quitting, bye bye !')
            if self.stand_alone == "False":
                self.spec.integration_time_micros(1000)
                sleep(1)
                self.spec.close()
            sleep(1)
            
            self.root.quit()     # stops mainloop
            self.root.destroy()

        else:
            messagebox.showinfo('Return','Going back')
            
    def print_time(self, event = None, Message = 'Now = '):
        now = datetime.now()
        current_time = now.strftime("%A %d %B %Y %H:%M:%S")
        print(Message + current_time)

def main():
    #Entry point in poetry pyproject.toml
    root = tk.Tk()
    init = Init.init(SCRIPT_DIR, 'Rubycond')
    stand_alone = init.init_var['Settings']['stand_alone']
    if stand_alone == "False":
        try:
            import seabreeze #https://pypi.org/project/seabreeze/
            seabreeze.use('pyseabreeze')
            from seabreeze.spectrometers import Spectrometer
            spec = Spectrometer.from_first_available()
            Main(root, init, spec)
        except Exception as e:
            messagebox.showerror(title = 'HR4000 Error', message = str(e) + "\n\nStarting in Stand Alone mode\n\nTo install drivers: \n 1) conda install -c conda-forge seabreeze\n 2) seabreeze_os_setup")
            Main(root, init)
    else:
        Main(root, init)
    root.mainloop() 
    
if __name__ == "__main__":
    main()

  