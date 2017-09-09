#################################################################################
#                                                                               #
#   (C) 2011-2012 Michael Bieri                                                 #
#   (C) 2013-2016 Edward d'Auvergne                                             #
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
from os import makedirs, sep
import pylab
from scipy import array, linspace, var, sqrt
from scipy.optimize import leastsq
from time import sleep
import wx


# NESSY modules
from conf.data import sync_data
from func.color_code import color_code, color_code_model
from curvefit.model_selection import Model_Selection
from func.plotting import create_pylab_graphs, Plot_intensities, surface_plot
from conf.message import message
from elements.variables import Pi, Constraints_container
from curvefit.chi2 import Chi2_container
from math_fns.r1p import fit_R1rho, R1rho_residuals, R1p_model_1, R1p_model_1_residuals, R1p_model_2, R1p_model_2_residuals, R1p_model_3, R1p_model_3_residuals, R1p_model_4, R1p_model_4_residuals
from math_fns.tests import AIC, AICc
from curvefit.exclude import exclude




class R1rho:
    """Class to store R1rho results."""
    # R1rho values
    r1rho = []          # [Experiment[Residue[x,y]]]

    # R1rho errors
    r1rho_error = []

    # Results for model 1
    model1 = []

    # Results for model 2
    model2 = []

    # Results for model 3
    model3 = []

    # Results for model 4
    model4 = []

    # Model selection
    selected = []

    # Errors of Monte Carlo Simulation
    montecarlo = []


