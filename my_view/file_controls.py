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



import numpy as np

import os, sys
from PyQt5 import QtWidgets, QtCore



       
class controls(QtWidgets.QScrollArea):
    
    signal_plot_data = QtCore.pyqtSignal(np.ndarray)
    signal_quit = QtCore.pyqtSignal()
    
    def __init__(self, model = None, debug = False, font_size = 15):
        super().__init__()
        self.model = model
        self.debug = debug
        
        #self.font_size = font_size
        if self.debug : print('\nopen_file_commands\n')
        
        # style = """
        #               * {
        #                   font-size: """ + str(int(self.font_size)) + """px;
        #             }
        #               """
        # QtWidgets.qApp.setStyleSheet(style)
        
        
        # Group File: file_
        
        self.file_button_saveData = QtWidgets.QPushButton("Save")
        self.file_button_saveFit = QtWidgets.QPushButton("Save Fit")
        self.file_button_openFile = QtWidgets.QPushButton("Open")
        self.file_button_quit = QtWidgets.QPushButton("Quit")
        
        self.group_file_layout = QtWidgets.QGridLayout()
        
        self.group_file_layout.addWidget(self.file_button_saveData, 0, 0)
        self.group_file_layout.addWidget(self.file_button_saveFit, 0, 1)
        self.group_file_layout.addWidget(self.file_button_openFile, 1, 0)
        self.group_file_layout.addWidget(self.file_button_quit, 1, 1)
        
        
        self.group_file = QtWidgets.QGroupBox("File")
        self.group_file.setLayout(self.group_file_layout)
        
        # Group Spectrometer: spec_
        
        self.spec_button_connect = QtWidgets.QPushButton("Connect")
        self.spec_label_connect = QtWidgets.QLabel()
        self.spec_button_calibPar = QtWidgets.QPushButton("Calib Params")
        self.spec_button_calibrator = QtWidgets.QPushButton("Calibrator")
        self.spec_checkb_calib = QtWidgets.QCheckBox("User Calib")
        self.spec_button_bkgTake = QtWidgets.QPushButton("Save as bkg")
        self.spec_checkb_bkgUse = QtWidgets.QCheckBox("Substract bkg")

        self.group_spec_layout = QtWidgets.QGridLayout()
        
        self.group_spec_layout.addWidget(self.spec_button_connect, 0, 0)
        self.group_spec_layout.addWidget(self.spec_label_connect, 0, 1)
        self.group_spec_layout.addWidget(self.spec_button_calibPar, 1, 0)
        self.group_spec_layout.addWidget(self.spec_checkb_calib, 1, 1)
        self.group_spec_layout.addWidget(self.spec_button_calibrator, 3, 0)
        self.group_spec_layout.addWidget(self.spec_button_bkgTake, 4, 0)
        self.group_spec_layout.addWidget(self.spec_checkb_bkgUse, 4, 1)
        
        
        self.group_spec = QtWidgets.QGroupBox("Spectrometer")
        self.group_spec.setLayout(self.group_spec_layout)
    
        # Group Measurements: meas_
        
        self.meas_button_snap = QtWidgets.QPushButton("Snap")
        self.meas_checkb_acq = QtWidgets.QCheckBox("Acquire")
        self.meas_label_int = QtWidgets.QLabel("Int Time (s)")
        self.meas_button_intTime = QtWidgets.QPushButton("1")
        self.meas_label_acc = QtWidgets.QLabel("Accumulations")
        self.meas_button_acc = QtWidgets.QPushButton("10")
        self.meas_button_abort = QtWidgets.QPushButton("ABORT")
        
        self.meas_pbar = QtWidgets.QProgressBar(self)
        self.meas_pbar.setValue(0)
        self.meas_pbar.setTextVisible(False)
        self.meas_pbar.setFixedHeight(10)
        #self.meas_pbar.setFixedWidth(250)
        self.group_meas_layout = QtWidgets.QGridLayout()
        
        self.group_meas_layout.addWidget(self.meas_button_snap, 0, 0)
        self.group_meas_layout.addWidget(self.meas_checkb_acq, 0, 1)
        self.group_meas_layout.addWidget(self.meas_label_int, 1, 0)
        self.group_meas_layout.addWidget(self.meas_button_intTime, 1, 1)
        self.group_meas_layout.addWidget(self.meas_label_acc, 2, 0)
        self.group_meas_layout.addWidget(self.meas_button_acc, 2, 1)
        self.group_meas_layout.addWidget(self.meas_pbar, 3, 0, 1, 2)
        self.group_meas_layout.addWidget(self.meas_button_abort, 4, 0, 1, 2)
        
        self.group_meas = QtWidgets.QGroupBox("Measurements")
        self.group_meas.setLayout(self.group_meas_layout)
        
        # Group Measurements Andor: measTemp_
        
        self.measTemp_label_temp = QtWidgets.QLabel("Temperature = -- °C")
        self.measTemp_button_target = QtWidgets.QPushButton("- 60 °C")
        self.measTemp_checkb_cool = QtWidgets.QCheckBox("Cooling")
        
        self.group_measTemp_layout = QtWidgets.QGridLayout()
        
        self.group_measTemp_layout.addWidget(self.measTemp_label_temp, 0, 0, 1, 2)
        self.group_measTemp_layout.addWidget(self.measTemp_button_target, 1, 0)
        self.group_measTemp_layout.addWidget(self.measTemp_checkb_cool, 1, 1)
        
        self.group_measTemp = QtWidgets.QGroupBox("Cooler")
        self.group_measTemp.setLayout(self.group_measTemp_layout)
        
        # Group Gauge: gauge_
        
        # Tab1
        
        self.gaugetabRuby_button_snap = QtWidgets.QPushButton("Snap")
        self.gaugetabRuby_checkb_cont = QtWidgets.QCheckBox("Continuos")
        self.gaugetabRuby_label_lambda0 = QtWidgets.QLabel("λ\u2080")
        self.gaugetabRuby_button_lambda0 = QtWidgets.QPushButton("694.1 nm")
        self.gaugetabRuby_label_gauge = QtWidgets.QLabel("P Calib")
        self.gaugetabRuby_combob_gauge = QtWidgets.QComboBox()
        self.gaugetabRuby_label_Tlambda0 = QtWidgets.QLabel("T(λ\u2080)")
        self.gaugetabRuby_button_Tlambda0  = QtWidgets.QPushButton("694.2 nm")
        self.gaugetabRuby_label_Tlambda = QtWidgets.QLabel("T(λ)")
        self.gaugetabRuby_button_Tlambda  = QtWidgets.QPushButton("694.3 nm")
        self.gaugetabRuby_label_Tcalib = QtWidgets.QLabel("T calib")
        self.gaugetabRuby_combob_Tcalib = QtWidgets.QComboBox()
        
        self.group_gauge_tabRuby_layout = QtWidgets.QGridLayout()
        
        self.group_gauge_tabRuby_layout.addWidget(self.gaugetabRuby_button_snap, 0, 0)
        self.group_gauge_tabRuby_layout.addWidget(self.gaugetabRuby_checkb_cont, 0, 1)
        self.group_gauge_tabRuby_layout.addWidget(self.gaugetabRuby_label_lambda0, 1, 0)
        self.group_gauge_tabRuby_layout.addWidget(self.gaugetabRuby_button_lambda0, 1, 1)
        self.group_gauge_tabRuby_layout.addWidget(self.gaugetabRuby_label_gauge, 2, 0)
        self.group_gauge_tabRuby_layout.addWidget(self.gaugetabRuby_combob_gauge, 2, 1)
        self.group_gauge_tabRuby_layout.addWidget(self.gaugetabRuby_label_Tlambda0, 3, 0)
        self.group_gauge_tabRuby_layout.addWidget(self.gaugetabRuby_button_Tlambda0, 3, 1)
        self.group_gauge_tabRuby_layout.addWidget(self.gaugetabRuby_label_Tlambda, 4, 0)
        self.group_gauge_tabRuby_layout.addWidget(self.gaugetabRuby_button_Tlambda, 4, 1)
        self.group_gauge_tabRuby_layout.addWidget(self.gaugetabRuby_label_Tcalib, 5, 0)
        self.group_gauge_tabRuby_layout.addWidget(self.gaugetabRuby_combob_Tcalib, 5, 1)
        
        self.widget_gauge_tabRuby = QtWidgets.QWidget()
        self.widget_gauge_tabRuby.setLayout(self.group_gauge_tabRuby_layout)
        
        # Tab2
        
        self.gaugetabSam_button_snap = QtWidgets.QPushButton("Snap")
        self.gaugetabSam_checkb_cont = QtWidgets.QCheckBox("Continuos")
        self.gaugetabSam_label_lambda0 = QtWidgets.QLabel("λ\u2080")
        self.gaugetabSam_button_lambda0 = QtWidgets.QPushButton("685.51 nm")
        self.gaugetabSam_label_gauge = QtWidgets.QLabel("P Calib")
        self.gaugetabSam_combob_gauge = QtWidgets.QComboBox()
        
        self.group_gauge_tabSam_layout = QtWidgets.QGridLayout()
        
        self.group_gauge_tabSam_layout.addWidget(self.gaugetabSam_button_snap, 0, 0)
        self.group_gauge_tabSam_layout.addWidget(self.gaugetabSam_checkb_cont, 0, 1)
        self.group_gauge_tabSam_layout.addWidget(self.gaugetabSam_label_lambda0, 1, 0)
        self.group_gauge_tabSam_layout.addWidget(self.gaugetabSam_button_lambda0, 1, 1)
        self.group_gauge_tabSam_layout.addWidget(self.gaugetabSam_label_gauge, 2, 0)
        self.group_gauge_tabSam_layout.addWidget(self.gaugetabSam_combob_gauge, 2, 1)
        self.group_gauge_tabSam_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        
        self.widget_gauge_tabSam = QtWidgets.QWidget()
        self.widget_gauge_tabSam.setLayout(self.group_gauge_tabSam_layout)
        
        
        
        
        # Tab Widget
        
        self.gaugetab_button_clean = QtWidgets.QPushButton("Clean Title")
        self.tabs_gauge = QtWidgets.QTabWidget()
        
        self.group_gauge_tabs1 = self.tabs_gauge.addTab(self.widget_gauge_tabRuby, "Ruby")
        self.group_gauge_tabs2 = self.tabs_gauge.addTab(self.widget_gauge_tabSam, "Samarium")
        
        self.group_gauge_layout = QtWidgets.QVBoxLayout()
        
        self.group_gauge_layout.addWidget(self.gaugetab_button_clean)
        self.group_gauge_layout.addWidget(self.tabs_gauge)
        
        self.group_gauge = QtWidgets.QGroupBox("Gauge")
        self.group_gauge.setLayout(self.group_gauge_layout)
                
        #Group Fit: fit_
        
        self.fit_button_snap = QtWidgets.QPushButton("Snap")
        self.fit_checkb_cont = QtWidgets.QCheckBox("Continuos")
        self.fit_label_func = QtWidgets.QLabel("Function")
        self.fit_combob_func = QtWidgets.QComboBox()
        self.fit_label_bkgDeg = QtWidgets.QLabel("Bkg poly degree")
        self.fit_button_bkgDeg  = QtWidgets.QPushButton("1")
        self.fit_label_min = QtWidgets.QLabel("min (nm)")
        self.fit_button_min  = QtWidgets.QPushButton("NaN")
        self.fit_label_max = QtWidgets.QLabel("max (nm)")
        self.fit_button_max  = QtWidgets.QPushButton("NaN")
        self.fit_label_iterLim = QtWidgets.QLabel("Iter Lim")
        self.fit_button_iterLim  = QtWidgets.QPushButton("50")
        self.fit_checkb_auto = QtWidgets.QCheckBox("Auto update")
        self.fit_button_report  = QtWidgets.QPushButton("Report")
        
        self.group_fit_layout = QtWidgets.QGridLayout()
        
        
        self.group_fit_layout.addWidget(self.fit_button_snap, 0, 0)
        self.group_fit_layout.addWidget(self.fit_checkb_cont, 0, 1)
        self.group_fit_layout.addWidget(self.fit_label_func, 1, 0)
        self.group_fit_layout.addWidget(self.fit_combob_func, 1, 1)
        self.group_fit_layout.addWidget(self.fit_label_bkgDeg, 2, 0)
        self.group_fit_layout.addWidget(self.fit_button_bkgDeg, 2, 1)
        self.group_fit_layout.addWidget(self.fit_label_min, 3, 0)
        self.group_fit_layout.addWidget(self.fit_button_min, 3, 1)
        self.group_fit_layout.addWidget(self.fit_label_max, 4, 0)
        self.group_fit_layout.addWidget(self.fit_button_max, 4, 1)
        self.group_fit_layout.addWidget(self.fit_label_iterLim, 5, 0)
        self.group_fit_layout.addWidget(self.fit_button_iterLim, 5, 1)
        self.group_fit_layout.addWidget(self.fit_checkb_auto, 6, 0)
        self.group_fit_layout.addWidget(self.fit_button_report, 6, 1)
        
        self.group_fit = QtWidgets.QGroupBox("Fit")
        self.group_fit.setLayout(self.group_fit_layout)
        
        #Group Fit: log_
        
        self.log_checkb_ONOFF = QtWidgets.QCheckBox("Active")
        self.log_label_delta = QtWidgets.QLabel("Log Time")
        self.log_button_delta = QtWidgets.QPushButton("1 s")
        self.log_label_threshold= QtWidgets.QLabel("Threshold")
        self.log_button_threshold = QtWidgets.QPushButton("1000")
        self.log_button_folder = QtWidgets.QPushButton("Folder")
        self.log_label_folder= QtWidgets.QLabel("C:\tmp")
        
        self.group_log_layout = QtWidgets.QGridLayout()
        
        self.group_log_layout.addWidget(self.log_checkb_ONOFF, 0, 0, 1, 2)
        self.group_log_layout.addWidget(self.log_label_delta, 1, 0)
        self.group_log_layout.addWidget(self.log_button_delta, 1, 1)
        self.group_log_layout.addWidget(self.log_label_threshold, 2, 0)
        self.group_log_layout.addWidget(self.log_button_threshold, 2, 1)
        self.group_log_layout.addWidget(self.log_button_folder, 3, 0, 1, 2)
        self.group_log_layout.addWidget(self.log_label_folder, 4, 0, 1, 2)
        
        self.group_log = QtWidgets.QGroupBox("Logger")
        self.group_log.setLayout(self.group_log_layout)
        
        
        # deacivate wheel event on QComboBox
        # https://stackoverflow.com/questions/61084951/how-to-disable-mouse-wheel-event-of-qcombobox-placed-in-qtablewidget-in-python

        self.fit_combob_func.wheelEvent = lambda event: None  
        self.gaugetabRuby_combob_gauge.wheelEvent = lambda event: None  
        self.gaugetabRuby_combob_Tcalib.wheelEvent = lambda event: None
        self.gaugetabSam_combob_gauge.wheelEvent = lambda event: None
        
        
        #Final layout
        layout_controlsH = QtWidgets.QHBoxLayout()
        layout_controlsV = QtWidgets.QVBoxLayout()

        layout_controlsV.addWidget(self.group_file)
        layout_controlsV.addWidget(self.group_spec)
        layout_controlsV.addWidget(self.group_meas)
        layout_controlsV.addWidget(self.group_measTemp)
        layout_controlsV.addWidget(self.group_fit)
        layout_controlsV.addWidget(self.group_gauge)
        layout_controlsV.addWidget(self.group_log)
        
        layout_controlsV.addStretch(1) #No vertical Stretch
        layout_controlsV.setAlignment(QtCore.Qt.AlignTop)
        # layout_controls = QtWidgets.QVBoxLayout()
        
        # layout_controls.addWidget(button_Open_csv)
        # layout_controls.addWidget(button_Open_dat)
        # layout_controls.addWidget(button_Open_custom)
        # #layout_controls.addWidget(self.combo)
        
        # layout_controls.addWidget(button_Accept)
        # layout_controls.addWidget(button_Cancel)
        # layout_controls.setAlignment(QtCore.Qt.AlignTop)
        layout_controlsH.addLayout(layout_controlsV)
        layout_controlsH.addStretch(1) #No horizontal Stretch
        
        self.frame = QtWidgets.QFrame()
        self.frame.setLayout(layout_controlsH)
        self.frame.setMinimumWidth(self.frame.sizeHint().width())
        
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        #self.setWidgetResizable(False)
        self.setWidget(self.frame)
        
        self.force_style_update(font_size)
        
        
    def sizeHint(self):
        if self.frame:
            #To include size of ScrollBar
            #self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            #return self.frame.sizeHint()
            style = self.style()
            scrollbar_width = style.pixelMetric(QtWidgets.QStyle.PM_ScrollBarExtent)
            content_width = self.frame.sizeHint().width()
            new_width = content_width + scrollbar_width 
            return QtCore.QSize(new_width, self.frame.sizeHint().height())
        return super().sizeHint()
    
    def _recursive_layout_update(self, widget):
        widget.updateGeometry()
        widget.repaint()
    
        if isinstance(widget, QtWidgets.QScrollArea) and widget.widget():
            self._recursive_layout_update(widget.widget())
            
        elif isinstance(widget, QtWidgets.QTabWidget):
            for i in range(widget.count()):
                tab_widget = widget.widget(i)
                if tab_widget:
                    self._recursive_layout_update(tab_widget)
    
        if widget.layout():
            widget.layout().invalidate()
            
            for i in range(widget.layout().count()):
                item = widget.layout().itemAt(i)
                child_widget = item.widget()
                
                if child_widget:
                    self._recursive_layout_update(child_widget)
                elif item.layout():
                    for j in range(item.layout().count()):
                        sub_item = item.layout().itemAt(j)
                        sub_child_widget = sub_item.widget()
                        if sub_child_widget:
                            self._recursive_layout_update(sub_child_widget)
    
        widget.adjustSize()
    
    
    def force_style_update(self, font_size = 15):
        """
        Applica il nuovo stylesheet e avvia il processo di aggiornamento ricorsivo
        dalla QScrollArea (self) o dal suo frame contenuto.
        """

        
        if self.debug: print("Forcing full style and layout update...")
        
        # 1. Applica il nuovo global stylesheet
        style = """
                      * {
                          font-size: """ + str(int(font_size)) + """px;
                    }
                      """
        QtWidgets.qApp.setStyleSheet(style)
        
        # 2. Avvia l'aggiornamento ricorsivo partendo dal QFrame interno
        if hasattr(self, 'frame') and self.frame:
            self._recursive_layout_update(self.frame)
        
        self.frame.setMinimumWidth(self.frame.sizeHint().width())
        
        # 3. Aggiorna il contenitore principale (la QScrollArea)
        self.setWidget(self.frame) # Risistema il widget nella scroll area
        self.frame.adjustSize()
        self.updateGeometry()
        self.adjustSize()
        self.update()
        
        # Forzare un evento di ridimensionamento sulla finestra principale
        # Se chiami force_style_update da una QMainWindow, è meglio eseguire questo lì:
        # QMainWindow.resize(size.width() + 1, size.height())
        
        if self.debug: print("Update complete.")
        
    
if __name__ == "__main__":
    
    #https://www.w3schools.com/cssref/css_colors.php
    
    app = QtWidgets.QApplication(sys.argv)
#     app.setStyleSheet("""
#                       * {
#                           font-size: 20px;
#                     }
# QGroupBox { font-weight: bold;  color : blueviolet; } 
# """)
    app.setStyleSheet(" * {font-size: 40px; } QGroupBox { font-weight: bold;  color : blueviolet; } ")
    window = controls()

    window.show()
    sys.exit(app.exec())