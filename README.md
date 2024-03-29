# Rubycond
Pressure by Ruby Luminescence (PRL) software to determine pressure in diamond anvil cell experiments  

## Install

1) Download and install Miniconda **OR** Anaconda (NOT both):

   - Miniconda  
   https://docs.anaconda.com/free/miniconda/miniconda-install/
  
   - Anaconda  
   https://docs.anaconda.com/anaconda/install/


2) from anaconda prompt (windows) or terminal (Ubuntu & MAC) create a virtual environment with name "my_env":

```bash
conda create -n my_env pip
```

3) activate the virtual environment with
```bash
conda activate my_env 
```

4) install rubycond with:

```bash

pip install rubycond
```

5) OPTIONAL: Install the [python-seabreeze](https://python-seabreeze.readthedocs.io/en/latest/install.html) for the Ocean Optics spectrometers:

```bash
conda install -c conda-forge seabreeze
seabreeze_os_setup
```

6) launch rubycond:

```bash

rubycond
```

## Shortcut

In windows the rubycond.exe can be found in the virtual environment Scripts folder, usually something like:  
- C:\Users\username\anaconda3\envs\my_env\Scripts
- C:\Users\username\miniconda\envs\my_env\Scripts

To check where the virtual environment has been installed:

```bash

conda env list 
```

# Manual

## Operating modes
**Rubycond** can operate in two modes, *Connected* or *Stand Alone*. If the parameter stand_alone in the the init file (*Rubycond_init.txt*) is set to False, **Rubycond** will start in *Stand Alone* mode. If the parameter stand_alone is set to True, **Rubycond** will try to load the spectrometer drivers and start in *Connected* mode. If an error occurs while opening the driver, **Rubycond** will start in *Stand Alone* mode.  

