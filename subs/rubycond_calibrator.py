# -*- coding: utf-8 -*-
"""

Rubycond Calibrator: calibration utility used stand alone or in Rubycond

Version 0.0.1
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

import configparser as cp
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import sys
import os
from tkinter import messagebox
from tkinter import font
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from scipy.optimize import curve_fit

from time import sleep

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(SCRIPT_DIR)


debug = False

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

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from PIL import Image, ImageTk

padx = 10
pady = 10





class Main:
    def __init__(self, root, init = None, wavelengths = None, intensities = None, res = None):
        """
        init coming from caller to save calibrated data
        if no init use Save Data

        """
        if init is not None:
            self.init = init
        else:
            self.init = None
        self.res = res #Passing values to caller if any
        
        if wavelengths is not None:
            self.wavelengths = wavelengths
            self.intensities = intensities
            print(wavelengths)
            print(intensities)
        else:
            self.wavelengths = np.linspace(1, 1000, 100)
            self.intensities = np.random.rand(len(self.wavelengths))
        
        self.Fit_results = None
        self.root = root
        root.protocol("WM_DELETE_WINDOW", self.QuitMain) #Intercept the close button
        #Fot Size
        #Font main application
        self.defaultFont = font.nametofont("TkDefaultFont") #ref_fontsize
        self.defaultFont.configure(size=14) 
        self.default_menu_Font = ("",14)
        self.Fit_window_font_size = ("",14)
        
        self.Neon_nm = np.array([607.43377, 609.61631, 614.30626, 616.35939,
                                621.72812, 626.6495 , 630.4789 , 633.44278, 
                                638.29917, 640.2246 , 650.65281, 653.28822, 
                                659.89529, 667.82764, 671.7043 , 692.94673,
                                703.24131, 717.39381, 724.51666, 743.8899 ])

        
        self.tabControl = ttk.Notebook(root)
        self.tab1 = ttk.Frame(self.tabControl, borderwidth=5, relief="sunken")
        self.tab2 = ttk.Frame(self.tabControl, borderwidth=5, relief="sunken")
        self.tab3 = ttk.Frame(self.tabControl, borderwidth=5, relief="sunken")
        
        self.tabControl.add(self.tab1, text ='Data')
        self.tabControl.add(self.tab2, text ='Results')
        self.tabControl.add(self.tab3, text ='About')
        
        self.tabControl.pack(expand = True, fill ="both")
        
        root.bind_all('<Control-Key-1>', lambda event:self.tabControl.select(self.tab1))
        root.bind_all('<Control-Key-2>', lambda event:self.tabControl.select(self.tab2))
        root.bind_all('<Control-Key-3>', lambda event:self.tabControl.select(self.tab3))
        
        
        
        res_x = int(448/2) # Image in About
        res_y = int(300/2) # Image in About
        ratio = 1
        self.figsize = (10*ratio,6*ratio)
        
        file_IMPMC = Path("logo_IMPMC.jpg")
        path_IMPMC = Path(__file__).parent.resolve() / file_IMPMC
        file_CP = Path("logo_CP.jpg")
        path_CP = Path(__file__).parent.resolve() / file_CP
            
        self.photo_IMPMC = ImageTk.PhotoImage(Image.open(path_IMPMC).resize((res_x, res_y)))
        self.photo_CP = ImageTk.PhotoImage(Image.open(path_CP).resize((res_x, res_y)))
        self.im_IMPMC = Image.open(path_IMPMC)
        self.im_CP = Image.open(path_CP)
        self.About = """
 
Rubycond Calibrator: calibration utility used stand alone or in Rubycond

