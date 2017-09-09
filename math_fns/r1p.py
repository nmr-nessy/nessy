#################################################################################
#                                                                               #
#   (C) 2010-2011 Michael Bieri                                                 #
#   (C) 2016 Edward d'Auvergne                                                  #
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

# Calculation of R1p (R1rho)

# Python modules
from scipy import sqrt, log, sin, cos, arctan, exp, array, sum
import time
import wx

# NESSY modules
from math_fns.models import limit_entries
from elements.variables import Pi, Constraints_container
from curvefit.chi2 import Chi2_container



def fit_R1rho(I0, T, R1rho):
    """ Function to fit to R1rho.

    I:      Intensity at spin lock time T
    I0:     Reference intensity at spin lock time 0
    T:      Spin lock time"""

    I = I0 * exp((-1)*R1rho*T)

    return I


def R1rho_residuals(p, y, x, I0, output=None):
    """Function to minimise R1rho function.

    p:  Parameter (R1rho)
    y:  Intensities at given time
    x:  Spin ock time
    I0: Reference intensity
    """

    # Minimise
    err = (y - fit_R1rho(I0, x, p))

    # Feedback
    if output:
            limit_entries(output)
            wx.CallAfter(output.AppendText, 'R1rho: ' + str(p[0])[0:6] + '\n')
            time.sleep(0.001)

    # Return error
    return err



def R1p_model_1(p, w1, dw):
    """No exchange."""

    # Parameters
    R1 = p[0]
    R2 = p[1]

    # angle of spin lock field
    theta = arctan(w1/dw)

    # Function (kex = 0)
    R1rho = R1 * (cos(theta))**2 + R2 * (sin(theta))**2

    return R1rho


