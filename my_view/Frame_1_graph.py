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

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent

import os, sys
from datetime import datetime
from PyQt5 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from PIL import Image

if __name__ == '__main__':
    script = os.path.abspath(__file__)
    script_dir = os.path.dirname(script)
    script_name = os.path.basename(script)
    now = datetime.now()
    date = now.isoformat(sep = ' ', timespec = 'seconds')
    date_short = date[2:].replace('-','').replace(' ','_').replace(':','') #example = '240327_141721'
    print("File folder = " + script_dir)
    print("File name = " + script_name)
    print("Current working directory (AKA Called from ...) = " + os.getcwd())
    print("Python version = " + sys.version)
    print("Python folder = " + sys.executable)
    print()
    print("Started @ " + date +' AKA ' + date_short)


class Frame_1_graph(QtWidgets.QFrame):
    
    signal_fig_on_click = QtCore.pyqtSignal(MouseEvent)
    signal_fig_click_no_drag = QtCore.pyqtSignal(MouseEvent)
    signal_fig_click_drag = QtCore.pyqtSignal(MouseEvent)
    
    def __init__(self, model = None, debug = False):
        
        super().__init__()
        self.model = model
        self.debug = debug
        if self.debug: print("\nDebug mode\n")
        
        res_x = int(448/4) # Image in About
        res_y = int(300/4) # Image in About
        
        self.pointer_line = None
        
        #Logo CP
        

        path_CP = Path("logo_CP.jpg")
        path_IMPMC = Path("logo_IMPMC.jpg")  

        try:
            path_IMPMC = Path(__file__).parent.resolve() / path_IMPMC
            path_CP = Path(__file__).parent.resolve() / path_CP
        except:
            pass

        self.im_IMPMC = Image.open(path_IMPMC)
        self.im_CP = Image.open(path_CP)
        
        
        self.fig_ref = [] #List of plot ref
        self.fig_ref_names = [] #List of plot names
        self.x_min_all = np.inf
        self.x_max_all = -np.inf
        self.y_min_all = np.inf
        self.y_max_all = -np.inf
        self.total_plot_n = 0 
        
        self.fig = plt.figure(figsize=(5, 5))
        self.click = None
        
        self.Fit_range_min_line = None
        self.Fit_range_max_line = None
        
        image_width = 0.09
        
        logo_ax_IMPMC = self.fig.add_axes([0, 0.01, image_width, image_width]) #[left, bottom, width, height], anchor='SE', anchor='SE'
        logo_ax_CP = self.fig.add_axes([1 - image_width, 0.01, image_width, image_width])
        
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
        
        self.canvas = FigureCanvas(self.fig)
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('button_release_event', self.off_click)
        
        NavigationToolbar.home = self.autoscale_ax
        self.navigationToolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        
        #https://discourse.matplotlib.org/t/overriding-save-button-on-toolbar/17852/2
        
        #self.navigationToolbar.home = self.autoscale_ax #Change home button behaviour
        
        self.ax_1 = self.fig.add_subplot(111)
        self.ax_1.grid()
        self.x_moving_ref_left = 0 #Ref to detect drag
        self.y_moving_ref_left = 0 #Ref to detect drag
        #self.navigationToolbar.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        
        
        self.ax_1.set_xlabel('Wavelength (nm)')
        self.ax_1.set_ylabel('Intensity (a.u.)')
        
        # show canvas
        self.canvas.show()
        
        # create main layout
        
        layout_V = QtWidgets.QVBoxLayout()
        
        layout_V.addWidget(self.canvas)
        
        
        layout_H = QtWidgets.QHBoxLayout()
        layout_H.addWidget(self.navigationToolbar)
        
        
        layout_V.addLayout(layout_H)
        self.setLayout(layout_V)
        
        
        self.data_plot_ref = None
        self.data_fit_full_ref = None
        self.data_fit_bkg_ref = None
        self.data_fit_P1_ref = None
        self.data_fit_P2_ref = None
        
        self.plot_ref = None
        self.data_x = None
        self.data_y = None
        self.plot_simple_calib_ref = None
    
    def set_title(self, title):
        self.ax_1.set_title(title)
        
    def erase_fit_plot(self):
            
        if self.data_fit_full_ref: 
            self.data_fit_full_ref.remove()
            self.data_fit_full_ref = None
            
        if self.data_fit_bkg_ref: 
            self.data_fit_bkg_ref.remove()
            self.data_fit_bkg_ref = None
                        
        if self.data_fit_P1_ref: 
            self.data_fit_P1_ref.remove()
            self.data_fit_P1_ref = None
            
        if self.data_fit_P2_ref: 
            self.data_fit_P2_ref.remove()
            self.data_fit_P2_ref = None
        
        
    
    def on_click(self, event):
        if self.debug: print('on_click')
        self.x_moving_ref_left = event.xdata
        self.y_moving_ref_left = event.ydata
        self.signal_fig_on_click.emit(event)
        
        button = event.button
        if event.xdata != None:
            x = event.x
            y = event.y
            xdata = event.xdata
            ydata = event.ydata
            self.click = [button, x, y, xdata, ydata]
            
            if event.button == 1:
                
                if self.pointer_line:
                    if self.debug: print('update pointer')
                    self.pointer_line.set_xdata([xdata,xdata])
                else:
                    if self.debug: print('create pointer')
                    self.pointer_line = self.ax_1.axvline(xdata, color = 'black', linestyle = ':')
            if event.button == 3:
                if self.pointer_line:
                    if self.debug: print('delete pointer')
                    self.pointer_line.remove()
                    self.pointer_line = None
            if self.debug: print(f'button = {button}, x = {x}, y = {y}, xdata = {xdata}, ydata = {ydata}')
            self.canvas.draw()
    
    def plot_red_min(self, new_value):
        #Plot red line ref
        if self.Fit_range_min_line == None:
            self.Fit_range_min_line = self.ax_1.axvline(new_value, color = 'red', linestyle = '--')
        else:
            self.Fit_range_min_line.set_xdata([new_value,new_value])
        self.canvas.draw()
    
    def plot_red_max(self, new_value):
        #Plot red line ref
        if self.Fit_range_max_line == None:
            self.Fit_range_max_line = self.ax_1.axvline(new_value, color = 'red', linestyle = '--')
        else:
            self.Fit_range_max_line.set_xdata([new_value,new_value])
        self.canvas.draw()
        
    def remove_red_lines(self):
        
        if self.Fit_range_min_line:
            self.Fit_range_min_line.remove()
            self.Fit_range_min_line = None
            
        if self.Fit_range_max_line:
            self.Fit_range_max_line.remove()
            self.Fit_range_max_line = None
        
        self.canvas.draw()
        
    def Rescale_to_fit(self, event = None):
        try:
            x_min = self.Fit_range_min_line.get_xdata()[0]
            x_max = self.Fit_range_max_line.get_xdata()[0]
            if (x_min is not None) and (x_max is not None):
                x_range = (x_max -x_min)*0.05*np.array((-1,1))+np.array((x_min,x_max))
                self.ax_1.set_xlim(x_range)
                _x = self.data_x
                mask = (_x > x_min) & (_x < x_max)
                y_min = self.data_y[mask].min()
                y_max = self.data_y[mask].max()
                y_range = (y_max -y_min)*0.05*np.array((-1,1))+np.array((y_min,y_max))
                self.ax_1.set_ylim(y_range)
                self.canvas.draw()
            if self.debug: print('Rescale x & y to fit')
        except:
            if self.debug: print('Error Rescale x & y to fit') 
        
    def off_click(self, event):
        if self.debug: print('off_click\n')
        _x = event.xdata
        _y = event.ydata
        not_moved = ((self.x_moving_ref_left == _x) and (self.y_moving_ref_left == _y))
        if not_moved:
            self.signal_fig_click_no_drag.emit(event)
        else:
            self.signal_fig_click_drag.emit(event)
    
    def plot_reset(self):
        if self.data_plot_ref is not None:
            self.data_plot_ref.remove()
            self.data_plot_ref = None
            #self.ax_1.cla()
            self.canvas.draw()
        
    def plot_data(self, data_y, label = None):
        self.data_y = data_y
        if self.data_plot_ref is None:
            self.data_plot_ref, = self.ax_1.plot(self.data_x, data_y, '-ok')
        else:
            self.data_plot_ref.set_ydata(data_y)
        #self.autoscale_ax()
        self.canvas.draw()
    
    def plot_fit_full(self, data_x, data_y, label = None):
        if self.data_fit_full_ref is not None:
            self.data_fit_full_ref.remove()
        self.data_fit_full_ref, = self.ax_1.plot(data_x, data_y, 'r', linewidth = 2)
        #self.autoscale_ax()
        
    def plot_fit_bkg(self, data_x, data_y, label = None):
        if self.data_fit_bkg_ref is not None:
            self.data_fit_bkg_ref.remove()
        self.data_fit_bkg_ref, = self.ax_1.plot(data_x, data_y, '--k')
        #self.autoscale_ax()
        
    def plot_fit_P1(self, data_x, data_y, label = None):
        if self.data_fit_P1_ref is not None:
            self.data_fit_P1_ref.remove()
        self.data_fit_P1_ref, = self.ax_1.plot(data_x, data_y,'--g')
        #self.autoscale_ax()
    
    def plot_fit_P2(self, data_x, data_y, label = None):
        if self.data_fit_P2_ref is not None:
            self.data_fit_P2_ref.remove()
        self.data_fit_P2_ref, = self.ax_1.plot(data_x, data_y,'--g')
        #self.autoscale_ax()
        
        
    def autoscale_ax(self, *args, **kwargs):
        #print('New scale .....')
        border = 0.1
        max_x = -np.inf
        max_y = -np.inf
        min_x = np.inf
        min_y = np.inf
        lines = self.ax_1.get_lines()
        for line in lines:
            x_data = np.array(line.get_xdata())
            y_data = line.get_ydata()
            # print(type(line))
            # print('\nx_data')
            # print(type(x_data))
            # print(x_data)
            # print('\ny_data')
            # print(type(y_data))
            # print(y_data)
            # print('\n')
            if (type(x_data) is np.ndarray) and (type(y_data) is np.ndarray):
                #vertical lines return y_data as list
            
                max_x = max(max_x, x_data.max())
                max_y = max(max_y, y_data.max())
                min_x = min(min_x, x_data.min())
                min_y = min(min_y, y_data.min())
        
        border_x = (max_x - min_x)*border/2
        border_y = (max_y - min_y)*border/2
        try:
            self.ax_1.set_xlim(min_x-border_x, max_x+border_x)
            self.ax_1.set_ylim(min_y-border_y, max_y+border_y)
            self.canvas.draw()
        except:
            pass
                
    

        

        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet("""
                      * {
                          font-size: 15px;
                    }
                      """)
 
    window = Frame_1_graph(debug = True)


    window.show()
    sys.exit(app.exec())