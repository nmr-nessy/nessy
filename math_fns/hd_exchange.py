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

# Calculation of Hydrogen-Deuterium Exchange

# Python modules
from scipy import exp
import time
import wx


def HD_fit(p, I, T, error=None, output=False):
    # Minimise using chi2 function
    err = ((HD(T, p)-I))**2

    # Output
    if output:
        wx.CallAfter(output.AppendText, 'I0: '+str(p[0])+' % to max, C: '+str(p[1])+', kex: ' + str(p[2]) + ' 1/min\n')
        time.sleep(0.001)

    # no negative I0
    if p[0] < 0:
        err = (1+err)**2
    if p[0] > 10:
        err = (1+err)**2
    # no negative C
    if p[1] < 0:
        err = (1+err)**2
    # no bigger C than 300
    if p[1] > 300:
        err = (1+err)**2
    # no negative kex
    if p[2] < 0:
        err = (1+err)**2

    return err



def HD(T, p):

    # Parameters
    I0 = p[0]
    C = p[1]
    kex = 0 - p[2]
    t = T/60

    a = C * exp(kex*t)

    I = a + I0

    return I
