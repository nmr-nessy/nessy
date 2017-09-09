#################################################################################
#                                                                               #
#   (C) 2010 Michael Bieri                                                      #
#   (C) 2013 Edward d'Auvergne                                                  #
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
import pylab
from random import random, uniform
from scipy import tanh, array, var, sqrt, cosh, arccosh
from scipy.optimize import leastsq
import time
import wx


# NESSY modules
from math_fns.models import model_1, model_1_residuals, model_2, model_2_residuals, model_3, model_3_residuals, model_4, model_4_residuals, model_5, model_5_residuals, model_6, model_6_residuals



def montecarlo(exp_index=0, exp_mode=0, mc_num=500, tolerance=1e-25, checkrun_label=None, isglobal=None, progressbar=None, report_panel=None, selected_models=None, Variance=None, X_values=None):
    """Function to perform Monte Carlo Simulations.

    exp_index                   Index of experiment (int)
    exp_mode                    Mode of experiment (CPMG: 1, On resonance: 2, Off resonance: 3) (int)
    mc_num                      Number of Monte Carlo simulations (int)
    tolerance                   Tolerance (float)
    checkrun_label              Panel displaying current action (wx.StaticText)
    isglobal                    Flag if global fit (Boolean)
    progressbar                 Prograssbar (wx.Gauge)
    report_panel                Report panel (wx.TextCtrl)
    selected_models             List of selected model (list of [Residue, Model, R2, kex, Rex, pb, dw])
    Variance                    List of variances per experiment (list)
    X_values                    List of x values per experiment (list)
    """


    # Functions
    # CPMG dispersion
    if exp_mode == 0:
        models_residuel = {'1':model_1_residuals, '2':model_2_residuals,  '3':model_3_residuals, '4':model_4_residuals, '5':model_5_residuals, '6':model_6_residuals}
        models = {'1':model_1, '2':model_2,  '3':model_3, '4':model_4, '5':model_5, '6':model_6}

    # Single fit
    if not isglobal:
        # Update Status
        if checkrun_label: wx.CallAfter(checkrun_label.SetLabel, 'Monte Carlo Simulation...')
        if report_panel: wx.CallAfter(report_panel.AppendText, '\n\n----------------------------------------------------------\nMonte Carlo Simulation\n----------------------------------------------------------\n\n')

        # Empty error container
        MODEL_SELECTION_ERROR = []

        # Monte Carlo Simulations
        n = mc_num  # Number of simulations

        # x-values
        x = []
        for x_value in range(0, len(X_values[exp_index])):
            if not float(X_values[exp_index][x_value]) == 0.0:   # exclude reference
                if not X_values[exp_index][x_value] == '':    # exclude empty datasets
                    x.append(float(X_values[exp_index][x_value]))

        # maximum number of entries
        max_entries = len(selected_models)

        # reser progress bar
        if progressbar: wx.CallAfter(progressbar.SetValue, 0)

        # loop over entries
        for entry in range(0, len(selected_models)):
            # empty error variables
            R2_err = []
            kex_err = []
            pb_err = []
            dw_err = []
            Phi_err = []
            kex2_err = []
            Phi2_err = []
            dw2_err = []
            pc_err = []

            # detect residue
            residue = selected_models[entry]['residue']
            residue_no = residue

            # detect model
            model = selected_models[entry]['model']

            # Calculated parameters
            p_calculated = selected_models[entry]['fit_params']

            # Error
            error = sqrt(Variance[exp_index][residue_no-1])

            # Monte Carlo Simulations
            for mc in range(0, n):
                y_sim = []

                # Feedback
                wx.CallAfter(report_panel.AppendText, 'Monte Carlo Simulation ' + str(mc+1) + ', Residue '+str(residue_no)+'\n' )
                time.sleep(0.001)


                #create noisy dataset
                for sim in range(0, len(x)):
                    y_sim.append(float(models[str(model)](x[sim], p_calculated)+uniform(-error, error)))

                # Fit
                fit = leastsq(models_residuel[str(model)], p_calculated, args=(array(y_sim), array(x), error, None, False), full_output = 1, col_deriv = 1, ftol = tolerance, xtol = tolerance, maxfev=20000000)

                # Model 1
                if model == 1:
                    # Save fits
                    R2_err.append(float(fit[0]))

                # Model 2
                if model == 2:
                    # Save fits
                    R2_err.append(fit[0][0])
                    Phi_err.append(fit[0][1])
                    kex_err.append(fit[0][2])

                # Model 3
                if model == 3:
                    # Save fits
                    R2_err.append(fit[0][0])
                    kex_err.append(fit[0][1])
                    dw_err.append(fit[0][2])
                    pb_err.append(fit[0][3])

                # Model 4
                if model == 4:
                    # Save fits
                    R2_err.append(fit[0][0])
                    Phi_err.append(fit[0][1])
                    kex_err.append(fit[0][2])
                    Phi2_err.append(fit[0][1])
                    kex2_err.append(fit[0][2])

                # Model 5
                if model == 5:
                    # Save fits
                    R2_err.append(fit[0][0])
                    kex_err.append(fit[0][1])
                    dw_err.append(fit[0][2])
                    pb_err.append(fit[0][3])
                    kex2_err.append(fit[0][4])
                    dw2_err.append(fit[0][5])
                    pc_err.append(fit[0][6])

                # Model 6
                if model == 6:
                    # Save fits
                    R2_err.append(fit[0][0])
                    kex_err.append(fit[0][1])
                    dw_err.append(fit[0][2])
                    pb_err.append(fit[0][3])


            # calculate and save errors
            # Model 1
            if model == 1:
                error_R2 = sqrt(var(R2_err, ddof = 1))

                # Save entries
                MODEL_SELECTION_ERROR.append({'residue':residue, 'R2':error_R2})

            # Model 2
            elif model == 2:
                error_R2 = sqrt(var(R2_err, ddof = 1))
                error_Phi = sqrt(var(Phi_err, ddof = 1))
                error_kex = sqrt(var(kex_err, ddof = 1))

                # calculate error of Rex
                Rex_err = []
                for calc_rex in range(0, len(kex_err)):
                    rex_tmp = Phi_err[calc_rex] / kex_err[calc_rex]
                    Rex_err.append(rex_tmp)
                error_Rex = sqrt(var(Rex_err, ddof = 1))

                # Save entries
                MODEL_SELECTION_ERROR.append({'residue':residue, 'R2':error_R2, 'Phi':error_Phi, 'kex':error_kex, 'Rex':error_Rex})

            # Model 3
            elif model == 3:
                error_R2 = sqrt(var(R2_err, ddof = 1))
                error_kex = sqrt(var(kex_err, ddof = 1))
                error_dw = sqrt(var(dw_err, ddof = 1))
                error_pb = sqrt(var(pb_err, ddof = 1))

                # calculate error of Rex
                Rex_err = []
                for calc_rex in range(0, len(kex_err)):
                    rex_tmp = (pb_err[calc_rex] * (1-pb_err[calc_rex]) * kex_err[calc_rex] * (dw_err[calc_rex]**2)) / ((kex_err[calc_rex]**2) + (dw_err[calc_rex]**2))
                    Rex_err.append(rex_tmp)
                error_Rex = sqrt(var(Rex_err, ddof = 1))

                # Save entry
                MODEL_SELECTION_ERROR.append({'residue':residue, 'R2':error_R2, 'kex':error_kex, 'Rex':error_Rex, 'pb':error_pb, 'dw':error_dw})

            # Model 4
            elif model == 4:
                error_R2 = sqrt(var(R2_err, ddof = 1))
                error_Phi = sqrt(var(Phi_err, ddof = 1))
                error_kex = sqrt(var(kex_err, ddof = 1))
                error_Phi2 = sqrt(var(Phi2_err, ddof = 1))
                error_kex2 = sqrt(var(kex2_err, ddof = 1))

                # kex mean
                error_kex_mean = error_kex + error_kex2

                # calculate error of Rex
                Rex_err = []
                for i in range(len(Phi_err)):
                    # Rex 1
                    rex1 = Phi_err[i] / kex_err[i]

                    # Rex 2
                    rex2 = Phi2_err[i] / kex2_err[i]

                    # Store rex
                    Rex_err.append(rex1+rex2)

                # Calculate error of Rex
                error_Rex = sqrt(var(Rex_err, ddof = 1))

                # Save entries
                MODEL_SELECTION_ERROR.append({'residue': residue, 'R2': error_R2, 'Phi': error_Phi, 'kex': error_kex_mean, 'kex1': error_kex, 'Rex': error_Rex, 'Phi2': error_Phi2, 'kex2': error_kex2,})

            # Model 5
            elif model == 5:
                error_R2 = sqrt(var(R2_err, ddof = 1))
                error_kex = sqrt(var(kex_err, ddof = 1))
                error_dw = sqrt(var(dw_err, ddof = 1))
                error_pb = sqrt(var(pb_err, ddof = 1))
                error_kex2 = sqrt(var(kex_err, ddof = 1))
                error_dw2 = sqrt(var(dw_err, ddof = 1))
                error_pc = sqrt(var(pb_err, ddof = 1))

                # kex mean
                error_kex_mean = error_kex + error_kex2

                # calculate error of Rex
                Rex_err = []
                for calc_rex in range(0, len(kex_err)):
                    # values
                    pb = pb_err[calc_rex]
                    pc = pc_err[calc_rex]
                    pa = 1 - pb - pc
                    dw1 = dw_err[calc_rex]
                    dw2 = dw2_err[calc_rex]
                    kex1 = kex_err[calc_rex]
                    kex2 = kex2_err[calc_rex]

                    rex_tmp1 = ((pa+pc)*(pb)*(dw1**2)*kex1)/(kex1**2 + dw1**2)
                    rex_tmp2 = ((pa+pb)*(pc)*(dw2**2)*kex2)/(kex2**2 + dw2**2)

                    Rex_err.append(rex_tmp1+rex_tmp2)

                error_Rex = sqrt(var(Rex_err, ddof = 1))

                # Save entry
                MODEL_SELECTION_ERROR.append({'residue':residue, 'R2':error_R2, 'kex':error_kex_mean, 'kex1':error_kex, 'kex2':error_kex2, 'Rex':error_Rex, 'pb':error_pb, 'dw':error_dw, 'pc':error_pc, 'dw2':error_dw2})

            # Model 6
            elif model == 6:
                error_R2 = sqrt(var(R2_err, ddof = 1))
                error_kex = sqrt(var(kex_err, ddof = 1))
                error_dw = sqrt(var(dw_err, ddof = 1))
                error_pb = sqrt(var(pb_err, ddof = 1))

                # calculate error of Rex
                Rex_err = []
                for calc_rex in range(0, len(kex_err)):
                    rex_tmp = (pb_err[calc_rex] * (1-pb_err[calc_rex]) * kex_err[calc_rex] * (dw_err[calc_rex]**2)) / ((kex_err[calc_rex]**2) + (dw_err[calc_rex]**2))
                    Rex_err.append(rex_tmp)
                error_Rex = sqrt(var(Rex_err, ddof = 1))

                # Save entry
                MODEL_SELECTION_ERROR.append({'residue':residue, 'R2':error_R2, 'kex':error_kex, 'Rex':error_Rex, 'pb':error_pb, 'dw':error_dw})

            # update progress bar
            per = 100*entry/max_entries
            if progressbar: wx.CallAfter(progressbar.SetValue, per)

    # Return results
    return MODEL_SELECTION_ERROR

