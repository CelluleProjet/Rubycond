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


import os, sys
from PyQt5 import QtWidgets, QtCore


class pop_up(QtWidgets.QFrame):
    def __init__(self, text = '', title = '', debug = False):
        super().__init__()
        
        self.setWindowTitle(title)
        self.resize(800, 500)
        
        text_edit = QtWidgets.QPlainTextEdit()
        try:
            text = self.format_dict(text)
        except:
            text = 'Reading Error'
        text_edit.setPlainText(text)
        #Final layout
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(text_edit)
        
        self.setLayout(layout)
        
        # self.setSizePolicy(
        #     QtWidgets.QSizePolicy.Fixed,
        #     QtWidgets.QSizePolicy.Fixed)
    
    def format_dict(self, text):
        new_text = str()
        for key, value in text.items():
            new_text += str(key)
            new_text +='\n\t'
            new_text += str(value)
            new_text +='\n'
            
        return new_text

class pop_up_simple(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel()
        self.label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        layout.addWidget(self.label)
        self.setLayout(layout)

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
        
    def format_dict(self, text):
        new_text = str()
        for key, value in text.items():
            new_text += str(key)
            new_text +='\n\t'
            new_text += str(value)
            new_text +='\n'
            
        return new_text
    

        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet("""
                      * {
                          font-size: 15px;
                    }
                      """)


    #window = pop_up("Ciao")
    #window.show()
    
    
    window = pop_up_error("Ciao, non ho ben capito")
    
    
    sys.exit(app.exec())