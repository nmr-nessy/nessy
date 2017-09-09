#################################################################################
#                                                                               #
#   (C) 2011 Michael Bieri                                                      #
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


# Collection of models

from scipy import tanh, sqrt, cosh, arccosh, log, cos, array
import time
import wx

# NESSY modules
from math_fns.models import limit_entries
from elements.variables import Pi, Constraints_container
from curvefit.chi2 import Chi2_container




def model_2(x, p):
        '''Class for fit data to model 2 (fast exchange):

                       Phi    |-    4v(CPMG)           kex    -|
        R2eff = R20 + ----- * | 1 - -------- * tanh --------   |
                       kex    |_      kex           4v(CPMG)  _|


        Phi = pa * pb * delta_omega^2'''

        # Parameters

        R20 = p[0]
        phi = p[1]
        kex = p[2]

        R2eff = R20+((phi)/kex)*(1-(((4*x)/kex)*tanh((kex/(4*x)))))
        return array(R2eff)


def model_2_residuals(p, y, x, variance, output=None, global_fit=False, freqs=None, rep_index=None):
    # global fit
    if global_fit:
        # Number of datasets
        n = len(x)

        # Initialize error
        error = variance

        # error storage
        err = []

        # shared variables
        kex = p[0]

        # Calculate chi2
        for i in range(0, n):
            # parameters
            phi = p[(2*rep_index[i])+1]
            R2 = p[(2*i)+2]

            # convert Phi to rad/sec
            phi_Hz = phi * (float(freqs[i].GetValue()) * 2 * Pi)**2

            # set up p
            p_est = [R2, phi_Hz, kex]

            # Chi2
            err_tmp = ((model_2(x[i], p_est)-y[i])**2/error[i])

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
        elif kex < Constraints_container.kex[1][0] or kex > Constraints_container.kex[1][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # Output
        if output:
            limit_entries(output)
            wx.CallAfter(output.AppendText, 'R2o: ' + str(R2)[0:6] + ', Phi: ' + str(phi) + ', kex: '+ str(kex) + '\n')
            time.sleep(0.001)

        # return error
        Chi2_container.chi2 = err
        return err


def model_3(x, p):
        """Slow exchange for 2 sites."""

        R20 = p[0]
        kex = p[1]
        dw = p[2]
        pb = p[3]
        pa = 1-pb

        # Psi
        Psi = kex**2 - dw**2

        # xi
        xi = (-2) * dw * ( (pa*kex) - (pb*kex) )

        # D+
        Dpos = 0.5 * ( 1 + ( (Psi + 2*dw**2) / (Psi**2 + xi**2)**(0.5) ) )

        # D-
        Dneg = 0.5 * ( ( (Psi + 2*dw**2) / (Psi**2 + xi**2)**(0.5) ) - 1 )

        # Eta+
        etapos = (Psi + (Psi**2 + xi**2)**(0.5) )**(0.5)   /    (2 * sqrt(2) * x)

        # Eta-
        etaneg = ( (Psi**2 + xi**2)**(0.5) - Psi)**(0.5)   /    (2 * sqrt(2) * x)

        R2eff = R20 + (kex/2) - (x * (arccosh((Dpos*cosh(etapos)) - (Dneg)*cos(etaneg))))
        return R2eff


def model_3_residuals(p, y, x, variance, output=None, global_fit=False, freqs=None, rep_index=None):
    """Minimising Model 3.

    p:          Array of initials guess: [kex1, pb, dw, R2(i)]
    y:          Array of y values (list of arrays if global fit)
    x:          Array of x values (list of arrays if global fit)
    output:     Output object (textctrl), None if no output
    global_fit: Flag if it is a global fit
    freqs:      List of spectrometer frequencies (only in global fit; output in ppm) (wx.TextCtrl)
    """
    # global fit
    if global_fit:
        # Number of datasets
        n = len(x)

        # Initialize error
        error = variance

        # error storage
        err = []

        # shared variables
        kex = p[0]
        pb = p[1]

        # Calculate chi2
        for i in range(0, n):
            # Parameters
            dw = p[(2*rep_index[i])+2]
            R2 = p[(2*i)+3]

            # dw on global fit ppm --> Hz
            dw_Hz = dw*float(freqs[i].GetValue()) * 2 * Pi

            # estimation
            p_est = [R2, kex, dw_Hz, pb]

            #Chi2 function
            err_tmp = ((y[i]-model_3(x[i], p_est))**2/error[i])

            # combine errors
            err.extend(err_tmp)

            # Constraints
            # R2
            if R2 < Constraints_container.r2[2][0] or R2 > Constraints_container.r2[2][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # kex
        if kex < Constraints_container.kex[2][0] or kex > Constraints_container.kex[2][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # dw
        elif dw < Constraints_container.dw[2][0] or dw > Constraints_container.dw[2][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # pb
        elif pb < Constraints_container.pb[2][0] or pb > Constraints_container.pb[2][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2


        # Output
        if output:
            limit_entries(output)
            wx.CallAfter(output.AppendText, 'R2o: ' + str(R2)[0:6] + ', kex: ' + str(kex) + ', dw: '+ str(dw) + ', pa: '+ str(1-pb) +'\n')
            time.sleep(0.001)

        Chi2_container.chi2 = err
        return err


def model_4(x, p):
    """Fast exchange for 3 state exchange.

                   _          _                               _   _         _          _                               _   _
                  /   Phi1    |     4v(CPMG)          kex1     |   \       /   Phi2    |     4v(CPMG)          kex2     |   \
    R2eff = R2 + |  ----- *   | 1 - -------- * tanh --------   |    |  +  |  ----- *   | 1 - -------- * tanh --------   |    |
                  \_  kex1    |_      kex1          4v(CPMG)  _|  _/       \_  kex2    |_      kex2          4v(CPMG)  _|  _/


    Phi1 = (pa + pc) * pb * delta_omega1**2

    Phi2 = (pa + pb) * pc * delta_omega2**2

    """

    R20 = p[0]
    phi1 = p[1]
    kex1 = p[2]
    phi2 = p[3]
    kex2 = p[4]

    R2eff = R20+((phi1)/kex1)*(1-(((4*x)/kex1)*tanh((kex1/(4*x)))))+((phi2)/kex2)*(1-(((4*x)/kex2)*tanh((kex2/(4*x)))))
    return R2eff


def model_4_residuals(p, y, x, variance, output=None, global_fit=False, freqs=None, rep_index=None):
    # global fit
    if global_fit:
        # Number of datasets
        n = len(x)

        # Initialize error
        error = variance

        # error storage
        err = []

        # shared variables
        kex1 = p[0]
        kex2 = p[1]

        # Calculate chi2
        for i in range(0, n):
            # parameters
            phi1 = p[(3*rep_index[i])+2]
            phi2 = p[(3*rep_index[i])+3]
            R2 = p[(3*i)+4]

            # Convert phi to Hz
            phi1_Hz = phi1 * (float(freqs[i].GetValue()) * 2 * Pi)**2
            phi2_Hz = phi2 * (float(freqs[i].GetValue()) * 2 * Pi)**2

            # stimation
            p_est = [R2, phi1_Hz, kex1, phi2_Hz, kex2]


            # Chi2 function
            err_tmp = ((model_4(x[i], p_est)-y[i])**2/error[i])

            # combine errors
            err.extend(err_tmp)

            # Constraints
            # R2
            if R2 < Constraints_container.r2[3][0] or R2 > Constraints_container.r2[3][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # kex1
        if kex1 < Constraints_container.kex[3][0] or kex1 > Constraints_container.kex[3][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # kex2
        elif kex2 < Constraints_container.kex2[3][0] or kex2 > Constraints_container.kex2[3][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # phi1
        elif phi1 < Constraints_container.phi[3][0] or phi1 > Constraints_container.phi[3][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # phi2
        elif phi2 < Constraints_container.phi2[3][0] or phi2 > Constraints_container.phi2[3][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # Output
        if output:
            limit_entries(output)
            wx.CallAfter(output.AppendText, 'R2o: ' + str(R2)[0:6] + ', Phi A-B: ' + str(phi1)[0:7] + ', kex A-B: '+ str(kex1)[0:6] + ', Phi B-C: ' + str(phi2)[0:7] + ', kex B-C: '+ str(kex2)[0:6] + '\n')
            time.sleep(0.001)
        Chi2_container.chi2 = err
        return err


def model_5(x, p):
        """Slow exchange for 3 state."""

        R20 = p[0]
        kex = p[1]
        dw = p[2]
        pb = p[3]
        kex2 = p[4]
        dw2 = p[5]
        pc = p[6]
        pa = 1 - (pc + pb)

        # Psi
        Psi = kex**2 - dw**2
        Psi2 = kex2**2 - dw2**2

        # Xi
        xi = (-2) * dw * ( (((pa+pc)-pb)*kex) - (pb*kex) )
        xi2 = (-2) * dw2 * ( (((pa+pb)-pc)*kex2) - (pc*kex2) )

        # D+
        Dpos = 0.5 * ( 1 + ( (Psi + 2*dw**2) / (Psi**2 + xi**2)**(0.5) ) )
        Dpos2 = 0.5 * ( 1 + ( (Psi2 + 2*dw2**2) / (Psi2**2 + xi2**2)**(0.5) ) )

        # D-
        Dneg = 0.5 * ( ( (Psi + 2*dw**2) / (Psi**2 + xi**2)**(0.5) ) - 1 )
        Dneg2 = 0.5 * ( ( (Psi2 + 2*dw2**2) / (Psi2**2 + xi2**2)**(0.5) ) - 1 )

        # Eta+
        etapos = (Psi + (Psi**2 + xi**2)**(0.5) )**(0.5)   /    (2 * sqrt(2) * x)
        etapos2 = (Psi2 + (Psi2**2 + xi2**2)**(0.5) )**(0.5)   /    (2 * sqrt(2) * x)

        # Eta-
        etaneg = ( (Psi**2 + xi**2)**(0.5) - Psi)**(0.5)   /    (2 * sqrt(2) * x)
        etaneg2 = ( (Psi2**2 + xi2**2)**(0.5) - Psi2)**(0.5)   /    (2 * sqrt(2) * x)

        R2eff = R20 + ((kex/2) - (x * (arccosh((Dpos*cosh(etapos)) - (Dneg)*cos(etaneg))))) + ((kex2/2) - (x * (arccosh((Dpos2*cosh(etapos2)) - (Dneg2)*cos(etaneg2)))))
        return R2eff



def model_5_residuals(p, y, x, variance, output=None, global_fit=False, freqs=None, rep_index=None):
    # global fit
    if global_fit:
        # Number of datasets
        n = len(x)

        # Initialize error
        error = variance

        # error storage
        err = []

        # shared variables
        kex1 = p[0]
        kex2 = p[1]
        pb = p[2]
        pc = p[3]

        # Calculate chi2
        for i in range(0, n):
            # parameters
            dw1 = p[(3*rep_index[i])+4]
            dw2 = p[(3*rep_index[i])+5]
            R2 = p[(3*i)+6]

            # dw on global fit ppm --> Hz
            dw1_Hz = dw1*float(freqs[i].GetValue()) * 2 * Pi
            dw2_Hz = dw2*float(freqs[i].GetValue()) * 2 * Pi

            # p_est
            p_est = [R2, kex1, dw1_Hz, pb, kex2, dw2_Hz, pc]

            # calculate
            err_tmp = ((model_5(x[i], p_est)-y[i])**2/error[i])

            # combine errors
            err.extend(err_tmp)

            # Constraints
            # R2
            if R2 < Constraints_container.r2[4][0] or R2 > Constraints_container.r2[4][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # kex1
        if kex1 < Constraints_container.kex[4][0] or kex1 > Constraints_container.kex[4][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # kex2
        elif kex2 < Constraints_container.kex2[4][0] or kex2 > Constraints_container.kex2[4][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # dw1
        elif dw1 < Constraints_container.dw[4][0] or dw1 > Constraints_container.dw[4][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # dw2
        elif dw2 < Constraints_container.dw2[4][0] or dw2 > Constraints_container.dw2[4][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # pb
        elif pb < Constraints_container.pb[4][0] or pb > Constraints_container.pb[4][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # pc
        elif pc < Constraints_container.pc[4][0] or pc > Constraints_container.pc[4][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # pa is major state
        pa = 1-(pb+pc)
        if pa > 1 or pa < -0.05:    # allow 5% fit error
               for j in range(0, len(err)):
                    err[j] = (err[j])*2
        if pa < pb:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2
        if pa < pc:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2
        if (pa+pb+pc) > 1.1:    # allow 10% fit error
                for j in range(0, len(err)):
                    err[j] = (err[j])*2
        if (pb+pc) > 0.5:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        if output:
            limit_entries(output)
            wx.CallAfter(output.AppendText, 'R2o: ' + str(R2)[0:6] + ', kex A-B: ' + str(kex1)[0:7] + ', dw A-B: '+ str(dw1)[0:6] + ', kex B-C: '+ str(kex2)[0:6] + ', dw B-C: '+ str(dw2)[0:6] + ', pa: ' + str(1-(pb+pc))[0:6] + ', pb: '+ str(pb)[0:6]  +', pc: '+str(pc)[0:6]+'\n')
            time.sleep(0.001)
        Chi2_container.chi2 = err
        return err


def model_6(x, p):
        """Exchange for 2 sites over all time scales (pa >>pb)."""

        R20 = p[0]
        kex = p[1]
        dw = p[2]
        pb = p[3]
        pa = 1-pb
        tcp = 1/(2*x)

        # R2eff
        R2eff = R20 + pa*pb*(dw**2)*kex / ( kex**2 + (pa**2 * dw**4 + 144/tcp**4)**(0.5) )

        return R2eff


def model_6_residuals(p, y, x, variance, output=None, global_fit=False, freqs=None, rep_index=None):
    """Minimising Model 6.

    p:          Array of initials guess: [kex1, pb, dw, R2(i)]
    y:          Array of y values (list of arrays if global fit)
    x:          Array of x values (list of arrays if global fit)
    output:     Output object (textctrl), None if no output
    global_fit: Flag if it is a global fit
    freqs:      List of spectrometer frequencies (only in global fit; output in ppm) (wx.TextCtrl)
    B0:         List of static magnetic fields in Tesla (wx.TextCtrl)
    Y:          Gyromagnetic ratio MHz/T
    """

    # global fit
    if global_fit:
        # Number of datasets
        n = len(x)

        # Initialize error
        error = variance

        # error storage
        err = []

        # shared variables
        kex = p[0]
        pb = p[1]

        # Calculate chi2
        for i in range(0, n):
            # Parameters
            dw = p[(2*rep_index[i])+2]
            R2 = p[(2*i)+3]

            # dw on global fit ppm --> Hz
            dw_Hz = dw*float(freqs[i].GetValue()) * 2 * Pi

            # estimation
            p_est = [R2, kex, dw_Hz, pb]

            #Chi2 function
            err_tmp = ((y[i]-model_7(x[i], p_est))**2/error[i])

            # combine errors
            err.extend(err_tmp)

            # Gradients
            # R2
            if R2 < Constraints_container.r2[5][0] or R2 > Constraints_container.r2[5][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # kex
        if kex < Constraints_container.kex[5][0] or kex > Constraints_container.kex[5][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # dw
        elif dw < Constraints_container.dw[5][0] or dw > Constraints_container.dw[5][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # pb
        elif pb < Constraints_container.pb[5][0] or pb > Constraints_container.pb[5][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # Output
        elif output:
            limit_entries(output)
            wx.CallAfter(output.AppendText, 'R2o: ' + str(R2)[0:6] + ', kex: ' + str(kex) + ', dw: '+ str(dw) + ', pa: '+ str(1-pb) +'\n')
            time.sleep(0.001)

        Chi2_container.chi2 = err
        return err


def model_7(x, p):
        """Exchange for 2 sites over all time scales (pa >>pb)."""

        R20 = p[0]
        kex = p[1]
        dw = p[2]
        pb = p[3]
        pa = 1-pb
        tcp = 1/(2*x)

        # Phi
        phi = pa*pb*dw**2

        # R2eff
        R2eff = R20+((phi)/kex)*(1-(((4*x)/kex)*tanh((kex/(4*x)))))

        return R2eff


def model_7_residuals(p, y, x, variance, output=None, global_fit=False, freqs=None, rep_index=None):
    """Minimising Model 6.

    p:          Array of initials guess: [kex1, pb, dw, R2(i)]
    y:          Array of y values (list of arrays if global fit)
    x:          Array of x values (list of arrays if global fit)
    output:     Output object (textctrl), None if no output
    global_fit: Flag if it is a global fit
    freqs:      List of spectrometer frequencies (only in global fit; output in ppm) (wx.TextCtrl)
    B0:         List of static magnetic fields in Tesla (wx.TextCtrl)
    Y:          Gyromagnetic ratio MHz/T
    """

    # global fit
    if global_fit:
        # Number of datasets
        n = len(x)

        # Initialize error
        error = variance

        # error storage
        err = []

        # shared variables
        kex = p[0]
        pb = p[1]

        # Calculate chi2
        for i in range(0, n):
            # Parameters
            dw = p[(2*rep_index[i])+2]
            R2 = p[(2*i)+3]

            # dw on global fit ppm --> Hz
            dw_Hz = dw*float(freqs[i].GetValue()) * 2 * Pi

            # estimation
            p_est = [R2, kex, dw_Hz, pb]

            #Chi2 function
            err_tmp = ((y[i]-model_7(x[i], p_est))**2/error[i])

            # combine errors
            err.extend(err_tmp)

            # Gradients
            # R2
            if R2 < Constraints_container.r2[5][0] or R2 > Constraints_container.r2[5][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # kex
        if kex < Constraints_container.kex[5][0] or kex > Constraints_container.kex[5][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # dw
        elif dw < Constraints_container.dw[5][0] or dw > Constraints_container.dw[5][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # pb
        elif pb < Constraints_container.pb[5][0] or pb > Constraints_container.pb[5][1]:
                for j in range(0, len(err)):
                    err[j] = (err[j])*2

        # Output
        elif output:
            limit_entries(output)
            wx.CallAfter(output.AppendText, 'R2o: ' + str(R2)[0:6] + ', kex: ' + str(kex) + ', dw: '+ str(dw) + ', pa: '+ str(1-pb) +'\n')
            time.sleep(0.001)

        Chi2_container.chi2 = err
        return err
