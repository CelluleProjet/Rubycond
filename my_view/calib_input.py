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

import os, sys
from datetime import datetime

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






import os, sys
from datetime import datetime
from PyQt5 import QtWidgets, QtCore
import traceback



class pop_up(QtWidgets.QWidget):
    
    signal_update_calibration_pars = QtCore.pyqtSignal(list)
    
    def __init__(self, title = '', debug = False):
        super().__init__()
        
        self.setWindowTitle(title)
        #self.resize(800, 500)
        self.calib_cn = [0,0,0,0] #max poly degree = 3
        
        #Group File: file_
        
        self.file_button_c0 = QtWidgets.QPushButton("c0")
        self.file_button_c1 = QtWidgets.QPushButton("c1")
        self.file_button_c2 = QtWidgets.QPushButton("c2")
        self.file_button_c3 = QtWidgets.QPushButton("c3")
        
        self.file_label_c0 = QtWidgets.QLabel()
        self.file_label_c1 = QtWidgets.QLabel()
        self.file_label_c2 = QtWidgets.QLabel()
        self.file_label_c3 = QtWidgets.QLabel()
        
        self.group_file_layout = QtWidgets.QGridLayout()
        
        self.group_file_layout.addWidget(self.file_button_c0, 0, 0)
        self.group_file_layout.addWidget(self.file_button_c1, 1, 0)
        self.group_file_layout.addWidget(self.file_button_c2, 2, 0)
        self.group_file_layout.addWidget(self.file_button_c3, 3, 0)
        
        self.group_file_layout.addWidget(self.file_label_c0, 0, 1)
        self.group_file_layout.addWidget(self.file_label_c1, 1, 1)
        self.group_file_layout.addWidget(self.file_label_c2, 2, 1)
        self.group_file_layout.addWidget(self.file_label_c3, 3, 1)
        
        self.update_labels()
        
        self.group_file = QtWidgets.QGroupBox("Calibration Parameters")
        self.group_file.setLayout(self.group_file_layout)
        
        #Group Action: act_
        
        self.act_button_accept = QtWidgets.QPushButton("Accept")
        self.act_button_calibrator = QtWidgets.QPushButton("Open Calibrator")
        self.act_button_cancel = QtWidgets.QPushButton("Cancel")
        
        self.group_act_layout = QtWidgets.QVBoxLayout()
        
        self.group_act_layout.addWidget(self.act_button_accept)
        self.group_act_layout.addWidget(self.act_button_calibrator)
        self.group_act_layout.addWidget(self.act_button_cancel)
        
        self.group_act = QtWidgets.QGroupBox()
        self.group_act.setLayout(self.group_act_layout)
        
        #Final layout
        layout_controlsH = QtWidgets.QHBoxLayout()
        layout_controlsV = QtWidgets.QVBoxLayout()

        layout_controlsV.addWidget(self.group_file)
        layout_controlsV.addWidget(self.group_act)
        
        layout_controlsV.addStretch(1) #No vertical Stretch
        layout_controlsV.setAlignment(QtCore.Qt.AlignTop)
        
        layout_controlsH.addLayout(layout_controlsV)
        layout_controlsH.addStretch(1) #No horizontal Stretch
        
        #self.frame = QtWidgets.QFrame()
        #self.frame.setLayout(layout_controlsH)
        self.setLayout(layout_controlsH)
        #self.setWidget(self.frame)
        #self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        #self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        #self.setWidgetResizable(True)
        #self.setWidget(self.frame)
        
        # self.setSizePolicy(
        #     QtWidgets.QSizePolicy.Fixed,
        #     QtWidgets.QSizePolicy.Fixed)
        
        self.file_button_c0.clicked.connect(self.test)
        self.file_button_c1.clicked.connect(self.test)
        self.file_button_c2.clicked.connect(self.test)
        self.file_button_c3.clicked.connect(self.test)
        
        
        self.act_button_cancel.clicked.connect(self.quit_main) 
        self.act_button_accept.clicked.connect(self.update_calibration_pars)
    
    def update_calibration_pars(self):
        self.signal_update_calibration_pars.emit(self.calib_cn)
        
    def update_labels(self):
        self.file_label_c0.setText(f"{self.calib_cn[0]:.5e}")
        self.file_label_c1.setText(f"{self.calib_cn[1]:.5e}")
        self.file_label_c2.setText(f"{self.calib_cn[2]:.5e}")
        self.file_label_c3.setText(f"{self.calib_cn[3]:.5e}")
    
    def test(self):
        par = self.sender().text()
        title = 'Calibration polynomial parameters'
        label = f'Enter {par} par value'
        value_str = str(self.calib_cn[int(par[1])])
        new_value, ok = self.open_input_dialog_float(title, label , value_str)
                                                     
        
        if ok:
            self.calib_cn[int(par[1])] = new_value
            self.update_labels()
        else:
            pop_up_error(traceback.format_exc(), 'Pythony Error')
        
    def open_input_dialog_float(self, title, label, value, minvalue = float("-inf"), maxvalue = float("inf")):
        ''' 
        Scientific notation not allowed in QInputDialog.getDouble
        Return float
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
        
    def quit_main(self):
        self.close()
        
class pop_up_error(QtWidgets.QMessageBox):
    def __init__(self, text, title = '', debug = False):
        super().__init__()
        
        self.setIcon(QtWidgets.QMessageBox.Critical)
        self.setWindowTitle(title)
        self.resize(800, 500)
        

        # try:
        #     text = self.format_dict(text)
        # except:
        #     text = 'Reading Error'

        self.setText(text)
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)
        
        # self.setSizePolicy(
        #     QtWidgets.QSizePolicy.Fixed,
        #     QtWidgets.QSizePolicy.Fixed)
        
        self.exec()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet("""
                      * {
                          font-size: 15px;
                    }
                      """)


    #window = pop_up("Ciao")
    #window.show()
    
    
    window = pop_up()
    window.show()
    sys.exit(app.exec())
    


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