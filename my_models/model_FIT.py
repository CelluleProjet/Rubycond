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


import numpy as np
import matplotlib.pyplot as plt
import os, sys
from datetime import datetime
from lmfit.models import LorentzianModel, GaussianModel, VoigtModel, PolynomialModel
from scipy.special import wofz 
from PyQt5 import QtWidgets
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


class fit():
    def __init__(self, debug = True):
        ''' 
        Units in nm, Fit preformed always in cm-1
        '''
        self.debug = debug 
        self.fit_function = "Double Voigt" #"Lorentz", "Gauss", "Voigt", "Double Lorentz", "Double Gauss", "Double Voigt"
        self.fit_functions = ["Lorentz", "Gauss", "Voigt", "Double Lorentz", "Double Gauss", "Double Voigt"]
        self.fit_report = 'No report'
        self.out = None
        self.bkg = False #Use background
        self.intensities = None 
        self.intensities_bkg = None 
        self.polynomial_degree = 1
        self.wavelengths = None
        self.wavelengths_units = 'nm'
        self.wavelengths_min = None
        self.wavelengths_max = None
        self.mask = None
        self.max_nfev = 50
        self.sigma_vary = False
        self.sigma = 0.637
        self.autoupdate = False
        self.x_fit = None
        self.y_fit = None
    
    def fit_autoupdate_pars(self):
        
        fit = self.fit_function
        #print('Autoupdate') 
        if fit == "Lorentz" or fit == "Gauss":
            pars_auto = ['pk_1_center','pk_1_amplitude','pk_1_sigma']
            
        elif fit == "Voigt" :
            pars_auto = ['pk_1_center','pk_1_amplitude','pk_1_gamma']
            
        if fit == "Double Lorentz" or fit == "Double Gauss":
            pars_auto = ['pk_1_center','pk_1_amplitude','pk_1_sigma','pk_2_center', 'pk_2_amplitude' , 'pk_2_sigma']
            
        elif fit == "Double Voigt" :
            pars_auto = ['pk_1_center','pk_1_amplitude','pk_1_gamma','delta','pk_2_amplitude','pk_2_gamma']  
        
        for i in pars_auto:
            self.pars[i].value = self.out.params[i].value
        
        pars_auto = ['bkg_c'+str(i) for i in range(self.polynomial_degree + 1)]
        
        for i in pars_auto:
            self.pars[i].value = self.out.params[i].value
    

    # def fit_update_pars(self):
    #     fit = self.fit_function

    #     if self.bkg:
    #         y0 = (self.intensities - self.intensities_bkg)[0]
    #         y1 = (self.intensities - self.intensities_bkg)[-1]
    #     else:
    #         y0 = self.intensities[0]
    #         y1 = self.intensities[-1]
        
    #     x0 = self.x_fit[0]
    #     x1 = self.x_fit[-1]
        

    #     try:
    #         slope = (y0-y1)/(x0-x1)
    #     except:
    #         slope = 0
                
    #     intercept = y0-slope*x0
        
    #     center = self.x_fit[self.y_fit.argmax()]

    #     if self.debug: print(f'Center = {center:.2f}, {1e7/center:.2f}')
        
    #     y_max_rel = self.y_fit.max() - (intercept+slope*center)

    #     self.pars['pk_1_center'].min = x0
    #     self.pars['pk_1_center'].max = x1
    #     self.pars['pk_1_center'].value = center

    #     if fit == "Lorentz" or fit == "Gauss":
            
    #         sigma_init = 10
    #         amplitude = y_max_rel*sigma_init*np.sqrt(2*np.pi)
            
    #         self.pars['pk_1_amplitude'].value = amplitude
    #         self.pars['pk_1_sigma'].value = sigma_init
        
    #     elif fit == "Voigt":
            
    #         gamma_init = 10
    #         amplitude = self.Voigt_amplitude(y_max_rel, gamma_init, self.sigma)

    #         self.pars['pk_1_amplitude'].value = amplitude
    #         self.pars['pk_1_gamma'].value = gamma_init

    #     elif fit == "Double Lorentz" or fit == "Double Gauss":
            
    #         sigma_init = 10
    #         amplitude = y_max_rel*sigma_init*np.sqrt(2*np.pi)
            
    #         self.pars['pk_1_amplitude'].value = amplitude
    #         self.pars['pk_1_sigma'].value = sigma_init
            
    #         delta =  14450.8 - 14421.8 #Syassen Table 4
            
    #         self.pars['pk_2_center'].value = center + delta
    #         self.pars['pk_2_center'].max = x0
    #         self.pars['pk_2_center'].min = x1
    #         self.pars['pk_2_amplitude'].value = amplitude
    #         self.pars['pk_2_sigma'].value = sigma_init

    #     elif fit == "Double Voigt":
    #         gamma_init = 10
    #         amplitude = self.Voigt_amplitude(y_max_rel, gamma_init, self.sigma)
    #         self.pars['pk_1_amplitude'].value = amplitude/2
    #         self.pars['pk_2_amplitude'].value = amplitude/2
    #         self.pars['delta'].value =  14450.8 - 14421.8 #Syassen Table 
    #         self.pars['pk_1_gamma'].value = gamma_init
    #         self.pars['pk_1_sigma'].value = self.sigma
    #         self.pars['pk_2_sigma'].value = self.sigma

 
    #     if self.debug: print(self.model)
    #     if self.debug: print(self.sigma_vary)
    #     if self.debug: print(self.pars.pretty_print())
    #     print('pars pk 2 center fit_update_pars =',  self.pars['pk_2_center'].value)
    
    def fit_set_y(self, intensities):
        
        self.intensities = intensities
        
        self.x_fit_range = self.x_fit[self.mask]

        if self.wavelengths_units == 'cm-1' and self.bkg:
            #Fit in cm-1, data OK, substract bkg

            self.y_fit_range = (self.intensities - self.intensities_bkg)[self.mask]
            
        elif self.wavelengths_units == 'cm-1' and not self.bkg:
            #Fit in cm-1, data OK, no bkg

            self.y_fit_range = self.intensities[self.mask]
            
        elif self.wavelengths_units == 'nm' and self.bkg:
            #Fit in cm-1, data in nm, arrange data, substract bkg

            self.y_fit_range = (self.intensities - self.intensities_bkg)[::-1][self.mask]
            
        elif self.wavelengths_units == 'nm' and not self.bkg:
            #Fit in cm-1, data in nm, arrange data, substract bkg

            self.y_fit_range = self.intensities[::-1][self.mask]

    def fit_run(self):
        
        
        if self.autoupdate and (self.out is not None): 
            self.fit_autoupdate_pars()
        else:
            self.fit_set_pars()
            
        #print(self.pars.pretty_print())
        #print(self.y_fit_range.max())
        try:
            if self.max_nfev is not None:
                self.out = self.model.fit(self.y_fit_range, self.pars, x = self.x_fit_range, max_nfev = self.max_nfev)
                #self.out = self.model.fit(self.y_fit_range, self.pars, x = self.x_fit_range, max_nfev = self.max_nfev, weights = 1/np.sqrt(np.abs(self.y_fit_range)))
            else:
                self.out = self.model.fit(self.y_fit_range, self.pars, x = self.x_fit_range) 
                #self.out = self.model.fit(self.y_fit_range, self.pars, x = self.x_fit_range, weights = 1/np.sqrt(np.abs(self.y_fit_range))) 
            #print(self.out.fit_report())
            self.out_dictionary = self.dictionary_out_creator(self.out)
            return 0
        except:
            pop_up_error(traceback.format_exc(), 'Pythony Error')
            #print(self.y_fit_range)
            return 1
        
        self.out_dictionary = self.dictionary_out_creator(self.out)
        
    def fit_update_report(self):
        #self.fit_report = self.out.fit_report()
        fit = self.fit_function
        self.fit_report =''
        try:
            
            
            center = self.out.params["pk_center"].value
            self.fit_report = f'Peak center = {center:.2f} cm\u207B\u00B9 {1e7/center:.2f} nm\n'
            
            if fit == "Voigt" or fit == "Double Voigt":
                gamma = self.out.params["pk_gamma"].value
                gammanm = 1e7/(center-gamma) - 1e7/(center+gamma)
                self.fit_report+= f'Peak gamma = {gamma:.2f} cm\u207B\u00B9 {gammanm:.2f} nm\n'
            else:
                sigma = self.out.params["pk_sigma"].value
                sigmanm = 1e7/(center-sigma) - 1e7/(center+sigma)
                self.fit_report+= f'Peak sigma = {sigma:.2f} cm\u207B\u00B9 {sigmanm:.2f} nm\n'
                
            if fit == "Double Lorentz" or fit == "Double Gauss" or fit == "Double Voigt" :
                self.fit_report+= '\n'
                center = self.out.params["pk_2_center"].value
                self.fit_report+= f'Peak 2 center = {center:.2f} cm\u207B\u00B9 {1e7/center:.2f} nm\n'
                if fit == "Double Lorentz" or fit == "Double Gauss":
                    sigma = self.out.params["pk_2_sigma"].value
                    sigmanm = 1e7/(center-sigma) - 1e7/(center+sigma)
                    self.fit_report+= f'Peak 2 sigma = {sigma:.2f} cm\u207B\u00B9 {sigmanm:.2f} nm\n'
                else:
                    gamma = self.out.params["pk_2_gamma"].value
                    gammanm = 1e7/(center-gamma) - 1e7/(center+gamma)
                    self.fit_report+= f'Peak 2 gamma = {gamma:.2f} cm\u207B\u00B9 {gammanm:.2f} nm\n'
            self.fit_report+= '\n'
        except:
            pass 
        self.fit_report+= f"Model = {fit} + Poly Degree {self.polynomial_degree}\n"
        if not self.wavelengths_units == 'nm':
            #True = cm-1
            self.fit_report+= f"Fit Range {self.wavelengths_min:.2f} to {self.wavelengths_max:.2f} cm\u207B\u00B9\n"
        else:
            self.fit_report+= f"Fit Range {1e7/self.wavelengths_min:.2f} to {1e7/self.wavelengths_max:.2f} cm\u207B\u00B9\n"
            self.fit_report+= f"Fit Range {self.wavelengths_min:.2f} to {self.wavelengths_max:.2f} nm\n"
        self.fit_report+= f"Maximum number of function evaluations = {self.max_nfev}\n\n"
        try:
            self.fit_report+= self.out.fit_report(show_correl = False)
        except:
            pass 
        #print(self.fit_report)
        
    def fit_init_model(self):
        
        self.out = None
        
        fit = self.fit_function
        
        if self.debug: print(f'Selected fit = {fit}')
        
        if fit == "Lorentz":
            peak = LorentzianModel(prefix='pk_1_')
        elif fit == "Gauss":
            peak = GaussianModel(prefix='pk_1_')
        elif fit == "Voigt":
            peak = VoigtModel(prefix='pk_1_')
        elif fit == "Double Lorentz":
            peak = LorentzianModel(prefix='pk_1_') + LorentzianModel(prefix='pk_2_')
        elif fit == "Double Gauss":
            peak = GaussianModel(prefix='pk_1_') + GaussianModel(prefix='pk_2_')
        elif fit == "Double Voigt":
            peak = VoigtModel(prefix='pk_1_') + VoigtModel(prefix='pk_2_')
        
        bkg_n = self.polynomial_degree
        
        background = PolynomialModel(bkg_n,prefix='bkg_')
        
        if bkg_n == 0:
            self.pars = background.make_params(c0=0)
        elif bkg_n == 1:
            self.pars = background.make_params(c0=0, c1=0)
        elif bkg_n == 2:
            self.pars = background.make_params(c0=0, c1=0, c2=0)
        elif bkg_n == 3:
            self.pars = background.make_params(c0=0, c1=0, c2=0, c3=0)
        elif bkg_n == 4:
            self.pars = background.make_params(c0=0, c1=0, c2=0, c3=0, c4=0)
        elif bkg_n == 5:
            self.pars = background.make_params(c0=0, c1=0, c2=0, c3=0, c4=0, c5=0)
        elif bkg_n == 6:
            self.pars = background.make_params(c0=0, c1=0, c2=0, c3=0, c4=0, c5=0, c6=0)
        elif bkg_n == 7:
            self.pars = background.make_params(c0=0, c1=0, c2=0, c3=0, c4=0, c5=0, c6=0, c7=0)
        
        
        
        self.pars += peak.make_params()
        self.model = peak + background
    
    def fit_set_x(self, wavelengths):
        ''' 
        Sorted array, x_fit in cm-1 increasing values
        data supposed to be in increasing order
        '''
        if (wavelengths == 0).sum() == 0:
            self.out = None
    
            self.wavelengths = wavelengths
            self.wavelengths_min = wavelengths.min()
            self.wavelengths_max = wavelengths.max()
            
            if self.wavelengths_units == 'cm-1':
                #Fit in cm-1, data OK
                self.x_fit = self.wavelengths
            else:
                #Fit in cm-1, data in nm, convert and arrange data
                self.x_fit = 1e7/self.wavelengths
                self.x_fit = np.sort(self.x_fit)
            
            self.fit_update_mask()
        else:
            self.x_fit = None

    
    
    
    def fit_update_mask(self):
        
        if self.wavelengths_min is None: 
            _min = self.wavelengths.min()
        else:
            _min = self.wavelengths_min
            
        if self.wavelengths_max is None: 
            _max = self.wavelengths.max()
        else:
            _max = self.wavelengths_max
            
        if self.wavelengths_units == 'cm-1':
            #Fit in cm-1, data OK
            self.x_fit_min = _min
            self.x_fit_max = _max
        else:
            #Fit in cm-1, data in nm, invert data
            self.x_fit_min = 1e7/_max
            self.x_fit_max = 1e7/_min 

        self.mask = (self.x_fit >= self.x_fit_min) * (self.x_fit <= self.x_fit_max)

        
    def fit_set_pars(self):
        #print('fit_set_pars')
        #print(self.y_fit_range.argmax())
        #print(self.y_fit_range.max())
        fit = self.fit_function

        y0 = self.y_fit_range[0]
        y1 = self.y_fit_range[-1]
        
        x0 = self.x_fit_range[0]
        x1 = self.x_fit_range[-1]
        
        if self.debug:
            print()
            print(f'Fit Range = {x0:.2f} to  {x1:.2f}')
            print()
        try:
            slope = (y0-y1)/(x0-x1)
        except:
            slope = 0
                
        intercept = y0-slope*x0
        
        if self.debug: print(f'Mask = {self.mask}')
        
        

        center = self.x_fit_range[self.y_fit_range.argmax()]

        if self.debug: print(f'Center = {center:.2f}, {1e7/center:.2f}')
        
        y_max_rel = self.y_fit_range.max() - (intercept+slope*center)
        
        #print('y_max_rel', y_max_rel)
        
        self.pars['bkg_c0'].value = intercept
        self.pars['bkg_c1'].value = slope 
        
        self.pars['pk_1_center'].min = x0
        self.pars['pk_1_center'].max = x1
        self.pars['pk_1_center'].value = center
        #print('pk_1_center = ', center)
        if fit == "Lorentz" or fit == "Gauss":
            
            sigma_init = 10
            amplitude = y_max_rel*sigma_init*np.sqrt(2*np.pi)
            
            self.pars['pk_1_amplitude'].min = 1
            self.pars['pk_1_amplitude'].value = amplitude
            
            self.pars['pk_1_sigma'].vary = True
            self.pars['pk_1_sigma'].value = sigma_init
        
        elif fit == "Voigt":
            
            gamma_init = 10
            amplitude = self.Voigt_amplitude(y_max_rel, gamma_init, self.sigma)
            
            self.pars['pk_1_amplitude'].min = .0001
            self.pars['pk_1_amplitude'].value = amplitude

            self.pars['pk_1_gamma'].set(vary=True, expr='')
            self.pars['pk_1_gamma'].vary = True
            self.pars['pk_1_gamma'].expr = None
            self.pars['pk_1_gamma'].value = gamma_init
            self.pars['pk_1_gamma'].min = 0.0001
            
            self.pars['pk_1_sigma'].vary = self.sigma_vary
            self.pars['pk_1_sigma'].value = self.sigma
        
        elif fit == "Double Lorentz" or fit == "Double Gauss":
            sigma_init = 10
            amplitude = y_max_rel*sigma_init*np.sqrt(2*np.pi)
            
            self.pars['pk_1_amplitude'].min = 1
            self.pars['pk_1_amplitude'].value = amplitude
            
            self.pars['pk_1_sigma'].vary = True
            self.pars['pk_1_sigma'].value = sigma_init
            
            delta =  14450.8 - 14421.8 #Syassen Table 4
            

            
            self.pars['pk_2_center'].value = center + delta
            #print('pars pk 2 center 1 =',  self.pars['pk_2_center'].value)
            #print(self.pars['pk_2_center'].min , self.pars['pk_2_center'].max)
            self.pars['pk_2_center'].max = x1
            self.pars['pk_2_center'].min = x0
            
            self.pars['pk_2_amplitude'].min = 1
            self.pars['pk_2_amplitude'].value = amplitude
            
            self.pars['pk_2_sigma'].vary = True
            self.pars['pk_2_sigma'].value = sigma_init
            #print('pars pk 2 center 2 =',  self.pars['pk_2_center'].value)

        elif fit == "Double Voigt":
            gamma_init = 10
            amplitude = self.Voigt_amplitude(y_max_rel, gamma_init, self.sigma)
            
            self.pars['pk_1_amplitude'].value = amplitude/2
            self.pars['pk_1_amplitude'].min = .0001
            
            self.pars['pk_2_amplitude'].value = amplitude/2
            self.pars['pk_2_amplitude'].min = .0001
            
            delta =  14450.8 - 14421.8 #Syassen Table 4
            
            self.pars.add('delta', value=delta,  vary=True, min=1)
            
            self.pars['pk_2_center'].expr = 'pk_1_center + delta'
            # self.pars['pk_2_center'].value = center + delta
            # self.pars['pk_2_center'].max = x0
            # self.pars['pk_2_center'].min = x1

            self.pars['pk_1_gamma'].set(vary=True, expr='')
            self.pars['pk_1_gamma'].vary = True
            self.pars['pk_1_gamma'].expr = None
            self.pars['pk_1_gamma'].value = gamma_init
            self.pars['pk_1_gamma'].min = 0.0001
            
            self.pars['pk_1_sigma'].vary = self.sigma_vary
            self.pars['pk_1_sigma'].value = self.sigma
            
            self.pars['pk_2_gamma'].set(vary=True, expr='')
            self.pars['pk_2_gamma'].vary = True
            self.pars['pk_2_gamma'].expr = None
            self.pars['pk_2_gamma'].value =gamma_init
            self.pars['pk_2_gamma'].min = 0.0001
            self.pars['pk_2_sigma'].value = self.sigma
            self.pars['pk_2_sigma'].vary = self.sigma_vary
            #print('pars pk 2 center 3 =',  self.pars['pk_2_center'].value)
            #print('pars pk 2 center fit_update_pars =',  self.pars['pk_2_center'].value)
        
    def fit_eval_comp(self):
        ''' 
        self.comps_x as x in eval_components in cm-1
        '''
        if self.out is not None:
            
            self.eval_comps_x = np.linspace(self.x_fit_min, self.x_fit_max, 500)
            comps = self.out.eval_components(x = self.eval_comps_x)
            
            fit = self.fit_function
            
            if fit == "Double Voigt" or fit == "Double Lorentz" or fit == "Double Gauss":
            
                self.eval_full = comps['pk_1_'] + comps['pk_2_'] + comps['bkg_']
                self.eval_P1 = comps['pk_1_'] + comps['bkg_']
                self.eval_P2 = comps['pk_2_'] + comps['bkg_']
                self.eval_bkg = comps['bkg_']
            else:
                self.eval_full = comps['pk_1_'] + comps['bkg_']
                self.eval_P1 = comps['pk_1_'] + comps['bkg_']
                self.eval_bkg = comps['bkg_']

                
    
    def dictionary_out_creator(self, out):
        description = ['method', 'function evals', 'data points', 'variables', 'chi-square', 'reduced chi-square', 'Akaike info crit', 'Bayesian info crit']
        ref = [out.result.method, out.nfev, out.ndata, out.nvarys, out.chisqr, out.redchi, out.aic, out.bic]
        _ = {i : j for i, j in zip(description,ref)}
        return _
    
    #Math Section
    
    def Voigt(self, x, amplitude, center, sigma, gamma):
        """
        Return the Voigt line shape at x with Lorentzian component gamma
        and Gaussian component sigma.
        sigma = HWHM / sqrt(2 * log(2)) = FWHM / ( 2 * sqrt(2 * log(2))) #FWHM = fG
        gamma = FWHM / 2 #FWHM = fL

        """

        return amplitude*np.real(wofz((x - center + 1j*gamma)/sigma/np.sqrt(2))) / sigma /np.sqrt(2*np.pi)
    
    def Voigt_amplitude(self, height, gamma, sigma):
        
        return height*(sigma*np.sqrt(2*np.pi))/wofz((1j*gamma)/(sigma*np.sqrt(2))).real

    def Voigt_height(self, amplitude, gamma, sigma):
        
        return amplitude/(sigma*np.sqrt(2*np.pi))*wofz((1j*gamma)/(sigma*np.sqrt(2))).real
    
    
    def fV(self, fG, fL):
        '''
        FWHM approximation , see wikipedia
        '''
        x = 0.5346
        return x*fL + np.sqrt( (1-x)**2 * fL**2 + fG ** 2)

    def fG(self, fV, fL):
        '''
        FWHM approximation , see wikipedia
        '''
        x = 0.5346
        return np.sqrt((fV - x*fL)**2 - (1 - x)**2 * fL**2)

    def fL(self, fV, fG):
        '''
        FWHM approximation , see wikipedia
        '''
        x = 0.5346
        num = x*fV - np.sqrt((x*fV)**2 - (2*x - 1)*(fV**2 - fG**2))
        
        den = 2*x - 1
        return num/den
    
    def Voigt_FWHM(self, gamma, sigma):
        '''
        FWHM approximation , see wikipedia
        '''
        fG = sigma * 2*np.sqrt(2*np.log(2))
        fL = 2 * gamma
        x = 0.5346
        return x*fL + np.sqrt( (1-x)**2 * fL**2 + fG ** 2)

    def Voigt_sigma(self, fV, gamma):
        '''
        FWHM approximation , see wikipedia
        '''
        fL = 2 * gamma
        x = 0.5346
        fG = np.sqrt((fV - x*fL)**2 - (1 - x)**2 * fL**2)
        return fG / ( 2*np.sqrt(2*np.log(2)) ) 

    def Voigt_gamma(self, fV, sigma):
        '''
        FWHM approximation , see wikipedia
        '''
        fG = sigma * 2*np.sqrt(2*np.log(2))
        x = 0.5346
        num = x*fV - np.sqrt((x*fV)**2 - (2*x - 1)*(fV**2 - fG**2))
        
        den = 2*x - 1
        fL =  num/den
        return fL / 2


