#################################################################################
#                                                                               #
#   (C) 2010 Michael Bieri                                                      #
#                                                                               #
#   This file is part of NESSY.                                                 #
#                                                                               #
#   NESSY is free software: you can redistribute it and/or modify               #
#   it under the terms of the GNU General Public License as published by        #
#   the Free Software Foundation, either version 3 of the License, or           #
#   (at your option) any later version.                                         #
#                                                                               #
#   NESSY is distributed in the hope that it will be useful,                    #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of              #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
#   GNU General Public License for more details.                                #
#                                                                               #
#   You should have received a copy of the GNU General Public License           #
#   along with NESSY; if not, write to the Free Software                        #
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                               #
#################################################################################


# Python modules
from scipy import exp, log



def Eyring_fit(p, kab, T, error):
    err = ((Eyring(T, p)-kab)/error)**2   # Chi2 function
    return err


def Eyring(T, p):
    """ Eyring equation to calculate activation barrier.

    ln(k(ab)/T) = -dH* / RT + ln(kb/h) + dS*/R

    R = gas constant (J/mol*K)
    kb = Bolzmann's constant (J/K)
    h = Planck's constant (Js)"""

    # Parameters
    dH = p[0]
    dS = p[1]

    # Constants
    R = 8.31447215
    kb = 1.3806504 * 10**(-23)
    h = 6.62606896 * 10**(-34)

    # equation
    y = T*kb/h * exp((-1)*dH/(R*T) + dS/R)

    return y


def log_fit(p, y, x, error):
    err = ((log_model(x, p)-y)/error)**2   # Chi2 function
    return err


def log_model(x, p):

    # Variable
    T = x

    # Parameter
    dS = p[0]
    dH = p[1]
    dCp = p[2]

    R = 8.31447215

    Ts =  exp(dCp - dS) * T

    Th = T - (dH/dCp)

    lnKa = (dCp/R) * ( (Th/T)- log(Ts/T) - 1)

    return lnKa


def lin_fit(p, y, x, error, is_dG=False):
    err = ((lin_model(x, p)-y)/error)**2   # Chi2 function
    return err


def lin_model(x, p):

    # Variable
    T = x

    # Parameter
    dS = p[0]
    dH = p[1]

    R = 8.31447215

    lnKa = (dS/R) - (dH/(R*T))

    return lnKa
