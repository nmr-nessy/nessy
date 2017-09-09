#################################################################################
#                                                                               #
#   (C) 2010 Michael Bieri                                                      #
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


# Collection of n-states models

# Python modules
from scipy import tanh, sqrt, cosh, arccosh, cos, array
import time
import wx

# NESSY modules
from math_fns.models import limit_entries
from elements.variables import Pi




def minimize_fast(p, x, y, variance, state, output=None, global_fit=False, freqs=None):
    # Global fit
    if global_fit:
        # output text
        text = ''

        # Number of datasets
        n = len(x)

        # Initialize error
        error = variance

        # error storage
        err = []

        # loop over experiment
        for exp in range(n):

            # container for parameters
            p_est = []

            # R2
            R2 = p[len(p)-(n-exp)]
            text = text + '\nR2_'+str(exp+1)+': '+str(R2)[0:8]

            # Append Phi and kex if not 1 state model
            if state > 1:

                # Read parameters for experiment
                for st in range(2, state+1):
                    # append Phi
                    Phi = p[2 * (state-2)] * (2 * Pi * float(freqs[exp].GetValue()))**2
                    p_est.append(Phi)
                    text = text + ', Phi_'+str(exp+1)+str(st)+': '+str(Phi)[0:8]

                    # append Kex
                    p_est.append(p[2 * (state-2) + 1])
                    text = text + ', kex_'+str(exp+1)+str(st)+': '+str(p[2 * (state-2) + 1])[0:8]

            # append R2
            p_est.append(R2)

            # Chi2
            err_tmp = ((model_fast(x[exp], state, p_est)-y[exp])/error[exp])**2

            # combine errors
            err.extend(err_tmp)

            # Gradients
            # R2
            if R2 < 0:
                for j in range(0, len(err)):
                    err[j] = (1+err[j])**2
            if R2 > 50:
                for j in range(0, len(err)):
                    err[j] = (1+err[j])**2

            # No negative values
            for neg in range(len(p_est)):
                if p_est[neg] < 0:
                    for j in range(0, len(err)):
                        err[j] = (1+err[j])**2

        # Output
        if output:
            limit_entries(output)
            wx.CallAfter(output.AppendText, text + '\n')
            time.sleep(0.001)

        # return error
        return err

    # Individual fit
    else:
        # Initialize error
        error = variance

        # Chi2 function
        err = ((model_fast(x, state, p)-y)/error)**2

        # Constrain that no neg values
        for i in range(0, len(p)):
            if p[i] < 0:
                err = (1+err)**2

        if output:
            limit_entries(output)
            text = str(state)+' state model:\nR2o: ' + str(p[len(p)-1])
            for i in range(0, state-1):
                text = text + ', Phi'+str(i+1)+': ' + str(p[(i * 2) + 0]) + ', kex'+str(i+1)+': '+ str(p[(i * 2) + 1])
            wx.CallAfter(output.AppendText, text + '\n')
            time.sleep(0.001)
        return err