if __name__ == "__main__":
    my_fit = fit(False)
    
    x_center = 14450
    x_nm = np.linspace(1e7/15000, 1e7/14000, 200)
    x_cm_1 = 1e7/x_nm
    
    sigma = 10
    y = my_fit.Voigt(x_cm_1, 1, x_center, sigma, 10)
    
    plt.plot(x_cm_1,y)
    plt.xlabel('Wavelengths (cm\u207B\u00B9)')
    plt.grid()
    plt.axvline(x_center, ls = '--', color = 'black')
    plt.show()
    
    x_nm = 1e7/x_cm_1 #x increasing
    
    plt.plot(x_nm,y)
    plt.xlabel('Wavelengths (nm)')
    plt.show()
    
    my_fit
    my_fit.wavelengths_units = 'nm'
    my_fit.fit_set_x(x_nm)
    my_fit.fit_set_y(y)
    my_fit.fit_function = 'Voigt'
    my_fit.fit_init_model()
    my_fit.fit_set_pars()
    my_fit.fit_run()
    
    init = my_fit.model.eval(my_fit.pars, x = x_cm_1)
    best = my_fit.model.eval(my_fit.out.params, x = x_cm_1)
    
    plt.plot(x_cm_1, y)
    #plt.plot(x_cm_1, init,'--k')
    #plt.plot(x_cm_1, my_fit.out.best_fit, 'r')
    plt.plot(x_cm_1, best, 'r')
    plt.xlabel('Wavelengths (cm\u207B\u00B9)')
    plt.grid()
    plt.axvline(x_center, ls = '--', color = 'black')
    plt.xlim((14300, 14600))
    plt.show()
    
    
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