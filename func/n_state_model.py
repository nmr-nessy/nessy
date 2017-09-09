#################################################################################
#                                                                               #
#   (C) 2011 Michael Bieri                                                      #
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

# Python modules
from os import sep
import os
import pylab
from scipy.optimize import leastsq
import sys
from scipy import sqrt, array, linspace
try:
    import thread as _thread
except ImportError:
    import _thread
import time
import wx

# NESSY modules
from conf.path import NESSY_PIC, N_STATE_FORMULA, N_STATE_FORMULA_SLOW, IMPORT_DATA_SIDE_PIC
from conf.message import question, message
from func.r2eff import R2_eff
from func.pooled_variance import Pooled_variance
from math_fns.tests import AICc
from math_fns.n_state import minimize_fast, minimize_slow, model_fast, model_slow
from elements.variables import Pi




class N_state_model(wx.Frame):
    """Calculate N-state model.

                        ___
                       \
        R2eff = R20 +   |   Rex
                       /___
                       i = 2
        """


    def __init__(self, main, model, *args, **kwds):
        # assign parameters
        self.main = main

        # running flag
        self.running = False

        # Detect model
        self.exchange_type = model
        if model == 'fast':
            self.title = 'n-States Model Fast Exchange'
            self.formula_pic = N_STATE_FORMULA
        else:
            self.title = 'n-States Model Slow Exchange'
            self.formula_pic = N_STATE_FORMULA_SLOW

        # Create Window
        kwds["style"] = wx.CAPTION
        wx.Frame.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        # Build Elements
        self.build()


    def build(self):
        # Image
        self.topsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(IMPORT_DATA_SIDE_PIC, wx.BITMAP_TYPE_ANY))
        self.topsizer.Add(self.bitmap, 0, wx.ALL, 5)

        # Mainsizer
        mainsizer = wx.BoxSizer(wx.VERTICAL)

        # Header
        self.header = wx.StaticText(self, -1, self.title)
        self.header.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        mainsizer.Add(self.header, 0, wx.ALL|wx.ALIGN_LEFT, 5)

        # Line
        self.static_line_2 = wx.StaticLine(self, -1)
        mainsizer.Add(self.static_line_2, 0, wx.EXPAND, 0)

        # Formula
        self.formula = wx.StaticBitmap(self, -1, wx.Bitmap(self.formula_pic, wx.BITMAP_TYPE_ANY))
        mainsizer.Add(self.formula, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)

        # Line
        self.static_line_1 = wx.StaticLine(self, -1)
        mainsizer.Add(self.static_line_1, 0, wx.EXPAND, 0)

        # Residues
        sizer_resi = wx.BoxSizer(wx.HORIZONTAL)
        self.label_resi = wx.StaticText(self, -1, "Include residues:")
        self.label_resi.SetMinSize((150, 17))
        sizer_resi.Add(self.label_resi, 0, 0, 0)

        self.residues = wx.ListBox(self, -1, choices=self.read_resi(), style = wx.LB_MULTIPLE)
        self.residues.SetMinSize((150, 150))
        self.residues.SetSelection(0)
        sizer_resi.Add(self.residues, 0, 0, 0)

        self.button_all = wx.Button(self, -1, "Select all")
        self.Bind(wx.EVT_BUTTON, self.select_all, self.button_all)
        sizer_resi.Add(self.button_all, 0, 0, 0)
        mainsizer.Add(sizer_resi, 1, wx.ALL|wx.EXPAND, 5)

        # Limit
        sizer_state = wx.BoxSizer(wx.HORIZONTAL)
        self.label_state = wx.StaticText(self, -1, "Limit of states:")
        self.label_state.SetMinSize((150, 17))
        sizer_state.Add(self.label_state, 0, 0, 0)

        self.no_states = wx.SpinCtrl(self, -1, "5", min=2, max=9)
        sizer_state.Add(self.no_states, 0, 0, 0)
        mainsizer.Add(sizer_state, 0, wx.ALL, 5)

        # Model selection
        sizer_selection = wx.BoxSizer(wx.HORIZONTAL)
        self.label_selection = wx.StaticText(self, -1, "Model-selection:")
        self.label_selection.SetMinSize((150, 17))
        sizer_selection.Add(self.label_selection, 0, 0, 0)

        self.aicc_box = wx.RadioButton(self, -1, "AICc")
        self.no_sele = wx.RadioButton(self, -1, "no selection")
        sizer_selection.Add(self.aicc_box, 0, 0, 0)
        sizer_selection.Add(self.no_sele, 0, wx.LEFT, 10)
        mainsizer.Add(sizer_selection, 0, wx.ALL, 5)

        # Buttons
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.button_start = wx.Button(self, -1, "Start calculation")
        self.Bind(wx.EVT_BUTTON, self.start, self.button_start)
        sizer_buttons.Add(self.button_start, 0, 0, 0)

        self.button_kill = wx.Button(self, -1, "Stop and kill")
        self.Bind(wx.EVT_BUTTON, self.kill, self.button_kill)
        self.button_kill.Enable(False)
        sizer_buttons.Add(self.button_kill, 0, 0, 0)

        self.button_close = wx.Button(self, -1, "Close")
        self.Bind(wx.EVT_BUTTON, self.close, self.button_close)
        sizer_buttons.Add(self.button_close, 0, 0, 0)
        mainsizer.Add(sizer_buttons, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)

        # Pack dialog
        self.topsizer.Add(mainsizer, 0, 0, 0)
        self.SetSizer(self.topsizer)
        self.topsizer.Fit(self)
        self.Layout()
        self.Center()


    def calc(self, residue_index):
        """Controlls the n-state model calculation."""
        # max number of states
        max_states = int(self.no_states.GetValue())

        # Data container
        n_state_storage = []        # [residue, no_states, fit_parameters, [Rex, kex], chi2, AICc]

        # Loop over states
        for i in range(1, max_states+1):
            # x and y values
            x = []
            y = []

            # Individual fit
            if not self.globalfit:
                for entry in range(0, len(self.main.R2eff[residue_index])):
                    if not self.main.R2eff[residue_index][entry] == None:
                        y.append(self.main.R2eff[residue_index][entry])
                        x.append(float(self.main.CPMGFREQ[0][entry]))

            # Global fit
            else:
                # loop over experiments
                for exp in range(len(self.R2effs)):
                    # increase datasets
                    x.append([])
                    y.append([])

                    # Loop over data
                    for data in range(len(self.R2effs[exp][residue_index])):
                        if not self.R2effs[exp][residue_index][data] == None:
                            y[exp].append(self.R2effs[exp][residue_index][data])
                            x[exp].append(float(self.main.CPMGFREQ[exp][data]))

            # abort if no x values
            if [] in x or x == []:
                continue

            # Report start of analysis
            wx.CallAfter(self.main.report_panel.AppendText, '\n\nCurve fit n-State Model to Residue ' + str(residue_index + 1)+': '+str(i)+' states\n\n')
            wx.CallAfter(self.main.checkrun_label.SetLabel, str(i)+'-state model, residue '+str(residue_index + 1))

            # Fast exchange
            if self.exchange_type == 'fast':
                # Global fit
                if self.globalfit:
                    # Original Values
                    R2 = self.main.INI_R2
                    Phi = self.main.INI_phi_global
                    kex = self.main.INI_kex_fast

                    # Block for one state
                    single_block = [Phi, kex]

                    # Multiply block for each state
                    block = single_block
                    if i > 2:
                        for state in range(i-1):
                            block = block + single_block

                    # Add R2 for each experiment to single block
                    for exp in range(len(x)):
                        block.append(R2)

                    # 1 state
                    if i == 1:
                        block = [R2] * len(x)

                    # Create variance and convert x, y values to arrays
                    variance = []
                    for exp_no in range(len(x)):  # loop over experiments
                        # convert to arrays
                        x[exp_no]=array(x[exp_no])
                        y[exp_no]=array(y[exp_no])

                        # Collect variance
                        variance.append(self.Variances[exp_no][residue_index])

                    # Minimise
                    model_fit = leastsq(minimize_fast, block, args=((x), (y), variance, i, self.main.report_panel, True, self.main.spec_freq), full_output = 1, col_deriv = 1, ftol = 1.49012e-08, xtol = 1.49012e-08, maxfev=200000)

                # Individual fit
                else:
                    # Original Values
                    R2 = self.main.INI_R2
                    Phi = self.main.INI_phi
                    kex = self.main.INI_kex_fast

                    # Block for one state
                    single_block = [Phi, kex]

                    # Multiply block for each state
                    block = single_block
                    if i > 2:
                        for state in range(i-1):
                            block = block + single_block

                    # Add R2
                    block.append(R2)

                    # 1 state
                    if i == 1:
                        block = [R2]

                    # Minimise
                    model_fit = leastsq(minimize_fast, block, args=(array(x), array(y), self.main.R2eff_variance[0][residue_index], i, self.main.report_panel), full_output = 1, col_deriv = 1, ftol = 1.49012e-08, xtol = 1.49012e-08, maxfev=200000)

            # slow exchange
            if self.exchange_type == 'slow':
                # Global fit
                if self.globalfit:
                    # Original Values
                    R2 = self.main.INI_R2
                    dw = self.main.INI_dw_global
                    pb = self.main.INI_pb
                    kex = self.main.INI_kex_slow

                    # Block for one state
                    single_block = [kex, dw, pb]

                    # Multiply block for each state
                    block = single_block
                    if i > 2:
                        for state in range(i-1):
                            block = block + single_block

                    # Add R2 for each experiment to single block
                    for exp in range(len(x)):
                        block.append(R2)

                    # 1 state
                    if i == 1:
                        block = [R2] * len(x)

                    # Create variance and convert x, y values to arrays
                    variance = []
                    for exp_no in range(len(x)):  # loop over experiments
                        # convert to arrays
                        x[exp_no]=array(x[exp_no])
                        y[exp_no]=array(y[exp_no])

                        # Collect variance
                        variance.append(self.Variances[exp_no][residue_index])

                    # Minimise
                    model_fit = leastsq(minimize_slow, block, args=((x), (y), variance, i, self.main.report_panel, True, self.main.spec_freq), full_output = 1, col_deriv = 1, ftol = 1.49012e-08, xtol = 1.49012e-08, maxfev=200000)

                # Individual fit
                else:
                    # Original Values
                    R2 = self.main.INI_R2
                    dw = self.main.INI_dw
                    pb = self.main.INI_pb
                    kex = self.main.INI_kex_slow

                    # Block for one state
                    single_block = [kex, dw, pb]

                    # Multiply block for each state
                    block = single_block
                    if i > 2:
                        for state in range(i-1):
                            block = block + single_block

                    # Add R2 for each experiment to single block
                    block.append(R2)

                    # 1 state
                    if i == 1:
                        block = [R2]

                    # Minimise
                    model_fit = leastsq(minimize_slow, block, args=(array(x), array(y), self.main.R2eff_variance[0][residue_index], i, self.main.report_panel), full_output = 1, col_deriv = 1, ftol = 1.49012e-27, xtol = 1.49012e-27, maxfev=20000000)

            # Workaround if 1 state
            if i == 1 and not self.globalfit:
                tmp = model_fit
                model_fit = []

                # first entry is list
                model_fit.append([tmp[0]])

                # loop over model_fit
                for l in range(1, len(tmp)):
                    model_fit.append(tmp[l])

            # Chi2 and AICc
            self.chi2_calc(i, model_fit, residue_index, x, y, i)

            # Number of parameters
            # number of experiments
            n_exp = 1
            if self.globalfit:
                n_exp = len(x)

            # fast exchange
            if self.exchange_type == 'fast':
                k = len(model_fit[0]) + 1       # no. Phi + no. kex + R2
            # slow exchaneg
            if self.exchange_type == 'slow':
                k = len(model_fit[0]) +1    # no. kex + no. dw + no. pb + R2

            # Number of Datapoints
            n = 0
            for no in range(0, len(self.main.CPMGFREQ[0])):
                if not self.main.CPMGFREQ[0][no] == '':
                    n = n + 1
            if self.globalfit:
                n = 2*n
            self.aicc = AICc(self.chi2, k, n)

            # Plot
            if self.globalfit:
                p = self.p_global
            else:
                p = model_fit[0]
            self.plot(x, y, residue_index, i, p)

            # Create CSV file
            self.csv(residue_index, i, p, self.chi2, self.aicc)

            # store
            n_state_storage.append([residue_index+1, i, model_fit[0], self.rex_kex(model_fit[0], self.exchange_type), self.chi2, self.aicc])

        # store
        self.n_state_storage.append(n_state_storage)

        # Disable killing of NESSY
        self.button_kill.Enable(False)
        self.running = False
        self.button_start.Enable(False)


    def chi2_calc(self, i, model_fit, residue_index, x, y, state):
        """
        i:              State index
        model_fit:      Solution array of least square minimisation
        residue_index:  Index of current residue
        """

        # global fit
        if self.globalfit:
                # Create global fit parameter container
                self.p_global = []

                # number of experiments
                n = len(x)

                # loop over experiments
                for exp in range(len(x)):
                    # extract values
                    x_values = x[exp]
                    y_real = y[exp]
                    y_estimated = []

                    # extract p
                    p = model_fit[0]

                    # Fast exchange
                    if self.exchange_type == 'fast':
                        # container for parameters
                        p_est = []

                        # R2
                        R2 = p[len(p)-(n-exp)]

                        # Append Phi and kex if not 1 state model
                        if state > 1:

                            # Read parameters for experiment
                            for st in range(2, state+1):
                                # append Phi
                                Phi = p[2 * (state-2)] * (float(self.main.spec_freq[exp].GetValue())*2*Pi)**2
                                p_est.append(Phi)

                                # append Kex
                                p_est.append(p[2 * (state-2) + 1])

                        # append R2
                        p_est.append(R2)

                        # Store in global fit container
                        self.p_global.append(p_est)

                        # Calculate fit
                        for t in range(0, len(x_values)):
                            if self.exchange_type == 'fast':
                                if state == 1:
                                    y_estimated.append(model_fast(x_values[t], i, p_est))
                                else:
                                    y_estimated.append(model_fast(x_values[t], i, p_est))

                        # Calculate Chi2
                        self.chi2 = sum((array(y_real) - array(y_estimated))**2/self.Variances[exp][residue_index])

                    # Slow exchange
                    if self.exchange_type == 'slow':
                        # container for parameters
                        p_est = []

                        # R2
                        R2 = p[len(p)-(n-exp)]

                        # Append Phi and kex if not 1 state model
                        if state > 1:

                            # Read parameters for experiment
                            for st in range(2, state+1):
                                # append kex
                                kex = p[(state-2) * 3]
                                p_est.append(kex)

                                # append dw and convert ppm to Hz
                                dw = p[(state-2) * 3 + 1]*float(self.main.spec_freq[exp].GetValue())*2*Pi
                                p_est.append(dw)

                                # append pb
                                pb = p[(state-2) * 3 + 2]
                                p_est.append(pb)

                        # append R2
                        p_est.append(R2)

                        # Store in global fit container
                        self.p_global.append(p_est)

                        # Calculate fit
                        for t in range(0, len(x_values)):
                            if self.exchange_type == 'slow':
                                if state == 1:
                                    y_estimated.append(model_slow(x_values[t], i, p_est))
                                else:
                                    y_estimated.append(model_slow(x_values[t], i, p_est))

                        # Calculate Chi2
                        self.chi2 = sum((array(y_real) - array(y_estimated))**2/self.Variances[exp][residue_index])

        # Individual fit
        else:
                y_real = array(y)
                y_estimated = []

                for t in range(0, len(x)):
                    # Fast exchange
                    if self.exchange_type == 'fast':
                        y_estimated.append(model_fast(x[t], i, model_fit[0]))
                    # slow exchaneg
                    if self.exchange_type == 'slow':
                        y_estimated.append(model_slow(x[t], i, model_fit[0]))
                self.chi2 = sum((y_real - y_estimated)**2/self.main.R2eff_variance[0][residue_index])


    def close(self, event):
        self.Destroy()


    def csv(self, residue_index, model, fit_params, chi2, aicc):
        """ Create CSV file.

        residue_index:          Residue number - 1 (Index of residue)
        model:                  Number of states
        fit_params:             Parameters of least square fit (list, or list of list for global fit)
        """

        # prefix if global fit
        prefix = ''
        if self.globalfit:
            prefix = 'Global_'

        # Folders
        residue_name = str(residue_index+1)+'_'+str(self.main.data_grid[0].GetCellValue(residue_index, 0))
        folder = str(self.main.proj_folder.GetValue())+sep+'n_states_plots'

        # Filename
        filename = residue_name+'_'+str(model)+'_states_'+self.exchange_type
        # craete folder, if not present
        try:
            os.makedirs(folder+sep+'csv')
        except:
            a = 'nothing happens'

        # Filename
        filename_csv = folder+sep+'csv'+sep+prefix+filename+'.csv'

        # open file
        file = open(filename_csv, 'w')

        # write header
        if self.globalfit:
            file.write('Parameter')
            # loop over experiment
            for exp in range(len(fit_params)):
                file.write(';Experiment '+str(exp+1))
        else:
            file.write('Parameter;Experiment 1')
        file.write('\n')

        # Dictionaries
        label_fast = {'0':'Phi', '1':'kex'}
        label_slow = {'0':'kex', '1':'dw', '2':'p'}

        # Write entries
        param = 0
        state = 1

        # loop over parameters
        exps = len(fit_params)-1
        if self.globalfit:
            exps =len(fit_params[0])-1

        for i in range(exps):  # exclude R2
            # fast exchange
            if self.exchange_type == 'fast':


                # Write entry
                if self.globalfit:
                    # reset param
                    if param == 2:
                        param = 0

                        # set next state
                        state = state + 1

                    # write Parameter
                    file.write(label_fast[str(param)]+'_'+str(state))

                    # loop over experiment
                    for exp in range(len(fit_params)):
                        file.write(';'+str(fit_params[exp][i]))

                    # New line
                    file.write('\n')

                # individual fit
                else:
                    # reset param
                    if param == 2:
                        param = 0

                        # set next state
                        state = state + 1

                    # write
                    file.write(label_fast[str(param)]+'_'+str(state)+';'+str(fit_params[i])+'\n')

            # Slow exchange
            if self.exchange_type == 'slow':


                # Write entry
                if self.globalfit:
                    # reset param
                    if param == 3:
                        param = 0

                        # set next state
                        state = state + 1

                    # write Parameter
                    file.write(label_slow[str(param)]+'_'+str(state))

                    # loop over experiment
                    for exp in range(len(fit_params)):
                        file.write(';'+str(fit_params[exp][i]))

                    # New line
                    file.write('\n')

                # individual fit
                else:
                    # reset param
                    if param == 3:
                        param = 0

                        # set next state
                        state = state + 1

                    # write
                    file.write(label_slow[str(param)]+'_'+str(state)+';'+str(fit_params[i])+'\n')

            # increase param
            param = param + 1

        # add r2
        if self.globalfit:
            file.write('R2')
            # loop over experiments
            for exp in range(len(fit_params)):
                file.write(';'+str(fit_params[exp][len(fit_params[exp])-1]))
        else:
            file.write('R2;'+str(fit_params[len(fit_params)-1]))

        # Chi2 and AICc
        file.write('\n\nChi2;'+str(chi2)+'\nAICc;'+str(aicc))

        # close file
        file.close()

        # add file to results tree
        self.main.tree_results.AppendItem (self.main.txt, filename_csv, 0)

        # save entry
        self.main.results_txt.append(filename_csv)


    def kill(self, event):
        if not self.running:
            return

        q = question('Abort calculation and kill NESSY session?', self)
        if q:
            sys.exit()


    def plot(self, x, y, residue_index, model, model_fit):
        """Plotting the models."""
        # prefix if global fit
        prefix = ''
        if self.globalfit:
            prefix = 'Global_'

        # Colors for plot
        colors = ['BLUE', 'RED', 'GREEN', 'YELLOW', 'CYAN', 'GOLD', 'MAGENTA', 'NAVY', 'ORANGE', 'PINK', 'PURPLE', 'BLACK', 'GRAY']

        # Folders
        residue_name = str(residue_index+1)+'_'+str(self.main.data_grid[0].GetCellValue(residue_index, 0))
        folder = str(self.main.proj_folder.GetValue())+sep+'n_states_plots'

        # Filename
        filename = residue_name+'_'+str(model)+'_states_'+self.exchange_type

        # Create Folders
        try:
            os.mkdir(folder)
        except:
            a = 'nothing happens'
        try:
            os.mkdir(folder+sep+'png')
        except:
            a = 'nothing happens'
        try:
            os.mkdir(folder+sep+self.main.PLOTFORMAT.replace('.', ''))
        except:
            a = 'nothing happens'

        # Frame width
        params={'axes.linewidth' : self.main.FRAMEWIDTH}
        pylab.rcParams.update(params)

        # detect maximum frequency
        max = 0
        for i in range(0, len(self.main.CPMGFREQ[0])):
            try:
                if int(self.main.CPMGFREQ[0][i]) > max:
                    max = int(self.main.CPMGFREQ[0][i])

            # empty data sets
            except:
                break

        # add extra border in graph
        max = max + (0.1*max)

        # Plots for global fit
        if self.globalfit:
            # loop over experiments
            for exp in range(len(x)):
                # Plot datapoints
                pylab.errorbar(x[exp], y[exp], yerr = sqrt(self.Variances[exp][residue_index]), color=colors[exp], fmt ='o')

                # Create fit
                x_fit = linspace(0, max, num=100)
                y_fit = []
                for value in range(0, len(x_fit)):
                    # fast exchange
                    if self.exchange_type == 'fast':
                        y_fit.append(model_fast(x_fit[value], model, model_fit[exp]))
                    # slow exchange
                    if self.exchange_type == 'slow':
                        y_fit.append(model_slow(x_fit[value], model, model_fit[exp]))

                # Plot fit
                pylab.plot(x_fit, y_fit, '-', color=colors[exp])

        # Single fit
        else:
            # Calculate fit
            x_fit = linspace(0, max, num=100)
            y_fit = []
            for value in range(0, len(x_fit)):
                # fast exchange
                if self.exchange_type == 'fast':
                    y_fit.append(model_fast(x_fit[value], model, model_fit))
                # slow exchange
                if self.exchange_type == 'slow':
                    y_fit.append(model_slow(x_fit[value], model, model_fit))

            # Data points
            pylab.errorbar(x, y, yerr = sqrt(self.main.R2eff_variance[0][residue_index]), fmt ='ko')

            # Fit
            pylab.plot(x_fit, y_fit, 'k-', label = 'Curve fit '+str(model)+'-state Model')

        # Create plot
        pylab.xlabel('v(CPMG) [Hz]', fontsize=19, weight='bold')
        pylab.ylabel('R2eff [rad/s]', fontsize=19, weight='bold')
        pylab.xticks(fontsize=19)
        pylab.yticks(fontsize=19)
        pylab.figtext(0.13, 0.85, residue_name, fontsize=16)
        pylab.xlim(0, max)

        # y axis limits
        y_min = float(self.main.SETTINGS[5])
        y_max = float(self.main.SETTINGS[6])

        pylab.ylim(y_min, y_max)

        # The legend
        #pylab.legend()

        # Save the plot as svg
        pylab.savefig(folder+sep+self.main.PLOTFORMAT.replace('.', '')+sep+prefix+filename+self.main.PLOTFORMAT)

        # Infos for global fit
        if self.globalfit:
            text = ''
            # loop over experiments:
            for exp in range(len(x)):
                text = text + 'R2_'+str(exp+1)+': '+str(model_fit[exp][len(model_fit[exp])-1])[0:5]+', kex: '+str(self.rex_kex(model_fit[exp], self.exchange_type)[1])[0:6]+', Rex: '+str(self.rex_kex(model_fit[exp], self.exchange_type)[0])[0:6]+'\n'
            text = text + ', Chi2 = '+str(self.chi2)[0:6]+', AICc = '+str(self.aicc)[0:6]
            pylab.figtext(0.13, 0.11, text)

        # Individual fit
        else:
            pylab.figtext(0.13, 0.11, 'R2: '+str(model_fit[len(model_fit)-1])[0:5]+', kex: '+str(self.rex_kex(model_fit, self.exchange_type)[1])[0:6]+', Rex: '+str(self.rex_kex(model_fit, self.exchange_type)[0])[0:6]+', Chi2 = '+str(self.chi2)[0:6]+', AICc = '+str(self.aicc)[0:6])

        # Save the plot as png
        pylab.savefig(folder+sep+'png'+sep+prefix+filename+'.png', dpi = 72, transparent = True)

        wx.CallAfter(self.main.report_panel.AppendText, '\nPlot '+filename+' created.\n')

        # Crear plot
        pylab.cla() # clear the axes
        pylab.close() #clear figure

        self.main.tree_results.AppendItem (self.main.plots2d, folder+sep+'png'+sep+prefix+filename+'.png', 0)
        # Add to results tab

        # Store item
        self.main.plot2d.append(folder+sep+'png'+sep+prefix+filename+'.png')


    def read_resi(self):
        residues = []
        # loop over residues
        for resi in range(0, self.main.RESNO):
            if not str(self.main.data_grid[0].GetCellValue(resi, 0)) == '':
                residues.append(str(resi+1)+'\t'+str(self.main.data_grid[0].GetCellValue(resi, 0)))

        #self.residues.InsertItems(residues, 0)
        return residues


    def rex_kex(self, p, model):
        # fast exchange
        if model == 'fast':
            # collect phi and kex
            phi = []
            kex = []
            for entry in range(0, ((len(p)-1)/2)):
                phi.append(p[2*entry])
                kex.append(p[(2*entry)+1])

            # calculate phi_mean and kex_mean
            top = 0
            bottom = 0
            for i in range(0, len(kex)):
                top = top + (phi[i]/kex[i])
                bottom = bottom + (phi[i]/(kex[i]**2))

            # 1 state
            if top == 0:
                return [None, None]

            # Phi_mean
            phi_mean = (top**2)/bottom

            # kex mean
            kex_mean = top/bottom

            # Rex
            Rex = phi_mean / kex_mean

            return [Rex, kex_mean]

        # slow exchange
        if model == 'slow':
            # collect kex
            kex = []
            dw = []
            population = []
            for entry in range(0, ((len(p)-1)/3)):
                kex.append(p[3*entry])
                dw.append(p[3*entry+1])
                population.append(p[3*entry+2])

            # Pool population
            pop = 0
            for entry in range(0, len(population)):
                pop = pop + population[entry]
            # missing population
            last_pop = 1 - pop
            population.append(last_pop)

            # calculate kex
            kex_mean = 0
            for i in range(0, len(kex)):
                kex_mean = kex_mean + kex[i]

            # calculate Rex
            Rex = 0
            for i in range(0, len(kex)):
                # current population
                p_current = population[i+1]

                # sum of other population
                p_sum = 0
                for sum in range(0, len(population)):
                    p_sum = p_sum + population[sum]
                p_sum = p_sum - p_current

                # Calculate Rex
                Rex = Rex + ((p_sum*p_current*(dw[i]**2))/kex[i])

            return [Rex, kex_mean]


    def select_all(self, event):
        for i in range(0, self.residues.GetCount()):
            self.residues.SetSelection(i, True)


    def selection(self):
        # clear selection
        for i in range(self.main.RESNO):
            self.main.INCLUDE_RES[i] = True

        # Sync with selections fro dialog
        for i in range(0, self.residues.GetCount()):
            # detect residue no
            tmp = str(self.residues.GetString(i))
            tmp = tmp.split('\t')
            res_index = int(tmp[0])-1

            # is selected
            if self.residues.IsSelected(i):
                self.main.INCLUDE_RES[res_index] = True

            # is not selected
            else:
                self.main.INCLUDE_RES[res_index] = False


    def start(self, event):
        # Enable killing of NESSY
        self.button_kill.Enable(True)
        self.running = True
        self.button_start.Enable(False)

        # Jump to analyse tab
        self.main.MainTab.SetSelection(self.main.MainTab.GetPageCount()-3)

        # Global fit
        self.globalfit = False
        if self.main.ISGLOBAL in [True, 1]:
            q = question('Do you really want to perform global fit?', self)
            if q:
                self.globalfit = True

        # Start calculation in thread
        _thread.start_new_thread(self.start_calc, ())


    def start_calc(self):
        # Storage
        self.n_state_storage = []

        # Save selected residues
        selection_save = self.main.INCLUDE_RES

        # Read selection of n-state model
        self.selection()

        # Individual fit
        if not self.globalfit:
            # Calculate R2eff
            R2_eff(self.main, 0)

            # calculate pooled variance
            Pooled_variance(self.main, 0)

        # Global fit
        else:
            # data containers
            self.R2effs = []
            self.Variances = []
            self.CPMGs = []

            # loop over experiments
            for exp in range(self.main.NUMOFDATASETS):
                # Calculate R2eff
                R2_eff(self.main, exp)

                # store R2eff
                self.R2effs.append(self.main.R2eff)

                # calculate pooled variance
                Pooled_variance(self.main, exp)

                # store variance
                self.Variances.append(self.main.R2eff_variance[exp])

                # CPMG frequencies
                self.CPMGs.append([])
                for i in range(len(self.main.CPMGFREQ[exp])):
                    if not  str(self.main.CPMGFREQ[exp][i]) in ['', 'None', '0']:
                        self.CPMGs[exp].append(float(self.main.CPMGFREQ[exp][i]))

        # Restore main selection
        self.main.INCLUDE_RES = selection_save

        # Residues
        calc_residues = []
        for i in range(0, self.residues.GetCount()):
            # is selected
            if self.residues.IsSelected(i):
                tmp = str(self.residues.GetString(i))
                tmp = tmp.split('\t')

                # Calculate
                calc_residues.append(tmp[0])

        # convert to index
        calc_residues = [(int(i)-1) for i in calc_residues]

        # Calculate n-state models
        # loop over selected residues
        for selection in range(0, len(calc_residues)):
            self.calc(calc_residues[selection])

        # Model selection
        # AICc
        # loop over residues
        if self.aicc_box.GetValue():
            wx.CallAfter(self.main.report_panel.AppendText, '\n\n-------------------- AICc Model selection --------------------\n')
            for residue in range(0, len(self.n_state_storage)):
                wx.CallAfter(self.main.report_panel.AppendText, '\n\nAICc for Residue '+str(self.n_state_storage[residue][0][0]))
                # Index for best fit
                index = 0

                # compare AICc
                wx.CallAfter(self.main.report_panel.AppendText, '\nAICc for '+str(self.n_state_storage[residue][0][1])+' state model is '+str(self.n_state_storage[residue][0][5]))
                for entry in range(1, len(self.n_state_storage[residue])):
                    wx.CallAfter(self.main.report_panel.AppendText, '\nAICc for '+str(self.n_state_storage[residue][entry][1])+' states model is '+str(self.n_state_storage[residue][entry][5]))
                    if self.n_state_storage[residue][entry][5] < self.n_state_storage[residue][index][5]:
                        index = entry

                # best fit
                no_states = self.n_state_storage[residue][index][1]
                wx.CallAfter(self.main.report_panel.AppendText, '\n\n'+str(no_states)+' State(s) Model selected for Residue '+str(self.n_state_storage[residue][0][0])+'.\n')
                time.sleep(0.2)

        # output
        wx.CallAfter(self.main.report_panel.AppendText, '\n--------------------------------------------------------------------\n')

        # Final output
        wx.CallAfter(self.main.report_panel.AppendText, '\n\n____________________________________________________________________________________\n\nn-States Model calculation finished.\nPlots are colelcted in Results tab, 2D plots.\n____________________________________________________________________________________\n')

        # Enable start button and disable kill button
        self.button_start.Enable(True)
        self.button_kill.Enable(False)