![Alert HR4000](https://github.com/CelluleProjet/Rubycond/assets/83216683/c9fc4473-440c-402a-abe0-62cf92eff6dd)


## *Connected* mode

![Mode_Connected](https://github.com/CelluleProjet/Rubycond/assets/83216683/9b05b7ad-02fd-48db-a72f-fec510278279)


## *Stand Alone* mode
  
![Mode_Stand_Alone](https://github.com/CelluleProjet/Rubycond/assets/83216683/c1ef0fc5-278a-421e-9997-61dff363dfae)


## Fit Window

A separate window that shows all the details of the fit results

![Fit Window](https://github.com/CelluleProjet/Rubycond/assets/83216683/76c2bde3-206d-481d-9e42-5f3cac5f82ae)



## Tab Shortcuts
- List of available shortcuts
```
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
```
## Tab Calc
- Let the user to perform simulations using different gauges, wavelenght, pressure and temperatures for Ruby and gauges, wavelenght and pressure for Samarium.

![Tab3_Calc](https://github.com/CelluleProjet/Rubycond/assets/83216683/504ab673-5e3d-49b9-880d-078ce759b997)


## Menus
> [!IMPORTANT]
> All main program controls are performed by menus, shortcuts or menu activation via the Alt key
 
### File
  - **Save** :warning: Not Available in **_Stand Alone_** mode   
    - Save the data in txt format, wavelenghts, intensity, plus all the accumulations if the **Measurement:Accumulation** option is selected. Save the header in rtf format, with a resume of the performed analisys. Save the main figure in png format.
  
  - **Save Fit**  
    - Save the data in txt format, wavelenghts, intensity, best fit (peak 1 , peak 2 and background if Double Function) plus all the accumulations if the **Measurement:Accumulation** option is selected. Save the header in rtf format, with a resume of the performed analisys. Save the main figure in png format.
  
  - **Open File**  
    - Read data from txt file, letting the user to select the x / first column units (nm or cm⁻¹)
  
  - **Quit**
    - Quit the main program  

### Graph
  - **Rescale Y**  
    - Rescale the Y axis
  
  - **Rescale X**   
    - Rescale the X axis
  
  - **Rescale XY**  
    - Rescale the X and the Y axis
  
  - **Rescale to Fit**  
    - rescale to the selected fit range, see **Fit:Min** and **Fit:Max**
  
  - **X axis units nm cm⁻¹**  
    - switch the Wavelenghts unit beetween nm and cm⁻¹

### Spectrometer :warning: Menu Not Available in **_Stand Alone_** mode   
  - **Model**
    - Shows the spectrometer model and serial number
  
  - **User Calibration**
    - If selected use the calibation saved in the init file *Rubycond_init.txt* as  
  **Wavelengths** (nm) = calibration_i + calibration_c1 * **pixels** + calibration_c2 * **pixels²** + calibration_c3 * **pixels³**
  
  - **Electronic Dark**
    - If requested and supported the average value of electric dark pixels on the ccd of the spectrometer is subtracted from the measurements to remove the noise floor in the measurements caused by non optical noise sources ([correct_dark_counts for HR4000](https://python-seabreeze.readthedocs.io/en/latest/api.html#seabreeze.spectrometers.Spectrometer.intensities))
  
  - **Take Background**
    - save the current acquisition as background reference
  
  - **Subtract Background**
    - substract the background reference from the current acquisition
  
  - **Calibrate**
    - launch the sub-routine Rubycond_calibrator

### Measurement :warning: Menu Not Available in **_Stand Alone_** mode  

  - **Snap**  
    - perform a single acquisition
  
  - **Acquire**  
    - start a nuos acquisition
  
  - **Int Time (s)**  
    - change the acquisition integration time in seconds, default value is 0.1 seconds

  - **Accumulation**  
    - change the number of accumulations, default value is 1

### Gauge
This menu allows to choose the gauge to be used and to change the default values for the reference wavelenghts and temperatures to be used both for Ruby and Samarium Sm²⁺:SrB₄O₇.  

![Gauge_Selection](https://github.com/CelluleProjet/Rubycond/assets/83216683/f7620eba-94d9-4ee6-9583-b69e295737f7)


- Ruby
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
    - Datchi 2004  

- Sm²⁺:SrB₄O₇
  - λ₀ (nm) = 685.51
  - P Calibration
    - Rashchenko 2015
    - Datchi 1997

### Fit
> [!IMPORTANT]
> Fit are always performed to the data with Wavelenghts in cm⁻¹
> If _sigma_vary_ = False, when _Voight_ or  _Double Voigt_ functions are selected the sigma corresponding to the gaussian component is fixed to the value of _sigma (cm-1)_ (See init file *Rubycond_init.txt*)  

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
  
  - **Poly Degree**
    - change the polynomial degree up to 7

  - **Min NNN**
    - Show the fit range minimum value and let to change it. **Enter value** let the user to manually input the new value, **Set NNN** directly set the value NNN where NNN is the actual cursor position showed by a dotted vertical line on the graph (left mouse click on the graph to change it)
  
  - **Max NNN**
    - Show the fit range minimum value and let to change it. **Enter value** let the user to manually input the new value, **Set NNN** directly set the value NNN where NNN is the actual cursor position showed by a dotted vertical line on the graph (left mouse click on the graph to change it)
  
  - **Iter Lim**
    - The maximum number of iterations used in the minimization routine. The default value is 150
  
  - **Autoupdate**
    - If not selected the Fit initial condition are automatically evaluated when the Fit range is changed (**Fit:Min** and **Fit:Max**), so not taking in account eventual changement in the afterwards acquired signal.
    - If selected the Fit results are used as the Fit initial condition in the next Fit.

  - **Clean Graph**
    - Remove the Fit plot from the graph

### Logger :warning: Menu Not Available in **_Stand Alone_** mode   

  - **Logger ON/OFF**
    - Turn ON / OFF the log functionality

  - **Logger Time (s)**
    - select the log save frequency in seconds

  - **Log Directory**
    - show the selected logging directory, can be changed during logging


## Logger :warning: Not Available in **_Stand Alone_** mode   
The logger will automatically create a **log file** in the log directory. A new file will be create if the log directory is changed. The filename format is: 

  - %y%m%d_%H%M%S.txt, i.e. 02 Jan 2024 12:03:04 => '240102_120304.txt'

The logger will save **3 files** for each log using the format:

  - %y%m%d_%H%M%S_header.rtf  
    - Main info of the measurement, including the fit results if the fit is selected
  - %y%m%d_%H%M%S_img.png
    - Image as displayed on the software
  - %y%m%d_%H%M%S_data.txt
    - All the data, including the fit results if the fit is selected

The logger will add a line to the **log file** with the following **parameters**:

  - Beginning of the **3 files** filename (starting with %y%m%d_%H%M%S)
  - [Unix time](https://www.epochconverter.com/) of the log
  - Measurement:Int Time (s)
  - Measurement:Accumulation
  - R1_center
  - R1_gamma
  - R1_fwhm
  - R2_center (if selected)
  - R2_gamma (if selected)
  - R2_fwhm (if selected)
  - Fit:Min
  - Fit:Max
  - Selected Pressure Gauge (if selected)
  - Selected Temperature Gauge (if selected)
  - Pressure
  - Temperaure

## Init file *Rubycond_init.txt*
In windows the init file can be found in the virtual environment packages folder, usually something like: 

- C:\Users\username\anaconda3\envs\my_env\Lib\site-packages\rubycond

Init file example:

```
[Settings]
stand_alone = False

[Spectrometer]
calibration_i = 1
calibration_c1 = 1
calibration_c2 = 0
calibration_c3 = 0
sigma_vary = False
sigma (cm-1) = 0.637
```

## Tested Spectrometers

Ocean Optics HR4000, based on [python-seabreeze](https://python-seabreeze.readthedocs.io/en/latest/install.html)

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
Rubycond: Pressure by Ruby Luminescence (PRL) software to determine pressure in diamond anvil cell experiments

Copyright (c) 2022-2023 Yiuri Garino

Rubycond is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

## Release notes

Version 0.1.1 Release 240222: First release  
Version 0.1.2 Release 240227: Fixed "LMFIT Error: pk_2_gauss" bug when "Double Gauss" fit function is selected  
