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


# scipt to calculate global fit

# Python Modules
from os import sep, makedirs
import pylab
from random import random, uniform
from scipy.optimize import leastsq
from scipy import linspace, array, sqrt, var, sum, log
import time
import wx
import sys

# NESSY modules
from curvefit.exclude import exclude
from func.pooled_variance import Pooled_variance
from func.r2eff import R2_eff as calc_R2eff
from func.color_code import color_code, color_code_model
from func.plotting import create_pylab_graphs
from math_fns.models import model_1, model_1_residuals, model_2, model_2_residuals, model_3, model_3_residuals, model_4, model_4_residuals, model_5, model_5_residuals, model_6, model_6_residuals, model_7, model_7_residuals
from math_fns.tests import Alpha, AIC, AICc, F_test
from math_fns.rex import Rex_fast, Rex_slow
from math_fns.gridsearch import gridsearch
from elements.variables import Pi
from curvefit.estimate import estimate
from func.plotting import surface_plot
from curvefit.chi2 import Chi2_container


class CPMG_fit():
    """Colelcts information and controlls global fit calculation."""

    def __init__(self, main, exp_mode):
        # connect parameters
        self.main = main

        # experiment mode
        self.exp_mode = exp_mode
        self.num_exp = []

        # detect residues
        self.residue = 1
        for i in range(self.main.RESNO):
            if not str(self.main.data_grid[0].GetCellValue(i, 0)) == '': self.residue = self.residue + 1

        # Create data container
        self.global_models = {'1': [], '1err':[],'2': [], '2err':[],'3': [], '3err':[],'4': [], '4err':[],'5': [], '5err':[], '6': [], '6err':[], '7': [], '7err':[]}

         # Report
        wx.CallAfter(self.main.report_panel.AppendText, '\n\n------------------------------------------------------\nStarting CPMG dispersion curvefit.\n------------------------------------------------------\n')
        time.sleep(1)


        # create directories
        base_dir = str(self.main.proj_folder.GetValue())

        # Pymol marcos
        try:
            makedirs(base_dir+sep+self.main.PYMOL_FOLDER)
        except:
            a = 'already exists'

        # Text files
        try:
            makedirs(base_dir+sep+self.main.TEXT_FOLDER)
        except:
            a = 'already exists'

        # Plot png
        try:
            makedirs(base_dir+sep+self.main.PLOT_FOLDER+sep+'png')
        except:
            a = 'already exists'

        # Plot vector
        try:
            makedirs(base_dir+sep+self.main.PLOT_FOLDER+sep+self.main.PLOTFORMAT.replace('.', ''))
        except:
            a = 'already exists'

        # collect R2eff
        self.pool_r2eff()

        # create x values (CPMG freqs)
        self.multiply_cpmgfreq()

        # Run calculations
        self.calculate()

        # Re-enable start button
        self.main.start_calc.Enable(True)


    def aicc_chi2_csv(self):
        """Creating CSV files containing AICc and Chi2 values."""
        # filename
        filename = str(self.main.proj_folder.GetValue())+sep+self.main.TEXT_FOLDER+sep+'Chi2_AICc.csv'

        # open file
        file = open(filename, 'w')

        # Write header
        file.write('Residue;Chi2 Model 1;AICc Model 1;Chi2 Model 2;AICc Model 2;Chi2 Model 3;AICc Model 3;Chi2 Model 4;AICc Model 4;Chi2 Model 5;AICc Model 5;\n')
        # loop over entries
        for entry in range(0, len(self.global_models['1'])):
            text = str(self.global_models['1'][entry]['residue']+1)+';'

            # add model 1
            text = text +str(self.global_models['1'][entry]['chi2'])+';'+str(AICc(self.global_models['1'][entry]['chi2'], 1, self.global_models['1'][entry]['n']))+';'

            # add model 2
            if self.global_models['2'] == []:
                text = text +';;'
            else:
                text = text +str(self.global_models['2'][entry]['chi2'])+';'+str(AICc(self.global_models['2'][entry]['chi2'], 4, self.global_models['2'][entry]['n']))+';'

            # add model 3
            if self.global_models['3'] == []:
                text = text +';;'
            else:
                text = text +str(self.global_models['3'][entry]['chi2'])+';'+str(AICc(self.global_models['3'][entry]['chi2'], 5, self.global_models['3'][entry]['n']))+';'

            # add model 4
            if self.global_models['4'] == []:
                text = text +';;'
            else:
                text = text +str(self.global_models['4'][entry]['chi2'])+';'+str(AICc(self.global_models['4'][entry]['chi2'], 6, self.global_models['4'][entry]['n']))+';'

            # add model 5
            if self.global_models['5'] == []:
                text = text +';;'
            else:
                text = text +str(self.global_models['5'][entry]['chi2'])+';'+str(AICc(self.global_models['5'][entry]['chi2'], 8, self.global_models['5'][entry]['n']))+';'

            # add model 6
            if self.global_models['6'] == []:
                text = text +';;'
            else:
                text = text +str(self.global_models['6'][entry]['chi2'])+';'+str(AICc(self.global_models['6'][entry]['chi2'], 5, self.global_models['6'][entry]['n']))+';'

            # add model 7
            if self.global_models['7'] == []:
                text = text +';;'
            else:
                text = text +str(self.global_models['7'][entry]['chi2'])+';'+str(AICc(self.global_models['7'][entry]['chi2'], 5, self.global_models['7'][entry]['n']))+';'

            # add new line
            text = text + '\n'

            # write text
            file.write(text)

        # Close file
        file.close()


    def calculate(self):
        """Calculates global fit."""

        # empty results containers
        self.main.MODEL1 = []            # [Residue, Fit_parameters, chi2]
        self.main.MODEL2 = []            # [Residue, Fit_parameters, chi2]
        self.main.MODEL3 = []            # [Residue, Fit_parameters, chi2]
        self.main.MODEL4 = []            # [Residue, Fit_parameters, chi2]
        self.main.MODEL5 = []            # [Residue, Fit_parameters, chi2]
        self.main.MODEL6 = []            # [Residue, Fit_parameters, chi2]
        self.main.MODEL7 = []            # [Residue, Fit_parameters, chi2]
        self.main.MODEL_SELECTION = []   # [Residue, Model, R2, kex]

        # empty entries for results tree
        self.main.results_plot = []
        self.main.results_txt = []

        # Model 1
        if self.main.MODELS[0]:
            self.model1(self.exp_mode)

        # Model 2
        if self.main.MODELS[1]:
            self.model2(self.exp_mode)

        # Model 3
        if self.main.MODELS[2]:
            self.model3(self.exp_mode)

        # Model 4
        if self.main.MODELS[3]:
            self.model4(self.exp_mode)

        # Model 5
        if self.main.MODELS[4]:
            self.model5(self.exp_mode)

        # Model 6
        if self.main.MODELS[5]:
            self.model6(self.exp_mode)

        # Model 7
        if self.main.MODELS[6]:
            self.model7(self.exp_mode)

        # Feedback
        wx.CallAfter(self.main.gauge_1.SetValue, 100)
        wx.CallAfter(self.main.report_panel.AppendText, '\n------------------------------------------------------------------------------------------------------\nR2eff Calculation finished and plots created.\n------------------------------------------------------------------------------------------------------' )

        # Model Selection
        self.model_selection(self.exp_mode)
        self.aicc_chi2_csv()
        wx.CallAfter(self.main.report_panel.AppendText, '\n\n------------------------------------------------------------------------------------------------------\nFinished Model Selection.\n------------------------------------------------------------------------------------------------------' )

        # Monte Carlo simulations
        self.montecarlo(self.exp_mode)

        # Color code structure
        wx.CallAfter(self.main.checkrun_label.SetLabel, 'Color coded structures')

        # the directory and pdb file
        directory = str(self.main.proj_folder.GetValue())+sep+self.main.PYMOL_FOLDER
        pdbfile = str(self.main.pdb_file.GetValue())

        # Model
        color_code_model(self.Model_residue, self.Model_value, 'Model_selection.pml', directory, pdb_file=pdbfile)
        # Add file to results tree
        self.main.tree_results.AppendItem (self.main.structures, directory+sep+'Model_selection.pml', 0)
        self.main.COLOR_PDB.append(directory+sep+'Model_selection.pml')

        # kex
        color_code(self.residue_no, self.kex, 'Kex.pml', directory, pdb_file=pdbfile)
        # Add file to results tree
        self.main.tree_results.AppendItem (self.main.structures, directory+sep+'Kex.pml', 0)
        self.main.COLOR_PDB.append(directory+sep+'Kex.pml')

        # Rex
        color_code(self.residue_no, self.Rex_values, 'Rex.pml', directory, pdb_file=pdbfile)
        # Add file to results tree
        self.main.tree_results.AppendItem (self.main.structures, directory+sep+'Rex.pml', 0)
        self.main.COLOR_PDB.append(directory+sep+'Rex.pml')

        wx.CallAfter(self.main.report_panel.AppendText, '\n\n------------------------------------------------------------------------------------------------------\nPymol Macros Created.\n------------------------------------------------------------------------------------------------------' )
        wx.CallAfter(self.main.checkrun_label.SetLabel, 'Done.')

        # update program status
        wx.CallAfter(self.main.gauge_1.SetValue, 100)
        wx.CallAfter(self.main.checkrun_label.SetLabel, 'Done.')


    def create_R2eff_plots(self, exp_index):
        '''Create pylab plots for R2eff.'''
        if self.exp_mode == 0:
            wx.CallAfter(self.main.checkrun_label.SetLabel, 'Creating R2eff plots')
        else:
            wx.CallAfter(self.main.checkrun_label.SetLabel, 'Creating R1rho plots')
        create_pylab_graphs(self.main, self.main.R2eff, self.main.include, self.residue, exp_index, self.exp_mode)
        wx.CallAfter(self.main.gauge_1.SetValue, 0)


    def csv(self, x, y, directory, residue, exp):
        '''Create CSV files.'''
        # Create folder
        textfolder = directory + sep + self.main.TEXT_FOLDER
        try:
            os.mkdir(textfolder)
        except:
            wx.CallAfter(self.main.report_panel.AppendText, '')

        # write file
        filename_txt = textfolder + sep +'Model_'+str(self.model)+'_' + str(residue+1) + '_' + str(self.main.data_grid[exp].GetCellValue(residue, 0)) +'.csv'
        file = open(filename_txt, 'w')
        if self.exp_mode == 0:
            file.write('CPMG [Hz];R2eff [1/s]\n\n')
        if self.exp_mode == 1:
            file.write('v1 [Hz];R1rho [1/s]\n\n')
        for i in range(0, len(x)):
            file.write(str(x[i]) + ';' + str(y[i]) + '\n')
        file.close()

        # add file to results tree
        self.main.tree_results.AppendItem (self.main.txt, filename_txt, 0)

        # save entry
        self.main.results_txt.append(filename_txt)


    def exclude(self, residue, r2effs, cpmgfreqs, prior=False):
        '''Function to exclude if difference betweendata is not big enougt.'''
        # minimal difference
        min_diff = self.main.SETTINGS[3]

        # excange is expected, if at least 1 experiment has bigger difference
        has_exchange = False

        # loop over experiments
        for exp in range(0, len(cpmgfreqs)):
            # collect CPMG frequencies and R2eff
            cpmg_freq = []
            r2effs = []

            # loop over CPMG frequencies
            for i in range(len(cpmgfreqs[exp])):
                # Check if CPMG frequency is set
                if not cpmgfreqs[exp][i] in ['', '0']:
                    # Check if Data is present
                    if not self.R2eff_pooled[exp][residue][i] in [None, '']:
                        # Append CPMG frequency
                        cpmg_freq.append(float(cpmgfreqs[exp][i]))

                        # Append R2eff
                        r2effs.append(self.R2eff_pooled[exp][residue][i])

            # Check if Rex is expected
            do_exclude = exclude(r2effs, cpmg_freq, min_diff, prior=False)

            # change flag
            if not do_exclude:
                has_exchange = True

        # exclude if no data set is expected to be exchanging
        if not has_exchange:
            return True

        else:
            return False


    def plot(self, model_fit, x, y, directory, residue, model, chi2):
        """Function to plot global fit plots."""

        # detect maximum frequency
        max = 0
        # loop over experiments
        for i in range(0, len(x)):
            # loop over entries
            for j in range(0, len(x[i])):
                if x[i][j] > max:
                    max = x[i][j]

        # add extra border in graph
        max = max + (0.1*max)

        # Colors
        colors = ['BLUE', 'RED', 'GREEN', 'YELLOW', 'CYAN', 'GOLD', 'MAGENTA', 'NAVY', 'ORANGE', 'PINK', 'PURPLE', 'BLACK', 'GRAY', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK' ]

        # Create directories
        if self.exp_mode == 0:
            png_dir = directory + sep + self.main.PLOT_FOLDER+sep+'png'
            svg_dir = directory + sep + self.main.PLOT_FOLDER+sep+self.main.PLOTFORMAT.replace('.', '')
        else:
            png_dir = directory + sep + 'R1rho_plots'+sep+'png'
            svg_dir = directory + sep + 'R1rho_plots'+sep+self.main.PLOTFORMAT.replace('.', '')

        # PNG dir
        try:
            makedirs(png_dir)
        except:
            wx.CallAfter(self.main.report_panel.AppendText, '')

        # SVG dir
        try:
            makedirs(svg_dir)
        except:
            wx.CallAfter(self.main.report_panel.AppendText, '')

        # Text summary of parameters
        text = ''

        # Create plots
        for exp in range(0, len(x)):
            # R2eff plot
            pylab.errorbar(x[exp], y[exp], yerr = sqrt(self.variance[exp]), color=colors[exp], fmt ='o')

            # fit
            # claculate fit
            # parameters
            p = []
            if model == 1:
                p.append(model_fit[exp])    # R2
            if model == 2:
                p.append(model_fit[2+exp])  # R2
                p.append(model_fit[1]*((float(self.main.spec_freq[exp].GetValue()))*2 * Pi)**2)  # Phi
                p.append(model_fit[0])  # kex
                text = 'kex: '+str(model_fit[0])[0:8]+' 1/s'
            if model in [3, 6, 7]:
                p.append(model_fit[exp+3])#[3+(2*exp)])  # R2
                p.append(model_fit[0])  # kex
                p.append(model_fit[2]*(float(self.main.spec_freq[exp].GetValue())*2 * Pi))  # dw
                p.append(model_fit[1])  # pb
                text = 'kex: '+str(model_fit[0])[0:8]+' 1/s, dw: '+str(model_fit[2])[0:6]+' ppm, pb: '+ str(model_fit[1])[0:6]
            if model == 4:
                p.append(model_fit[4+exp])  # R2
                p.append(model_fit[2]*((float(self.main.spec_freq[exp].GetValue()))*2 * Pi)**2)  # Phi
                p.append(model_fit[0])  # kex
                p.append(model_fit[3]*((float(self.main.spec_freq[exp].GetValue()))*2 * Pi)**2)  # Phi2
                p.append(model_fit[1])  # kex2
                text = 'kex A-B: '+str(model_fit[0])[0:9]+' 1/s, kex B-C: '+str(model_fit[1])[0:9]+' 1/s'
            if model == 5:
                p.append(model_fit[6+exp])  # R2
                p.append(model_fit[0])  # kex
                p.append(model_fit[4]*(float(self.main.spec_freq[exp].GetValue())*2 * Pi))   # dw
                p.append(model_fit[2])  # pb
                p.append(model_fit[1])  # kex2
                p.append(model_fit[5]*(float(self.main.spec_freq[exp].GetValue())*2 * Pi))   # dw2
                p.append(model_fit[3])  # pc
                text = text + 'kex A-B: '+str(model_fit[0])[0:9]+' 1/s, kex B-C: '+str(model_fit[1])[0:9]+' 1/s, dw A-B: '+str(model_fit[4])[0:5]+' ppm\ndw B-C: '+str(model_fit[5])[0:9]+' pb: '+str(model_fit[2])[0:5] +', pc: '+str(model_fit[3])[0:5]

            # craete data points
            x_values = linspace(0, max, num=100)
            y_values = self.models[str(model)](x_values, p)

            # plot
            pylab.plot(x_values, y_values, '-', color=colors[exp], label = str(self.main.spec_freq[exp].GetValue())+' MHz')

            # Create CSV files
            self.csv(x_values, y_values, directory, residue, exp)

        # Labels
        pylab.xlim(0, max)
        y_min = float(self.main.SETTINGS[5])
        y_max = float(self.main.SETTINGS[6])
        pylab.ylim(y_min, y_max)
        if self.exp_mode == 0:
            pylab.xlabel('v(CPMG) [Hz]', fontsize=19, weight='bold')
            pylab.ylabel('R2eff [1/s]', fontsize=19, weight='bold')
        elif self.exp_mode == 1:
            pylab.xlabel('v1 [Hz]', fontsize=19, weight='bold')
            pylab.ylabel('R1rho [1/s]', fontsize=19, weight='bold')
        pylab.xticks(fontsize=19)
        pylab.yticks(fontsize=19)
        pylab.figtext(0.13, 0.85, str(residue+1)+' '+str(self.main.data_grid[0].GetCellValue(residue, 0)), fontsize=19)
        pylab.legend()

        # Frame width
        params={'axes.linewidth' : self.main.FRAMEWIDTH}
        pylab.rcParams.update(params)

        # SVG plot
        pylab.savefig(svg_dir+sep+'Model_'+str(model)+'_'+str(residue+1)+self.main.PLOTFORMAT)

        # Save plots
        # PNG
        # add chi2 to text
        text = text + ', Chi2: '+str(chi2)[0:8]
        pylab.figtext(0.13, 0.11, text)
        filename = png_dir+sep+'Model_'+str(model)+'_'+str(residue+1)+'.png'
        pylab.savefig(filename, dpi = 72, transparent = True)

        # clear plot
        pylab.cla()
        pylab.close()

        # Add to results tree and save entry
        if self.model == 1:
            self.main.tree_results.AppendItem (self.main.plots_model1, filename, 0)
            self.main.results_model1.append(filename)
        if self.model == 2:
            self.main.tree_results.AppendItem (self.main.plots_model2, filename, 0)
            self.main.results_model2.append(filename)
        if self.model == 3:
            self.main.tree_results.AppendItem (self.main.plots_model3, filename, 0)
            self.main.results_model3.append(filename)
        if self.model == 4:
            self.main.tree_results.AppendItem (self.main.plots_model4, filename, 0)
            self.main.results_model4.append(filename)
        if self.model == 5:
            self.main.tree_results.AppendItem (self.main.plots_model5, filename, 0)
            self.main.results_model5.append(filename)
        if self.model == 6:
            self.main.tree_results.AppendItem (self.main.plots_model6, filename, 0)
            self.main.results_model6.append(filename)
        if self.model == 7:
            self.main.tree_results.AppendItem (self.main.plots_model7, filename, 0)
            self.main.results_model7.append(filename)


    def plots(self, Rex_exp=''):
        # output directory
        directory = str(self.main.proj_folder.GetValue())

        # prefix
        self.prefix = ''

        # Sort values
        x_values = []   # Residue
        sel_model = []
        y_R2 = []
        y_R2_err = []
        y_kex = []
        y_kex_err = []
        y_kex1 = []
        y_kex1_err = []
        y_kex2 = []
        y_kex2_err = []
        y_Rex = []
        y_Rex_err = []
        pb_value = []
        pb_value_err = []
        dw_value = []
        dw_value_err = []
        dw2_value = []
        dw2_value_err = []
        pc_value = []
        pc_value_err = []
        dG = []
        dG_tr = []
        Chi2 = []

        # loop over entries
        for i in range(0, len(self.main.MODEL_SELECTION)):
            # Detect model
            model = self.main.MODEL_SELECTION[i]['model']

            # Residue Number
            x_values.append(self.main.MODEL_SELECTION[i]['residue'])

            # Chi2
            Chi2.append(self.main.MODEL_SELECTION[i]['chi2'])

            # model
            sel_model.append(model)

            # R2
            y_R2.append(self.main.MODEL_SELECTION[i]['R2'])
            y_R2_err.append(self.main.MODEL_SELECTION_ERROR[i]['R2'])

            # Craete entries
            y_kex.append(None)
            y_kex_err.append(None)
            y_Rex.append(None)
            y_Rex_err.append(None)
            dw_value.append(None)
            dw_value_err.append(None)
            pb_value.append(None)
            pb_value_err.append(None)
            y_kex1.append(None)
            y_kex1_err.append(None)
            y_kex2.append(None)
            y_kex2_err.append(None)
            dw2_value.append(None)
            dw2_value_err.append(None)
            pc_value.append(None)
            pc_value_err.append(None)
            dG.append(None)
            dG_tr.append(None)

            # Model 2
            if model == 2:
                # kex
                y_kex[i] = self.main.MODEL_SELECTION[i]['kex']
                y_kex_err[i] = self.main.MODEL_SELECTION_ERROR[i]['kex']

                # Rex
                y_Rex[i] = self.main.MODEL_SELECTION[i]['Rex']
                y_Rex_err[i] = self.main.MODEL_SELECTION_ERROR[i]['Rex']

            # Model 3, 6
            if model in [3, 6, 7]:
                # kex
                y_kex[i] = self.main.MODEL_SELECTION[i]['kex']
                y_kex_err[i] = self.main.MODEL_SELECTION_ERROR[i]['kex']

                # Rex
                y_Rex[i] = self.main.MODEL_SELECTION[i]['Rex']
                y_Rex_err[i] = self.main.MODEL_SELECTION_ERROR[i]['Rex']

                # dw
                dw_value[i] = self.main.MODEL_SELECTION[i]['dw']
                dw_value_err[i] = self.main.MODEL_SELECTION_ERROR[i]['dw']

                # pb
                pb_value[i] = self.main.MODEL_SELECTION[i]['pb']
                pb_value_err[i] = self.main.MODEL_SELECTION_ERROR[i]['pb']

            # Model 4
            if model == 4:
                # kex
                y_kex[i] = self.main.MODEL_SELECTION[i]['kex']
                y_kex_err[i] = self.main.MODEL_SELECTION_ERROR[i]['kex']

                # kex1
                y_kex1[i] = self.main.MODEL_SELECTION[i]['kex1']
                y_kex1_err[i] = self.main.MODEL_SELECTION_ERROR[i]['kex1']

                # kex2
                y_kex2[i] = self.main.MODEL_SELECTION[i]['kex2']
                y_kex2_err[i] = self.main.MODEL_SELECTION_ERROR[i]['kex2']

                # Rex
                y_Rex[i] = self.main.MODEL_SELECTION[i]['Rex']
                y_Rex_err[i] = self.main.MODEL_SELECTION_ERROR[i]['Rex']

            # Model 5
            if model == 5:
                # kex
                y_kex[i] = self.main.MODEL_SELECTION[i]['kex']
                y_kex_err[i] = self.main.MODEL_SELECTION_ERROR[i]['kex']

                # kex1
                y_kex1[i] = self.main.MODEL_SELECTION[i]['kex1']
                y_kex1_err[i] = self.main.MODEL_SELECTION_ERROR[i]['kex1']

                # kex2
                y_kex2[i] = self.main.MODEL_SELECTION[i]['kex2']
                y_kex2_err[i] = self.main.MODEL_SELECTION_ERROR[i]['kex2']

                # Rex
                y_Rex[i] = self.main.MODEL_SELECTION[i]['Rex']
                y_Rex_err[i] = self.main.MODEL_SELECTION_ERROR[i]['Rex']

                # dw
                dw_value[i] = self.main.MODEL_SELECTION[i]['dw']
                dw_value_err[i] = self.main.MODEL_SELECTION_ERROR[i]['dw']

                # dw2
                dw2_value[i] = self.main.MODEL_SELECTION[i]['dw2']
                dw2_value_err[i] = self.main.MODEL_SELECTION_ERROR[i]['dw2']

                # pb
                pb_value[i] = self.main.MODEL_SELECTION[i]['pb']
                pb_value_err[i] = self.main.MODEL_SELECTION_ERROR[i]['pb']

                # pc
                pc_value[i] = self.main.MODEL_SELECTION[i]['pc']
                pc_value_err[i] = self.main.MODEL_SELECTION_ERROR[i]['pc']

        # Write summray
        for i in range(len(x_values)):
            # The model
            self.main.Final_grid.SetCellValue(x_values[i]-1, 0, str(sel_model[i])[:9])
            # Rex
            if y_Rex[i]:
                self.main.Final_grid.SetCellValue(x_values[i]-1, 1, str(y_Rex[i])[:9])
                self.main.Final_grid.SetCellValue(x_values[i]-1, 2, str(y_Rex_err[i])[:9])
            # kex (1)
            if y_kex[i]:
                self.main.Final_grid.SetCellValue(x_values[i]-1, 3, str(y_kex[i])[:9])
                self.main.Final_grid.SetCellValue(x_values[i]-1, 4, str(y_kex_err[i])[:9])
                if sel_model[i] in [4, 5]:
                    self.main.Final_grid.SetCellValue(x_values[i]-1, 3, str(y_kex1[i])[:9])
                    self.main.Final_grid.SetCellValue(x_values[i]-1, 4, str(y_kex1_err[i])[:9])
            # dw 1
            if dw_value[i]:
                self.main.Final_grid.SetCellValue(x_values[i]-1, 5, str(dw_value[i])[:9])
                self.main.Final_grid.SetCellValue(x_values[i]-1, 6, str(dw_value_err[i])[:9])
            # pb
            if pb_value[i]:
                self.main.Final_grid.SetCellValue(x_values[i]-1, 7, str(pb_value[i])[:9])
                self.main.Final_grid.SetCellValue(x_values[i]-1, 8, str(pb_value_err[i])[:9])
                # dG
                dG[i] = 8.3144621*298*log((1-pb_value[i])/pb_value[i])/1000                                             # = RTln(pa/pb) in kJ/mol at 298 K
                self.main.Final_grid.SetCellValue(x_values[i]-1, 16, str(dG[i]))
                # dG*
                dG_tr[i] = 8.3144621*298*log(298*1.3806488*10**(-23)/(6.62606957*10**(-34)*y_kex[i]*pb_value[i]))/1000  # = RTln(kb*T/(kAB*h))
                self.main.Final_grid.SetCellValue(x_values[i]-1, 17, str(dG_tr[i]))
                
            # kex 2
            if y_kex2[i]:
                self.main.Final_grid.SetCellValue(x_values[i]-1, 9, str(y_kex2[i])[:9])
                self.main.Final_grid.SetCellValue(x_values[i]-1, 11, str(y_kex2_err[i])[:9])
            # dw 1
            if dw2_value[i]:
                self.main.Final_grid.SetCellValue(x_values[i]-1, 11, str(dw2_value[i])[:9])
                self.main.Final_grid.SetCellValue(x_values[i]-1, 12, str(dw2_value_err[i])[:9])
            # pc
            if pc_value[i]:
                self.main.Final_grid.SetCellValue(x_values[i]-1, 13, str(pc_value[i])[:9])
                self.main.Final_grid.SetCellValue(x_values[i]-1, 14, str(pc_value_err[i])[:9])

        # Create csv file
        # header
        text = 'Residue;Model;R2 [1/s];err;kex [1/s];err;Rex exp. '+Rex_exp+' [rad/s];err;pb;err;dw [ppm];err;kex1 [1/s];err;pc;err;dw2 [ppm];err;kex2 [1/s];err;dG at 298 K [kj/mol];dG* at 298 K [kj/mol];Chi2\n'

        # Write data
        for i in range(0, len(x_values)):
            text = text + str(x_values[i]) + ';'+str(sel_model[i])+';'+str(y_R2[i])+';'+str(y_R2_err[i])+';'+str(y_kex[i])+';'+str(y_kex_err[i])+';'+str(y_Rex[i])+';'+str(y_Rex_err[i])+';'+str(pb_value[i])+';'+str(pb_value_err[i])+';'+str(dw_value[i])+';'+str(dw_value_err[i])+';'+str(y_kex1[i])+';'+str(y_kex1_err[i])+';'+str(pc_value[i])+';'+str(pc_value_err[i])+';'+str(dw2_value[i])+';'+str(dw2_value_err[i])+';'+str(y_kex2[i])+';'+str(y_kex2_err[i])+';'+str(dG[i])+';'+str(dG_tr[i])+';'+str(Chi2[i])+'\n'

        # Replace None entries
        text = text.replace('None', '')

        # Write file
        filename = directory + sep + self.main.TEXT_FOLDER + sep +self.prefix+ 'Summary.csv'
        file = open(filename, 'w')
        file.write(text)
        file.close()

        # Add csv file to results tree.
        self.main.tree_results.AppendItem (self.main.txt, filename, 0)

        # Save csv file
        self.main.results_txt.append(filename)

        # store items
        # kex
        self.kex = []
        self.residue_no = []
        for i in range(len(y_kex)):
            if y_kex[i]:
                kex_tmp = y_kex[i]
                if y_kex1[i]:
                    kex_tmp = kex_tmp + y_kex1[i]
                # store
                self.kex.append(kex_tmp)
                self.residue_no.append(x_values[i])
        self.kex = [float(i) for i in self.kex]
        self.residue_no = [int(i) for i in self.residue_no]

        # Rex
        self.Rex_values = []
        for i in range(len(y_Rex)):
            if y_Rex[i]:
                # store
                self.Rex_values.append(y_Rex[i])
        self.Rex_values = [float(i) for i in self.Rex_values]

        # Model
        self.Model_value = []
        self.Model_residue = []
        for i in range(len(sel_model)):
            if sel_model[i]:
                self.Model_value.append(int(sel_model[i]))
                self.Model_residue.append(str(x_values[i]))

        # Create Plots
        directory = directory + sep + self.main.PLOT_FOLDER

        # convert list to array
        min = x_values[0]
        max = x_values[len(x_values)-1]
        x_values = array(x_values)

        y_R2 = array(y_R2)

        x_kex_value = []
        y_kex_value = []
        y_kex_value_err = []
        for i in range(0, len(y_kex)):
            if not y_kex[i] == None:
                y_kex_value.append(y_kex[i])
                y_kex_value_err.append(y_kex_err[i])
                x_kex_value.append(x_values[i])
        y_kex_value = array(y_kex_value)
        y_kex_value_err = array(y_kex_value_err)
        x_kex_value = array(x_kex_value)

        x_Rex_value = []
        y_Rex_value = []
        y_Rex_value_err = []
        for i in range(0, len(y_Rex)):
            if not y_Rex[i] == None:
                y_Rex_value.append(y_Rex[i])
                y_Rex_value_err.append(y_Rex_err[i])
                x_Rex_value.append(x_values[i])
        y_Rex_value = array(y_Rex_value)
        y_Rex_value_err = array(y_Rex_value_err)
        x_Rex_value = array(x_Rex_value)

        x_pb = []
        y_pb = []
        y_pb_err = []
        for i in range(0, len(pb_value)):
            if not pb_value[i] == None:
                y_pb.append(pb_value[i])
                y_pb_err.append(pb_value_err[i])
                x_pb.append(x_values[i])
        y_pb = array(y_pb)
        y_pb_err = array(y_pb_err)
        x_pb = array(x_pb)

        # Model Selection plot
        pylab.xticks(fontsize=19)
        pylab.yticks(fontsize=19)
        pylab.plot(x_values, sel_model, 'ko')
        pylab.xlim(min-5, max+5)
        pylab.ylim(0, 8)
        pylab.xlabel('Residue Number', fontsize=19, weight='bold')
        pylab.ylabel('Model', fontsize=19, weight='bold')

        # png image
        filename = directory + sep + 'png' + sep +self.prefix+ 'Model_Selection.png'
        pylab.savefig(filename, dpi = 72, transparent = True)

        # svg image
        filename_svg = directory + sep + self.main.PLOTFORMAT.replace('.', '') + sep +self.prefix+ 'Model_Selection'+self.main.PLOTFORMAT
        pylab.savefig(filename_svg)

        pylab.cla() # clear the axes
        pylab.close() #clear figure

        # add to results tree
        self.main.tree_results.AppendItem (self.main.plots_modelselection, filename, 0)
        self.main.FINAL_RESULTS.append(filename)


        # R2 plot
        pylab.xticks(fontsize=19)
        pylab.yticks(fontsize=19)
        pylab.errorbar(x_values, y_R2, yerr = y_R2_err, fmt ='ko')
        pylab.xlim(min-5, max+5)
        pylab.xlabel('Residue Number', fontsize=19, weight='bold')
        pylab.ylabel('R2 [1/s]', fontsize=19, weight='bold')

        # png image
        filename = directory + sep + 'png' + sep +self.prefix+ 'Model_Selection_R2.png'
        pylab.savefig(filename, dpi = 72, transparent = True)

        # svg image
        filename_svg = directory + sep + self.main.PLOTFORMAT.replace('.', '') + sep +self.prefix+ 'Model_Selection_R2'+self.main.PLOTFORMAT
        pylab.savefig(filename_svg)

        pylab.cla() # clear the axes
        pylab.close() #clear figure

        # add to results tree
        self.main.tree_results.AppendItem (self.main.plots_modelselection, filename, 0)
        self.main.FINAL_RESULTS.append(filename)

        # kex plot
        try:
            pylab.errorbar(x_kex_value, y_kex_value, yerr = y_kex_value_err, fmt ='ko')
            pylab.xlim(min, max)
            pylab.xticks(fontsize=19)
            pylab.yticks(fontsize=19)
            pylab.xlabel('Residue Number', fontsize=19, weight='bold')
            pylab.ylabel('kex [1/s]', fontsize=19, weight='bold')

            # png image
            filename = directory + sep + 'png' + sep +self.prefix+ 'Model_Selection_kex.png'
            pylab.savefig(filename, dpi = 72, transparent = True)

            # svg image
            filename_svg = directory + sep + self.main.PLOTFORMAT.replace('.', '') + sep +self.prefix+ 'Model_Selection_kex'+self.main.PLOTFORMAT
            pylab.savefig(filename_svg)

            pylab.cla() # clear the axes
            pylab.close() #clear figure

            # add to results tree
            self.main.tree_results.AppendItem (self.main.plots_modelselection, filename, 0)
            self.main.FINAL_RESULTS.append(filename)

        except:
            wx.CallAfter(self.main.report_panel.AppendText, '\nNo kex detected, skipping...\n')

        # Rex plot
        try:
            pylab.errorbar(x_Rex_value, y_Rex_value, yerr = y_Rex_value_err, fmt ='ko')
            pylab.xlim(min, max)
            pylab.xticks(fontsize=19)
            pylab.yticks(fontsize=19)
            pylab.xlabel('Residue Number', fontsize=19, weight='bold')
            pylab.ylabel('Rex exp. '+Rex_exp+' [rad/s]', fontsize=19, weight='bold')

            # png image
            filename = directory + sep + 'png' + sep +self.prefix+ 'Model_Selection_Rex.png'
            pylab.savefig(filename, dpi = 72, transparent = True)

            # svg image
            filename_svg = directory + sep + self.main.PLOTFORMAT.replace('.', '') + sep +self.prefix+ 'Model_Selection_Rex'+self.main.PLOTFORMAT
            pylab.savefig(filename_svg)

            pylab.cla() # clear the axes
            pylab.close() #clear figure

            # add to results tree
            self.main.tree_results.AppendItem (self.main.plots_modelselection, filename, 0)
            self.main.FINAL_RESULTS.append(filename)

        except:
            wx.CallAfter(self.main.report_panel.AppendText, '\nNo Rex detected, skipping...\n')

        # pb plot
        try:
            pylab.errorbar(x_pb, y_pb, yerr = y_pb_err, fmt ='ko')
            pylab.xlim(min, max)
            pylab.ylim(0, 0.5)
            pylab.xticks(fontsize=19)
            pylab.yticks(fontsize=19)
            pylab.xlabel('Residue Number', fontsize=19, weight='bold')
            pylab.ylabel('pb', fontsize=19, weight='bold')

            # png image
            filename = directory + sep + 'png' + sep +self.prefix+ 'Model_Selection_pb.png'
            pylab.savefig(filename, dpi = 72, transparent = True)

            # svg image
            filename_svg = directory + sep + self.main.PLOTFORMAT.replace('.', '') + sep +self.prefix+ 'Model_Selection_pb'+self.main.PLOTFORMAT
            pylab.savefig(filename_svg)

            pylab.cla() # clear the axes
            pylab.close() #clear figure

            # add to results tree
            self.main.tree_results.AppendItem (self.main.plots_modelselection, filename, 0)
            self.main.FINAL_RESULTS.append(filename)

        except:
            wx.CallAfter(self.main.report_panel.AppendText, '\nNo pb detected, skipping...\n')


    def pool_r2eff(self):
        """Removes offset of effective R2eff."""
        # Detect number of experiments
        exp_no = self.main.NUMOFDATASETS

        # R2
        R2= []

        # R2eff
        R2eff = []

        # self.R2eff_pooled
        self.R2eff_pooled = []

        # poooled variance storage
        self.pooled_variance_store = []

        # loop over calculated experiments
        for exp in range(0, exp_no):
            # create new entry
            R2 = []       # [Residue, R2]

            # Calculate R2eff
            calc_R2eff(self.main, exp, self.exp_mode)

            # Calculate pooled variance
            Pooled_variance(self.main, exp)

            # save pooled variance
            self.pooled_variance_store.append(self.main.R2eff_variance[exp])

            # save R2eff without offset
            self.R2eff_pooled.append(self.main.R2eff)

            # Create Graphs and Text files
            if self.main.CREATE_R2EFFPLOT == 0:
                self.create_R2eff_plots(exp)


    def minimise(self, residue, directory, exp_index, model, exp_mode):
        """Function to perform global fit."""
        # clear chi2_surface container
        Chi2_container.chi2_surface = [[], [], []]

        # Prefix for files
        self.prefix = ''

        # Model
        self.model = model

        # Model dictionaries
        self.models = {'1': model_1, '2': model_2, '3': model_3, '4': model_4, '5': model_5, '6': model_6, '7': model_7}
        self.models_residuals = {'1': model_1_residuals, '2': model_2_residuals, '3': model_3_residuals, '4': model_4_residuals, '5': model_5_residuals, '6': model_6_residuals, '7': model_7_residuals}

        # create data containers
        x = []
        y = []

        # loop over experiments
        for exp in range(0, len(self.R2eff_pooled)):
            # append storages
            x.append([])
            y.append([])

            # loop over entries
            for dataset in range(0, len(self.R2eff_pooled[exp][residue])):
                # store entries
                if not self.R2eff_pooled[exp][residue][dataset] == None:
                    x[exp].append(float(self.cpmgfreqs[exp][dataset]))
                    y[exp].append(float(self.R2eff_pooled[exp][residue][dataset]))

        # Check if data is present for any experiments; abort if not
        data_flag = False
        for i in range(len(y)):
            if len(y[i]):
                data_flag = True
            if not data_flag:
                return

        # Trim the data if data sets are missing.
        x_new = []
        y_new = []
        R2eff_pooled = []
        cpmgfreqs = []
        for i in range(len(x)):
            if len(x[i]):
                x_new.append(x[i])
                y_new.append(y[i])
                R2eff_pooled.append(self.R2eff_pooled[i])
                cpmgfreqs.append(self.cpmgfreqs[i])
        x = x_new
        y = y_new
        self.num_exp.append(len(x))

        # update program status
        wx.CallAfter(self.main.checkrun_label.SetLabel, 'Fitting to Model '+str(model)+', Residue '+str(residue+1))

        # number of experiments
        if type(x[0]).__name__ == 'list':   self.exp_no = len(x)
        else:                               self.exp_no = 1

        # number of data points n
        n = 0
        for i in range(0, len(x)):
            # multiple experiments
            if type(x[i]).__name__ == 'list':
                for j in range(0, len(x[i])):
                    n = n + 1

            # only one experiment
            else:
                n = n + 1

        # check if exchange is expected for models 2++
        if self.main.FITALLMODELS == False:
            if self.model > 1:
                check = self.exclude(residue, R2eff_pooled, cpmgfreqs, prior=True)

                # stop, if no exchange is expected
                if check:
                    #  dummy fit results
                    fit = [0, 0, 0, 0, 0, 0, 0, 0, 0]
                    # save dummy minimisation results
                    self.global_models[str(model)].append({'residue':residue, 'fit':fit, 'chi2':999999999999999, 'n':n, 'n_exp':self.exp_no, 'x':x, 'y':y, 'variance':self.variance})
                    wx.CallAfter(self.main.report_panel.AppendText, "\n\nSkipping model %s for residue %s - no exchange is expected." % (self.model, residue + 1))
                    return

        # Report start of analysis
        wx.CallAfter(self.main.report_panel.AppendText, '\n\nFitting Model '+str(self.model)+' to Residue ' + str(residue + 1)+'\n\n')

        # convert to arrays
        for i in range(0, len(x)):
            x[i]=array(x[i])
            y[i]=array(y[i])

        # initial guess
        p_estimated = estimate(self, model=self.model, isglobal=self.num_exp[-1])

        # Error
        self.error = []
        self.variance = []
        for i in range(0, len(self.pooled_variance_store)):
            self.error.append(sqrt(self.pooled_variance_store[i][residue]))
            self.variance.append(self.pooled_variance_store[i][residue])

        # grid search
        if self.main.GRIDSEARCH and not model in [1]:
            p_estimated = gridsearch(base_dir=str(self.main.proj_folder.GetValue()), data=[x, y], experiment='cpmg', output=self.main.report_panel, fileroot='Residue_'+str(residue)+'_Model_'+str(self.model)+'_Surface', frequencies=self.main.spec_freq, grid_size=self.main.GRID_INCREMENT, INI_R2=self.main.INI_R2, model=model, variance=self.error, output_tree=self.main.tree_results, savecont=self.main.plot3d, output1=self.main.plots3d, globalfit=True)

        # convergence method
        if self.main.CONVERGENCE:
            # chi2 to compare
            chi2_old = 999
            chi2_current = 9999999999

            # repeat until convergence
            while not chi2_old == chi2_current:
                # minimise
                model_fit = leastsq(self.models_residuals[str(self.model)], p_estimated, args=((y), (x), self.error, self.main.report_panel, True, self.main.spec_freq, self.main.SHIFT_DIFFERENCE[residue]), full_output = 1, col_deriv = 1, ftol = self.main.tolerance/2, xtol = self.main.tolerance/2, maxfev=2000000)

                # adjust ch2
                chi2_old = chi2_current
                chi2_current = sum(Chi2_container.chi2)

                # new estimation
                p_estimated = model_fit[0]

        # least square only or grid search minimisation method
        else:
            # minimise
            model_fit = leastsq(self.models_residuals[str(self.model)], p_estimated, args=((y), (x), self.error, self.main.report_panel, True, self.main.spec_freq, self.main.SHIFT_DIFFERENCE[residue]), full_output = 1, col_deriv = 1, ftol = self.main.tolerance, xtol = self.main.tolerance, maxfev=2000000)

        # chi2
        chi2 = sum(Chi2_container.chi2)

        # set shift difference for model 5 and 6, if manually set
        if model in [3, 6, 7]:
            if self.main.SHIFT_DIFFERENCE[residue]:
                model_fit[0][2] = float(self.main.SHIFT_DIFFERENCE[residue])

        # Plot
        self.plot(model_fit[0], x, y, directory, residue, model, chi2)

        # save values
        self.global_models[str(model)].append({'residue':residue, 'fit':model_fit[0], 'chi2':chi2, 'n':n, 'n_exp':self.exp_no, 'x':x, 'y':y, 'variance':self.variance})

        # Printout formatting string.
        format = "%-20s %20.15f\n"

        # Write to summary
        if model == 1:
            # Chi2
            self.main.Model1_grid.SetCellValue(residue, 0, str(chi2))

            # Printout of the parameter values.
            wx.CallAfter(self.main.report_panel.AppendText, "\nFitted parameters:\n")
            for exp in range(0, self.num_exp[-1]):
                frq_MHz = "%.3f" % float(self.main.spec_freq[exp].GetValue())
                R2 = model_fit[0][exp]
                wx.CallAfter(self.main.report_panel.AppendText, format % ("R2 (%s MHz):" % frq_MHz, R2))
            wx.CallAfter(self.main.report_panel.AppendText, format % ("Chi-squared:", chi2))
            wx.CallAfter(self.main.report_panel.AppendText, "\n")

        if self.model == 2:
            kex = model_fit[0][0]
            phi = model_fit[0][1]*((float(self.main.spec_freq[0].GetValue()))*2 * Pi)**2

            # Phi
            self.main.Model2_grid.SetCellValue(residue, 2, str(phi))
            # kex
            self.main.Model2_grid.SetCellValue(residue, 0, str(kex))
            # chi2
            self.main.Model2_grid.SetCellValue(residue, 3, str(chi2))

            # Printout of the parameter values.
            wx.CallAfter(self.main.report_panel.AppendText, "\nFitted parameters:\n")
            for exp in range(0, self.num_exp[-1]):
                frq_MHz = "%.3f" % float(self.main.spec_freq[exp].GetValue())
                R2 = model_fit[0][2+exp]
                wx.CallAfter(self.main.report_panel.AppendText, format % ("R2 (%s MHz):" % frq_MHz, R2))
            wx.CallAfter(self.main.report_panel.AppendText, format % ("phi:", (model_fit[0][1])))
            wx.CallAfter(self.main.report_panel.AppendText, format % ("kex:", kex))
            wx.CallAfter(self.main.report_panel.AppendText, format % ("Chi-squared:", chi2))
            wx.CallAfter(self.main.report_panel.AppendText, "\n")

        if self.model == 3:
            kex = model_fit[0][0]
            pb = model_fit[0][1]
            dw = model_fit[0][2]*(float(self.main.spec_freq[0].GetValue())*2 * Pi)
            R2 = model_fit[0][3]
            # kex
            self.main.Model3_grid.SetCellValue(residue, 0, str(kex))
            # dw
            self.main.Model3_grid.SetCellValue(residue, 2, str(model_fit[0][2]))
            # pb
            self.main.Model3_grid.SetCellValue(residue, 3, str(model_fit[0][1]))
            # Chi2
            self.main.Model3_grid.SetCellValue(residue, 4, str(chi2))
            # dG
            dG = 8.3144621*298*log((1-pb)/pb)/1000
            self.main.Model3_grid.SetCellValue(residue, 5, str(dG))

            # Printout of the parameter values.
            wx.CallAfter(self.main.report_panel.AppendText, "\nFitted parameters:\n")
            for exp in range(0, self.num_exp[-1]):
                frq_MHz = "%.3f" % float(self.main.spec_freq[exp].GetValue())
                R2 = model_fit[0][3+exp]
                wx.CallAfter(self.main.report_panel.AppendText, format % ("R2 (%s MHz):" % frq_MHz, R2))
            wx.CallAfter(self.main.report_panel.AppendText, format % ("pA:", (1 - model_fit[0][1])))
            wx.CallAfter(self.main.report_panel.AppendText, format % ("pB:", (model_fit[0][1])))
            wx.CallAfter(self.main.report_panel.AppendText, format % ("dw:", (model_fit[0][2])))
            wx.CallAfter(self.main.report_panel.AppendText, format % ("kex:", kex))
            wx.CallAfter(self.main.report_panel.AppendText, format % ("Chi-squared:", chi2))
            wx.CallAfter(self.main.report_panel.AppendText, "\n")

        if self.model == 4:
            kex1 = model_fit[0][0]
            kex2 = model_fit[0][1]
            phi1 = model_fit[0][2]*((float(self.main.spec_freq[0].GetValue()))*2 * Pi)**2
            phi2 = model_fit[0][3]*((float(self.main.spec_freq[0].GetValue()))*2 * Pi)**2
            R2 = model_fit[0][4]
            # kex 1
            self.main.Model4_grid.SetCellValue(residue, 0, str(kex1))
            # Phi 1
            self.main.Model4_grid.SetCellValue(residue, 2, str(phi1))
            # kex 2
            self.main.Model4_grid.SetCellValue(residue, 3, str(kex2))
            # Phi 2
            self.main.Model4_grid.SetCellValue(residue, 5, str(phi2))
            # Chi2
            self.main.Model4_grid.SetCellValue(residue, 7, str(chi2))
        if self.model == 5:
            kex1 = model_fit[0][0]
            kex2 = model_fit[0][1]
            pb = model_fit[0][2]
            pc = model_fit[0][3]
            dw1 = model_fit[0][4]*(float(self.main.spec_freq[exp].GetValue())*2 * Pi)
            dw2 = model_fit[0][5]*(float(self.main.spec_freq[exp].GetValue())*2 * Pi)
            R2 = model_fit[0][exp+6]
            # kex 1
            self.main.Model5_grid.SetCellValue(residue, 0, str(kex1))
            # dw1 1
            self.main.Model5_grid.SetCellValue(residue, 2, str(model_fit[0][4]))
            # pb
            self.main.Model5_grid.SetCellValue(residue, 3, str(model_fit[0][2]))
            # kex 2
            self.main.Model5_grid.SetCellValue(residue, 4, str(kex2))
            # dw1 2
            self.main.Model5_grid.SetCellValue(residue, 6, str(model_fit[0][5]))
            # pc
            self.main.Model5_grid.SetCellValue(residue, 7, str(model_fit[0][3]))
            # chi2
            self.main.Model5_grid.SetCellValue(residue, 8, str(chi2))
        if self.model == 6:
            kex = model_fit[0][0]
            pb = model_fit[0][1]
            dw = model_fit[0][2]*(float(self.main.spec_freq[0].GetValue())*2 * Pi)
            R2 = model_fit[0][3]
            # kex
            self.main.Model6_grid.SetCellValue(residue, 0, str(kex))
            # dw
            self.main.Model6_grid.SetCellValue(residue, 2, str(model_fit[0][2]))
            # pb
            self.main.Model6_grid.SetCellValue(residue, 3, str(model_fit[0][1]))
            # Chi2
            self.main.Model6_grid.SetCellValue(residue, 4, str(chi2))
            # dG
            dG = 8.3144621*298*log((1-pb)/pb)/1000
            self.main.Model6_grid.SetCellValue(residue, 5, str(dG))
        if self.model == 7:
            kex = model_fit[0][0]
            pb = model_fit[0][1]
            dw = model_fit[0][2]*(float(self.main.spec_freq[0].GetValue())*2 * Pi)
            R2 = model_fit[0][3]
            # kex
            self.main.Model7_grid.SetCellValue(residue, 0, str(kex))
            # dw
            self.main.Model7_grid.SetCellValue(residue, 2, str(model_fit[0][2]))
            # pb
            self.main.Model7_grid.SetCellValue(residue, 3, str(model_fit[0][1]))
            # Chi2
            self.main.Model7_grid.SetCellValue(residue, 4, str(chi2))
            # dG
            dG = 8.3144621*298*log((1-pb)/pb)/1000
            self.main.Model7_grid.SetCellValue(residue, 5, str(dG))

        # Create Chi2 trace for models 2,3,6,7
        if self.model in [2, 3, 6, 7]:
            surface_plot(base_dir=str(self.main.proj_folder.GetValue()), fileroot='Residue_'+str(residue)+'_Model_'+str(self.model)+'_Trace', model=self.model, output=self.main.tree_results, savecont=self.main.plot3d, output1=self.main.plots3d, vec=self.main.PLOTFORMAT.replace('.', ''))


    def model1(self, mode):
        '''Fit to model 1.'''
        directory = str(self.main.proj_folder.GetValue())
        status = 0
        for i in range(0, self.main.RESNO):
            # self.minimise
            self.minimise(i, directory, 0, 1, mode)

            # Update progress bar
            progress = int((status * 100 ) / self.residue)
            wx.CallAfter(self.main.gauge_1.SetValue, min(100, progress))
            status = status + 1
            time.sleep(0.001)

        wx.CallAfter(self.main.gauge_1.SetValue, 0)


    def model2(self, mode):
        '''Fit to model 2.'''
        directory = str(self.main.proj_folder.GetValue())
        status = 0
        for i in range(0, self.main.RESNO):

            self.minimise(i, directory, 0, 2, mode)

            # Update progress bar
            progress = int((status * 100 ) / self.residue)
            wx.CallAfter(self.main.gauge_1.SetValue, min(100, progress))
            status = status + 1
            time.sleep(0.001)

        # Create .csv file
        file = open(directory+sep+self.main.TEXT_FOLDER+sep+'Model_2.csv', 'w')

        # fits
        fit_param = self.global_models['2'][0]['fit']

        # header
        header= 'Residue;kex [1/s];Phi [ppm**2]'
        n = (len(fit_param)-3)/2
        for h in range(0, n):
            header = header + ';R2_'+str(h+1)
        file.write(header+'\n')

        # content
        for i in range(0, len(self.global_models['2'])):
            text = str(self.global_models['2'][i]['residue']+1)+';'
            for entry in range(0, len(self.global_models['2'][i]['fit'])):
                text = text + str(self.global_models['2'][i]['fit'][entry]) + ';'
            file.write(text+'\n')
        file.close()

        # add file to results tree
        self.main.tree_results.AppendItem (self.main.txt, directory+sep+self.main.TEXT_FOLDER+sep+'Model_2.csv', 0)

        # save entry
        self.main.results_txt.append(directory+sep+self.main.TEXT_FOLDER+sep+'Model_2.csv')

        wx.CallAfter(self.main.gauge_1.SetValue, 0)


    def model3(self, mode):
        '''Fit to model 3.'''
        directory = str(self.main.proj_folder.GetValue())
        status = 0
        for i in range(0, self.main.RESNO):

            self.minimise(i, directory, 0, 3, mode)

            # Update progress bar
            progress = int((status * 100 ) / self.residue)
            wx.CallAfter(self.main.gauge_1.SetValue, min(100, progress))
            status = status + 1
            time.sleep(0.001)

        # Create .csv file
        file = open(directory+sep+self.main.TEXT_FOLDER+sep+'Model_3.csv', 'w')

        # fits
        fit_param = self.global_models['3'][0]['fit']

        # header
        header= 'Residue;kex [1/s];pb;dw [ppm];'
        n = (len(fit_param)-4)/2
        for h in range(0, n):
            header = header + ';R2_'+str(h+1)
        file.write(header+'\n')

        # content
        for i in range(0, len(self.global_models['3'])):
            text = str(self.global_models['3'][i]['residue']+1)+';'
            for entry in range(0, len(self.global_models['3'][i]['fit'])):
                text = text + str(self.global_models['3'][i]['fit'][entry]) + ';'
            file.write(text+'\n')
        file.close()

        # add file to results tree
        self.main.tree_results.AppendItem (self.main.txt, directory+sep+self.main.TEXT_FOLDER+sep+'Model_3.csv', 0)

        # save entry
        self.main.results_txt.append(directory+sep+self.main.TEXT_FOLDER+sep+'Model_3.csv')

        wx.CallAfter(self.main.gauge_1.SetValue, 0)


    def model4(self, mode):
        '''Fit to model 4.'''
        directory = str(self.main.proj_folder.GetValue())
        status = 0
        for i in range(0, self.main.RESNO):

            self.minimise(i, directory, 0, 4, mode)

            # Update progress bar
            progress = int((status * 100 ) / self.residue)
            wx.CallAfter(self.main.gauge_1.SetValue, min(100, progress))
            status = status + 1
            time.sleep(0.001)

        # Create .csv file
        file = open(directory+sep+self.main.TEXT_FOLDER+sep+'Model_4.csv', 'w')

        # fits
        fit_param = self.global_models['4'][0]['fit']

        # header
        header= 'Residue;kexA-B [1/s];kexB-C [1/s];PhiA-B [ppm**2];PhiB-C [ppm**2]'
        n = (len(fit_param)-3)/2
        for h in range(0, n):
            header = header + ';R2_'
        file.write(header+'\n')

        # content
        for i in range(0, len(self.global_models['4'])):
            text = str(self.global_models['4'][i]['residue']+1)+';'
            for entry in range(0, len(self.global_models['4'][i]['fit'])):
                text = text + str(self.global_models['4'][i]['fit'][entry]) + ';'
            file.write(text+'\n')
        file.close()

        # add file to results tree
        self.main.tree_results.AppendItem (self.main.txt, directory+sep+self.main.TEXT_FOLDER+sep+'Model_4.csv', 0)

        # save entry
        self.main.results_txt.append(directory+sep+self.main.TEXT_FOLDER+sep+'Model_4.csv')

        wx.CallAfter(self.main.gauge_1.SetValue, 0)


    def model5(self, mode):
        '''Fit to model 5.'''
        directory = str(self.main.proj_folder.GetValue())
        status = 0
        for i in range(0, self.main.RESNO):

            self.minimise(i, directory, 0, 5, mode)

            # Update progress bar
            progress = int((status * 100 ) / self.residue)
            wx.CallAfter(self.main.gauge_1.SetValue, min(100, progress))
            status = status + 1
            time.sleep(0.001)

        # Create .csv file
        file = open(directory+sep+self.main.TEXT_FOLDER+sep+'Model_5.csv', 'w')

        # fits
        fit_param = self.global_models['5'][0]['fit']

        # header
        header= 'Residue;kexA-B [1/s];kexB-C [1/s];pb;pc;dwA-B [ppm];dwB-C [ppm]'
        n = (len(fit_param)-5)/2
        for h in range(0, n):
            header = header + ';R2_'+str(h+1)
        file.write(header+'\n')

        # content
        for i in range(0, len(self.global_models['5'])):
            text = str(self.global_models['5'][i]['residue']+1)+';'
            for entry in range(0, len(self.global_models['5'][i]['fit'])):
                text = text + str(self.global_models['5'][i]['fit'][entry]) + ';'
            file.write(text+'\n')
        file.close()

        # add file to results tree
        self.main.tree_results.AppendItem (self.main.txt, directory+sep+self.main.TEXT_FOLDER+sep+'Model_5.csv', 0)

        # save entry
        self.main.results_txt.append(directory+sep+self.main.TEXT_FOLDER+sep+'Model_5.csv')

        wx.CallAfter(self.main.gauge_1.SetValue, 0)

    def model6(self, mode):
        '''Fit to model 6.'''
        directory = str(self.main.proj_folder.GetValue())
        status = 0
        for i in range(0, self.main.RESNO):

            self.minimise(i, directory, 0, 6, mode)

            # Update progress bar
            progress = int((status * 100 ) / self.residue)
            wx.CallAfter(self.main.gauge_1.SetValue, min(100, progress))
            status = status + 1
            time.sleep(0.001)

        # Create .csv file
        file = open(directory+sep+self.main.TEXT_FOLDER+sep+'Model_6.csv', 'w')

        # fits
        fit_param = self.global_models['6'][0]['fit']

        # header
        header= 'Residue;kex [1/s];pb;dw [ppm];'
        n = (len(fit_param)-4)/2
        for h in range(0, n):
            header = header + ';R2_'+str(h+1)
        file.write(header+'\n')

        # content
        for i in range(0, len(self.global_models['6'])):
            text = str(self.global_models['6'][i]['residue']+1)+';'
            for entry in range(0, len(self.global_models['6'][i]['fit'])):
                text = text + str(self.global_models['6'][i]['fit'][entry]) + ';'
            file.write(text+'\n')
        file.close()

        # add file to results tree
        self.main.tree_results.AppendItem (self.main.txt, directory+sep+self.main.TEXT_FOLDER+sep+'Model_6.csv', 0)

        # save entry
        self.main.results_txt.append(directory+sep+self.main.TEXT_FOLDER+sep+'Model_6.csv')

        wx.CallAfter(self.main.gauge_1.SetValue, 0)


    def model7(self, mode):
        '''Fit to model 7.'''
        directory = str(self.main.proj_folder.GetValue())
        status = 0
        for i in range(0, self.main.RESNO):

            self.minimise(i, directory, 0, 7, mode)

            # Update progress bar
            progress = int((status * 100 ) / self.residue)
            wx.CallAfter(self.main.gauge_1.SetValue, min(100, progress))
            status = status + 1
            time.sleep(0.001)

        # Create .csv file
        file = open(directory+sep+self.main.TEXT_FOLDER+sep+'Model_7.csv', 'w')

        # fits
        fit_param = self.global_models['7'][0]['fit']

        # header
        header= 'Residue;kex [1/s];pb;dw [ppm];'
        n = (len(fit_param)-4)/2
        for h in range(0, n):
            header = header + ';R2_'+str(h+1)
        file.write(header+'\n')

        # content
        for i in range(0, len(self.global_models['7'])):
            text = str(self.global_models['7'][i]['residue']+1)+';'
            for entry in range(0, len(self.global_models['7'][i]['fit'])):
                text = text + str(self.global_models['7'][i]['fit'][entry]) + ';'
            file.write(text+'\n')
        file.close()

        # add file to results tree
        self.main.tree_results.AppendItem (self.main.txt, directory+sep+self.main.TEXT_FOLDER+sep+'Model_7.csv', 0)

        # save entry
        self.main.results_txt.append(directory+sep+self.main.TEXT_FOLDER+sep+'Model_7.csv')

        wx.CallAfter(self.main.gauge_1.SetValue, 0)


    def model_selection(self, exp_mode):
        """Function for model selection."""
        # selection mode
        mode = self.main.SETTINGS[0]

        # model selection container
        self.selections = []

        # report
        wx.CallAfter(self.main.checkrun_label.SetLabel, 'Model selection')
        wx.CallAfter(self.main.report_panel.AppendText, '\n\n__________________________________\n\nModel Selection Mode: '+mode+'\n__________________________________\n\n')

        # loop over entries
        for entry in range(0, len(self.global_models['1'])):
            # Alpha model selection
            if mode == 'Alpha':
                    # Phi and kex
                    kex = self.global_models['2'][entry]['fit'][0]
                    Phi = self.global_models['2'][entry]['fit'][1]

                    # Model was not calculated
                    if kex == 0:
                        self.selections.append('1')
                        wx.CallAfter(self.main.report_panel.AppendText, '\nResidue '+str(self.global_models['1'][entry]['residue']+1)+' has no exchange\n')
                        time.sleep(0.2)
                        continue

                    # Static magnetic fields
                    B1 = float(self.main.B0[0].GetValue())
                    B2 = float(self.main.B0[1].GetValue())

                    # ppm to Hz
                    w1 = float(self.main.spec_freq[0].GetValue())*2 * Pi
                    w2 = float(self.main.spec_freq[1].GetValue())*2 * Pi

                    # Calculate Rex
                    Rex1 = (Phi * w1 * w1) / kex
                    Rex2 = (Phi * w2 * w2) / kex

                    # Calculate alpha
                    a = Alpha(B1, B2, Rex1, Rex2)

                    # store alpha value in summary
                    self.main.Final_grid.SetCellValue(int(self.global_models['1'][entry]['residue']), 17, str(a))

                    # Select
                    # slow exchange (model 3); alpha between 0 and 1
                    if a < 1:
                        self.selections.append('3')
                        wx.CallAfter(self.main.report_panel.AppendText, '\nResidue '+str(self.global_models['1'][entry]['residue']+1)+' is in slow exchange\n')
                        time.sleep(0.2)

                    # fast exchange
                    else:
                        self.selections.append('2')
                        wx.CallAfter(self.main.report_panel.AppendText, '\nResidue '+str(self.global_models['1'][entry]['residue']+1)+' is in fast exchange\n')
                        time.sleep(0.2)

                    # continue with next entry
                    continue

            # Manual selection
            if mode == 'Manual':
                # residue
                current_res = str(self.global_models['1'][entry]['residue']+1)

                # set to 1 if not set up
                if not self.main.MANUAL_SELECTION:
                    self.selections.append('1')
                    wx.CallAfter(self.main.report_panel.AppendText, '\nSelected Model 1 for Residue '+str(self.global_models['1'][entry]['residue']+1)+'\n')

                #detect selection
                else:
                    for i in range(len(self.main.MANUAL_SELECTION)):
                        # Match with selection
                        if str(self.main.MANUAL_SELECTION[i][0]) == current_res:
                            self.selections.append(str(self.main.MANUAL_SELECTION[i][1]))
                            wx.CallAfter(self.main.report_panel.AppendText, '\nSelected Model '+str(self.main.MANUAL_SELECTION[i][1])+' for Residue '+str(self.global_models['1'][entry]['residue']+1)+'\n')

                # calculate nes entry
                time.sleep(0.2)
                continue

            # AICc / AIC container
            aic = []

            # output
            wx.CallAfter(self.main.report_panel.AppendText, '\n\n'+mode+' Residue '+str(self.global_models['1'][entry]['residue']+1)+':\n----------------------------------------------------------------------\n')

            # loop over data container
            for model in range(0, (len(self.global_models)/2)):
                # exclude not calculated models
                if self.global_models[str(model+1)] == []:
                    continue

                # number of parameters
                if model == 0:
                    k = 1
                elif model == 1:
                    k = 4
                elif model in [2, 5, 6]:
                    k = 5
                elif model == 3:
                    k = 6
                elif model == 4:
                    k = 8

                # number of experiments
                n = self.global_models[str(model+1)][entry]['n']

                # chi2
                chi2 = self.global_models[str(model+1)][entry]['chi2']

                # AICc
                if mode == 'AICc':
                    aic.append([AICc(chi2, k, n), model+1])
                    wx.CallAfter(self.main.report_panel.AppendText, 'Model '+str(model+1)+': '+ str(AICc(chi2, k, n))+'\n')

                # AIC
                elif mode == 'AIC':
                    aic.append([AIC(chi2, k, n), model+1])
                    wx.CallAfter(self.main.report_panel.AppendText, 'Model '+str(model+1)+': '+ str(AIC(chi2, k, n))+'\n')

            # sort test values
            for i in range(0, len(aic)):
                for j in range(0, len(aic)):
                    # skip
                    if i == j:
                        continue

                    # swap entries
                    if aic[i][0] < aic[j][0]:
                        # swap entries
                        save = aic[j]
                        aic[j] = aic[i]
                        aic[i] = save

            # report
            wx.CallAfter(self.main.report_panel.AppendText, '\nModel '+str(aic[0][1])+' selected.\n')
            time.sleep(0.2)

            # append selections
            self.selections.append(str(aic[0][1]))


    def montecarlo(self, mode):
        """Monte Carlo Simulation.

        Rex and Phi is calculated for last experiment.
        """

        # Dummy model selection container
        self.main.MODEL_SELECTION = []
        self.main.MODEL_SELECTION_ERROR = []

        # Update Status
        wx.CallAfter(self.main.checkrun_label.SetLabel, 'Monte Carlo Simulation')
        wx.CallAfter(self.main.report_panel.AppendText, '\n\n----------------------------------------------------------\nMonte Carlo Simulation\n----------------------------------------------------------\n\n')

        # maximum number of entries
        self.max_entries = len(self.selections)

        # reser progress bar
        wx.CallAfter(self.main.gauge_1.SetValue, 0)

        # dictionaries of functions
        func = {'1':model_1, '2':model_2, '3':model_3, '4':model_4, '5':model_5, '6':model_6, '7':model_7}
        residuals = {'1':model_1_residuals, '2':model_2_residuals, '3':model_3_residuals, '4':model_4_residuals, '5':model_5_residuals, '6':model_6_residuals, '7':model_7_residuals}


        # loop over selections
        for sel in range(0, len(self.selections)):
            # container for extracted parameters per experiment
            p = []

            # Number of experiments
            expno = self.num_exp[sel]

            # empty error variables
            R2_err = [] * expno
            kex_err = []
            pb_err = []
            dw_err = []
            Phi_err = []
            kex2_err = []
            Phi2_err = []
            dw2_err = []
            pc_err = []

            # selected model
            model = str(self.selections[sel])

            # residue number
            residue_no = self.global_models[model][sel]['residue']+1

            # model 1
            if self.selections[sel] == '1':
                R2 = []
                for i in range(expno):
                    R2.append(self.global_models['1'][sel]['fit'][i])
                    p.append(self.global_models['1'][sel]['fit'][i])

                self.main.MODEL_SELECTION.append({'residue':self.global_models['1'][sel]['residue']+1, 'model':1, 'R2':R2[0], 'chi2':self.global_models['1'][sel]['chi2'], 'fit_params':self.global_models['1'][sel]['fit']})

            # model 2
            if self.selections[sel] == '2':
                phi=self.global_models['2'][sel]['fit'][1]
                kex=self.global_models['2'][sel]['fit'][0]
                R2 = []
                for i in range(expno):
                    R2.append(self.global_models['2'][sel]['fit'][2+i])
                    p.append([self.global_models['2'][sel]['fit'][2+i], phi*(float(self.main.spec_freq[i].GetValue())*2 * Pi)**2, kex])
                self.main.MODEL_SELECTION.append({'residue':self.global_models['2'][sel]['residue']+1, 'model':2, 'R2':R2[0], 'kex':kex, 'Rex':self.Rex(2, array([R2[0], phi*(2 * Pi*float(self.main.spec_freq[i].GetValue()))**2, kex])), 'chi2':self.global_models['2'][sel]['chi2'], 'fit_params':self.global_models['2'][sel]['fit']})

            # model 3
            if self.selections[sel] == '3':
                kex=self.global_models['3'][sel]['fit'][0]
                dw=self.global_models['3'][sel]['fit'][2]
                pb=self.global_models['3'][sel]['fit'][1]
                R2 = []
                for i in range(expno):
                    R2.append(self.global_models['3'][sel]['fit'][3+i])
                    p.append([self.global_models['3'][sel]['fit'][3+i], kex, dw*(float(self.main.spec_freq[i].GetValue())*2 * Pi), pb])

                self.main.MODEL_SELECTION.append({'residue':self.global_models['3'][sel]['residue']+1, 'model':3, 'R2':R2[0], 'kex':kex, 'dw':dw, 'pb':pb, 'Rex':self.Rex(3, array([R2[0], kex, dw*(2 * Pi*float(self.main.spec_freq[i].GetValue())), pb])), 'chi2':self.global_models['3'][sel]['chi2'], 'fit_params':self.global_models['3'][sel]['fit']})

            # model 4
            if self.selections[sel] == '4':
                kex1=self.global_models['4'][sel]['fit'][0]
                kex2=self.global_models['4'][sel]['fit'][1]
                Phi1=self.global_models['4'][sel]['fit'][2]
                Phi2=self.global_models['4'][sel]['fit'][3]
                R2 = []
                for i in range(expno):
                    R2.append(self.global_models['4'][sel]['fit'][4+i])
                    p.append([self.global_models['4'][sel]['fit'][4+i], Phi1*(2 * Pi*float(self.main.spec_freq[i].GetValue()))**2, kex1, Phi2*(2 * Pi*float(self.main.spec_freq[i].GetValue()))**2, kex2])

                self.main.MODEL_SELECTION.append({'residue':self.global_models['4'][sel]['residue']+1, 'model':4, 'R2':R2[0], 'kex':(kex1+kex2), 'kex1':kex1, 'kex2':kex2, 'Rex':self.Rex(4, array([R2[0], Phi1*(2 * Pi*float(self.main.spec_freq[i].GetValue()))**2, kex1, Phi2*(2 * Pi*float(self.main.spec_freq[i].GetValue()))**2, kex2])), 'chi2':self.global_models['4'][sel]['chi2'], 'fit_params':self.global_models['4'][sel]['fit']})

            # model 5
            if self.selections[sel] == '5':
                kex1=self.global_models['5'][sel]['fit'][0]
                kex2=self.global_models['5'][sel]['fit'][1]
                dw1=self.global_models['5'][sel]['fit'][4]
                dw2=self.global_models['5'][sel]['fit'][5]
                pb=self.global_models['5'][sel]['fit'][2]
                pc=self.global_models['5'][sel]['fit'][3]
                R2 = []
                for i in range(expno):
                    R2.append(self.global_models['5'][sel]['fit'][6+i])
                    p.append([self.global_models['5'][sel]['fit'][6+i], kex1, dw1*(2 * Pi*float(self.main.spec_freq[i].GetValue())), pb, kex2, dw2*(2 * Pi*float(self.main.spec_freq[i].GetValue())), pc])

                self.main.MODEL_SELECTION.append({'residue':self.global_models['5'][sel]['residue']+1, 'model':5, 'R2':R2[0], 'kex':(kex1+kex2), 'kex1':kex1, 'kex2':kex2, 'dw':dw1, 'dw2':dw2, 'pb':pb, 'pc':pc, 'Rex':self.Rex(5, array([R2[0], kex1, dw1*(2 * Pi*float(self.main.spec_freq[i].GetValue())), pb, kex2, dw2*(2 * Pi*float(self.main.spec_freq[i].GetValue())), pc])), 'chi2':self.global_models['5'][sel]['chi2'], 'fit_params':self.global_models['5'][sel]['fit']})

            # model 6
            if self.selections[sel] == '6':
                kex=self.global_models['6'][sel]['fit'][0]
                dw=self.global_models['6'][sel]['fit'][2]
                pb=self.global_models['6'][sel]['fit'][1]
                R2 = []
                for i in range(expno):
                    R2.append(self.global_models['6'][sel]['fit'][3+i])
                    p.append([self.global_models['6'][sel]['fit'][3+i], kex, dw*(float(self.main.spec_freq[i].GetValue())*2 * Pi), pb])

                self.main.MODEL_SELECTION.append({'residue':self.global_models['6'][sel]['residue']+1, 'model':6, 'R2':R2[0], 'kex':kex, 'dw':dw, 'pb':pb, 'Rex':self.Rex(6, array([R2[0], kex, dw*(2 * Pi*float(self.main.spec_freq[i].GetValue())), pb])), 'chi2':self.global_models['6'][sel]['chi2'], 'fit_params':self.global_models['6'][sel]['fit']})

            # model 7
            if self.selections[sel] == '7':
                kex=self.global_models['7'][sel]['fit'][0]
                dw=self.global_models['7'][sel]['fit'][2]
                pb=self.global_models['7'][sel]['fit'][1]
                R2 = []
                for i in range(expno):
                    R2.append(self.global_models['7'][sel]['fit'][3+i])
                    p.append([self.global_models['7'][sel]['fit'][3+i], kex, dw*(float(self.main.spec_freq[i].GetValue())*2 * Pi), pb])

                self.main.MODEL_SELECTION.append({'residue':self.global_models['7'][sel]['residue']+1, 'model':7, 'R2':R2[0], 'kex':kex, 'dw':dw, 'pb':pb, 'Rex':self.Rex(6, array([R2[0], kex, dw*(2 * Pi*float(self.main.spec_freq[i].GetValue())), pb])), 'chi2':self.global_models['7'][sel]['chi2'], 'fit_params':self.global_models['7'][sel]['fit']})

            # experimental x and y values
            x_value = self.global_models[model][sel]['x']
            y_value = self.global_models[model][sel]['y']

            # Monte Carlo simulation
            for mc in range(int(self.main.SETTINGS[1])):
                # Feedback
                wx.CallAfter(self.main.report_panel.AppendText, 'Monte Carlo Simulation ' + str(mc+1) + ', Residue '+str(residue_no)+'\n' )
                wx.Yield()

                # create synthetic y values
                y_synth = []

                # loop over experiments
                for exp in range(len(x_value)):
                    # temporary y container (one experiment)
                    y_sim = []

                    # error
                    error = sqrt(self.global_models[model][sel]['variance'][exp])

                    # loop over x values for particular experiment
                    for sim in range(len(x_value[exp])):
                        y_sim.append(func[model](x_value[exp][sim], p[exp])+uniform(-error, error))

                    # store simulated y values
                    y_synth.append(array(y_sim))

                # minimise new dataset
                # model 1
                if model == '1':
                    fit = leastsq(residuals[model], self.global_models[model][sel]['fit'], args=(y_synth, x_value, self.global_models[model][sel]['variance'], None, True), full_output = 1, col_deriv = 1, ftol = self.main.tolerance, xtol = self.main.tolerance, maxfev=20000000)

                    # Save fits
                    R2_err.append(fit[0])

                # models 2-7
                else:
                    fit = leastsq(residuals[model], self.global_models[model][sel]['fit'], args=(y_synth, x_value, self.global_models[model][sel]['variance'], None, True, self.main.spec_freq, self.main.SHIFT_DIFFERENCE[residue_no-1]), full_output = 1, col_deriv = 1, ftol = self.main.tolerance, xtol = self.main.tolerance, maxfev=20000000)

                    # store parameters
                    # R2
                    for ent in range(expno):
                        R2_err.append(float(fit[0][len(fit[0]) - expno + ent]))

                    # model 2
                    if model == '2':
                        kex_err.append(fit[0][0])
                        Phi_err.append(fit[0][1])

                    # model 3, 6
                    if model in ['3', '6', '7']:
                        kex_err.append(fit[0][0])
                        pb_err.append(fit[0][1])
                        dw_err.append(fit[0][2])

                    # model 4:
                    if model == '4':
                        kex_err.append(fit[0][0])
                        kex2_err.append(fit[0][1])
                        Phi_err.append(fit[0][2])
                        Phi2_err.append(fit[0][3])

                    # model 5:
                    if model == '5':
                        kex_err.append(fit[0][0])
                        kex2_err.append(fit[0][1])
                        pb_err.append(fit[0][2])
                        pc_err.append(fit[0][3])
                        dw_err.append(fit[0][4])
                        dw2_err.append(fit[0][5])

            # Calculate error
            residue = residue_no

            # R2
            error_R2 = []
            for i in range(len(R2_err)):
                error_R2.append(sqrt(var(R2_err, ddof = 1)))

            # model 1
            if model == '1':
                # Save entries
                self.main.MODEL_SELECTION_ERROR.append({'residue':residue, 'R2':error_R2[0]})

            # model 2
            elif model == '2':
                error_Phi = sqrt(var(Phi_err, ddof = 1))
                error_kex = sqrt(var(kex_err, ddof = 1))

                # calculate error of Rex
                Rex_err = []
                for calc_rex in range(0, len(kex_err)):
                    # Parameters
                    Phi = Phi_err[calc_rex]*(2 * Pi*float(self.main.spec_freq[expno-1].GetValue()))**2
                    kex = kex_err[calc_rex]
                    rex_tmp = Rex_fast(Phi, kex)
                    Rex_err.append(rex_tmp)
                error_Rex = sqrt(var(Rex_err, ddof = 1))

                # Save entries
                self.main.MODEL_SELECTION_ERROR.append({'residue':residue, 'R2':error_R2[0], 'Phi':error_Phi, 'kex':error_kex, 'Rex':error_Rex})

            # Model 3, 6 and 7
            elif model in ['3', '6', '7']:
                error_kex = sqrt(var(kex_err, ddof = 1))
                error_dw = sqrt(var(dw_err, ddof = 1))
                error_pb = sqrt(var(pb_err, ddof = 1))

                # calculate error of Rex
                Rex_err = []
                for calc_rex in range(0, len(kex_err)):
                    # Parameters
                    pb = pb_err[calc_rex]
                    kex = kex_err[calc_rex]
                    dw = dw_err[calc_rex]*2 * Pi*float(self.main.spec_freq[expno-1].GetValue())
                    rex_tmp = Rex_slow(pb, kex, dw)
                    Rex_err.append(rex_tmp)
                error_Rex = sqrt(var(Rex_err, ddof = 1))

                # Save entry
                self.main.MODEL_SELECTION_ERROR.append({'residue':residue, 'R2':error_R2[0], 'kex':error_kex, 'Rex':error_Rex, 'pb':error_pb, 'dw':error_dw})

            # Model 4
            elif model == '4':
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
                    Phi1 = Phi_err[i]*(2 * Pi*float(self.main.spec_freq[expno-1].GetValue()))**2
                    kex1 = kex_err[i]
                    rex1 = Rex_fast(Phi1, kex1)

                    # Rex 2
                    Phi2 = Phi2_err[i]*(2 * Pi*float(self.main.spec_freq[expno-1].GetValue()))**2
                    kex2 = kex2_err[i]
                    rex2 = Rex_fast(Phi2, kex2)

                    # Store rex
                    Rex_err.append(rex1+rex2)

                # Calculate error of Rex
                error_Rex = sqrt(var(Rex_err, ddof = 1))

                # Save entries
                self.main.MODEL_SELECTION_ERROR.append({'residue': residue, 'R2': error_R2[0], 'Phi': error_Phi, 'kex': error_kex_mean, 'kex1': error_kex, 'Rex': error_Rex, 'Phi2': error_Phi2, 'kex2': error_kex2,})

            # Model 5
            elif model == '5':
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
                    dw1 = dw_err[calc_rex]*2 * Pi*float(self.main.spec_freq[expno-1].GetValue())
                    dw2 = dw2_err[calc_rex]*2 * Pi*float(self.main.spec_freq[expno-1].GetValue())
                    kex1 = kex_err[calc_rex]
                    kex2 = kex2_err[calc_rex]

                    rex_tmp1 = Rex_slow(pb, kex1, dw1)
                    rex_tmp2 = Rex_slow(pc, kex2, dw2)

                    Rex_err.append(rex_tmp1+rex_tmp2)

                error_Rex = sqrt(var(Rex_err, ddof = 1))

                # Save entry
                self.main.MODEL_SELECTION_ERROR.append({'residue':residue, 'R2':error_R2[0], 'kex':error_kex_mean, 'kex1':error_kex, 'kex2':error_kex2, 'Rex':error_Rex, 'pb':error_pb, 'dw':error_dw, 'pc':error_pc, 'dw2':error_dw2})

            # update progress bar
            per = int(100 * sel / self.max_entries)
            wx.CallAfter(self.main.gauge_1.SetValue, min(100, per))

        # Create plots
        self.plots(Rex_exp=str(expno))


    def multiply_cpmgfreq(self):
        """Multiply to generate x values."""

        # Multiply CPMG frequencies to generate x values
        self.cpmgfreqs = []

        # loop over calculated experiments
        for exp in range(0, self.main.NUMOFDATASETS):
            # add cpmg freq
            self.cpmgfreqs.append(self.main.CPMGFREQ[exp])


    def Rex(self, model, p):
        """Function to calculate Rex

        Model 2:    Rex = Phi / kex, (Phi = pa * pb * dw^2)

        Model 3:    Rex = (pa * pb * dw^2) / kex

        Model 4:    Rex1 = Phi1 / kex
                    Rex2 = Phi2 / kex"""

        Rex = None

        # Model 2 (fast exchange)
        if model == 2:
            phi = p[1]
            kex = p[2]

            Rex = phi / kex

            return Rex

        # Model 3 (slow exchange)
        if model in [3, 6, 7]:
            pb=p[3]
            pa=1-pb
            kex=p[1]
            dw=p[2]

            Rex = (pa * pb * kex * (dw)**2) / (kex**2 + dw**2)

            return Rex

        # Model 4 (A - B -C)
        if model == 4:
            phi=p[1]
            kex=p[2]
            phi2=p[3]
            kex2=p[4]

            # Rex A-B
            rex1 = phi / kex

            # Rex B -C
            rex2 = phi2 / kex2

            # Rex
            Rex = rex1 + rex2

            return Rex

        if model == 5:
            pb=p[3]
            kex=p[1]
            dw=p[2]
            pc=p[6]
            kex2=p[4]
            dw2=p[5]
            pa = 1-pb-pc

            Rex = (((pa+pc)*pb*kex*dw**2)/(kex**2+dw**2)) + (((pa+pb)*pc*kex2*dw2**2)/(kex2**2+dw2**2))

            return Rex
