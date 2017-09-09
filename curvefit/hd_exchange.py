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


# scipt to fit R2eff to no exchange model

# Python modules
from random import random, uniform
from scipy.optimize import leastsq
import pylab
from scipy import array, sqrt, linspace, var, sort
import wx
import os
from os import sep, makedirs
import time

# NESSY modules
from math_fns.hd_exchange import HD, HD_fit


class Calculate_HD():
    '''Class for fit H/D exchange'''


    def __init__(self, gui):
        '''Initialize and start calculation.'''

        # Synchronize data
        self.main = gui

        # Data container
        self.Fits = [] # list of {'residue':...., 'fit':...., 'error':....}

        # loop over experiment
        self.reference_index = 0
        for exp in range(0, self.main.NUMOFDATASETS):

            # detect maximum time
            max = 0
            for i in range(0, len(self.main.HD_TIME[exp])):
                if str(self.main.HD_TIME[exp][i]) == '':
                    continue
                if float(self.main.HD_TIME[exp][i]) > max:
                    max = float(self.main.HD_TIME[exp][i])

            # loop over residues
            for residue_index in range(0, self.main.RESNO):
                # only calculate if residue is selected to calculate
                if not self.main.INCLUDE_RES[residue_index]:
                    continue

                # T container
                T = []

                # time dependent intensity
                I = []
                for entry in range(0, int(self.main.SETTINGS[2])):
                    # data is present
                    if not str(self.main.data_grid[exp].GetCellValue(residue_index, entry+1)) == '':
                        # save intensity
                        I.append(float(self.main.data_grid[exp].GetCellValue(residue_index, entry+1)))
                        T.append(float(self.main.HD_TIME[exp][entry]))

                # check if data is present
                if I in [[], None]:
                    continue

                # error = noise of data
                error_noise = float(self.main.HD_NOISE[exp])

                # aboort if not more data points than variables
                if len(I) < 3:
                    continue

                # write comment
                # Report start of analysis
                wx.CallAfter(self.main.report_panel.AppendText, '\n\nCurve fit to Residue ' + str(residue_index + 1)+'\n\n')

                # values
                y = I
                x = T

                # convert in % to max
                max_value = 0
                for i in range(0, len(y)):
                    if y[i] > max_value:
                        max_value = y[i]
                y = [(100*i)/max_value for i in y]
                error_noise = (error_noise * 100)/max_value

                # estimated initial values
                if self.main.INITIAL_HD[0] == 'error':
                    I_0 = error_noise
                else:
                    I_0 = float(self.main.INITIAL_HD[0])
                kex = float(self.main.INITIAL_HD[2])
                C = float(self.main.INITIAL_HD[1])
                p_est = [I_0, C, kex]

                # minimise
                fit = leastsq(HD_fit, p_est, args=(array(y), array(x), error_noise, self.main.report_panel), full_output = 1, col_deriv = 1, ftol = self.main.tolerance, xtol = self.main.tolerance, maxfev=2000000)

                # Monte carlo simulation
                mc = self.monte_carlo(x, y, error_noise, fit[0])

                # calculate chi2
                chi2 = self.chi2(x, y, error_noise, fit[0])

                # save calculation
                self.Fits.append({'residue':(residue_index+1), 'fit':fit[0], 'error':mc, 'chi2':chi2})

                # plot
                self.plot(x=x, y=y, error=error_noise, p=fit[0], residue=residue_index+1, directory=str(self.main.proj_folder.GetValue()), max=max, mc=mc, experiment=exp+1)

            # Write csv summary
            self.csv_summary(exp+1)

            # Create color coded structure
            self.color_code(exp+1)


    def chi2(self, x, y, error_noise, p):
        '''Calculation of chi2.'''
        # chi2 function
        chi2 = sum(((HD(array(x), p) - y))**2)

        # return value
        return chi2


    def color_code(self, exp):
        '''Craete color coded structure.'''
        # directory
        dir =str(self.main.proj_folder.GetValue())+sep+'HD_exchange'+sep+'pymol_macro'
        try:
            makedirs(dir)
        except:
            a=''

        # read kex and residues
        residue = []
        kex = []
        for i in range(0, len(self.Fits)):
            residue.append(self.Fits[i]['residue'])
            kex.append(self.Fits[i]['fit'][2])

        # detect highest kex
        max = 0
        for i in range(0, len(kex)):
            if kex[i] > max:
                max = kex[i]

        # normalize kex
        kex = [i/max for i in kex]

        # open file
        file = open(dir+sep+'Exp_'+str(exp)+'_kex.pml', 'w')

        # Load structure file.
        if not str(self.main.pdb_file.GetValue()) == '':
            file.write('load '+str(self.main.pdb_file.GetValue())+'\n')

        # Hide everything
        file.write('hide all\n')

        # set white background
        file.write('bg_color white\n')

        # colour molecule in gray
        file.write('color gray90\n')

        # show backbone
        file.write('show sticks, name C+N+CA\nset stick_quality, 10\n')

        # color coded entries
        for i in range(0, len(residue)):
            #thickness
            file.write('set_bond stick_radius, '+str(sqrt(kex[i]))+', resi '+str(residue[i])+'\n')

            # color
            file.write('set_color resicolor'+str(residue[i])+', '+str([1, 1- sqrt(kex[i]), 0])+'\n')
            file.write('color resicolor'+str(residue[i])+', resi '+str(residue[i])+'\n')

        # ray trace structure
        file.write('ray\n')

        # close file
        file.close()

        # Add file to results tree
        self.main.tree_results.AppendItem (self.main.structures, dir+sep+'Exp_'+str(exp)+'_kex.pml', 0)
        self.main.COLOR_PDB.append(dir+sep+'Exp_'+str(exp)+'_kex.pml')

        # report
        wx.CallAfter(self.main.report_panel.AppendText, '\n\n-------------------------------------------------\nPyMol macro created.\n-------------------------------------------------\n')


    def csv_summary(self, exp):
        '''Create a final CSV file.'''
        # filename
        filename = str(self.main.proj_folder.GetValue())+sep+'HD_exchange'+sep+'csv'+sep+'Summary_experiment_'+str(exp)+'.csv'

        # open file
        file = open(filename, 'w')

        # header
        file.write('residue;I(inf) [% to max];error;C;error;kex [1/s];error;Chi2\n')

        # write entries
        for entry in range(0, len(self.Fits)):
            file.write(str(self.Fits[entry]['residue'])+';'+str(self.Fits[entry]['fit'][0])+';'+str(self.Fits[entry]['error'][0])+';'+str(self.Fits[entry]['fit'][1])+';'+str(self.Fits[entry]['error'][1])+';'+str(self.Fits[entry]['fit'][2]/60)+';'+str(self.Fits[entry]['error'][2]/60)+';'+str(self.Fits[entry]['chi2'])+'\n')

        # close file
        file.close()

        # add file to results tree
        self.main.tree_results.AppendItem (self.main.txt, filename, 0)
        # save entry
        self.main.results_txt.append(filename)

        # report
        wx.CallAfter(self.main.report_panel.AppendText, '\n\n-------------------------------------------------\nCSV File summary created.\n-------------------------------------------------\n')

        # create plot
        # filename
        fileroot = str(self.main.proj_folder.GetValue())+sep+'HD_exchange'+sep+'Summary_experiment_'+str(exp)

        # collect x, y and error
        x = []
        y = []
        err = []
        for entry in range(0, len(self.Fits)):
            x.append(self.Fits[entry]['residue'])
            y.append(self.Fits[entry]['fit'][2]/60)
            err.append(self.Fits[entry]['error'][2]/60)

        # Frame width
        params={'axes.linewidth' : self.main.FRAMEWIDTH}
        pylab.rcParams.update(params)

        # plot
        pylab.errorbar(array(x), array(y), yerr=err, fmt='ko')

        # detect minimum
        min = 0
        while min < self.main.RESNO and str(self.main.data_grid[exp-1].GetCellValue(min, 0)) == '': min += 1

        # detect maximum
        max = min+1
        while max < self.main.RESNO and not str(self.main.data_grid[exp-1].GetCellValue(max, 0)) == '': max += 1

        # Labels
        pylab.xlabel('Residue Number', fontsize=19, weight='bold')
        pylab.ylabel('kex [1/s]', fontsize=19, weight='bold')
        pylab.xticks(fontsize=19)
        pylab.yticks(fontsize=19)
        pylab.xlim(min, max)

        # save plots
        pylab.savefig(fileroot+self.main.PLOTFORMAT)
        pylab.savefig(fileroot+'.png', dpi = 72, transparent = True)

        # add to results tab
        self.main.tree_results.AppendItem (self.main.plots2d, fileroot+'.png', 0)
        self.main.plot2d.append(fileroot+'.png')

        # Crear plot
        pylab.cla() # clear the axes
        pylab.close() #clear figure

        # report
        wx.CallAfter(self.main.report_panel.AppendText, '\n\n-------------------------------------------------\nkex plot created.\n-------------------------------------------------\n')


    def monte_carlo(self, x, y, error, p):
        """monte carlo simulation."""
        mc_num = int(self.main.SETTINGS[1])

        # containers
        I0 = []
        C = []
        kex = []

        # monte carlo simulation
        for mc in range(0, mc_num):
            wx.CallAfter(self.main.report_panel.AppendText, '\nMonte Carlo Simulation '+str(mc+1))

            # loop over x values
            y_synth = []
            for i in range(0, len(x)):
                y_synth.append(HD(x[i], p) + uniform(-error, error))

            # fit
            fit = leastsq(HD_fit, p, args=(array(y_synth), array(x), error, False), full_output = 1, col_deriv = 1, ftol = self.main.tolerance, xtol = self.main.tolerance, maxfev=2000000)

            # store fits
            I0.append(fit[0][0])
            C.append(fit[0][1])
            kex.append(fit[0][2])

        # calculate error
        I0_err = sqrt(var(I0, ddof = 1))
        C_err = sqrt(var(C, ddof = 1))
        kex_err = sqrt(var(kex, ddof = 1))

        return [I0_err, C_err, kex_err]


    def plot(self, x=None, y=None, error=None, p=None, residue=None, directory=None, max=None, mc=None, experiment=None):
        # Create plots for HD exchange

        # directory
        directory = directory+sep+'HD_exchange'
        try:
            makedirs(directory)
        except:
            a = 'already exists'

        # detect minimum and maximum
        t = y
        sort(t)
        min = t[0]
        max = max

        # Frame width
        params={'axes.linewidth' : self.main.FRAMEWIDTH}
        pylab.rcParams.update(params)

        # plot of datapoints
        pylab.errorbar(array(x), array(y), yerr=error, fmt='ko')

        # fit
        x_fit = linspace(min, max, num=1000)
        y_fit = HD(array(x_fit), p)

        # plot fit
        pylab.plot(array(x_fit), array(y_fit), 'r-')

        # Labels
        pylab.xlabel('T [s]', fontsize=19, weight='bold')
        pylab.ylabel('Intensity [% to max]', fontsize=19, weight='bold')
        pylab.xticks(fontsize=19)
        pylab.yticks(fontsize=19)
        pylab.xlim(0, max)
        pylab.ylim(0, 120)

        # svg image
        pylab.savefig(directory+sep+'Residue '+str(residue)+self.main.PLOTFORMAT)

        # png
        pylab.figtext(0.13, 0.85, 'Residue '+str(residue)+', kex = '+str(p[2]/60)+' +/- '+str(mc[2]/60)+' 1/s.', fontsize=12)
        pylab.savefig(directory+sep+'Residue '+str(residue)+'.png', dpi = 72, transparent = True)

        # add to results tab
        self.main.tree_results.AppendItem (self.main.plots2d, directory+sep+'Residue '+str(residue)+'.png', 0)
        self.main.plot2d.append(directory+sep+'Residue '+str(residue)+'.png')

        # Crear plot
        pylab.cla() # clear the axes
        pylab.close() #clear figure

        # create csv file
        try:
            makedirs(directory+sep+'csv')
        except:
            a = ''

        # data points
        file = open(directory+sep+'csv'+sep+'Exp_'+str(experiment)+'_Residue_'+str(residue)+'.csv', 'w')
        file.write('Time [s];Intensity [% to max]\n')
        for i in range(0, len(x)):
            file.write(str(x[i])+';'+str(y[i])+'\n')
        file.close()

        # add file to results tree
        self.main.tree_results.AppendItem (self.main.txt, directory+sep+'csv'+sep+'Exp_'+str(experiment)+'_Residue_'+str(residue)+'.csv', 0)
        # save entry
        self.main.results_txt.append(directory+sep+'csv'+sep+'Exp_'+str(experiment)+'_Residue_'+str(residue)+'.csv')

        # fit
        file = open(directory+sep+'csv'+sep+'Exp_'+str(experiment)+'_Residue_'+str(residue)+'_fit.csv', 'w')
        file.write('Time [s];Intensity [% to max]\n')
        for i in range(0, len(x_fit)):
            file.write(str(x_fit[i])+';'+str(y_fit[i])+'\n')
        file.close()

        # add file to results tree
        self.main.tree_results.AppendItem (self.main.txt, directory+sep+'csv'+sep+'Exp_'+str(experiment)+'_Residue_'+str(residue)+'_fit.csv', 0)
        # save entry
        self.main.results_txt.append(directory+sep+'csv'+sep+'Exp_'+str(experiment)+'_Residue_'+str(residue)+'_fit.csv')
