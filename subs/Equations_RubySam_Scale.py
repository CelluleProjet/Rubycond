# -*- coding: utf-8 -*-
"""

Equations_RubySam_Scale

This file is part of Rubycond

Rubycond: Pressure by Ruby Luminescence (PRL) software to determine pressure in diamond anvil cell experiments.

Version 0.1.0
Release 240222

Contacts

Yiuri Garino:
    yiuri.garino@cnrs.fr
    
Silvia Boccato: 
    silvia.boccato@upmc.fr
    

Copyright (c) 2023 Yiuri Garino - Silvia Boccato

Future Download: https://github.com/CelluleProjet/Rubycond

License: GPLv3

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

"""


def Ruby_Datchi_T(T, L):
    """ Datchi 2007, Ruby temperature scale. 
    Datchi et al., High Pressure Research, 27:4, 447-463 (2007).
    Valid up to 100 GPa and 1000 K.
    For temperatures up to 50 K: L - A, A = 0.887 nm. Equation (3).
    For temperatures from 50 to 296 K: L - A*(T-296 K) - B*(T-296 K)^2 + C*(T-296 K)^3, A = .00664 nm/K, B = 6.76e-6 nm/K^2, C = 2.33e-8 nm/K^3. Equation (4).
    For temperatures from from 296 to 900 K: L - A*(T-296 K) - B*(T-296 K)^2 + C*(T-296 K)^3, A = .00746 nm/K, B = 3.01e-6 nm/K^2, C = 8.76e-9 nm/K^3. Equation (2).
    """
    if T <= 50:
        delta = - 0.887
    elif 50 <= T < 296:
        dT = T-296
        delta = 0.00664 * dT + 6.76e-6 * dT**2 - 2.33e-8 * dT**3
    elif 296 <= T < 900:
        dT = T - 296
        delta = 0.00746 * dT - 3.01e-6 * dT**2 + 8.76e-9 * dT**3
    return L - delta


def Ruby_Dorogokupets_forDatchiT(L,L0):
    """
    Dorogokupets 2007, Ruby pressure scale.
    Dorogokupets and Oganov, Physical Review B 75, 024115 (2007), equation (16).
    Valid from ambient to 150 GPa, at ambient temperature.
    A*(L-L0)/L0*(1+B*(L-L0)/L0): A = 1884 GPa, B = 5.5.
    """
    A = 1884
    B = 5.5
    dLL0 = (L-L0)/L0
    return A*dLL0*(1+B*dLL0)


def Ruby_P(L, L0, A, B):
    return (A/B)*((L/L0)**B-1)

def Ruby_Dewaele2004(L, L0):
    """ Dewaele 2004, Hydrostatic ruby pressure scale (PTM He).
    Dewaele et al., PRB 70, 094112 (2004); equation (1).
    Valid from ambient pressure to 150 GPa, at 298 K.
    (A/B)*((L/L0)**B-1), A = 1904 GPa B = 9.61.
    """
    return Ruby_P(L, L0, 1904, 9.61) 

def Ruby_Dewaele(L, L0):
    """ Dewaele 2008, Quasi-hydrostatic ruby pressure scale (PTM He).
    Dewaele et al., PRB 78, 104102 (2008); caption of Figure 3.
    Valid from ambient pressure to 180 GPa, at 298 K.
    (A/B)*((L/L0)**B-1), A = 1920 GPa B = 9.61. 
    """
    return Ruby_P(L, L0, 1920, 9.61) 

def Ruby_hydro(L, L0):
    """
    Mao 1986, Quasi-hydrostatic ruby pressure scale (PTM Ar).
    Mao et al., Journal of Geophysical Research, 91, B5, 4673-4676 (1986).
    Valid from ambient pressure to 80 GPa, at 298 K.    
    (A/B)*((L/L0)**B-1), A = 1904 GPa B =7.665 L0 = 694.22 nm.
    """
    return Ruby_P(L, L0, 1904, 7.665)

def Ruby_non_hydro(L, L0):
    """
    Mao 1978, Non-hydrostatic ruby pressure scale.
    Mao et al., Journal of Applied Physics, 49(6) (1978); equation (3).
    Valid from 6 to 100 GPa, at 298 K.    
    (A/B)*((L/L0)**B-1), A = 1904 GPa B = 5 L0 = 694.22 nm.
    """
    return Ruby_P(L, L0, 1904, 5)

def Ruby_Shen(L, L0):
    """
    Shen 2020, Quasi-hydrostatic ruby pressure scale (PTM He).
    Shen et al., High Pressure Research, 40, 3, 299-314 (2020), equation (3).
    Valid from ambient pressure to 150 GPa, at 298 K.
    A * (L - L0)/L0 * (1 + B * (L - L0)/L0), A = 1870 GPa B = 5.63 L0 = 694.25 nm.
    """
    A = 1870
    B = 5.63
    exp = ((L - L0)/L0)
    return A * exp * (1 + B * exp)

def Sam_Rashchenko(L, L0):
    """
    Rashchenko 2015, Sm2+:SrB4O7 pressure scale.
    Rashchenko et al., Journal of Applied Physics 117, 145902 (2015).
    Valid from ambient pressure to 120 GPa.
    A*(L-L0)*((1+B*(L-L0))/(1+C*(L-L0))), A = 4.2 GPa B = 2e-2 C = 3.6e-2 L0 = 685.51 nm. 
    """
    C1 = 4.2
    C2 = 2E-2
    C3 = 3.6E-2
    dL = L - L0
    return (C1*dL)*((1+dL*C2)/(1+dL*C3))

def Sam_Datchi(L, L0):
    """
    Datchi 1997, Sm2+:SrB4O7 pressure scale.
    Datchi et al., Journal of Applied Physics, 81(8) (1997), equation (4).
    Valid from ambient to 124 GPa in hydrostatic conditions (He), and up to 130 GPa in non-hydrostatic medium (H2O); temperatures up to 900 K.
    A*(L-L0)*((1+B*(L-L0))/(1+C*(L-L0))), A = 4.032 GPa B = 9.29e-3 C = 2.32e-2 L0 = 685.41 nm.
    """
    C1 = 4.032
    C2 = 9.29E-3
    C3 = 2.32E-2
    dL = L - L0
    return C1*dL*((1+dL*C2)/(1+dL*C3))

