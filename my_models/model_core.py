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

import os
from datetime import datetime

debug = True


script = os.path.abspath(__file__)
script_dir = os.path.dirname(script)
script_name = os.path.basename(script)


class my_model():
    def __init__(self, debug = False):
        self.statusbar_message_ref = [print] #List of messages method (print, label, statusbar, etc)
        
        self.script = script
        self.script_dir = script_dir
        self.script_name = script_name
        self.start_date = datetime.now()
        self.start_name = self.start_date.strftime("%y%m%d_%H%M%S")
        
        
    def statusbar_message_add(self, method):
        #print(method)
        self.statusbar_message_ref.append(method)
        
    def statusbar_message(self, message):
        now = datetime.now()
        text = now.strftime("%H:%M:%S : ") + message
        for method in self.statusbar_message_ref:
            method(text)