def minimize_slow(p, x, y, variance, state, output=None, global_fit=False, freqs=None):
    # Global fit
    if global_fit:
        # output text
        text = ''

        # increase error
        raise_error = False

        # Number of datasets
        n = len(x)

        # Initialize error
        error = variance

        # error storage
        err = []

        # loop over experiment
        for exp in range(n):

            # container for parameters
            p_est = []
            px = []
            dwx = []

            # R2
            R2 = p[len(p)-(n-exp)]
            text = text + '\nR2_'+str(exp+1)+': '+str(R2)[0:8]
            if R2 > 50 or R2 < 0:
                raise_error = True

            # Append Phi and kex if not 1 state model
            if state > 1:

                # Read parameters for experiment
                for st in range(2, state+1):
                    # append kex
                    kex = p[(state-2) * 3]
                    p_est.append(kex)
                    text = text + ', kex_'+str(exp+1)+str(st)+': '+str(kex)[0:8]
                    if kex < 0:
                        raise_error = True

                    # append dw and convert ppm to Hz
                    dw = p[(state-2) * 3 + 1]*float(freqs[exp].GetValue())* 2 * Pi
                    p_est.append(dw)
                    dwx.append(dw/(float(freqs[exp].GetValue()))* 2 * Pi)   # ppm
                    text = text + ', dw_'+str(exp+1)+str(st)+': '+str(dw/(float(freqs[exp].GetValue())*2*Pi))[0:8]
                    if dw < 0:
                        raise_error = True

                    # append pb
                    pb = p[(state-2) * 3 + 2]
                    p_est.append(pb)
                    px.append(pb)
                    text = text + ', p'+str(st)+'_'+str(exp+1)+': '+str(pb)[0:8]
                    if pb < 0:
                        raise_error = True
                    if pb > 0.5:
                        raise_error = True

            # append R2
            p_est.append(R2)

            # Chi2
            err_tmp = ((model_slow(x[exp], state, p_est)-y[exp])/error[exp])**2

            # combine errors
            err.extend(err_tmp)

            # If something was previously detected
            if raise_error:
                for j in range(0, len(err)):
                        err[j] = (1+err[j])**2

                # reset error flag
                raise_error = False

        # Gradients
        # pa is major population
        pa = 1 - sum(px)

        # pa is major population
        if pa < sum(px):
            for j in range(0, len(err)):
                err[j] = (1+err[j])**2

        # compare each population
        for i in range(len(px)):
            if pa < px[i]:
                for j in range(0, len(err)):
                    err[j] = (1+err[j])**2

        # compare dwx
        # loop over dw
        if state > 1:
            dw_mean = sum(dwx)/len(dwx)
            for i in range(len(dwx)):
                if not dwx[i] > (dwx[i] + (0.1*dwx[i])) or not dwx[i] < (dwx[i] - (0.1*dwx[i])):  # allow 10% of error
                    for j in range(0, len(err)):
                        err[j] = (1+err[j])**2

        # Output
        if output:
            limit_entries(output)
            wx.CallAfter(output.AppendText, text + '\n')
            time.sleep(0.001)

        # return error
        return err

    # single fit
    else:
        # Initialize error
        error = variance

        #Chi2 function
        err = ((model_slow(x, state, p)-y)/error)**2

        # Constrain that no neg values
        for i in range(0, len(p)):
            if p[i] < 0:
                err = (1+err)**2

        if output:
            limit_entries(output)
            text = str(state)+' state model:\nR2o: ' + str(p[len(p)-1])
            for i in range(0, state-1):
                text = text + ', kex'+str(i+1)+': ' + str(p[(i * 3) + 0]) + ', dw'+str(i+1)+': '+ str(p[(i * 3) + 1])+ ', p'+str(i+1)+': '+ str(p[(i * 3) + 2])[0:4]
            wx.CallAfter(output.AppendText, text + '\n')
            time.sleep(0.001)
        return err



def model_fast(x, state, p):
        """N-state model.

        state:  Number of states
        p:      parameters: [Phi, kex, ..... , R2]
        """

        if state == 1:
            # R2
            R2 = p[0]
            return R2

        else:
            # R2
            R2 = p[len(p)-1]

            # Phi
            phi = []
            for i in range(0, state-1):
                phi.append(p[(i * 2) + 0])

            # kex
            kex = []
            for i in range(0, state-1):
                kex.append(p[(i * 2) + 1])


            # N state model
            Rex = 0
            for i in range (0, len(phi)):
                Rex = Rex + ((phi[i])/kex[i])*(1-(((4*x)/kex[i])*tanh((kex[i]/(4*x)))))

            # R2eff
            R2eff = R2 + Rex

            return R2eff


def model_slow(x, state, p):
        """Slow exchange for n sites."""

        if state == 1:
            # R2
            R2 = p[0]
            return R2

        else:
            # R2
            R2 = p[len(p)-1]

            # Phi
            kex = []
            for i in range(0, state-1):
                kex.append(p[(i * 3) + 0])

            # dw
            dw = []
            for i in range(0, state-1):
                dw.append(p[(i * 3) + 1])

            # px
            px = []
            for i in range(0, state-1):
                px.append(p[(i * 3) + 2])

            # N state model
            Rex = 0
            for i in range (0, state-1):

                # current population
                p_current = px[i]

                # remaining populations
                p_sum = 1 - p_current

                # Psi
                Psi = kex[i]**2 - dw[i]**2

                # Xi
                xi = (-2) * dw[i] * ( ((p_sum)*kex[i]) - (p_current*kex[i]) )

                # D+
                Dpos = 0.5 * ( 1 + ( (Psi + 2*dw[i]**2) / (Psi**2 + xi**2)**(0.5) ) )

                # D-
                Dneg = 0.5 * ( ( (Psi + 2*dw[i]**2) / (Psi**2 + xi**2)**(0.5) ) - 1 )

                # Eta+
                etapos = (Psi + (Psi**2 + xi**2)**(0.5) )**(0.5)   /    (2 * sqrt(2) * x)

                # Eta-
                etaneg = ( (Psi**2 + xi**2)**(0.5) - Psi)**(0.5)   /    (2 * sqrt(2) * x)

                # Calculate Rex
                Rex = Rex + ((kex[i]/2) - (x * (arccosh((Dpos*cosh(etapos)) - (Dneg)*cos(etaneg)))))

            # Calculate R2eff
            R2eff = R2 + Rex

            # Return
            return R2eff