Version 0.0.1
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
        self.Shortcuts = """
ctrl + # = Select the # Tab

ctrl + z = Set min as cursor
ctrl + x = Set max as cursor
ctrl + c = Zoom to fit
ctrl + q = Rescale to full scale
ctrl + f = Fit snap
ctrl + g = Fit continuos

ctrl + r = Read file
ctrl + s = Save image
ctrl + v = Save fit
"""
        
        self.x_axis_units = tk.BooleanVar()
        self.x_axis_units.set(False) #False = nm
        
        self.Neon_plot = tk.BooleanVar()
        self.Neon_plot.set(False)
        
        self.Fit_plot = tk.BooleanVar()
        self.Fit_plot.set(False)
        #Tab About
        
        label_CP = tk.Label(self.tab3, image = self.photo_CP, padx = padx, pady = pady)
        label_CP.grid(row = 0, column = 0, sticky = tk.NSEW)

        label_IMPMC = tk.Label(self.tab3, image = self.photo_IMPMC, padx = padx, pady = pady)
        label_IMPMC.grid(row = 0, column = 1, sticky = tk.NSEW)

        #label_About = tk.Label(self.tab4, text = self.About, anchor = 'e', justify = "left", padx = padx, pady = pady, wraplength=2*res_x)

        label_About = tk.Text(self.tab3, borderwidth=0, font = self.Fit_window_font_size) #ref_fontsize
        label_About.insert(1.0, self.About)
        label_About.grid(row = 1, column = 0, columnspan = 2, sticky = tk.NSEW)
        
        #Menu
        
        menu = tk.Menu(root)
        root.config(menu=menu)
        
        # File Menu
        
        fileMenu = tk.Menu(menu, font = self.default_menu_Font)
        
        fileMenu.add_command(label="Open File", command=self.Read_file, font = self.default_menu_Font, underline = 0)#ToDo, accelerator = 'Control + r')
        fileMenu.add_command(label="Save", command=self.Save_data, font = self.default_menu_Font, underline = 0) #ToDo, font = self.menu_font) NOT WORKING in add_cascade menu_font = None #("", 50)
        fileMenu.add_command(label="Quit", command=self.QuitMain, font = self.default_menu_Font, underline = 0)
        
        menu.add_cascade(label="File", menu=fileMenu, font = self.default_menu_Font, underline = 0)
        
        # Graph Menu
        
        graphMenu = tk.Menu(menu, font = self.default_menu_Font)
        
        graphMenu.add_command(label='Rescale Y', command=self.Fig1_Rescale_y, font = self.default_menu_Font, underline = 8)
        graphMenu.add_command(label='Rescale X', command=self.Fig1_Rescale_x, font = self.default_menu_Font, underline = 8)
        graphMenu.add_command(label='Rescale XY', command=self.Fig1_Rescale_xy, font = self.default_menu_Font, underline = 1)
        #graphMenu.add_command(label='Rescale to Fit', command=self.Rescale_to_fit, font = self.default_menu_Font, underline = 0)
        
        #X_axis_units sub menu / Graph Menu
        
        x_axisMenu = tk.Menu(menu, tearoff = 0, font = self.default_menu_Font)
        x_axisMenu.add_radiobutton(label='nm', variable = self.x_axis_units, value=False, command = self.Change_x_axis_units, font = self.default_menu_Font, underline = 0) #False = nm
        x_axisMenu.add_radiobutton(label='cm\u207B\u00B9', variable = self.x_axis_units, value=True, command = self.Change_x_axis_units, font = self.default_menu_Font, underline = 0)
        graphMenu.add_cascade(label="X axis units", menu=x_axisMenu, font = self.default_menu_Font, underline = 2) #unicode ref https://groups.google.com/g/comp.lang.tcl/c/9uQXrnfbt8c
        
        menu.add_cascade(label="Graph", menu=graphMenu, font = self.default_menu_Font, underline = 0)
        
        # Calib Menu
        
        calibMenu = tk.Menu(menu, font = self.default_menu_Font)
        
        calibMenu.add_checkbutton(label='Neon', variable = self.Neon_plot, command=self.plot_Neon_ref, font = self.default_menu_Font, underline = 0)
        calibMenu.add_command(label='Fit Peaks', command=self.fit_peaks, font = self.default_menu_Font, underline = 0)
        
        menu.add_cascade(label="Calib", menu=calibMenu, font = self.default_menu_Font, underline = 0)
        
        
        
        # filename = '230728_115117_1s.txt
        # data = np.loadtxt(filename)
        # self.wavelengths = data[:,0]
        # self.intensities = data[:,1]
        
        self.Init_figure_1()
        self.Init_figure_2()
        self.Fig1_Rescale_xy()
    
    def lorenziana(self, x, a, b, gamma, x0,const):
        return a+b/(np.pi*gamma*(1+((x-x0)/gamma)**2))+const*x
    
    def polynomial(self, x,a,b,c,d):
        return a + b*x + c*x**2 + d*x**3 
    
    def QuitMain(self, event = None):

        if self.init is not None:
            """
            init from Caller, save calib to file
            """
            MsgBox = messagebox.askquestion ('Quitting ...','Save New Calib ?',icon = 'warning')
            if MsgBox == 'yes':
                self.init.init_var['Spectrometer']['calibration_i'] = str(self.res[0])
                self.init.init_var['Spectrometer']['calibration_c1'] = str(self.res[1])
                self.init.init_var['Spectrometer']['calibration_c2'] = str(self.res[2])
                self.init.init_var['Spectrometer']['calibration_c3'] = str(self.res[3])
                self.init.save()
            else:
                pass
            self.root.destroy()
        else:
            MsgBox = messagebox.askquestion ('Quitting ...','Are you sure you want to quit ?',icon = 'warning')
            if MsgBox == 'yes':
                if debug: print('Quitting, bye bye !')
                sleep(1)
                
                self.root.quit()     # stops mainloop
                self.root.destroy()

            else:
                messagebox.showinfo('Return','Going back')
            
    def fit_peaks(self):
        self.peak_fit_results = np.zeros(len(self.Neon_nm))
        self.pixel_peaks = np.zeros(len(self.Neon_nm))

        for i, Neon in enumerate(self.Neon_nm):
            #print(i)
            if self.x_axis_units.get():
                #True = cm-1
                
                x = 1e7/self.wavelengths 
            else:
                x = self.wavelengths

            xdata_forfit = x[x>Neon-.8]
            ydata_forfit = self.intensities[x>Neon-.8]
            
            xdata_forfit = xdata_forfit[xdata_forfit<Neon+.8] 

            ydata_forfit = ydata_forfit[:len(xdata_forfit)]

            p0=[0,ydata_forfit.max()/np.pi,.1,Neon,0]
            
            ac, pcovUS = curve_fit(self.lorenziana,xdata_forfit,ydata_forfit,p0,maxfev=90000)
            self.peak_fit_results[i] = ac[3]
            self.pixel_peaks[i] = np.abs(x-ac[3]).argmin()
        print(self.pixel_peaks)
        print(self.peak_fit_results)
        print('Done fit')
        p0 = [600.,0.06,0.,0.]
        ac, pcovUS = curve_fit(self.polynomial,self.pixel_peaks,self.Neon_nm,p0,maxfev=10000)
        self.Fit_results = ac
        
        if self.res is not None:
            for i, val in enumerate(ac): self.res[i] = val #Passing values to caller if any
        
        self.x_pixel = np.arange(0,float(len(x)) )

        _x = self.polynomial(self.x_pixel,*ac)
        if self.x_axis_units.get():
            #True = cm-1
            self.x_calibrated = 1e7/_x
        else:
            self.x_calibrated = _x

            
        # _update= np.vstack((self.pixel_peaks, self.Neon_nm))
        # print(_update)
        # self.ax_Spectro_2_Neon_ref.set_offsets(_update)
        # _update= np.vstack((self.pixel_peaks, self.peak_fit_results))
        # print(_update)
        # self.ax_Spectro_2_Neon_Meas.set_offsets(_update)
        
        self.ax_Spectro_2_Neon_ref.set_data(self.pixel_peaks, self.Neon_nm)
        self.ax_Spectro_2_Neon_Meas.set_data((self.pixel_peaks, self.peak_fit_results))
        self.ax_Spectro_2_calib.set_data(self.x_pixel,self.x_calibrated)
        self.Fit_plot.set(True)
        Fig2_Title = f'Wavelengths (nm) = {ac[0]:.2f} {ac[1]:+.2e} * pixels {ac[2]:+.1e} * pixels\u00B2 {ac[3]:+.1e} * pixels\u00B3'
        self.ax_Spectro_2.set_title(Fig2_Title)
        self.Fig2_Rescale_xy()
        
        try:
            self.ax_Spectro_1_calibrated.remove()
        except:
            pass
        self.ax_Spectro_1_calibrated, = self.ax_Spectro_1.plot(self.x_calibrated, self.intensities,'-ro', markersize = 3, label = 'Calibrated')
        #Update legend according to Neon lines
        if self.Neon_plot.get():

            handles, labels = self.ax_Spectro_1.get_legend_handles_labels()
            line = Line2D([0], [0], label='Neon Lines', color='orange')
            handles.extend([line])
            leg = self.ax_Spectro_1.legend(handles=handles)

        else:
            leg = self.ax_Spectro_1.legend()
        leg.set_draggable(True) 
        self.canvas1.draw()
        
        print(f'calibration_i = {ac[0]}')
        print(f'calibration_c1 = {ac[1]}')
        print(f'calibration_c2 = {ac[2]}')
        print(f'calibration_c3 = {ac[3]}')
        #self.root.event_generate("<<CalibDone>>") # see line 581 in caller: self.root.bind_all("<<CalibDone>>", self.print_time)
        
    
    def create_header(self):
        now = datetime.now()
        current_time = now.strftime("%A %d %B %Y %H:%M:%S")
        header = '\n' + current_time + '\n\n'
        try:
            header+= f'Filename = {self.filename}\n\n'
        except:
            pass
        ac = self.Fit_results
        header+= f'calibration_i = {ac[0]}\n'
        header+= f'calibration_c1 = {ac[1]}\n'
        header+= f'calibration_c2 = {ac[2]}\n'
        header+= f'calibration_c3 = {ac[3]}\n\n'
        header+= 'Wavelengths (nm) = calibration_i + calibration_c1 * pixels + calibration_c2 * pixels\u00B2 + calibration_c3 * pixels\u00B3\n'
        header+= f'Wavelengths (nm) = {ac[0]:.2f} {ac[1]:+.2e} * pixels {ac[2]:+.2e} * pixels\u00B2 {ac[3]:+.2e} * pixels\u00B3\n\n'
        header+= "Saved data: Calibrated wavelength, Original intensity, Original wavelength"
        return header
    
    def Save_data(self):
        if self.Fit_results is not None:
            try:
                now = datetime.now()
                filename = tk.filedialog.asksaveasfile(mode='w', defaultextension=".dat", initialfile = now.strftime("%y%m%d_%H%M%S"))
                if filename is None: #cancel button
                    return
                #Save figure
                _f =  Path(filename.name) #, encoding='utf-16 LE'
                _f_1 = _f.with_name(_f.stem + '_data_fit')
                _f_2 = _f.with_name(_f.stem + '_linear_fit')
                print(_f_1)
                self.fig_Spectro_1.savefig(_f_1.with_suffix('.png'),dpi=300,format='png') #,bbox_inches='tight'
                
                print(_f_2)
                self.fig_Spectro_2.savefig(_f_2.with_suffix('.png'),dpi=300,format='png', bbox_inches='tight') #,bbox_inches='tight'
            
                #Save Header
                _f =  Path(filename.name)
                _header = _f.with_name(_f.stem + '_header.rtf')
                _header.write_text(self.create_header(), encoding="utf-8") 
                
                data = np.c_[self.x_calibrated, self.intensities, self.wavelengths]
    
                np.savetxt(filename, data)
    
                filename.close()
                
            except Exception as e:
                messagebox.showerror(title = 'Save Error', message = e)
                return
        else:
            messagebox.showerror(title = 'Save Error', message = "No Fit Performed")

    def Fig2_Rescale_xy(self, event = None):
        x_min = 0
        x_max = self.x_pixel.max()
        x_range = (x_max -x_min)*0.05*np.array((-1,1))+np.array((x_min,x_max))
        self.ax_Spectro_2.set_xlim(x_range)
        if debug: print('Rescale Fig 2 x')
        y_min = min(self.Neon_nm.min(), self.peak_fit_results.min(), self.x_calibrated.min())
        y_max = max(self.Neon_nm.max(), self.peak_fit_results.max(), self.x_calibrated.max())
        y_range = (y_max -y_min)*0.05*np.array((-1,1))+np.array((y_min,y_max))
        self.ax_Spectro_2.set_ylim(y_range)
        self.canvas2.draw()
        if debug: print('Rescale Fig2 y')
        
    def plot_Neon_ref(self):
        print(self.Neon_plot.get())
        if self.Neon_plot.get():
            self.Neon_plot_ref = []
            self.Neon_text_ref = []
            y_pos = (self.intensities.max()+self.intensities.min())/2
    
            if self.x_axis_units.get():
                #True = cm-1
                Neon = 1e7/self.Neon_nm
            else:
                Neon = self.Neon_nm
            
            for i in range(0,len(Neon)):
                print(Neon[i])
                self.Neon_plot_ref.append(self.ax_Spectro_1.axvline(Neon[i], color = 'orange'))
                if (i%2) == 0: 
                    self.Neon_text_ref.append(self.ax_Spectro_1.text(Neon[i], self.intensities.max()-y_pos*2/3, f'{Neon[i]:.2f}', fontdict=None, rotation = 'vertical'))
                else:
                    self.Neon_text_ref.append(self.ax_Spectro_1.text(Neon[i], y_pos, f'{Neon[i]:.2f}', fontdict=None, rotation = 'vertical'))
            # access legend objects automatically created from data
            handles, labels = self.ax_Spectro_1.get_legend_handles_labels()
            line = Line2D([0], [0], label='Neon Lines', color='orange')
            handles.extend([line])

            leg = self.ax_Spectro_1.legend(handles=handles)
        else:
            
            [i.remove() for i in self.Neon_plot_ref]
            [i.remove() for i in self.Neon_text_ref]
            leg = self.ax_Spectro_1.legend()
        print('Neon')
        
        
        leg.set_draggable(True) 
        self.canvas1.draw()
    
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
            self.ax_Spectro_1.set_xlabel('Wavelengths (nm)')
        def Button2():
            message.set(f'Select file X units, nm or cm\u207B\u00B9\n Data in file from {_min:.1f} to {_max:.1f}\n\nNow selected cm\u207B\u00B9')
            self.x_axis_units.set(True)
            if debug: print(f' Units = cm-1 {self.x_axis_units.get()}')
            self.ax_Spectro_1.set_xlabel('Wavelengths (cm\u207B\u00B9)')
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
    
    def ReDo_Neon_Lines(self):
        self.Neon_plot.set(False)
        self.plot_Neon_ref()
        self.Neon_plot.set(True)
        self.plot_Neon_ref()
        
    def Read_file(self, event = None):
        self.Fit_results = None
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
        if self.Fit_plot.get():
            self.ax_Spectro_1_calibrated.remove()
            self.Fit_plot.set(False)
        try:
            self.ax_Spectro_1_data.set_data(self.wavelengths, self.intensities)
            
            #Update legend according to Neon lines
            if self.Neon_plot.get():
    
                handles, labels = self.ax_Spectro_1.get_legend_handles_labels()
                line = Line2D([0], [0], label='Neon Lines', color='orange')
                handles.extend([line])
                leg = self.ax_Spectro_1.legend(handles=handles)
    
            else:
                leg = self.ax_Spectro_1.legend()
            leg.set_draggable(True) 
        except:
            pass
        if debug: print(f' data xy len {len(self.wavelengths)} {len(self.intensities)}')
        
        if self.Neon_plot.get(): self.ReDo_Neon_Lines()

        self.Fig1_Rescale_y()
        self.Fig1_Rescale_x()
        self.canvas1.draw()
        
        #Reset Fig2 Title
        
        self.ax_Spectro_2.set_title('')
        self.Fig2_Rescale_xy()
        
        if debug: print(filename)
        if debug: print(data.shape)
        if debug: print(self.wavelengths.shape)
        if debug: print(self.intensities.shape)
        
        self.reset_fig2() 
        
        
    def print_time(self, event = None, Message = 'Now = '):
        now = datetime.now()
        current_time = now.strftime("%A %d %B %Y %H:%M:%S")
        print(Message + current_time)
    
    def Init_figure_1(self):
        #fig_Spectro, ax_Spectro = plt.subplots(figsize=self.figsize)
        fig_Spectro, ax_Spectro = plt.subplots()
        self.fig_Spectro_1 = fig_Spectro
        self.ax_Spectro_1 = ax_Spectro
        
        
        image_width = 0.1
        
        logo_ax_IMPMC = self.fig_Spectro_1.add_axes([0, 0.01, image_width, image_width]) #[left, bottom, width, height], anchor='SE', anchor='SE'
        logo_ax_CP = self.fig_Spectro_1.add_axes([1 - image_width, 0.01, image_width, image_width])
        
        
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
        
        self.ax_Spectro_1_data, = ax_Spectro.plot(self.wavelengths,self.intensities,'-ko', markersize = 3, label = 'Data')
        if debug: print(f' data xy len {len(self.wavelengths)} {len(self.intensities)}')

        
        leg = ax_Spectro.legend()
        leg.set_draggable(True) 
        ax_Spectro.grid()
        ax_Spectro.set_xlabel('Wavelengths (nm)')
        ax_Spectro.set_ylabel('Intensity (a.u.)')
        #ax_Spectro.set_title(self.Main_title)
        
        self.canvas1 = FigureCanvasTkAgg(fig_Spectro, master = self.tab1)
        self.canvas1.get_tk_widget().pack(side="top",fill='both',expand=True)
       
        self.canvas1.draw()
        self.canvas1.mpl_connect('button_press_event', self.onclick)
        
        toolbar_frame1=tk.Frame(self.tab1)
        toolbar_frame1.pack(side="bottom",fill='both',expand=False)
        
        toolbar1 = NavigationToolbar2Tk(self.canvas1,toolbar_frame1)
        toolbar1.grid(row=1,column=0, sticky='NESW')
    
    
    def Init_figure_2(self):
        #fig_Spectro, ax_Spectro = plt.subplots(figsize=self.figsize)
        fig_Spectro, ax_Spectro = plt.subplots()
        self.fig_Spectro_2 = fig_Spectro
        self.ax_Spectro_2 = ax_Spectro
        
        
        image_width = 0.1
        
        logo_ax_IMPMC = self.fig_Spectro_2.add_axes([0, 0.01, image_width, image_width], anchor='NE')
        logo_ax_CP = self.fig_Spectro_2.add_axes([0.99 - image_width, 0.01, image_width, image_width], anchor='SE')
        
        
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
        
        _x = np.arange(0,len(self.wavelengths))
        _y = np.zeros_like(_x)
        
        #self.ax_Spectro_2_Neon_ref = ax_Spectro.scatter(_x, _y, label = 'Neon reference')
        #self.ax_Spectro_2_Neon_Meas = ax_Spectro.scatter(_x, _y, s = 10, label = 'Measured Neon')

        
        self.ax_Spectro_2_Neon_Meas, = self.ax_Spectro_2.plot(_x, _y, 'o', markersize = 10, label = 'Measured Neon', linestyle='None')
        self.ax_Spectro_2_Neon_ref, = self.ax_Spectro_2.plot(_x, _y, 'o', label = 'Neon reference', linestyle='None')
        self.ax_Spectro_2_calib, = self.ax_Spectro_2.plot(_x, _y,'--k', label = 'calibration')
        
        #plt.scatter(pixel_peaks, Neon_select, label = 'Neon reference')

        
        leg = ax_Spectro.legend()
        leg.set_draggable(True) 
        ax_Spectro.grid()
        ax_Spectro.set_xlabel('pixels')
        ax_Spectro.set_ylabel('Wavelengths (nm)')
        #ax_Spectro.set_title(self.Main_title)
        
        self.canvas2 = FigureCanvasTkAgg(fig_Spectro, master = self.tab2)
        self.canvas2.get_tk_widget().pack(side="top",fill='both',expand=True)
       
        self.canvas2.draw()
        self.canvas2.mpl_connect('button_press_event', self.onclick)
        
        toolbar_frame2=tk.Frame(self.tab2)
        toolbar_frame2.pack(side="bottom",fill='both',expand=False)
        
        toolbar2 = NavigationToolbar2Tk(self.canvas1,toolbar_frame2)
        toolbar2.grid(row=1,column=0, sticky='NESW')
        
    def reset_fig2(self):
        #self.ax_Spectro_2_data, = ax_Spectro.plot(np.arange(0,len(self.Neon_nm)),self.Neon_nm,'ko', markersize = 3, label = 'Data')
        _x = np.arange(0,len(self.wavelengths))
        _y = np.zeros_like(_x)
        
        #self.ax_Spectro_2_Neon_ref = ax_Spectro.scatter(_x, _y, label = 'Neon reference')
        #self.ax_Spectro_2_Neon_Meas = ax_Spectro.scatter(_x, _y, s = 10, label = 'Measured Neon')

        self.ax_Spectro_2_Neon_ref.set_data(_x, _y)
        self.ax_Spectro_2_Neon_Meas.set_data((_x, _y))
        self.ax_Spectro_2_calib.set_data(_x, _y)
        self.x_pixel = _x
        self.peak_fit_results = _y
        self.Fig2_Rescale_xy()
        self.canvas2.draw()
        
    def Change_x_axis_units(self):
        actual = self.ax_Spectro_1.get_xlabel()
        if self.x_axis_units.get():
            #True = cm-1
            new = 'Wavelengths (cm\u207B\u00B9)'
            #self.ax_Spectro_1.set_xlabel('Wavelengths (cm\u207B\u00B9)')
        else:
            new = 'Wavelengths (nm)'
            #self.ax_Spectro_1.set_xlabel('Wavelengths (nm)')
        if actual is not new:
            
            self.ax_Spectro_1.set_xlabel(new)
            self.wavelengths = 1e7/self.wavelengths
            self.ax_Spectro_1_data.set_xdata(self.wavelengths)
        

            if self.Fit_plot.get(): 
                self.x_calibrated = 1e7/self.x_calibrated
                self.ax_Spectro_1_calibrated.set_xdata(self.x_calibrated)
            
            if self.Neon_plot.get(): self.ReDo_Neon_Lines()
            
            if debug: print(f' data xy len {len(self.wavelengths)} {len(self.intensities)}')
            if debug: print(f' {self.wavelengths.min()} {self.wavelengths.max()}')
            
            self.Fig1_Rescale_x()
    
    def Update_menu(self, n, menu, label):
        menu.entryconfigure(n, label=label)
        
    def Update_x_axis_units(self):
        
        self.click = [ float("NaN"), float("NaN"),float("NaN"),float("NaN"),float("NaN") ]
        # self.Update_menu(2, self.minMenu, f'Set {self.click[3]:.2f}')
        # self.Update_menu(2, self.maxMenu, f'Set {self.click[3]:.2f}')

        self.fit.set(False) 
        self.fitMenu.entryconfig(1, state=tk.NORMAL)
        
        entry = self.wavelengths.min()
        self.Fit_range_min.set(entry)
        # self.Update_menu(6, self.fitMenu, f'Min {self.Fit_range_min.get():.2f}')
        self.Fit_range_min_line.set_xdata([entry,entry])
        self.Fit_range_min_idx = abs(self.wavelengths-entry).argmin()
        
        entry = self.wavelengths.max()
        self.Fit_range_max.set(entry)
        # self.Update_menu(7, self.fitMenu, f'Max {self.Fit_range_max.get():.2f}')
        self.Fit_range_max_line.set_xdata([entry,entry])
        self.Fit_range_max_idx = abs(self.wavelengths-entry).argmin()
        
        if debug: print(f'x range = {int(self.wavelengths.min())} to {int(self.wavelengths.max())}')
        if debug: print(f'x Fit range = {self.Fit_range_min.get()} {self.Fit_range_max.get()}')
        if debug: print(f'x id range {self.Fit_range_min_idx} {self.Fit_range_max_idx}')

        self.ax_Spectro_1_data.set_xdata(self.wavelengths)
        if debug: print(f' data xy len {len(self.wavelengths)} {len(self.intensities)}')
        self.canvas1.draw()
        self.Fig1_Rescale_x()
        
        
    def Fig1_Rescale_y(self):
        y_min = self.intensities.min()
        y_max = self.intensities.max()
        y_range = (y_max -y_min)*0.05*np.array((-1,1))+np.array((y_min,y_max))
        self.ax_Spectro_1.set_ylim(y_range)
        self.canvas1.draw()
        if debug: print('Rescale y')
    
    def Fig1_Rescale_xy(self, event = None):
        x_min = self.wavelengths.min()
        x_max = self.wavelengths.max()
        x_range = (x_max -x_min)*0.05*np.array((-1,1))+np.array((x_min,x_max))
        self.ax_Spectro_1.set_xlim(x_range)
        if debug: print('Rescale x')
        y_min = self.intensities.min()
        y_max = self.intensities.max()
        y_range = (y_max -y_min)*0.05*np.array((-1,1))+np.array((y_min,y_max))
        self.ax_Spectro_1.set_ylim(y_range)
        self.canvas1.draw()
        if debug: print('Rescale y')
        
    def Fig1_Rescale_x(self):
        x_min = self.wavelengths.min()
        x_max = self.wavelengths.max()
        x_range = (x_max -x_min)*0.05*np.array((-1,1))+np.array((x_min,x_max))
        self.ax_Spectro_1.set_xlim(x_range)
        self.canvas1.draw()
        if debug: print('Rescale x')
    
    def Rescale_to_fit(self, event = None):
        x_min = self.Fit_range_min.get()
        x_max = self.Fit_range_max.get()
        x_range = (x_max -x_min)*0.05*np.array((-1,1))+np.array((x_min,x_max))
        self.ax_Spectro_1.set_xlim(x_range)
        _x = self.wavelengths
        mask = (_x > x_min) & (_x < x_max)
        y_min = self.intensities[mask].min()
        y_max = self.intensities[mask].max()
        y_range = (y_max -y_min)*0.05*np.array((-1,1))+np.array((y_min,y_max))
        self.ax_Spectro_1.set_ylim(y_range)
        self.canvas1.draw()
        if debug: print('Rescale x & y to fit')
        
    def onclick(self, event):
        button = event.button
        if event.xdata != None:
            x = event.x
            y = event.y
            xdata = event.xdata
            ydata = event.ydata
            self.click = [button, x, y, xdata, ydata]
            if debug: 
                print(f'button = {button}, x = {x}, y = {y}, xdata = {xdata}, ydata = {ydata}')
                print(f'xlim = {self.ax_Spectro_1.get_xlim()} {self.fig_Spectro_1.get_xlim()}')

        else:
            if debug: print('Click out of graph')
            
def main():
    reset()
    root = tk.Tk()
    Main(root)
    root.mainloop() 

if __name__ == "__main__":
    main()
