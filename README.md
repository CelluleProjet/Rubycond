# Rubycond
Python software to determine pressure in diamond anvil cell experiments by Ruby and Samarium luminescence  
  
<img width="1108" height="705" alt="fullscreen_Ruby" src="https://github.com/user-attachments/assets/d78b5e29-4230-41aa-9dbe-e33dd1ed3bd4" />


  

# Manual
> [!IMPORTANT]
> All controls are available both in the left sidebar and within the menus, with the exception of the items in the Help menu, which are only accessible through the menu bar. The left sidebar can be hidden to maximize the size of the figures.

## File
<img width="243" height="98" alt="1_File" src="https://github.com/user-attachments/assets/698e9f2f-cbed-438c-b1fd-59192d73d976" />  

  - **Save**
    - Save the data in txt, csv and npy format (wavelenghts, intensity), plus all the accumulations if the **Measurement:Accumulation** option is selected. Save the header in rtf format, with a resume of the performed analisys. Save the main figure in png format.
  - **Save Fit**  
    - WIP, not yet implemented
  - **Open File**  
    - Read data from file using the [Rubycond Open File software](https://github.com/CelluleProjet/Rubycond_OF)
  - **Quit**
    - Quit the main program

## Spectrometer
<img width="240" height="165" alt="Spectrometer_commands" src="https://github.com/user-attachments/assets/e6140fed-e6c4-436b-9754-d0f67fb89a4a" />  
  
  - **Calib Params**
     - Opens the **Calibration Parameters** window to manually input data, manage calibration files (Open/Save), or edit the default settings.  Click Accept when finished to confirm the new values.
   <img width="213" height="362" alt="2_Calibration_Parameters" src="https://github.com/user-attachments/assets/4466c19c-eb22-43e6-b8a3-61eb5af63792" />
  
  - **User Calib**
     - Select to use the calibration
  - **Calibrator**
     - Open the [Rubycond Calibrator software](https://github.com/CelluleProjet/Rubycond_CB)
  - **Save as bkg**
     - Capture the current spectrum to be used as a background reference
  - **Substract bkg**
     - Enable background subtraction to remove the stored reference from the active measurement

## Cooler :warning: Available only for Andor spectrometers.
<img width="240" height="69" alt="Cooler" src="https://github.com/user-attachments/assets/34aa6d2b-4458-4da0-8216-d5338fde0ed1" />  

Displays the target cooling temperature and the current temperature. 

### Measurements
<img width="239" height="177" alt="3_Measurements_commands" src="https://github.com/user-attachments/assets/058c5be8-3a32-47ac-a395-c13d082b16c4" />


  - **Snap**
    - perform a single acquisition
  - **Acquire**
    - start a continuos acquisition
  - **Int Time (s)**
    - change the acquisition integration time in seconds, default value is 0.1 seconds
  - **Accumulation**
    - change the number of accumulations, default value is 1
### Fit
> [!IMPORTANT]
> Fit are always performed to the data with Wavelenghts in cm⁻¹
<img width="235" height="255" alt="4_Fit_commands" src="https://github.com/user-attachments/assets/edada1fb-c67b-42b3-9a4b-eff715a4fd5f" />

  - **Snap**
    - perform a single fit
  - **Continuos**
    - start a continuos fitting routine
  - **Function**
    - Voigt
    - Gauss
    - Lorentz
    - Double Voigt
    - Double Gauss
    - Double Lorentz
  - **Bkg poly Degree**
    - change the polynomial degree up to 7
  - **Min (nm)**
    - Fit range minimum value. Click on the value to change it. If you click on the graph first, the value of the selected point will be suggested automatically.
  - **Max (nm)**
    - Fit range maximum value. Click on the value to change it. If you click on the graph first, the value of the selected point will be suggested automatically.
  - **Iter Lim**
    - The maximum number of iterations used in the minimization routine. The default value is 150
  - **Autoupdate**
    - If not selected the Fit initial condition are automatically evaluated when the Fit range is changed (**Fit:Min** and **Fit:Max**), so not taking in account eventual changement in the afterwards acquired signal.
    - If selected the Fit results are used as the Fit initial condition in the next Fit.
  - **Report**
    - Opens a window with the detailed fit report  
### Gauge
<img width="237" height="304" alt="5_Gauge_Commands" src="https://github.com/user-attachments/assets/0e75939d-769b-458c-b3ba-782e2ebd8d53" />  

This menu allows to choose the gauge to be used and to change the default values for the reference wavelenghts and temperatures to be used both for Ruby and Samarium Sm²⁺:SrB₄O₇.  



- Ruby Cr³⁺:Al₂O₃  
  - λ₀ (nm) = 694.25
  - P Calibration
    - Shen 2020
    - Mao hydro 1986
    - Mao non hydro 1986
    - Dewaele 2008
    - Dorogokupets and Oganov 2007
  - T(λ₀) (K) = 298
  - T(λ) (K) = 298
  - T Calibration
    - Not Used 
    - Datchi 2004  
- Sm²⁺:SrB₄O₇
  - λ₀ (nm) = 685.51
  - P Calibration
    - Rashchenko 2015
    - Datchi 1997
### Logger
<img width="241" height="180" alt="6_logger" src="https://github.com/user-attachments/assets/0321ab96-1384-4b69-b9d3-ede52f417e92" />  

WIP, not yet implemented  

## Tab Shortcuts
- List of available shortcuts  
  Available layouts: QWERTY and AZERTY  
  To switch layouts, uncomment the corresponding line (line 127 or 128). Default is QWERTY.
```bash
self.keyboard = 'QWERTY'#uncomment to select
#self.keyboard = 'AZERTY' #uncomment to select
```
QWERTY Shortcuts  
```

ctrl + Z = Set Fit:Min as cursor
ctrl + X = Set Fit:Max as cursor
ctrl + C = Zoom to fit
ctrl + Q = Rescale to full scale
ctrl + F = Fit snap
ctrl + G = Fit continuos

ctrl + O = Open file
ctrl + S = Save file
```
AZERTY Shortcuts  
```

ctrl + W = Set Fit:Min as cursor
ctrl + X = Set Fit:Max as cursor
ctrl + C = Zoom to fit
ctrl + Q = Rescale to full scale
ctrl + F = Fit snap
ctrl + G = Fit continuos

ctrl + O = Open file
ctrl + S = Save file
```

## Tab Calc
- Let the user to perform simulations using different gauges, wavelenght, pressure and temperatures for Ruby and gauges, wavelenght and pressure for Samarium using the [Ruby and Samarium pressure/wavelength calculator](https://github.com/CelluleProjet/Rubycond_calc)

# Install
Use pip to install the program **within a virtual environment (strongly recommended).**  
[Here's a short tutorial on installing a virtual environment.](https://github.com/CelluleProjet/Install/tree/main?tab=readme-ov-file#install-virtual-environment)
```bash
pip install rubycond
```
5) OPTIONAL: Install the [python-seabreeze](https://python-seabreeze.readthedocs.io/en/latest/install.html) for the Ocean Optics spectrometers:

```bash
conda install -c conda-forge seabreeze
seabreeze_os_setup
```
# About
## Author

**Yiuri Garino**  

## Contacts

**Yiuri Garino**  
- yiuri.garino@cnrs.fr
   
**Silvia Boccato**
- silvia.boccato@cnrs.fr
  
<img src="https://github.com/CelluleProjet/Rubycond/assets/83216683/b728fe64-2752-4ecd-843b-09d335cf4f93" width="100" height="100">
<img src="https://github.com/CelluleProjet/Rubycond/assets/83216683/0a81ce1f-089f-49d8-ae65-d19af8078492" width="100" height="100">


[Cellule Projet](http://impmc.sorbonne-universite.fr/fr/plateformes-et-equipements/cellule-projet.html) @ [IMPMC](http://impmc.sorbonne-universite.fr/en/index.html)


## License
**Rubycond**: Python software to determine pressure in diamond anvil cell experiments by Ruby and Samarium luminescence

Copyright (c) 2022-2026 Yiuri Garino

**Rubycond** is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

## Release notes

Version 0.1.1 Release 240222: First release  
Version 0.1.2 Release 240227: Fixed "LMFIT Error: pk_2_gauss" bug when "Double Gauss" fit function is selected  
Version 0.2.0 Release 260301: Total program rewrite: migration from Tkinter to Qt5 libraries. Version 0.1.2 is still available [here](https://github.com/CelluleProjet/Rubycond_Tk).
