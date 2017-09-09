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


# script to select model

# Python modules
from math import sqrt
from numpy import array
from os import sep
import pylab
import sys
import time
import wx

# NESSY modules
from func.montecarlo import montecarlo
from math_fns.tests import Alpha, AIC, AICc, F_test
from curvefit.exclude import exclude



class Model_Selection():
    """Model Selection to find best fit."""
    def __init__(self, main, directory, exp_index, exp_mode):
        # link parameters
        self.main = main

        # Experiment index
        self.exp_index = exp_index

        # Prepare output
        self.selected_model = [] # Residue, Model, R2, kex, pb, dw, kex2, rex2

        # combine models
        self.main.MODEL = []
        if not self.main.MODEL1 == []:
             self.main.MODEL.append([1, self.main.MODEL1])
        if not self.main.MODEL2 == []:
             self.main.MODEL.append([2, self.main.MODEL2])
        if not self.main.MODEL3 == []:
             self.main.MODEL.append([3, self.main.MODEL3])
        if not self.main.MODEL4 == []:
             self.main.MODEL.append([4, self.main.MODEL4])
        if not self.main.MODEL5 == []:
             self.main.MODEL.append([5, self.main.MODEL5])
        if not self.main.MODEL6 == []:
             self.main.MODEL.append([6, self.main.MODEL6])

        # Abort if no model was calculated
        if self.main.MODEL == []:
            return

        # only 1 model was selected
        if len(self.main.MODEL) < 2:
            # only model 1
            if self.main.MODEL[0][0] == 1:
                for i in range(0, len(self.main.MODEL1)):
                    self.selected_model.append({'residue':self.main.MODEL1[i][0], 'model':1, 'r2':self.main.MODEL1[i][1], 'chi2':self.main.MODEL1[i][2]})

            # only model 2
            if self.main.MODEL[0][0] == 2:
                for i in range(0, len(self.main.MODEL2)):
                    self.selected_model.append({'residue':self.main.MODEL2[i][0], 'model':2, 'r2':self.main.MODEL2[i][1][0], 'kex':self.main.MODEL2[i][1][2], 'Rex':self.Rex(2, i+1), 'chi2':self.main.MODEL2[i][2]})

            # only model 3
            if self.main.MODEL[0][0] == 3:
                for i in range(0, len(self.main.MODEL3)):
                    self.selected_model.append({'residue':self.main.MODEL3[i][0], 'model':3, 'r2':self.main.MODEL3[i][1][0], 'kex':self.main.MODEL3[i][1][1], 'Rex':self.Rex(3, i+1), 'dw':self.main.MODEL3[i][1][2], 'pb':self.main.MODEL3[i][1][3], 'chi2':self.main.MODEL3[i][2]})

            # only model 4
            if self.main.MODEL[0][0] == 4:
                for i in range(0, len(self.main.MODEL4)):
                    self.selected_model.append({'residue':self.main.MODEL4[i][0], 'model':2, 'r2':self.main.MODEL4[i][1][0], 'kex1':self.main.MODEL4[i][1][2], 'Rex1':self.Rex(41, i+1), 'kex2':self.main.MODEL4[i][1][4], 'Rex2':self.Rex(42, i+1), 'chi2':self.main.MODEL4[i][2]})

                        # only model 4
            if self.main.MODEL[0][0] == 5:
                for i in range(0, len(self.main.MODEL5)):
                    self.selected_model.append({'residue':self.main.MODEL5[i][0], 'model':5, 'r2':self.main.MODEL5[i][1][0], 'kex':self.main.MODEL5[i][1][1], 'Rex': None, 'dw':self.main.MODEL5[i][1][2], 'xi':self.main.MODEL5[i][1][3], 'chi2':self.main.MODEL5[i][2]})

            # only model 6
            if self.main.MODEL[0][0] == 6:
                for i in range(0, len(self.main.MODEL6)):
                    self.selected_model.append({'residue':self.main.MODEL6[i][0], 'model':6, 'r2':self.main.MODEL6[i][1][0], 'kex':self.main.MODEL6[i][1][1], 'Rex':self.Rex(6, i+1), 'dw':self.main.MODEL6[i][1][2], 'pb':self.main.MODEL6[i][1][3], 'chi2':self.main.MODEL6[i][2]})

            # abort
            return


        # read model selection mode
        mode = self.main.SETTINGS[0]

        # Manual model selection
        if mode == 'Manual' and self.main.MANUAL_SELECTION:
            # loop over selections
            for i in range(len(self.main.MANUAL_SELECTION)):
                # chosen model
                if self.main.MANUAL_SELECTION:
                    model_chosen = str(self.main.MANUAL_SELECTION[i][1])
                else:
                    model_chosen = '1'

                # residue
                selected_residue = str(self.main.MANUAL_SELECTION[i][0])

                # Calculated flag
                calc = False

                # model 1
                if model_chosen == '1':
                    # find matchin residue
                    for entry in range(len(self.main.MODEL1)):
                        # match
                        if str(self.main.MODEL1[entry][0]) == selected_residue:
                            self.selected_model.append({'residue':self.main.MODEL1[entry][0], 'model':1, 'R2':float(self.main.MODEL1[entry][1]), 'chi2':self.main.MODEL1[entry][2], 'fit_params':self.main.MODEL1[entry][1]})
                            calc = True

                # model 2
                if model_chosen == '2':
                    # find matchin residue
                    for entry in range(len(self.main.MODEL2)):
                        # match
                        if str(self.main.MODEL2[entry][0]) == selected_residue and not self.main.MODEL2[entry][1][0] == 0:
                            self.selected_model.append({'residue':self.main.MODEL2[entry][0], 'model':2, 'R2':self.main.MODEL2[entry][1][0], 'kex':self.main.MODEL2[entry][1][2], 'Rex':self.Rex(2, self.main.MODEL2[entry][0]), 'chi2':self.main.MODEL2[entry][2], 'fit_params':self.main.MODEL2[entry][1]})
                            calc = True

                # model 3
                if model_chosen == '3':
                    # find matchin residue
                    for entry in range(len(self.main.MODEL3)):
                        # match
                        if str(self.main.MODEL3[entry][0]) == selected_residue and not self.main.MODEL2[entry][1][0] == 0:
                            self.selected_model.append({'residue':self.main.MODEL3[entry][0], 'model':3, 'R2':self.main.MODEL3[entry][1][0], 'kex':self.main.MODEL3[entry][1][1], 'Rex':self.Rex(3, self.main.MODEL3[entry][0]), 'dw':self.main.MODEL3[entry][1][2], 'pb':self.main.MODEL3[entry][1][3], 'chi2':self.main.MODEL3[entry][2], 'fit_params':self.main.MODEL3[entry][1]})
                            calc = True

                # model 4
                if model_chosen == '4':
                    # find matchin residue
                    for entry in range(len(self.main.MODEL4)):
                        # match
                        if str(self.main.MODEL4[entry][0]) == selected_residue and not self.main.MODEL2[entry][1][0] == 0:
                            self.selected_model.append({'residue':self.main.MODEL4[entry][0], 'model':4, 'R2':self.main.MODEL4[entry][1][0], 'kex':self.main.MODEL4[entry][1][2]+self.main.MODEL4[entry][1][4],'kex1':self.main.MODEL4[entry][1][2], 'Rex':self.Rex(4, self.main.MODEL4[entry][0]), 'kex2':self.main.MODEL4[entry][1][4], 'chi2':self.main.MODEL4[entry][2], 'fit_params':self.main.MODEL4[entry][1]})
                            calc = True

                # model 5
                if model_chosen == '5':
                    # find matchin residue
                    for entry in range(len(self.main.MODEL5)):
                        # match
                        if str(self.main.MODEL5[entry][0]) == selected_residue and not self.main.MODEL2[entry][1][0] == 0:
                            self.selected_model.append({'residue':self.main.MODEL5[entry][0], 'model':5, 'R2':self.main.MODEL5[entry][1][0], 'kex':self.main.MODEL5[entry][1][1]+self.main.MODEL5[entry][1][4], 'kex1':self.main.MODEL5[entry][1][1], 'kex2':self.main.MODEL5[entry][1][4], 'Rex':self.Rex(5, self.main.MODEL5[entry][0]), 'pb':self.main.MODEL5[entry][1][3], 'dw':self.main.MODEL5[entry][1][2], 'pc':self.main.MODEL5[entry][1][6], 'dw2':self.main.MODEL5[entry][1][5], 'chi2':self.main.MODEL5[entry][2],'fit_params':self.main.MODEL5[entry][1]})
                            calc = True

                # model 6
                if model_chosen == '6':
                    # find matchin residue
                    for entry in range(len(self.main.MODEL6)):
                        # match
                        if str(self.main.MODEL6[entry][0]) == selected_residue and not self.main.MODEL2[entry][1][0] == 0:
                            self.selected_model.append({'residue':self.main.MODEL6[entry][0], 'model':6, 'R2':self.main.MODEL6[entry][1][0], 'kex':self.main.MODEL6[entry][1][1], 'Rex':self.Rex(6, self.main.MODEL6[entry][0]), 'dw':self.main.MODEL6[entry][1][2], 'pb':self.main.MODEL6[entry][1][3], 'chi2':self.main.MODEL6[entry][2], 'fit_params':self.main.MODEL6[entry][1]})
                            calc = True

                # only model 1 calculated
                if not calc:
                    # find matchin residue
                    for entry in range(len(self.main.MODEL1)):
                        # match
                        if str(self.main.MODEL1[entry][0]) == selected_residue:
                            self.selected_model.append({'residue':self.main.MODEL1[entry][0], 'model':1, 'R2':float(self.main.MODEL1[entry][1]), 'chi2':self.main.MODEL1[entry][2], 'fit_params':self.main.MODEL1[entry][1]})

        # Manual model selection is not set up
        else:
            mode = 'AICc'

        # least chi2
        if mode == 'Chi2':
            wx.CallAfter(self.main.report_panel.AppendText, '\n\n__________________________________\n\nModel Selection Mode: Chi2\n__________________________________\n\n')
            time.sleep(0.5)
            self.select('Chi2')

        # F-test
        if mode == 'F':
            wx.CallAfter(self.main.report_panel.AppendText, '\n\n__________________________________\n\nModel Selection Mode: F-Test\n__________________________________\n\n')
            time.sleep(0.5)
            self.select('F-test')

        # AIC
        if mode == 'AIC':
            wx.CallAfter(self.main.report_panel.AppendText, '\n\n__________________________________\n\nModel Selection Mode: AIC\n__________________________________\n\n')
            time.sleep(0.5)
            self.select('AIC')

        # AICc (AIC with second order correction)
        if mode == 'AICc':
            wx.CallAfter(self.main.report_panel.AppendText, '\n\n__________________________________\n\nModel Selection Mode: AICc\n__________________________________\n\n')
            time.sleep(0.5)
            self.select('AICc')

        # save model selection.
        self.main.MODEL_SELECTION = self.selected_model

        # Monte Carlo Simulations
        self.main.MODEL_SELECTION_ERROR = montecarlo(exp_index=self.exp_index, exp_mode=exp_mode, mc_num=int(self.main.SETTINGS[1]), tolerance=self.main.tolerance, checkrun_label=self.main.checkrun_label, isglobal=None, progressbar=self.main.gauge_1, report_panel=self.main.report_panel, selected_models=self.main.MODEL_SELECTION, Variance=self.main.R2eff_variance, X_values=self.main.CPMGFREQ)

        # Create plots
        self.create_plots()

        # Chi2 and AICc plots
        self.chi2_plots()


    def chi2_plots(self):
        """Function to create Chi2 plots and csv files."""
        # output directory
        directory = str(self.main.proj_folder.GetValue())

        # prefix
        self.prefix = 'Exp_'+str(self.exp_index+1)+'_'
        # Global fit
        if self.main.ISGLOBAL:
            self.prefix = 'Global_fit_'

        # create plots
        # loop over models
        for i in range(0, len(self.main.MODEL)):
            # if model was calculated
            if not self.main.MODEL[i] == []:
                residue = []
                chi2 = []
                aicc = []

                # loop over entries
                for entry in range(0, len(self.main.MODEL[i][1])):
                    residue.append(self.main.MODEL[i][1][entry][0])
                    chi2.append(self.main.MODEL[i][1][entry][2])

                    # AICc
                    k = 0
                    # Number of parameters
                    if self.main.MODEL[i][0] == 1:
                        k = 1
                    if self.main.MODEL[i][0] == 2:
                        k = 4
                    if self.main.MODEL[i][0] == 3:
                        k = 5
                    if self.main.MODEL[i][0] == 4:
                        k = 6
                    if self.main.MODEL[i][0] == 5:
                        k = 8
                    if self.main.MODEL[i][0] == 6:
                        k = 5

                    # number of experiments
                    n = 0
                    for e in range(0, len(self.main.CPMGFREQ[self.exp_index])):
                        if not self.main.CPMGFREQ[self.exp_index][e] == '':
                            n = n + 1

                    aicc.append(AICc(self.main.MODEL[i][1][entry][2], k, n))

                # Create csv file
                filename = directory+sep+'R2eff_txt'+sep+self.prefix+'Model_'+str(self.main.MODEL[i][0])+'_Chi2-AICc.csv'
                file = open(filename, 'w')
                file.write('Resdiue;Chi2;AICc\n')
                for t in range(0, len(residue)):
                    file.write(str(residue[t])+';'+str(chi2[t])+';'+str(aicc[t])+'\n')
                file.close()

                # save entries
                # Add csv file to results tree.
                self.main.tree_results.AppendItem (self.main.txt, filename, 0)

                # Save csv file
                self.main.results_txt.append(filename)

                # Create plots

                # Chi2
                pylab.plot(residue, chi2, 'ko')
                pylab.xticks(fontsize=19)
                pylab.yticks(fontsize=19)
                pylab.xlabel('Residue Number', fontsize=19, weight='bold')
                pylab.ylabel('Chi2', fontsize=19, weight='bold')

                # png
                filename = directory+sep+'R2eff_plots'+sep+'png'+sep+self.prefix+'Model_'+str(self.main.MODEL[i][0])+'_Chi2.png'
                pylab.savefig(filename, dpi = 72, transparent = True)
                # add to results tree
                self.main.tree_results.AppendItem (self.main.plots_modelselection, filename, 0)
                self.main.FINAL_RESULTS.append(filename)

                # svg
                pylab.savefig(directory+sep+'R2eff_plots'+sep+self.main.PLOTFORMAT.replace('.', '')+sep+self.prefix+'Model_'+str(self.main.MODEL[i][0])+'_Chi2'+self.main.PLOTFORMAT)

                # Clear plots
                pylab.cla() # clear the axes
                pylab.close() #clear figure

                # AICc
                pylab.plot(residue, aicc, 'ko')
                pylab.xticks(fontsize=19)
                pylab.yticks(fontsize=19)
                pylab.xlabel('Residue Number', fontsize=19, weight='bold')
                pylab.ylabel('AICc', fontsize=19, weight='bold')

                # png
                filename = directory+sep+'R2eff_plots'+sep+'png'+sep+self.prefix+'Model_'+str(self.main.MODEL[i][0])+'_AICc.png'
                pylab.savefig(filename, dpi = 72, transparent = True)
                # add to results tree
                self.main.tree_results.AppendItem (self.main.plots_modelselection, filename, 0)
                self.main.FINAL_RESULTS.append(filename)

                # svg
                pylab.savefig(directory+sep+'R2eff_plots'+sep+self.main.PLOTFORMAT.replace('.', '')+sep+self.prefix+'Model_'+str(self.main.MODEL[i][0])+'_AICc'+self.main.PLOTFORMAT)

                # Clear plots
                pylab.cla() # clear the axes
                pylab.close() #clear figure


    def create_plots(self):
        # output directory
        directory = str(self.main.proj_folder.GetValue())

        # prefix
        self.prefix = 'Exp_'+str(self.exp_index+1)+'_'
        # Global fit
        if self.main.ISGLOBAL:
            self.prefix = 'Global_fit_'

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

        # loop over entries
        for i in range(0, len(self.main.MODEL_SELECTION)):
            # Detect model
            model = self.main.MODEL_SELECTION[i]['model']

            # Residue Number
            x_values.append(self.main.MODEL_SELECTION[i]['residue'])

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

            # Model 2
            if model == 2:
                # kex
                y_kex[i] = self.main.MODEL_SELECTION[i]['kex']
                y_kex_err[i] = self.main.MODEL_SELECTION_ERROR[i]['kex']

                # Rex
                y_Rex[i] = self.main.MODEL_SELECTION[i]['Rex']
                y_Rex_err[i] = self.main.MODEL_SELECTION_ERROR[i]['Rex']

            # Model 3
            if model in [3, 6]:
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
            # R2
            self.main.Final_grid.SetCellValue(x_values[i]-1, 1, str(y_R2[i])[:9])
            self.main.Final_grid.SetCellValue(x_values[i]-1, 2, str(y_R2_err[i])[:9])
            # Rex
            if y_Rex[i]:
                self.main.Final_grid.SetCellValue(x_values[i]-1, 3, str(y_Rex[i])[:9])
                self.main.Final_grid.SetCellValue(x_values[i]-1, 4, str(y_Rex_err[i])[:9])
            # kex (1)
            if y_kex[i]:
                self.main.Final_grid.SetCellValue(x_values[i]-1, 5, str(y_kex[i])[:9])
                self.main.Final_grid.SetCellValue(x_values[i]-1, 6, str(y_kex_err[i])[:9])
                if sel_model[i] in [4, 5]:
                    self.main.Final_grid.SetCellValue(x_values[i]-1, 5, str(y_kex1[i])[:9])
                    self.main.Final_grid.SetCellValue(x_values[i]-1, 6, str(y_kex1_err[i])[:9])
            # dw 1
            if dw_value[i]:
                self.main.Final_grid.SetCellValue(x_values[i]-1, 7, str(dw_value[i])[:9])
                self.main.Final_grid.SetCellValue(x_values[i]-1, 8, str(dw_value_err[i])[:9])
            # pb
            if pb_value[i]:
                self.main.Final_grid.SetCellValue(x_values[i]-1, 9, str(pb_value[i])[:9])
                self.main.Final_grid.SetCellValue(x_values[i]-1, 10, str(pb_value_err[i])[:9])
            # kex 2
            if y_kex2[i]:
                self.main.Final_grid.SetCellValue(x_values[i]-1, 11, str(y_kex2[i])[:9])
                self.main.Final_grid.SetCellValue(x_values[i]-1, 12, str(y_kex2_err[i])[:9])
            # dw 1
            if dw2_value[i]:
                self.main.Final_grid.SetCellValue(x_values[i]-1, 13, str(dw2_value[i])[:9])
                self.main.Final_grid.SetCellValue(x_values[i]-1, 14, str(dw2_value_err[i])[:9])
            # pc
            if pc_value[i]:
                self.main.Final_grid.SetCellValue(x_values[i]-1, 15, str(pc_value[i])[:9])
                self.main.Final_grid.SetCellValue(x_values[i]-1, 16, str(pc_value_err[i])[:9])

        # Create csv file
        # header
        text = 'Residue;Model;R2 [1/s];err;Rex total [1/s];err;kex [1/s];err;pb;err;dw [1/s];err;kex1 [1/s];err;pc;err;dw2 [1/s];err;kex2 [1/s];err\n'

        # Data
        for i in range(0, len(x_values)):
            text = text + str(x_values[i]) + ';'+str(sel_model[i])+';'+str(y_R2[i])+';'+str(y_R2_err[i])+';'+str(y_Rex[i])+';'+str(y_Rex_err[i])+';'+str(y_kex[i])+';'+str(y_kex_err[i])+';'+str(pb_value[i])+';'+str(pb_value_err[i])+';'+str(dw_value[i])+';'+str(dw_value_err[i])+';'+str(y_kex1[i])+';'+str(y_kex1_err[i])+';'+str(pc_value[i])+';'+str(pc_value_err[i])+';'+str(dw2_value[i])+';'+str(dw2_value_err[i])+';'+str(y_kex2[i])+';'+str(y_kex2_err[i])+'\n'

        # replace None
        text = text.replace('None', '')

        # create file
        filename = directory + sep + 'R2eff_txt' + sep +self.prefix+ 'Model_selection.csv'
        file = open(filename, 'w')
        file.write(text)
        file.close()

        # Add csv file to results tree.
        self.main.tree_results.AppendItem (self.main.txt, filename, 0)

        # Save csv file
        self.main.results_txt.append(filename)

        # Create Plots
        directory = directory + sep + 'R2eff_plots'

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

        # Model Selection plot
        pylab.xticks(fontsize=19)
        pylab.yticks(fontsize=19)
        pylab.plot(x_values, sel_model, 'ko')
        pylab.xlim(min-5, max+5)
        pylab.ylim(0, 7)
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
            pylab.ylabel('Rex [1/s]', fontsize=19, weight='bold')

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


    def Rex(self, model, residue):
        """Function to calculate Rex

        Model 2:    Rex = Phi / kex, (Phi = pa * pb * dw^2)

        Model 3:    Rex = (pa * pb * dw^2) / kex

        Model 4:    Rex1 = Phi1 / kex
                    Rex2 = Phi2 / kex"""

        Rex = None

        # Model 2 (fast exchange)
        if model == 2:

            for i in range(0, len(self.main.MODEL2)):
                if self.main.MODEL2[i][0] == residue:
                    phi = self.main.MODEL2[i][1][1]
                    kex = self.main.MODEL2[i][1][2]

            Rex = phi / kex

            return Rex

        # Model 3 (slow exchange)
        if model == 3:

            for i in range(0, len(self.main.MODEL3)):
                if self.main.MODEL3[i][0] == residue:
                    kex = self.main.MODEL3[i][1][1]
                    dw = self.main.MODEL3[i][1][2]
                    pb = self.main.MODEL3[i][1][3]
                    pa = 1 - pb


            Rex = (pa * pb * kex * (dw)**2) / (kex**2 + dw**2)

            return Rex

        # Model 4 (A - B -C)
        if model == 4:

            for i in range(0, len(self.main.MODEL4)):
                if self.main.MODEL4[i][0] == residue:
                    # A - B
                    phi = self.main.MODEL4[i][1][1]
                    kex = self.main.MODEL4[i][1][2]
                    # B - C
                    phi2 = self.main.MODEL4[i][1][3]
                    kex2 = self.main.MODEL4[i][1][4]

            # Rex A-B
            rex1 = phi / kex

            # Rex B -C
            rex2 = phi2 / kex2

            # Rex
            Rex = rex1 + rex2

            return Rex

        if model == 5:

            for i in range(0, len(self.main.MODEL3)):
                if self.main.MODEL3[i][0] == residue:
                    kex = self.main.MODEL5[i][1][1]
                    dw = self.main.MODEL5[i][1][2]
                    pb = self.main.MODEL5[i][1][3]
                    kex2 = self.main.MODEL5[i][1][4]
                    dw2 = self.main.MODEL5[i][1][5]
                    pc = self.main.MODEL5[i][1][6]
                    pa = 1 - (pb+pc)


            Rex = (((pa+pc)*pb*kex*dw**2)/(kex**2+dw**2)) + (((pa+pb)*pc*kex2*dw2**2)/(kex2**2+dw2**2))

            return Rex

        # Model 6
        if model == 6:

            for i in range(0, len(self.main.MODEL6)):
                if self.main.MODEL6[i][0] == residue:
                    kex = self.main.MODEL6[i][1][1]
                    dw = self.main.MODEL6[i][1][2]
                    pb = self.main.MODEL6[i][1][3]
                    pa = 1 - pb


            Rex = (pa * pb * kex * (dw)**2) / (kex**2 + dw**2)

            return Rex



    def select(self, test):
        """Model selection according to Akaike information criterion with correction for small sample size."""

        for entry in range(0, len(self.main.MODEL[0][1])):   # loop over calculated entries of lowest model

            # Number of parameters
            k1 = 1  # number of parameters for model 1
            k2 = 4  # number of parameters for model 2
            k3 = 5  # number of parameters for model 3
            k4 = 6  # number of parameters for model 4
            k5 = 8  # number of parameters for model 5

            # Num of datasets
            n=0
            for i in range(0, len(self.main.CPMGFREQ[self.exp_index])):
                if not self.main.CPMGFREQ[self.exp_index][i] == '':
                    n = n+1
            n = n-1  #exclude reference

            # Residue
            residue = str(self.main.MODEL[0][1][entry][0])

            # calculate statistical tests
            calc_test = []

            # output
            wx.CallAfter(self.main.report_panel.AppendText, '\n\n'+test+' Residue '+residue+':\n----------------------------------------------------------------------\n')

            for i in range(0, len(self.main.MODEL)):     # loop over calculated models
                # detect model
                model = self.main.MODEL[i][0]

                # Calculate AICc
                if test in ['AICc', 'Alpha']:
                    if model == 1:
                        calc_test.append([AICc(self.main.MODEL[i][1][entry][2], k1, n), 1])
                        wx.CallAfter(self.main.report_panel.AppendText, 'Model 1: '+ str(AICc(self.main.MODEL[i][1][entry][2], k1, n))+'\n')

                    if model == 2:
                        calc_test.append([AICc(self.main.MODEL[i][1][entry][2], k2, n), 2])
                        wx.CallAfter(self.main.report_panel.AppendText, 'Model 2: '+ str(AICc(self.main.MODEL[i][1][entry][2], k2, n))+'\n')

                    if model == 3:
                        calc_test.append([AICc(self.main.MODEL[i][1][entry][2], k3, n), 3])
                        wx.CallAfter(self.main.report_panel.AppendText, 'Model 3: '+ str(AICc(self.main.MODEL[i][1][entry][2], k3, n))+'\n')

                    if model == 4:
                        calc_test.append([AICc(self.main.MODEL[i][1][entry][2], k4, n), 4])
                        wx.CallAfter(self.main.report_panel.AppendText, 'Model 4: '+ str(AICc(self.main.MODEL[i][1][entry][2], k4, n))+'\n')

                    if model == 5:
                        calc_test.append([AICc(self.main.MODEL[i][1][entry][2], k5, n), 5])
                        wx.CallAfter(self.main.report_panel.AppendText, 'Model 5: '+ str(AICc(self.main.MODEL[i][1][entry][2], k4, n))+'\n')

                    if model == 6:
                        calc_test.append([AICc(self.main.MODEL[i][1][entry][2], k3, n), 6])
                        wx.CallAfter(self.main.report_panel.AppendText, 'Model 6: '+ str(AICc(self.main.MODEL[i][1][entry][2], k3, n))+'\n')


                # Calculate AIC
                if test == 'AIC':
                    if model == 1:
                        calc_test.append([AIC(self.main.MODEL[i][1][entry][2], k1), 1])
                        wx.CallAfter(self.main.report_panel.AppendText, 'Model 1: '+ str(AIC(self.main.MODEL[i][1][entry][2], k1))+'\n')

                    if model == 2:
                        calc_test.append([AIC(self.main.MODEL[i][1][entry][2], k2), 2])
                        wx.CallAfter(self.main.report_panel.AppendText, 'Model 2: '+ str(AIC(self.main.MODEL[i][1][entry][2], k2))+'\n')

                    if model == 3:
                        calc_test.append([AIC(self.main.MODEL[i][1][entry][2], k3), 3])
                        wx.CallAfter(self.main.report_panel.AppendText, 'Model 3: '+ str(AIC(self.main.MODEL[i][1][entry][2], k3))+'\n')

                    if model == 4:
                        calc_test.append([AIC(self.main.MODEL[i][1][entry][2], k4), 4])
                        wx.CallAfter(self.main.report_panel.AppendText, 'Model 4: '+ str(AIC(self.main.MODEL[i][1][entry][2], k4))+'\n')

                    if model == 5:
                        calc_test.append([AIC(self.main.MODEL[i][1][entry][2], k5, n), 5])
                        wx.CallAfter(self.main.report_panel.AppendText, 'Model 5: '+ str(AIC(self.main.MODEL[i][1][entry][2], k4, n))+'\n')

                    if model == 6:
                        calc_test.append([AIC(self.main.MODEL[i][1][entry][2], k3, n), 6])
                        wx.CallAfter(self.main.report_panel.AppendText, 'Model 6: '+ str(AIC(self.main.MODEL[i][1][entry][2], k3, n))+'\n')


                # Calculate AIC
                if test == 'Chi2':
                    if model == 1:
                        calc_test.append([self.main.MODEL[i][1][entry][2], 1])
                        wx.CallAfter(self.main.report_panel.AppendText, 'Model 1: '+ str(self.main.MODEL[i][1][entry][2])+'\n')

                    if model == 2:
                        calc_test.append([self.main.MODEL[i][1][entry][2], 2])
                        wx.CallAfter(self.main.report_panel.AppendText, 'Model 2: '+ str(self.main.MODEL[i][1][entry][2])+'\n')

                    if model == 3:
                        calc_test.append([self.main.MODEL[i][1][entry][2], 3])
                        wx.CallAfter(self.main.report_panel.AppendText, 'Model 3: '+ str(self.main.MODEL[i][1][entry][2])+'\n')

                    if model == 4:
                        calc_test.append([self.main.MODEL[i][1][entry][2], 4])
                        wx.CallAfter(self.main.report_panel.AppendText, 'Model 4: '+ str(self.main.MODEL[i][1][entry][2])+'\n')

                    if model == 5:
                        calc_test.append([self.main.MODEL[i][1][entry][2], 5])
                        wx.CallAfter(self.main.report_panel.AppendText, 'Model 5: '+ str(self.main.MODEL[i][1][entry][2])+'\n')

                    if model == 6:
                        calc_test.append([self.main.MODEL[i][1][entry][2], 6])
                        wx.CallAfter(self.main.report_panel.AppendText, 'Model 6: '+ str(self.main.MODEL[i][1][entry][2])+'\n')



                # Calculate F-Test
                if test == 'F-test':
                    # Loop over calculated models
                    for simpler_model in range(0, len(self.main.MODEL)):
                        # Loop over models to compare (models are ordered in increasing complexity!)
                        selected_model = 1

                        for higher_model in range(simpler_model-1, len(self.main.MODEL)):
                            # Skip if same model
                            if simpler_model == higher_model:
                                continue

                            # Skip if lower model is compared to higher in wrong way
                            if simpler_model > higher_model:
                                continue

                            # Values
                            chi2_1= self.main.MODEL[simpler_model][1][entry][2]
                            chi2_2 =self.main.MODEL[higher_model][1][entry][2]

                            # Parameters of simpler model
                            if self.main.MODEL[simpler_model][0] == 1:
                                k_1 = k1
                            if self.main.MODEL[simpler_model][0] == 2:
                                k_1 = k2
                            if self.main.MODEL[simpler_model][0] in [3, 6]:
                                k_1 = k3
                            if self.main.MODEL[simpler_model][0] == 4:
                                k_1 = k4
                            if self.main.MODEL[simpler_model][0] == 5:
                                k_1 = k5

                            # Parameters of higher model
                            if self.main.MODEL[higher_model][0] == 1:
                                k_2 = k1
                            if self.main.MODEL[higher_model][0] == 2:
                                k_2 = k2
                            if self.main.MODEL[higher_model][0] in [3, 6]:
                                k_2 = k3
                            if self.main.MODEL[higher_model][0] == 4:
                                k_2 = k4
                            if self.main.MODEL[simpler_model][0] == 5:
                                k_1 = k5

                            # Calculate F-test
                            tmp_test = F_test(chi2_1, k_1, chi2_2, k_2, n)

                            if tmp_test > 0.05:
                                tmp_model = self.main.MODEL[higher_model][0]
                                stop = True
                            else:
                                tmp_model = self.main.MODEL[simpler_model][0]
                                stop = False

                            selected_model = tmp_model

                            # Report
                            wx.CallAfter(self.main.report_panel.AppendText, 'Model '+str(self.main.MODEL[simpler_model][0])+' to Model '+str(self.main.MODEL[higher_model][0])+': '+str(tmp_test)+'\n')

                            # Abort, if a higher model fits better
                            if stop:
                                break

                    selected_model = tmp_model
                    calc_test.append([0, selected_model])

                    # stop loopng over entries
                    break


            # sort test values
            for i in range(0, len(calc_test)):
                for j in range(0, len(calc_test)):
                    # skip
                    if i == j:
                        continue

                    # swap entries
                    if calc_test[i][0] < calc_test[j][0]:
                        # swap entries
                        save = calc_test[j]
                        calc_test[j] = calc_test[i]
                        calc_test[i] = save

            # check if exchange is expected
            if self.main.FITALLMODELS:
                # collect R2eff values
                cpmgs = []
                r2effs = []
                # load data.
                for i in range(0, len(self.main.R2eff[int(residue)-1])):
                    if not self.main.R2eff[int(residue)-1][i] == None:
                        r2effs.append(float(self.main.R2eff[int(residue)-1][i]))
                        cpmgs.append(float(self.main.CPMGFREQ[self.exp_index][i]))

                # exclude
                e = exclude(r2effs, cpmgs, self.main.SETTINGS[3], prior=False)

            else:
                e = False

            if e:
                selected_model = 1
                wx.CallAfter(self.main.report_panel.AppendText, '\nExcluded residue '+str(self.main.MODEL[0][1][entry][0])+' as no exchange is observed.\n')
                wx.CallAfter(self.main.report_panel.AppendText, 'Model '+str(selected_model)+' selected for residue '+str(self.main.MODEL[0][1][entry][0])+'\n')
            else:
                selected_model = calc_test[0][1]
                wx.CallAfter(self.main.report_panel.AppendText, '\nModel '+str(selected_model)+' selected for residue '+str(self.main.MODEL[0][1][entry][0])+'\n')

            # add value
            if selected_model == 1:
                self.selected_model.append({'residue':self.main.MODEL1[entry][0], 'model':1, 'R2':float(self.main.MODEL1[entry][1]), 'chi2':self.main.MODEL1[entry][2], 'fit_params':self.main.MODEL1[entry][1]})
            if selected_model == 2:
                self.selected_model.append({'residue':self.main.MODEL2[entry][0], 'model':2, 'R2':self.main.MODEL2[entry][1][0], 'kex':self.main.MODEL2[entry][1][2], 'Rex':self.Rex(2, self.main.MODEL2[entry][0]), 'chi2':self.main.MODEL2[entry][2], 'fit_params':self.main.MODEL2[entry][1]})
            if selected_model == 3:
                self.selected_model.append({'residue':self.main.MODEL3[entry][0], 'model':3, 'R2':self.main.MODEL3[entry][1][0], 'kex':self.main.MODEL3[entry][1][1], 'Rex':self.Rex(3, self.main.MODEL3[entry][0]), 'dw':self.main.MODEL3[entry][1][2], 'pb':self.main.MODEL3[entry][1][3], 'chi2':self.main.MODEL3[entry][2], 'fit_params':self.main.MODEL3[entry][1]})
            if selected_model == 4:
                self.selected_model.append({'residue':self.main.MODEL4[entry][0], 'model':4, 'R2':self.main.MODEL4[entry][1][0], 'kex':self.main.MODEL4[entry][1][2]+self.main.MODEL4[entry][1][4],'kex1':self.main.MODEL4[entry][1][2], 'Rex':self.Rex(4, self.main.MODEL4[entry][0]), 'kex2':self.main.MODEL4[entry][1][4], 'chi2':self.main.MODEL4[entry][2], 'fit_params':self.main.MODEL4[entry][1]})
            if selected_model == 5:
                self.selected_model.append({'residue':self.main.MODEL5[entry][0], 'model':5, 'R2':self.main.MODEL5[entry][1][0], 'kex':self.main.MODEL5[entry][1][1]+self.main.MODEL5[entry][1][4], 'kex1':self.main.MODEL5[entry][1][1], 'kex2':self.main.MODEL5[entry][1][4], 'Rex':self.Rex(5, self.main.MODEL5[entry][0]), 'pb':self.main.MODEL5[entry][1][3], 'dw':self.main.MODEL5[entry][1][2], 'pc':self.main.MODEL5[entry][1][6], 'dw2':self.main.MODEL5[entry][1][5], 'chi2':self.main.MODEL5[entry][2],'fit_params':self.main.MODEL5[entry][1]})
            if selected_model == 6:
                self.selected_model.append({'residue':self.main.MODEL6[entry][0], 'model':6, 'R2':self.main.MODEL6[entry][1][0], 'kex':self.main.MODEL6[entry][1][1], 'Rex':self.Rex(6, self.main.MODEL6[entry][0]), 'dw':self.main.MODEL6[entry][1][2], 'pb':self.main.MODEL6[entry][1][3], 'chi2':self.main.MODEL6[entry][2], 'fit_params':self.main.MODEL6[entry][1]})


            time.sleep(0.05)