class Run_spinlock():
    """Class to control Spin Lock experiments adata analysis."""


    def __init__(self, self_main, exp_index=0, num_exp=1, globalfit=False, onresonance=True):
        """Control executions."""
        # Empy R1rho containers
        R1rho.r1rho = []
        R1rho.r1rho_error = []
        R1rho.model1 = []
        R1rho.model2 = []
        R1rho.model3 = []
        R1rho.selected = []
        R1rho.montecarlo = []

        # Connect variables.
        self.main = self_main

        # Experiment mode
        self.exp_mode = self.main.sel_experiment[exp_index].GetSelection()

        # Create directories
        self.create_directories()

        # experiment index
        self.exp_index = exp_index

        # Synchronize data.
        sync_data(self.main, index=self.exp_index)

        # Initialize data
        self.init_data()

        # Read Data
        self.read_data(num_exp=num_exp, onresonance=onresonance)

        # Calculate R1rho
        self.calc_r1rho(num_exp=num_exp, onresonance=onresonance)

        # Calculate error
        self.calc_error(onresonance=onresonance)

        # Fit to model 1
        if self.main.MODELS[0]:
            self.minimise(num_exp=num_exp, model=1, globalfit=globalfit, onresonance=onresonance)

        # Fit to model 2
        if self.main.MODELS[1]:
            self.minimise(num_exp=num_exp, model=2, globalfit=globalfit, onresonance=onresonance)

        # Fit to model 3
        if self.main.MODELS[2]:
            self.minimise(num_exp=num_exp, model=3, globalfit=globalfit, onresonance=onresonance)

        # Fit to model 4
        if self.main.MODELS[3]:
            self.minimise(num_exp=num_exp, model=4, globalfit=globalfit, onresonance=onresonance)

        # Model selection
        wx.CallAfter(self.main.checkrun_label.SetLabel, 'Model selection')
        self.modelselection()

        # Monte Carlo Simulation
        self.montecarlo(globalfit=globalfit, onresonance=onresonance)

        # Create final plots
        self.plots()
        wx.CallAfter(self.main.report_panel.AppendText, '\n\n--------------------------------\nCreated plots.\n--------------------------------')

        # create pymol macros
        # the directory and pdb file
        directory = str(self.main.proj_folder.GetValue())+sep+self.main.PYMOL_FOLDER
        pdbfile = str(self.main.pdb_file.GetValue())

        # Model
        color_code_model(self.color_residue, self.color_model, 'Model_selection.pml', directory, pdb_file=pdbfile)
        # Add file to results tree
        self.main.tree_results.AppendItem (self.main.structures, directory+sep+'Model_selection.pml', 0)
        self.main.COLOR_PDB.append(directory+sep+'Model_selection.pml')

        # kex
        color_code(self.color_residue_kex, self.color_kex, 'Kex.pml', directory, pdb_file=pdbfile)
        # Add file to results tree
        self.main.tree_results.AppendItem (self.main.structures, directory+sep+'Kex.pml', 0)
        self.main.COLOR_PDB.append(directory+sep+'Kex.pml')

        wx.CallAfter(self.main.report_panel.AppendText, '\n\n--------------------------------\nPymol Macros Created.\n--------------------------------' )

        # Final feed back
        wx.CallAfter(self.main.checkrun_label.SetLabel, 'Done.')
        wx.CallAfter(self.main.report_panel.AppendText, '\n\n====================================================\nFinished R1rho analysis\n====================================================\n')


    def calc_error(self, onresonance=False):
        """Function to calculate pooled variance of R1rho."""

        # container for error
        R1rho.r1rho_error = []

        # loop over experiments
        for exp in range(len(R1rho.r1rho)):
            # create error container for experiment
            R1rho.r1rho_error.append([])

            # read x values
            if onresonance: x = self.spinlock_power[0]         # on resonance
            else:           x = self.offset[0]                 # off resonace

            # containers of indexes of doublicates
            doublicates = []

            # number of doublicates
            n = []

            # checked list
            checked = []

            # loop over x values
            for x_values in x:
                # skip, if values was already checked
                if x_values in checked: continue

                # temporary douplicates
                d_tmp = []

                # loop over x values to compare
                for i in range(len(x)):
                    if x_values == x[i]:   d_tmp.append(i)

                # more than 1 entry = doublicates
                if len(d_tmp) > 1:
                    doublicates.append(d_tmp)
                    n.append(len(d_tmp))

                # add to checked lits
                checked.append(x_values)

            # calculate pooled variance for each residue
            for residue in range(self.main.RESNO):
                # create error container for residue within experiment
                R1rho.r1rho_error[exp].append([])

                # skip, if no data is present
                if R1rho.r1rho[exp][residue][1] == []:  continue    # no y values

                # read R1rho values
                y = R1rho.r1rho[exp][residue][1]

                # calculate pooled variance
                a = 0
                b = 0

                # loop over doublicated values
                for doub in range(len(doublicates)):
                    # values
                    v = []

                    # loop over doublicates
                    for ns in range(len(doublicates[doub])):
                        v.append(y[doublicates[doub][ns]])

                    # calculate
                    a = (n[doub] - 1) * var(v, ddof=1)
                    b = (n[doub] - 1)

                # calculate pooled variance
                # calculate
                if b == 0:  pooled_variance = 1
                else:       pooled_variance = a/b

                # store globally
                R1rho.r1rho_error[exp][residue] = sqrt(pooled_variance)

                # Feedback
                wx.CallAfter(self.main.report_panel.AppendText, '\nPooled variance for residue '+str(residue+1)+', of experiment '+str(exp+1)+' is '+str(sqrt(pooled_variance)))
                sleep(0.01)

        # spacer
        wx.CallAfter(self.main.report_panel.AppendText, '\n')


    def calc_r1rho(self, num_exp=1, onresonance=False):
        """Class to calculate R1rho for each dataset."""
        # Feedback
        wx.CallAfter(self.main.report_panel.AppendText, '\nStarting R1rho calculation.\n')

        #REMOVEME
        testy = []
        testx = []

        # loop over experiments
        for exp in range(num_exp):
            # reference spectrum
            reference_index = self.spinlock_time[exp].index(min(self.spinlock_time[exp]))

            # create new R1rho container for experiment
            R1rho.r1rho.append([])

            # loop over residues
            for residue in range(self.main.RESNO):
                # don't calculate residue
                if not self.main.INCLUDE_RES[residue] == True:
                    R1rho.r1rho[exp].append([[], []])
                    continue

                # feedback
                wx.CallAfter(self.main.checkrun_label.SetLabel, 'Fitting to R1rho, Residue '+str(residue+1)+', exp '+str(exp+1))

                # Container for R1rho experiments (x and y values)
                x_tmp = []
                y_tmp = []

                # On-resonance
                if onresonance:
                    # loop over spin lock power
                    for spinlockpower in range(len(self.spinlock_power[exp])):
                        # containers for x and y values
                        x = []
                        y = []

                        #loop over spin lock time(x)
                        for spinlocktime in range(len(self.spinlock_time[exp])):
                            # create x and y values, if data is present or not reference spectrum
                            if not self.spinlock_time[exp][spinlocktime] in [0, '']:
                                # only store data pair if intensity is present
                                if not str(self.main.data_grid_r1rho[exp][1][spinlockpower].GetCellValue(residue, spinlocktime+1)) == '':
                                    # Spin lock time
                                    x.append(float(self.spinlock_time[exp][spinlocktime]))
                                    # intensity
                                    y.append(float(self.main.data_grid_r1rho[exp][1][spinlockpower].GetCellValue(residue, spinlocktime+1)))

                        # abort if no data is present
                        if x == []:
                            continue

                        # Reference intensity
                        I0 = float(self.main.data_grid_r1rho[exp][1][spinlockpower].GetCellValue(residue, reference_index+1))

                        # Feedback
                        if onresonance: wx.CallAfter(self.main.report_panel.AppendText, '\nCalculating R1rho for residue '+str(residue+1)+', Spin lock power: '+str(self.spinlock_power[exp][spinlockpower])+'Hz\n')
                        else:           wx.CallAfter(self.main.report_panel.AppendText, '\nCalculating R1rho for residue '+str(residue+1)+', Offset: '+str(self.offset[exp][spinlockpower])+'Hz\n')

                        # fit to R1rho
                        fit = leastsq(R1rho_residuals, 15.1, args=(array(y), array(x), I0, self.main.report_panel), full_output = 1, col_deriv = 1, ftol = self.main.tolerance, xtol = self.main.tolerance, maxfev=2000000)

                        # Save calculated value
                        y_tmp.append(fit[0][0])
                        if onresonance: x_tmp.append(float(self.spinlock_power[exp][spinlockpower]))
                        else:           x_tmp.append(float(self.offset[exp][spinlockpower]))

                # Off-resonance
                else:
                    #loop over offset
                    for offset in range(len(self.offset[exp])):
                        # containers for x and y values
                        x = []
                        y = []

                        #loop over spin lock time(x)
                        for spinlocktime in range(len(self.spinlock_time[exp])):
                            # create x and y values, if data is present or not reference spectrum
                            if not self.spinlock_time[exp][spinlocktime] in [0, '']:
                                # only store data pair if intensity is present
                                if not str(self.main.data_grid_r1rho[exp][1][offset].GetCellValue(residue, spinlocktime+1)) == '':
                                    # Spin lock time
                                    x.append(float(self.spinlock_time[exp][spinlocktime]))
                                    # intensity
                                    y.append(float(self.main.data_grid_r1rho[exp][1][offset].GetCellValue(residue, spinlocktime+1)))

                        # abort if no data is present
                        if x == []:
                            continue

                        # Reference intensity
                        I0 = float(self.main.data_grid_r1rho[exp][1][offset].GetCellValue(residue, reference_index+1))

                        # Feedback
                        if onresonance: wx.CallAfter(self.main.report_panel.AppendText, '\nCalculating R1rho for residue '+str(residue+1)+', Spin lock power: '+str(self.spinlock_power[exp][spinlockpower])+'Hz\n')
                        else:           wx.CallAfter(self.main.report_panel.AppendText, '\nCalculating R1rho for residue '+str(residue+1)+', Offset: '+str(self.offset[exp][offset])+'Hz\n')

                        # fit to R1rho
                        fit = leastsq(R1rho_residuals, 15.1, args=(array(y), array(x), I0, self.main.report_panel), full_output = 1, col_deriv = 1, ftol = self.main.tolerance, xtol = self.main.tolerance, maxfev=2000000)

                        # Save calculated value
                        y_tmp.append(fit[0][0])
                        if onresonance: x_tmp.append(float(self.spinlock_power[exp][spinlockpower]))
                        else:           x_tmp.append(float(self.offset[exp][offset]))

                # Store R1rho values for residue and experiment
                R1rho.r1rho[exp].append([x_tmp, y_tmp])

                # Create plots
                if float(self.main.CREATE_R2EFFPLOT) == 0.0 and not x_tmp == []:
                    self.plot_r1rho(x_tmp, y_tmp, residue, exp, onresonance)


    def create_directories(self):
        """Create results directories."""
        # create directories
        base_dir = str(self.main.proj_folder.GetValue())
        self.basedir = base_dir
        self.pymoldir = base_dir+sep+self.main.PYMOL_FOLDER
        self.textdir = base_dir+sep+self.main.TEXT_FOLDER
        self.pngdir = base_dir+sep+self.main.PLOT_FOLDER+sep+'png'
        self.vectordir = base_dir+sep+self.main.PLOT_FOLDER+sep+self.main.PLOTFORMAT.replace('.', '')

        # Pymol marcos
        try:
            makedirs(self.pymoldir)
        except:
            a = 'already exists'

        # Text files
        try:
            makedirs(self.textdir)
        except:
            a = 'already exists'

        # Plot png
        try:
            makedirs(self.pngdir)
        except:
            a = 'already exists'

        # Plot vector
        try:
            makedirs(self.vectordir)
        except:
            a = 'already exists'


    def estimate(self, model=1, num_exp=1):
        """Function to estimate parameters."""
        # container
        p = []

        # Model 1
        if model == 1:
            for i in range(num_exp):
                # R1
                p.append(0.0)

                # R2
                p.append(self.main.INI_R2[0])

        # Model 2
        if model == 2:
            # kex
            p.append(self.main.INI_kex[1])

            # Phi
            p.append(self.main.INI_phi[1])

            for i in range(num_exp):
                # R1
                p.append(0.0)

                # R2
                p.append(self.main.INI_R2[1])

        # Model 3 or 4
        if model in [3, 4]:
            # kex
            p.append(self.main.INI_kex[2])

            # dw
            p.append(self.main.INI_dw[2])

            # pb
            p.append(self.main.INI_pb[2])

            for i in range(num_exp):
                # R1
                p.append(0.0)

                # R2
                p.append(self.main.INI_R2[2])

        # Return
        return p


    def exclude(self, x, y, prior=False):
        '''Function to exclude if difference betweendata is not big enougt.'''
        # minimal difference
        min_diff = self.main.SETTINGS[3]

        # excange is expected, if at least 1 experiment has bigger difference
        has_exchange = False

        # loop over experiments
        for exp in range(0, len(x)):
            # Check if Rex is expected
            do_exclude = exclude(y[exp], x[exp], min_diff, prior=False)

            # change flag
            if not do_exclude:
                has_exchange = True

        # exclude if no data set is expected to be exchanging
        if not has_exchange:
            return True

        else:
            return False


    def init_data(self):
        '''Initialize and clean variables.'''
        # empty results containers
        self.main.MODEL1 = []            # [Residue, Fit_parameters, chi2]
        self.main.MODEL2 = []            # [Residue, Fit_parameters, chi2]
        self.main.MODEL3 = []            # [Residue, Fit_parameters, chi2]
        self.main.MODEL_SELECTION = []   # [Residue, Model, R2, kex]

        # empty entries for results tree
        self.main.results_plot = []
        self.main.results_grace = []
        self.main.results_txt = []


    def plots(self):
        """Function to create final plots."""

        # Containers
        residue = []
        model = []
        r1 = []
        r1_err = []
        r2 = []
        r2_err = []
        kex = []
        kex_err = []
        phi = []
        phi_err =[]
        pb = []
        pb_err = []
        dw = []
        dw_err = []
        k = []
        n = []
        chi2 = []

        # loop over calculated values
        for entry in range(len(R1rho.selected)):
            # residue
            residue_tmp = R1rho.selected[entry]['residue']

            # selected model
            sel_model = R1rho.selected[entry]['model']

            # model 1
            if sel_model == 1:
                # read corresponding residue
                for res in range(len(R1rho.model1)):
                    if R1rho.model1[res]['residue'] == residue_tmp:
                        break

                for res_mc in range(len(R1rho.montecarlo)):
                    if R1rho.montecarlo[res_mc] == None: continue
                    if R1rho.montecarlo[res_mc]['residue'] == residue_tmp:
                        break

                # store entries
                residue.append(residue_tmp)
                model.append(sel_model)
                '''r1.append(R1rho.model1[res]['r1'])
                r1_err.append(R1rho.montecarlo[res_mc]['r1'])
                r2.append(R1rho.model1[res]['r2'])
                r2_err.append(R1rho.montecarlo[res_mc]['r2'])'''
                kex.append(None)
                kex_err.append(None)
                phi.append(None)
                phi_err.append(None)
                pb.append(None)
                pb_err.append(None)
                dw.append(None)
                dw_err.append(None)
                k.append(R1rho.model1[res]['k'])
                n.append(R1rho.model1[res]['n'])
                chi2.append(R1rho.model1[res]['chi2'])

        # model 2
        if sel_model == 2:
                # read corresponding residue
                for res in range(len(R1rho.model2)):
                    if R1rho.model2[res]['residue'] == residue_tmp:
                        break

                for res_mc in range(len(R1rho.montecarlo)):
                    if R1rho.montecarlo[res_mc] == None: continue
                    if R1rho.montecarlo[res_mc]['residue'] == residue_tmp:
                        break

                # store entries
                residue.append(residue_tmp)
                model.append(sel_model)
                '''r1.append(R1rho.model2[res]['r1'])
                r1_err.append(R1rho.montecarlo[res_mc]['r1'])
                r2.append(R1rho.model2[res]['r2'])
                r2_err.append(R1rho.montecarlo[res_mc]['r2'])'''
                kex.append(R1rho.model2[res]['kex'])
                kex_err.append(R1rho.montecarlo[res_mc]['kex'])
                phi.append(R1rho.model2[res]['phi'])
                phi_err.append(R1rho.montecarlo[res_mc]['phi'])
                pb.append(None)
                pb_err.append(None)
                dw.append(None)
                dw_err.append(None)
                k.append(R1rho.model2[res]['k'])
                n.append(R1rho.model2[res]['n'])
                chi2.append(R1rho.model2[res]['chi2'])

        # Create csv file
        file = open(self.textdir+sep+'Model_selection.csv', 'w')

        # write header
        file.write('residue;model;kex;err;phi;err;pb;err;dw;err;k;n;chi2\n')

        # loop over entries
        for i in range(len(residue)):
            # create line
            text = str(residue[i])+';'+str(model[i])+';'+str(kex[i])+';'+str(kex_err[i])+';'+str(phi[i])+';'+str(phi_err[i])+';'+str(pb[i])+';'+str(pb_err[i])+';'+str(dw[i])+';'+str(dw_err[i])+';'+str(k[i])+';'+str(n[i])+';'+str(chi2[i])

            # remove None
            text.replace('None', '')

            # write line
            file.write(text+'\n')

        # close file
        file.close()

        # Add csv file to results tree.
        self.main.tree_results.AppendItem (self.main.txt, self.textdir+sep+'Model_selection.csv', 0)

        # Save csv file
        self.main.results_txt.append(self.textdir+sep+'Model_selection.csv')

        # create plots  #

        # plot properties
        # Frame width
        params={'axes.linewidth' : self.main.FRAMEWIDTH}
        pylab.rcParams.update(params)

        # models
        pylab.plot(residue, model, 'ko')
        # labels
        pylab.xlabel('Residue Number', fontsize=19, weight='bold')
        pylab.ylabel('Model', fontsize=19, weight='bold')
        # Size of axis labels
        pylab.xticks(fontsize=19)
        pylab.yticks(fontsize=19)
        # range
        pylab.ylim(0, 4)
        # png
        pylab.savefig(self.pngdir+sep+'Models.png', dpi = 72, transparent = True)
        pylab.savefig(self.vectordir+sep+'Models.svg')
        # clear graph
        pylab.cla()
        pylab.close()
        # add to results tree
        self.main.tree_results.AppendItem (self.main.plots_modelselection, self.pngdir+sep+'Models.png', 0)
        self.main.FINAL_RESULTS.append(self.pngdir+sep+'Models.png')

        # r1
        color = ['BLACK', 'BLUE', 'RED', 'GREEN', 'WHITE']
        for i in range(len(r1)):
            pylab.errorbar(residue, r1[i], yerr=r1_err[i], c = color[i], marker = 'o')
        # labels
        pylab.xlabel('Residue Number', fontsize=19, weight='bold')
        pylab.ylabel('R1 [1/s]', fontsize=19, weight='bold')
        # Size of axis labels
        pylab.xticks(fontsize=19)
        pylab.yticks(fontsize=19)
        # png
        pylab.savefig(self.pngdir+sep+'R1.png', dpi = 72, transparent = True)
        pylab.savefig(self.vectordir+sep+'R1.svg')
        # clear graph
        pylab.cla()
        pylab.close()
        # add to results tree
        self.main.tree_results.AppendItem (self.main.plots_modelselection, self.pngdir+sep+'R1.png', 0)
        self.main.FINAL_RESULTS.append(self.pngdir+sep+'R1.png')

        # r2
        for i in range(len(r2)):
            pylab.errorbar(residue, r2[i], yerr=r2_err[i], c = color[i], marker = 'o')
        # labels
        pylab.xlabel('Residue Number', fontsize=19, weight='bold')
        pylab.ylabel('R2 [1/s]', fontsize=19, weight='bold')
        # Size of axis labels
        pylab.xticks(fontsize=19)
        pylab.yticks(fontsize=19)
        # png
        pylab.savefig(self.pngdir+sep+'R2.png', dpi = 72, transparent = True)
        pylab.savefig(self.vectordir+sep+'R2.svg')
        # clear graph
        pylab.cla()
        pylab.close()
        # add to results tree
        self.main.tree_results.AppendItem (self.main.plots_modelselection, self.pngdir+sep+'R2.png', 0)
        self.main.FINAL_RESULTS.append(self.pngdir+sep+'R2.png')

        # store models
        self.color_model = model
        self.color_residue = residue

        # kex
        x = []
        y = []
        err = []
        for i in range(len(kex)):
            if not kex[i] == None:
                x.append(residue[i])
                y.append(kex[i])
                err.append(kex_err[i])
        # store kex
        self.color_residue_kex = x
        self.color_kex = y

        # plot
        if not x == []:
            pylab.errorbar(x, y, yerr=err, color='k', fmt ='o')
            # labels
            pylab.xlabel('Residue Number', fontsize=19, weight='bold')
            pylab.ylabel('kex [1/s]', fontsize=19, weight='bold')
            # Size of axis labels
            pylab.xticks(fontsize=19)
            pylab.yticks(fontsize=19)
            # png
            pylab.savefig(self.pngdir+sep+'kex.png', dpi = 72, transparent = True)
            pylab.savefig(self.vectordir+sep+'kex.svg')
            # clear graph
            pylab.cla()
            pylab.close()
            # add to results tree
            self.main.tree_results.AppendItem (self.main.plots_modelselection, self.pngdir+sep+'kex.png', 0)
            self.main.FINAL_RESULTS.append(self.pngdir+sep+'kex.png')

        # Phi
        x = []
        y = []
        err = []
        for i in range(len(phi)):
            if not phi[i] == None:
                x.append(residue[i])
                y.append(phi[i])
                err.append(phi[i])
        if not x == []:
            pylab.errorbar(x, y, yerr=err, color='k', fmt ='o')
            # labels
            pylab.xlabel('Residue Number', fontsize=19, weight='bold')
            pylab.ylabel('Phi', fontsize=19, weight='bold')
            # Size of axis labels
            pylab.xticks(fontsize=19)
            pylab.yticks(fontsize=19)
            # png
            pylab.savefig(self.pngdir+sep+'Phi.png', dpi = 72, transparent = True)
            pylab.savefig(self.vectordir+sep+'Phi.svg')
            # clear graph
            pylab.cla()
            pylab.close()
            # add to results tree
            self.main.tree_results.AppendItem (self.main.plots_modelselection, self.pngdir+sep+'Phi.png', 0)
            self.main.FINAL_RESULTS.append(self.pngdir+sep+'Phi.png')


    def read_data(self, num_exp=1, onresonance=False):
        """Function to read data from spin lock data grid and group them."""
        # Feedback
        wx.CallAfter(self.main.report_panel.AppendText, '\nReading data....')

        # Create data continers
        self.spinlock_power = []
        self.spinlock_time = []
        self.offset = []
        self.spinlock_data = []

        # Pop container (list of indexes to skip)
        pop_container = []

        # Loop over experiments
        for exp in range(num_exp):
            # On resonance
            if onresonance:
                # Read Spin Lock power
                spinlock_power_tmp = self.main.data_grid_r1rho[exp][2]

                # Check if values are set, othervise add to pop container
                for pp in range(len(spinlock_power_tmp)):
                    if spinlock_power_tmp[pp] == '':
                        pop_container.append(pp)

                # Create new container for spin lock time
                self.spinlock_time.append(self.main.CPMGFREQ[exp])

                # create spin lock data container for experiment
                self.spinlock_data.append([])

                # loop over spin lock power
                for power in range(len(spinlock_power_tmp)):
                    # if no spin lock field was set, skip this entries
                    if power in pop_container:
                        continue

                    # create spin lock data for each spin lock power
                    self.spinlock_data[exp].append([])

                    # loop over residues
                    for residue in range(self.main.RESNO):
                        # create data set for each residue
                        self.spinlock_data[exp][power].append([])

                        # loop over spin lock time
                        for sptime in range(len(self.spinlock_time[exp])):
                            # create for each spin lock time
                            self.spinlock_data[exp][power][residue].append(str(self.main.data_grid_r1rho[exp][1][power].GetCellValue(residue, sptime+1)))

                # Convert to Numbers
                # Spin lock time
                for i in range(len(self.spinlock_time[exp])):
                    if not self.spinlock_time[exp][i] == '': self.spinlock_time[exp][i] = float(self.spinlock_time[exp][i])

                # Spin lock power
                while '' in spinlock_power_tmp: spinlock_power_tmp.remove('')
                spinlock_power_tmp = [float(i) for i in spinlock_power_tmp]

                # Store spin lock data
                self.spinlock_power.append(spinlock_power_tmp)

                # Spin lock data
                for i in range(len(self.spinlock_data[exp])):           # loop over tab
                    for j in range(len(self.spinlock_data[exp][i])):    # loop over data set
                        for r in range(len(self.spinlock_data[exp][i][j])):                # loop over residue
                            if not self.spinlock_data[exp][i][j][r] == '': self.spinlock_data[exp][i][j][r] = float(self.spinlock_data[exp][i][j][r])

                # Offset
                offset_tmp = len(spinlock_power_tmp) * [0]
                self.offset.append(offset_tmp)

            # Off resonance
            else:
                # Read Offset
                offset_tmp = self.main.data_grid_r1rho[exp][2]

                # Create new container for spin lock time
                self.spinlock_time.append(self.main.CPMGFREQ[exp])

                # Check if values are set, othervise add to pop container
                for pp in range(len(self.spinlock_time)):
                    if self.spinlock_time[pp] == '':
                        pop_container.append(pp)

                # create spin lock data container for experiment
                self.spinlock_data.append([])

                # loop over spin lock power
                for power in range(len(offset_tmp)):
                    # if no offset was set, skip this entries
                    if power in pop_container:
                        continue

                    # create spin lock data for each spin lock power
                    self.spinlock_data[exp].append([])

                    # loop over residues
                    for residue in range(self.main.RESNO):
                        # create data set for each residue
                        self.spinlock_data[exp][power].append([])

                        # loop over spin lock time
                        for sptime in range(len(self.spinlock_time[exp])):
                            # create for each spin lock time
                            self.spinlock_data[exp][power][residue].append(str(self.main.data_grid_r1rho[exp][1][power].GetCellValue(residue, sptime+1)))

                # Offset
                while '' in offset_tmp: offset_tmp.remove('')
                offset_tmp = [float(i) for i in offset_tmp]

                # Spin lock time
                for i in range(len(self.spinlock_time[exp])):
                    if not self.spinlock_time[exp][i] == '': self.spinlock_time[exp][i] = float(self.spinlock_time[exp][i])

                ## Spin lock power
                #for i in range(len(offset_tmp)):
                #    if not offset_tmp[i] == '': offset_tmp[i] = float(offset_tmp[i])

                # Spin lock data
                for i in range(len(self.spinlock_data[exp])):           # loop over tab
                    for j in range(len(self.spinlock_data[exp][i])):    # loop over data set
                        for r in range(len(self.spinlock_data[exp][i][j])):                # loop over residue
                            if not self.spinlock_data[exp][i][j][r] == '': self.spinlock_data[exp][i][j][r] = float(self.spinlock_data[exp][i][j][r])

                # Spin Lock power
                self.spinlock_power.append(len(offset_tmp) * [float(self.main.CPMG_DELAY[0])])

                # Store offset
                self.offset.append(offset_tmp)

        # Convert Hz to rad/s
        for exp in range(len(self.spinlock_power)):
            # Spin lock power
            self.spinlock_power[exp] = [i*2*Pi for i in self.spinlock_power[exp]]

            # Offset
            self.offset[exp] = [i*2*Pi for i in self.offset[exp]]

        # Feedback
        wx.CallAfter(self.main.report_panel.AppendText, 'done.\n')


    def plot_r1rho(self, x_tmp, y_tmp, residue, experiment, onresonance):
        """ Function to create blank R1rho plots."""
        # Frame width
        params={'axes.linewidth' : self.main.FRAMEWIDTH}
        pylab.rcParams.update(params)

        # Labels
        if onresonance:
            pylab.xlabel('Spin lock power [Hz]', fontsize=19, weight='bold')
            pylab.ylabel('R1rho [1/s]', fontsize=19, weight='bold')
        else:
            pylab.xlabel('Offset [Hz]', fontsize=19, weight='bold')
            pylab.ylabel('R1rho [1/s]', fontsize=19, weight='bold')

        # Plot
        pylab.plot(x_tmp, y_tmp, 'ko')

        # y axis limits
        y_min = float(self.main.SETTINGS[5])
        y_max = float(self.main.SETTINGS[6])
        pylab.ylim(y_min, y_max)

        # Size of numbers
        pylab.xticks(fontsize=19)
        pylab.yticks(fontsize=19)

        # Save plot
        # vector plot
        pylab.savefig(self.vectordir+sep+'R1rho.Experiment.'+str(experiment+1)+'.Residue.'+str(residue+1)+self.main.PLOTFORMAT)

        # png
        pylab.savefig(self.pngdir+sep+'R1rho.Experiment.'+str(experiment+1)+'.Residue.'+str(residue+1)+'.png', dpi = 72, transparent = True)

        # clear plot
        pylab.cla() # clear the axes
        pylab.close() #clear figure

        # Store and add to results
        self.main.results_plot.append(self.pngdir+sep+'R1rho.Experiment.'+str(experiment+1)+'.Residue.'+str(residue+1)+'.png')
        self.main.tree_results.AppendItem (self.main.plots_plots, self.pngdir+sep+'R1rho.Experiment.'+str(experiment+1)+'.Residue.'+str(residue+1)+'.png', 0)

        # create csv file
        filename = self.textdir +sep+'R1rho.Experiment.'+str(experiment+1)+'.Residue.'+str(residue+1)+'.csv'

        # create file
        file = open(filename, 'w')

        # write header
        if onresonance: file.write('Spin Lock power [Hz];R1rho [1/s]\n')
        else: file.write('Offset [Hz];R1rho [1/s]\n')

        # write entries
        for i in range(len(x_tmp)):
            file.write(str(x_tmp[i])+';'+str(y_tmp[i])+'\n')

        # close file
        file.close()

        # save
        self.main.tree_results.AppendItem (self.main.txt, filename, 0)
        self.main.results_txt.append(filename)


    def minimise(self, num_exp=1, model=1, globalfit=False, onresonance=False):
        """Function to fit to models."""
        # Dictionary for models
        func = {'1':R1p_model_1, '2':R1p_model_2, '3':R1p_model_3, '4':R1p_model_4}
        fit_func = {'1':R1p_model_1_residuals, '2':R1p_model_2_residuals, '3':R1p_model_3_residuals, '4':R1p_model_4_residuals}

        # Numbers of data points
        n = 0

        # number of parameters
        k = 0

        # loop over residues
        for residue in range(self.main.RESNO):
            # Collect x and y values
            x = []
            y = []
            for exp in range(len(R1rho.r1rho)):
                x.append(array(R1rho.r1rho[exp][residue][0]))
                y.append(array(R1rho.r1rho[exp][residue][1]))
                n = n+len(R1rho.r1rho[exp][residue][0])

            # Abort if no values present
            if R1rho.r1rho[exp][residue][0] == []: continue

            # check if exchange is expected for models 2++
            if self.main.FITALLMODELS == False:
                if model > 1:
                    check = self.exclude(x, y, prior=True)

                    # stop, if no exchange is expected
                    if check:
                        #  dummy fit results
                        fit = [0, 0, 0, 0, 0, 0, 0, 0, 0]
                        # save dummy minimisation results
                        if model == 2: R1rho.model2.append({'residue':residue+1, 'chi2':999999999999999, 'fit':fit, 'n':100, 'k':1})
                        if model == 3: R1rho.model3.append({'residue':residue+1, 'chi2':999999999999999, 'fit':fit, 'n':100, 'k':1})
                        if model == 4: R1rho.model4.append({'residue':residue+1, 'chi2':999999999999999, 'fit':fit, 'n':100, 'k':1})
                        if model == 5: R1rho.model5.append({'residue':residue+1, 'chi2':999999999999999, 'fit':fit, 'n':100, 'k':1})
                        continue

            # error container
            error = []
            for exp in range(len(R1rho.r1rho)):
                error.append(R1rho.r1rho_error[exp][residue])

            # Feedback
            wx.CallAfter(self.main.report_panel.AppendText, '\nFitting residue '+str(residue+1)+' to model '+str(model)+'...\n')

            # update program status
            wx.CallAfter(self.main.checkrun_label.SetLabel, 'Fitting to Model '+str(model)+', Residue '+str(residue+1))

            # estimate
            p = self.estimate(model, num_exp)

            # field and offset
            field = array(self.spinlock_power)
            offset = array(self.offset)

            # Fit
            fit = leastsq(fit_func[str(model)], p, args=(y, error, field, offset, globalfit, self.main.report_panel, self.main.spec_freq), full_output = 1, col_deriv = 1, ftol = self.main.tolerance, xtol = self.main.tolerance, maxfev=2000000)

            # number of parameters
            k = len(p)

            # extract R1 and R2
            r1 = []
            r2 = []

            # Model 1
            if model == 1:
                for i in range(len(p)):
                    # R1
                    if i%2 == 0:
                        r1.append(fit[0][i])
                    # R2
                    else:
                        r2.append(fit[0][i])

                # Store results
                R1rho.model1.append({'residue':residue+1, 'r1':r1, 'r2':r2, 'chi2':Chi2_container.chi2, 'fit':fit[0], 'n':n, 'k':k})

            # Model 2
            if model == 2:
                # kex
                kex = fit[0][0]

                # Phi
                phi = fit[0][1]

                for i in range(2, len(p)):
                    # R1
                    if i%2 == 0:
                        r1.append(fit[0][i])
                    # R2
                    else:
                        r2.append(fit[0][i])

                # Store results
                R1rho.model2.append({'residue':residue+1, 'kex':kex, 'phi':phi, 'r1':r1, 'r2':r2, 'chi2':Chi2_container.chi2, 'fit':fit[0], 'n':n, 'k':k})

            # Model 3
            if model == 3:
                # kex
                kex = fit[0][0]

                # dw
                shiftdiff = fit[0][1]

                # pb
                pb = fit[0][2]

                for i in range(3, len(p)):
                    # R2
                    if i%2 == 0:
                        r2.append(fit[0][i])
                    # R1
                    else:
                        r1.append(fit[0][i])

                # Store results
                R1rho.model3.append({'residue':residue+1, 'kex':kex, 'dw':shiftdiff, 'pb':pb, 'r1':r1, 'r2':r2, 'chi2':Chi2_container.chi2, 'fit':fit[0], 'n':n, 'k':k})

            # Model 4
            if model == 3:
                # kex
                kex = fit[0][0]

                # dw
                shiftdiff = fit[0][1]

                # pb
                pb = fit[0][2]

                for i in range(3, len(p)):
                    # R2
                    if i%2 == 0:
                        r2.append(fit[0][i])
                    # R1
                    else:
                        r1.append(fit[0][i])

                # Store results
                R1rho.model4.append({'residue':residue+1, 'kex':kex, 'dw':shiftdiff, 'pb':pb, 'r1':r1, 'r2':r2, 'chi2':Chi2_container.chi2, 'fit':fit[0], 'n':n, 'k':k})

            # Create regression curve
            # min and max
            min = 1000000
            max = -10000000
            for i in range(len(x)):
                for j in range(len(x[i])):
                    if x[i][j] < min:
                        min = x[i][j]
                    if x[i][j] > max:
                        max = x[i][j]

            # create regression curve
            reg_x = []
            reg_y = []

            # loop over experiments
            for i in range(len(x)):
                # parameters
                p = fit[0]

                # Model 1
                if model == 1:
                    p_calc = p[(i*2):(2+i*2)]

                # model 2
                if model == 2:
                    p = fit[0]

                    # kex
                    kex = p[0]

                    # Phi
                    phi = p[1]*(float(self.main.spec_freq[i].GetValue()) * 2 * Pi)**2

                    # R1 and R2
                    r1 = p[(2+2*i)]
                    r2 = p[(3+2*i)]

                    # Parameters
                    p_calc = [kex, phi, r1, r2]

                # model 3 or 4
                if model in [3, 4]:
                    p = fit[0]

                    # kex
                    kex = p[0]

                    # dw
                    shiftdiff = p[1]*(float(self.main.spec_freq[i].GetValue()) * 2 * Pi)

                    # pb
                    pb = p[2]

                    # R1 and R2
                    r1 = p[(3+2*i)]
                    r2 = p[(4+2*i)]

                    # Parameters
                    p_calc = [kex, shiftdiff, pb, r1, r2]

                # x values
                if min < 0: reg_x.append(linspace(min+0.1*min, max+0.1*max, num=100))
                else:       reg_x.append(linspace(min-0.1*min, max+0.1*max, num=100))

                # on resonance
                if onresonance:
                    reg_y.append(func[str(model)](p_calc, array(reg_x[i]), offset[i][0]))

                # off resonance
                else:
                    reg_y.append(func[str(model)](p_calc, field[i][0], array(reg_x[i])))

            # Feedback
            wx.CallAfter(self.main.report_panel.AppendText, '\nFitting model '+str(model)+' to residue '+str(residue+1)+' completed. Chi2 = '+str(Chi2_container.chi2)+'\n')

            # Plot
            if onresonance:     # on resonance
                self.plot(x, y, reg_x, reg_y, error=error, fileroot='Residue_'+str(residue+1)+'_model_'+str(model), xlabel='Spin lock field w1 [rad/s]', ylabel='R1rho [1/s]', max=max, min=min, model=model)
            else:               # off resonance
                self.plot(x, y, reg_x, reg_y, error=error, fileroot='Residue_'+str(residue+1)+'_model_'+str(model), xlabel='Offset [rad/s]', ylabel='R1rho [1/s]', max=max, min=min, model=model)

            # Chi2 trace plots
            if model in [2, 3]:
                surface_plot(base_dir=str(self.main.proj_folder.GetValue()), fileroot='R1rho_'+str(residue+1)+'_Model_'+str(model), model=model, output=self.main.tree_results, savecont=self.main.plot3d, output1=self.main.plots3d, vec=self.main.PLOTFORMAT.replace('.', ''))


    def modelselection(self):
        """Function to perform model selection according to AIC and AICc."""
        # spacer
        wx.CallAfter(self.main.report_panel.AppendText, '\n')

        # selection method
        if self.main.SETTINGS[0] == 'AIC':  mode = 'AIC'
        else:                               mode = 'AICc'

        # loop over residues
        for entry in range(len(R1rho.model1)):
            # values
            values = []

            # current residue
            residue = R1rho.model1[entry]['residue']

            # feedback
            wx.CallAfter(self.main.report_panel.AppendText, '\n'+mode+' model selection for residue '+str(residue)+'\n==========================================')

            # Caclulate AICc / Aicc for model 1
            if self.main.SETTINGS[0] == 'AIC':
                tmp = AIC(R1rho.model1[entry]['chi2'], R1rho.model1[entry]['k'])
                values.append(tmp)
                wx.CallAfter(self.main.report_panel.AppendText, '\nModel 1:\t'+str(tmp))

            else:
                tmp = AICc(R1rho.model1[entry]['chi2'], R1rho.model1[entry]['k'], R1rho.model1[entry]['n'])
                values.append(tmp)
                wx.CallAfter(self.main.report_panel.AppendText, '\nModel 1:\t'+str(tmp))

            # model 2
            if self.main.MODELS[1] == True:
                index = None
                # get index of residue in model 2
                for i in range(len(R1rho.model2)):
                    if R1rho.model2[i]['residue'] == residue:
                        index = i
                        break

                if not index == None:
                    if self.main.SETTINGS[0] == 'AIC':
                        tmp = AIC(R1rho.model2[index]['chi2'], R1rho.model2[index]['k'])
                        values.append(tmp)
                        wx.CallAfter(self.main.report_panel.AppendText, '\nModel 2:\t'+str(tmp))

                    else:
                        tmp = AICc(R1rho.model2[index]['chi2'], R1rho.model2[index]['k'], R1rho.model2[index]['n'])
                        values.append(tmp)
                        wx.CallAfter(self.main.report_panel.AppendText, '\nModel 2:\t'+str(tmp))

            else: values.append(False)

            # model 3
            if self.main.MODELS[2] == True:
                index = None
                # get index of residue in model 3
                for i in range(len(R1rho.model3)):
                    if R1rho.model3[i]['residue'] == residue:
                        index = i
                        break

                if not index == None:
                    if self.main.SETTINGS[0] == 'AIC':
                        tmp = AIC(R1rho.model3[index]['chi2'], R1rho.model3[index]['k'])
                        values.append(tmp)
                        wx.CallAfter(self.main.report_panel.AppendText, '\nModel 3:\t'+str(tmp))

                    else:
                        tmp = AICc(R1rho.model3[index]['chi2'], R1rho.model3[index]['k'], R1rho.model3[index]['n'])
                        values.append(tmp)
                        wx.CallAfter(self.main.report_panel.AppendText, '\nModel 3:\t'+str(tmp))

            else: values.append(False)

            # model 4
            if self.main.MODELS[3] == True:
                index = None
                # get index of residue in model 4
                for i in range(len(R1rho.model4)):
                    if R1rho.model4[i]['residue'] == residue:
                        index = i
                        break

                if not index == None:
                    if self.main.SETTINGS[0] == 'AIC':
                        tmp = AIC(R1rho.model4[index]['chi2'], R1rho.model4[index]['k'])
                        values.append(tmp)
                        wx.CallAfter(self.main.report_panel.AppendText, '\nModel 4:\t'+str(tmp))

                    else:
                        tmp = AICc(R1rho.model4[index]['chi2'], R1rho.model4[index]['k'], R1rho.model4[index]['n'])
                        values.append(tmp)
                        wx.CallAfter(self.main.report_panel.AppendText, '\nModel 4:\t'+str(tmp))

            else: values.append(False)


            # Select
            selection_value = 9999999999999999999999
            selection = 0

            for i in range(len(values)):
                if values[i] == False:
                    continue

                if values[i] < selection_value:
                    selection = i
                    selection_value = values[i]

            # Save selection
            R1rho.selected.append({'residue':residue, 'model':selection + 1})

            # Feedback
            wx.CallAfter(self.main.report_panel.AppendText, '\n\nModel '+str(selection+1)+' selected.\n==========================================\n')

        # spacer
        wx.CallAfter(self.main.report_panel.AppendText, '\n')


    def montecarlo(self, globalfit=False, onresonance=False):
        """Function to perform monte carlo simulation."""

        # field and offset
        field = array(self.spinlock_power)
        offset = array(self.offset)

        # loop over residues
        for residue in range(len(R1rho.r1rho[0])):
            # fit container
            fit_container = []

            # x values container
            x = []

            # loop over experiments
            for exp in range(len(R1rho.r1rho)):
                # read x values
                x.append(R1rho.r1rho[exp][residue][0])

            # selected model
            model = None
            for i in range(len(R1rho.selected)):
                if (residue+1) == R1rho.selected[i]['residue']:
                    model = R1rho.selected[i]['model']

            # Skip, if residue is not in selected models and set mc error to None
            if model == None:
                R1rho.montecarlo.append(None)
                continue

            # Extracted parameters
            p_extracted = None
            if model == 1:
                for i in range(len(R1rho.model1)):
                    if (residue+1) == R1rho.model1[i]['residue']:
                        p_extracted = R1rho.model1[i]['fit']
            if model == 2:
                for i in range(len(R1rho.model2)):
                    if (residue+1) == R1rho.model2[i]['residue']:
                        p_extracted = R1rho.model2[i]['fit']
            if model == 3:
                for i in range(len(R1rho.model3)):
                    if (residue+1) == R1rho.model3[i]['residue']:
                        p_extracted = R1rho.model3[i]['fit']
            if model == 4:
                for i in range(len(R1rho.model4)):
                    if (residue+1) == R1rho.model4[i]['residue']:
                        p_extracted = R1rho.model4[i]['fit']

            # abort if p = None
            if p_extracted == None:
                continue

            # Dictionary for models
            func = {'1':R1p_model_1, '2':R1p_model_2, '3':R1p_model_3, '4':R1p_model_4}
            fit_func = {'1':R1p_model_1_residuals, '2':R1p_model_2_residuals, '3':R1p_model_3_residuals, '4':R1p_model_4_residuals}

            # feedback
            wx.CallAfter(self.main.checkrun_label.SetLabel, 'Monte Carlo Simulation, Residue '+str(residue+1))

            # Monte Carlo Simulation
            for mc in range(int(self.main.SETTINGS[1])):
                # feedback
                wx.CallAfter(self.main.report_panel.AppendText, '\nMonte Carlo Simulation '+str(mc+1)+', Residue '+str(residue+1))

                # synthetic data container
                y_synth = []

                # loop over experiment
                for exp in range(len(x)):
                    # error container
                    error = []
                    for exp1 in range(len(R1rho.r1rho)):
                        error.append(R1rho.r1rho_error[exp1][residue])

                    # Y container
                    y_tmp = []

                    # Create synthetic data
                    for i in range(len(x[exp])):
                        # On resonance
                        if onresonance:
                            dw = len(x[exp]) * [0]
                            y_tmp.append(func[str(model)](p_extracted, array(x[exp][i]), array(dw[i])))

                        # on resonance
                        else:
                            w1 = len(x[exp]) * [0]
                            y_tmp.append(func[str(model)](p_extracted, array(w1[i]), array(x[exp][i])))

                    # Store
                    y_synth.append(array(y_tmp))

                # fit
                fit = leastsq(fit_func[str(model)], p_extracted, args=(y_synth, error, field, offset, globalfit, False, self.main.spec_freq), full_output = 1, col_deriv = 1, ftol = self.main.tolerance, xtol = self.main.tolerance, maxfev=2000000)

                # Store
                fit_container.append(fit[0])

            # Calculate errors
            errors = []

            # loop over parameters
            for par in range(len(fit_container[0])):
                errors.append([])

                # loop over mc simulations
                for mc in range(len(fit_container)):
                    errors[par].append(fit_container[mc][par])

            # calculate errors
            errors_pooled = []
            for i in range(len(errors)):
                errors_pooled.append(sqrt(var(errors[i], ddof=1)))

            # Assign errors
            r1 = []
            r2 = []

            # Model 1
            if model == 1:
                for i in range(len(errors_pooled)):
                    # R1
                    if i%2 == 0:
                        r1.append(errors_pooled[i])
                    # R2
                    else:
                        r2.append(errors_pooled[i])

                # Store results
                R1rho.montecarlo.append({'residue':residue+1, 'r1':r1, 'r2':r2})

            # Model 2
            if model == 2:
                # kex
                kex = errors_pooled[0]

                # Phi
                phi = errors_pooled[1]

                for i in range(2, len(errors_pooled)):
                    # R1
                    if i%2 == 0:
                        r1.append(errors_pooled[i])
                    # R2
                    else:
                        r2.append(errors_pooled[i])

                # Store results
                R1rho.montecarlo.append({'residue':residue+1, 'kex':kex, 'phi':phi, 'r1':r1, 'r2':r2})

            # Model 3 or 4
            if model in [3, 4]:
                # kex
                kex = errors_pooled[0]

                # dw
                dw = errors_pooled[1]

                # pb
                pb = errors_pooled[2]

                for i in range(3, len(errors_pooled)):
                    # R2
                    if i%2 == 0:
                        r2.append(errors_pooled[i])
                    # R1
                    else:
                        r1.append(errors_pooled[i])

                # Store results
                R1rho.montecarlo.append({'residue':residue+1, 'kex':kex, 'dw':dw, 'pb':pb, 'r1':r1, 'r2':r2})


    def plot(self, x, y, x1, y1, error=None, fileroot='', xlabel='', ylabel='', max=0, min=0, model=1):
        """ Function to create plots."""
        # Colors
        color = ['BLUE', 'RED', 'GREEN', 'YELLOW', 'CYAN', 'GOLD', 'MAGENTA', 'NAVY', 'ORANGE', 'PINK', 'PURPLE', 'BLACK', 'GRAY', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK' ]

        # Frame width
        params={'axes.linewidth' : self.main.FRAMEWIDTH}
        pylab.rcParams.update(params)

        # Create plots
        for i in range(len(x)):
            # Data plots
            pylab.errorbar(x[i], y[i], yerr = error[i], color=color[i], fmt ='o')

            # Regression
            pylab.plot(x1[i], y1[i], '-', color=color[i])

        # labels
        pylab.xlabel(xlabel, fontsize=19, weight='bold')
        pylab.ylabel(ylabel, fontsize=19, weight='bold')

        # Size of axis labels
        pylab.xticks(fontsize=19)
        pylab.yticks(fontsize=19)

        # Range
        if min < 0: pylab.xlim(min+0.1*min, max+0.1*max)
        else:       pylab.xlim(min-0.1*min, max+0.1*max)

        # save png
        pylab.savefig(self.pngdir+sep+fileroot+'.png', dpi = 72, transparent = True)

        # Store 3d plots
        if model == 1:
            self.main.tree_results.AppendItem (self.main.plots_model1, self.pngdir+sep+fileroot+'.png', 0)
            self.main.results_model1.append(self.pngdir+sep+fileroot+'.png')
        if model ==2:
            self.main.tree_results.AppendItem (self.main.plots_model2, self.pngdir+sep+fileroot+'.png', 0)
            self.main.results_model2.append(self.pngdir+sep+fileroot+'.png')
        if model ==3:
            self.main.tree_results.AppendItem (self.main.plots_model3, self.pngdir+sep+fileroot+'.png', 0)
            self.main.results_model3.append(self.pngdir+sep+fileroot+'.png')
        if model ==4:
            self.main.tree_results.AppendItem (self.main.plots_model4, self.pngdir+sep+fileroot+'.png', 0)
            self.main.results_model4.append(self.pngdir+sep+fileroot+'.png')

        # save vector file
        pylab.savefig(self.vectordir+sep+fileroot+self.main.PLOTFORMAT)

        # clear graph
        pylab.cla()
        pylab.close()