def R1p_model_1_residuals(p, y, error, spinlock_field, offset, globalfit=False, output=None, freqs=None):
        # Number of datasets
        if globalfit: n = len(spinlock_field)
        else: n = 1

        # Chi2 function
        err = []
        for exp in range(0, n):
            # R1
            R1 = p[exp * 2]

            # R2
            R2 = p[exp * 2 + 1]

            # Parameters
            p_exp = [R1, R2]

            # Chi2
            err_tmp = ((R1p_model_1(p_exp, spinlock_field[exp], offset[exp])-y[exp])/error[exp])**2

            # combine errors
            err.extend(err_tmp)

        # R2
        for i in range(0, len(p)):
            if p[i] < Constraints_container.r2[0][0] or p[i] > Constraints_container.r2[0][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        if output:
            limit_entries(output)
            wx.CallAfter(output.AppendText, 'R1: '+ str(R1)[0:6] +  '1/s, R2: ' + str(R2)[0:6] + ' 1/s\n')
            time.sleep(0.001)

        # Chi2
        Chi2_container.chi2 = sum(err)

        # Return
        return err


def R1p_model_2(p, w1, dw):
    """Fast exchange 2 site model."""

    # Variables
    kex = p[0]
    phi = p[1]
    R1 = p[2]
    R2 = p[3]

    # Parameters
    we = We(w1, dw)
    theta = Theta(w1, dw)

    # Calculate
    R1rho = R1 * (cos(theta))**2 + R2 * (sin(theta))**2 + phi * kex/(kex**2 + we**2) * (sin(theta))**2

    # return
    return R1rho


def R1p_model_2_residuals(p, y, error, spinlock_field, offset, globalfit=False, output=None, freqs=None):
        # Number of datasets
        if globalfit: n = len(spinlock_field)
        else: n = 1

        # error storage
        err = []

        # shared variables
        kex = p[0]
        phi = p[1]

        # Calculate chi2
        for i in range(0, n):
            # parameters
            R1 = p[2+2*i]
            R2 = p[3+2*i]

            # store normalized phi
            frq = float(freqs[i].GetValue()) * 2 * Pi

            # convert phi to Hz
            phi_Hz = phi * frq * frq

            # set up p
            p_est = [kex, phi_Hz, R1, R2]

            # Chi2
            err_tmp = ((R1p_model_2(p_est, spinlock_field[i], offset[i])-y[i])/error[i])**2

            # combine errors
            err.extend(err_tmp)

            # Constraints
            # R2
            if R2 < Constraints_container.r2[1][0] or R2 > Constraints_container.r2[1][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # Phi
        if phi < Constraints_container.phi[1][0] or phi > Constraints_container.phi[1][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # kex
        if kex < Constraints_container.kex[1][0] or kex > Constraints_container.kex[1][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # Output
        if output:
            limit_entries(output)
            wx.CallAfter(output.AppendText, 'R1: ' + str(R1)[0:6] + ', R2: ' + str(R2)[0:6] + ', Phi: ' + str(phi) + ', kex: '+ str(kex) + '\n')
            time.sleep(0.001)

        # return error
        Chi2_container.chi2_surface[0].append(kex)
        Chi2_container.chi2_surface[1].append(phi)
        Chi2_container.chi2_surface[2].append(sum(err))
        Chi2_container.chi2 = sum(err)
        return err


def R1p_model_3(p, w1, dw):
    """Fast exchange 2 site model."""

    # Variables
    kex = p[0]
    shiftdiff = p[1]
    pb = p[2]
    pa = 1-pb
    R1 = p[3]
    R2 = p[4]

    # Parameters
    we = We(w1, dw)
    theta = Theta(w1, dw)

    # Rex
    Rex = (sin(theta))**2 * pa * pb * kex * shiftdiff**2 / (kex**2 + dw**2 + w1**2)

    # Calculate
    R1rho = R1 * (cos(theta))**2 + R2 * (sin(theta))**2 + Rex

    # return
    return R1rho


def R1p_model_3_residuals(p, y, error, spinlock_field, offset, globalfit=False, output=None, freqs=None):
        # Number of datasets
        if globalfit: n = len(spinlock_field)
        else: n = 1

        # error storage
        err = []

        # shared variables
        kex = p[0]
        shiftdiff = p[1]
        pb = p[2]

        # Calculate chi2
        for i in range(0, n):
            # parameters
            R1 = p[3+2*i]
            R2 = p[4+2*i]

            # store normalized phi
            frq = float(freqs[i].GetValue()) * 2 * Pi

            # convert phi to Hz
            shiftdiff = shiftdiff * frq

            # set up p
            p_est = [kex, shiftdiff, pb, R1, R2]

            # Chi2
            err_tmp = ((R1p_model_3(p_est, spinlock_field[i], offset[i])-y[i])/error[i])**2

            # combine errors
            err.extend(err_tmp)

            # Constraints
            # R2
            if R2 < Constraints_container.r2[2][0] or R2 > Constraints_container.r2[2][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # dw
        if shiftdiff < Constraints_container.dw[2][0] or shiftdiff > Constraints_container.dw[2][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # kex
        if kex < Constraints_container.kex[2][0] or kex > Constraints_container.kex[2][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

         # pb
        if pb < Constraints_container.pb[2][0] or pb > Constraints_container.pb[2][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # Output
        if output:
            limit_entries(output)
            wx.CallAfter(output.AppendText, 'R1: ' + str(R1)[0:6] + ', R2: ' + str(R2)[0:6] + ', kex: '+ str(kex)[0:9] + ', dw: ' + str(shiftdiff)[0:6] + ', pb: ' + str(pb)[0:6] +'\n')
            time.sleep(0.001)

        # return error
        Chi2_container.chi2 = sum(err)
        Chi2_container.chi2_surface[0].append(kex)
        Chi2_container.chi2_surface[1].append(pb)
        Chi2_container.chi2_surface[2].append(sum(err))
        return err


def R1p_model_4(p, w1, dw):
    """General expression of R1rho."""

    # Variables
    kex = p[0]
    shiftdiff = p[1]
    pb = p[2]
    pa = 1-pb
    R1 = p[3]
    R2 = p[4]

    # Parameters
    we = We(w1, dw)
    theta = Theta(w1, dw)

    # Rex
    Rex = kex/2 - kex/2 * ( 1 - ( (4 * (sin(theta))**2 * pa * pb * shiftdiff**2) / ( we**2 + kex**2 - (sin(theta))**2 * pa * pb * shiftdiff**2 * kex**2 * 4 * we**2 / (we**4 + we**2*kex**2))))**(0.5)

    # Calculate
    R1rho = R1 * (cos(theta))**2 + R2 * (sin(theta))**2 + Rex

    # return
    return R1rho


def R1p_model_4_residuals(p, y, error, spinlock_field, offset, globalfit=False, output=None, freqs=None):
        # Number of datasets
        if globalfit: n = len(spinlock_field)
        else: n = 1

        # error storage
        err = []

        # shared variables
        kex = p[0]
        shiftdiff = p[1]
        pb = p[2]

        # Calculate chi2
        for i in range(0, n):
            # parameters
            R1 = p[3+2*i]
            R2 = p[4+2*i]

            # store normalized phi
            frq = float(freqs[i].GetValue()) * 2 * Pi

            # convert phi to Hz
            shiftdiff = shiftdiff * frq

            # set up p
            p_est = [kex, shiftdiff, pb, R1, R2]

            # Chi2
            err_tmp = ((R1p_model_4(p_est, spinlock_field[i], offset[i])-y[i])/error[i])**2

            # combine errors
            err.extend(err_tmp)

            # Constraints
            # R2
            if R2 < Constraints_container.r2[2][0] or R2 > Constraints_container.r2[2][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # dw
        if shiftdiff < Constraints_container.dw[2][0] or shiftdiff > Constraints_container.dw[2][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # kex
        if kex < Constraints_container.kex[2][0] or kex > Constraints_container.kex[2][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

         # pb
        if pb < Constraints_container.pb[2][0] or pb > Constraints_container.pb[2][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # Output
        if output:
            limit_entries(output)
            wx.CallAfter(output.AppendText, 'R1: ' + str(R1)[0:6] + ', R2: ' + str(R2)[0:6] + ', kex: '+ str(kex)[0:9] + ', dw: ' + str(shiftdiff)[0:6] + ', pb: ' + str(pb)[0:6] +'\n')
            time.sleep(0.001)

        # return error
        Chi2_container.chi2 = sum(err)
        return err


def We(w1, dw):
    """Calculation of effective spin lock field."""

    return sqrt(w1**2 + dw**2)


def Theta(w1, dw):
    """Calculation of angle between effective magnetic field and z-axis."""

    return arctan((w1/dw))
