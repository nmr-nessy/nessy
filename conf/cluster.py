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


# Selection of residues to calculate

# Python modules
from os import makedirs, sep
import pylab
from random import random, uniform
from scipy.optimize import leastsq
from scipy import array, sqrt, linspace, var
try:
    import thread as _thread
except ImportError:
    import _thread
import time
import wx

# NESSY modules
from conf.path import NESSY_PIC, IMPORT_DATA_SIDE_PIC
from conf.message import question, message
from func.color_code import color_code
from func.r2eff import R2_eff as calc_R2eff
from func.pooled_variance import Pooled_variance
from elements.variables import Pi
from curvefit.estimate import estimate
from math_fns.gridsearch import gridsearch
from curvefit.chi2 import Chi2_container


# Models
from math_fns.cluster import model_2, model_2_residuals, model_3, model_3_residuals, model_4, model_4_residuals, model_5, model_5_residuals, model_6, model_6_residuals, model_7, model_7_residuals



class Cluster_residues(wx.Frame):
    def __init__(self, main, *args, **kwds):
        # assign parameters
        self.main = main

        # Store selected residues
        self.included_residues = self.main.INCLUDE_RES

        # running flag
        self.running = False

        # Create Window
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX
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
        self.header = wx.StaticText(self, -1, "Cluster Residues")
        self.header.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        mainsizer.Add(self.header, 0, wx.ALL|wx.ALIGN_LEFT, 5)

        # Line
        self.static_line_2 = wx.StaticLine(self, -1)
        mainsizer.Add(self.static_line_2, 0, wx.EXPAND, 0)

        # Text
        self.header = wx.StaticText(self, -1, "Clustered residues will be fitted simultaneously.")
        mainsizer.Add(self.header, 0, wx.ALL|wx.ALIGN_LEFT, 5)

        # Line
        self.static_line_1 = wx.StaticLine(self, -1)
        mainsizer.Add(self.static_line_1, 0, wx.EXPAND, 0)

        # Residues
        sizer_resi = wx.BoxSizer(wx.HORIZONTAL)
        self.label_resi = wx.StaticText(self, -1, "Cluster residues:")
        self.label_resi.SetMinSize((150, 17))
        sizer_resi.Add(self.label_resi, 0, 0, 0)

        self.residues = wx.ListBox(self, -1, choices=self.read_resi(), style = wx.LB_MULTIPLE)
        self.residues.SetMinSize((150, 250))
        sizer_resi.Add(self.residues, 0, 0, 0)
        # Select according to settings
        for i in range(0, self.residues.GetCount()):
            self.residues.SetSelection(i, self.main.INCLUDE_RES[i])

        self.button_all = wx.Button(self, -1, "Select all")
        self.Bind(wx.EVT_BUTTON, self.select_all, self.button_all)
        sizer_resi.Add(self.button_all, 0, 0, 0)
        mainsizer.Add(sizer_resi, 1, wx.ALL|wx.EXPAND, 5)

        # Line
        self.static_line_3 = wx.StaticLine(self, -1)
        mainsizer.Add(self.static_line_3, 0, wx.EXPAND, 0)

        # Model
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.label_model = wx.StaticText(self, -1, "Select Model:")
        self.label_model.SetMinSize((150, 17))
        sizer.Add(self.label_model, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.model = wx.Choice(self, -1, choices=["Model 2", "Model 3", "Model 4", "Model 5", "Model 6", "Model 7"])
        self.model.SetMinSize((130, 25))
        sizer.Add(self.model, 0, 0, 0)
        mainsizer.Add(sizer, 0, wx.ALL, 5)

        # sizer
        sizer_exp = wx.BoxSizer(wx.HORIZONTAL)

        # data file number text
        self.experiment_text = wx.StaticText(self, -1, "Experiment No.:")
        self.experiment_text.SetMinSize((150, 17))
        sizer_exp.Add(self.experiment_text, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        # Data file number selector
        # Detect experiment
        # on settings tab
        if self.main.MainTab.GetSelection() < 0:
            page = 1

        # on start or results tab
        elif self.main.MainTab.GetSelection() > (self.main.MainTab.GetPageCount()-2):
            page = 1

        # experiment tab
        else:
            page = self.main.MainTab.GetSelection()

        # Pack sizer
        mainsizer.Add(sizer_exp, 0, wx.ALL, 5)

        # Line
        self.static_line_4 = wx.StaticLine(self, -1)
        mainsizer.Add(self.static_line_4, 0, wx.EXPAND, 0)

        # Buttons
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.button_start = wx.Button(self, -1, "Start")
        self.Bind(wx.EVT_BUTTON, self.start, self.button_start)
        sizer_buttons.Add(self.button_start, 0, 0, 0)

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


    def close(self, event):
        # restore selected residues
        self.main.INCLUDE_RES = self.included_residues

        # Destroy dialog
        self.Destroy()


    def cluster(self):
        """Function to cluster R2eff and variance."""
        # containers
        self.r2eff_cluster = []
        self.residue_container = []
        self.cpmg_container = []
        self.freqs = []
        self.B0 = []
        self.variance_cluster = []
        self.experiment_cluster = []

        # Repetitions index
        self.repetitions = []
        self.repetitions_index = []

        # residue index
        self.residue_cont = []

        # number of repetitions
        self.num_of_exp = len(self.R2eff_pooled)

        # loop over experiments
        for exp in range(len(self.R2eff_pooled)):
            # loop over residues
            for residue in range(len(self.R2eff_pooled[exp])):
                # check if values are present
                present = False
                for i in range(len(self.R2eff_pooled[exp][residue])):
                    if self.R2eff_pooled[exp][residue][i]:
                        present = True

                # store if data present
                if present:

                    # Store r2eff
                    self.r2eff_cluster.append(self.R2eff_pooled[exp][residue])

                    # store residue
                    self.residue_container.append(residue+1)

                    # store cpmg times
                    self.cpmg_container.append(self.pooled_cpmg[exp])

                    # heteronuclear frequency
                    self.freqs.append(self.main.spec_freq[exp])

                    # heteronuclear frequency
                    self.B0.append(self.main.spec_freq[exp])

                    # store variance
                    self.variance_cluster.append(self.pooled_variance_store[exp][residue])

                    # experiment
                    self.experiment_cluster.append(str(exp+1))

                    # if global fit, save information about doublicate
                    if (residue+1) in self.residue_cont:
                        # This is a repetitions
                        self.repetitions.append(True)

                        # index residue
                        self.residue_cont.append(residue+1)
                        self.repetitions_index.append(self.residue_cont.index(residue+1))

                    else:
                        # index residue
                        self.residue_cont.append(residue+1)
                        self.repetitions_index.append(len(self.residue_container)-1)

                        # This is a not repetitions
                        self.repetitions.append(False)


    def color_code(self):
        """Creating color coded structures of Phi (model 2) or dw (model 3)."""

        # Feedback
        wx.CallAfter(self.main.checkrun_label.SetLabel, 'Color coded structure')
        wx.CallAfter(self.main.report_panel.AppendText, '\n\n----------------------------------------------------------\nCreating color coded structures: ')


        # Selected model
        sel_model = int(self.model.GetSelection())+2

        # Model 2
        if sel_model == 2:
            color_code(self.color_residue, self.phi, 'Color_code_phi_model_'+str(sel_model)+'.pml', str(self.main.proj_folder.GetValue()) +sep+'cluster', pdb_file=self.main.PDB)

        if sel_model == 3:
            color_code(self.color_residue, self.dw, 'Color_code_phi_model_'+str(sel_model)+'.pml', str(self.main.proj_folder.GetValue()) +sep+'cluster', pdb_file=self.main.PDB)

        # Feedback
        wx.CallAfter(self.main.report_panel.AppendText, 'done.\n----------------------------------------------------------\n\n')


    def create_csv(self, xy):
        """Function to create csv text."""
        # directory
        directory = str(self.main.proj_folder.GetValue())+sep+'cluster'
        try:
            makedirs(directory)
        except:
            a = 'dir exists'

        # open file
        file = open(directory+sep+'Cluster.csv', 'w')

        # model 2
        if int(self.model.GetSelection()) == 0:
            # write header
            file.write('Residue;R2 [1/s];err;kex [1/s];err;Phi [(ppm/s)**2];err;Rex first exp. [rad/s];err;Chi2\n')

            # loop over results
            for i in range(len(xy[0])):
                # Residue
                file.write(str(self.residue_container[i])+';')
                # R2
                file.write(str(self.fit[0][2+(2*i)])+';')
                file.write(str(self.error[2+(2*i)])+';')
                # Kex
                file.write(str(self.fit[0][0])+';')
                file.write(str(self.error[0])+';')
                # Phi
                file.write(str(self.fit[0][(2*self.repetitions_index[i])+1])+';')
                file.write(str(self.error[(2*self.repetitions_index[i])+1]/(float(self.freqs[i].GetValue())*2*Pi)**2)+';')
                # Rex
                file.write(str(self.fit[0][(2*self.repetitions_index[i])+1] * (2*Pi*float(self.freqs[0].GetValue()))**2/self.fit[0][0])+';')
                file.write(';')
                # chi2
                file.write(str(self.chi2_individual[i])+'\n')

        # model 3, 6 and 7
        if int(self.model.GetSelection()) in [1, 4, 5]:
            # write header
            file.write('Residue;R2 [1/s];err;kex [1/s];err;pb;err;dw [ppm];err;Rex first exp. [rad/s];err;Chi2\n')

            # loop over results
            for i in range(len(xy[0])):
                # Residue
                file.write(str(self.residue_container[i])+';')
                # R2
                file.write(str(self.fit[0][(2*i)+3])+';')
                file.write(str(self.error[(2*i)+3])+';')
                # Kex
                file.write(str(self.fit[0][0])+';')
                file.write(str(self.error[0])+';')
                # pb
                file.write(str(self.fit[0][1])+';')
                file.write(str(self.error[1])+';')
                # dw
                file.write(str(self.fit[0][(2*self.repetitions_index[i])+2])+';')
                file.write(str(self.error[(2*self.repetitions_index[i])+2]/(float(self.freqs[i].GetValue())*2*Pi))+';')
                # Rex
                file.write(str((self.fit[0][1]*(1-self.fit[0][1])*self.fit[0][0]) / (1 + (self.fit[0][0]/(self.fit[0][(2*self.repetitions_index[i])+2]* float(self.freqs[0].GetValue())*2*Pi)**2)))+';')
                file.write(';')
                # chi2
                file.write(str(self.chi2_individual[i])+'\n')

        # model 4
        if int(self.model.GetSelection()) == 2:
            # write header
            file.write('Residue;R2 [1/s];err;kex A-B [1/s];err;Phi A-B [(rad/s)**2];err;Rex A-B first exp. [rad/s];err;kex B-C [1/s];err;Phi B-C [(rad/s)**2];err;Rex B-C first exp. [rad/s];err;Chi2\n')

            # loop over results
            for i in range(len(xy[0])):
                # parameters
                kex = self.fit[0][0]
                kex2 = self.fit[0][1]
                phi = self.fit[0][(3*self.repetitions_index[i])+2]
                phi2 = self.fit[0][(3*self.repetitions_index[i])+3]
                R2 = self.fit[0][4+(3*i)]

                # Residue
                file.write(str(self.residue_container[i])+';')
                # R2
                file.write(str(R2)+';')
                file.write(str(self.error[4+(3*i)])+';')
                # Kex
                file.write(str(kex)+';')
                file.write(str(self.error[0])+';')
                # Phi
                file.write(str(phi)+';')
                file.write(str(self.error[(3*self.repetitions_index[i])+2]/(float(self.freqs[i].GetValue())*2*Pi)**2)+';')
                # Rex
                file.write(str(phi * (2*Pi * float(self.freqs[0].GetValue()))**2/kex)+';')
                file.write(';')
                # Kex2
                file.write(str(kex2)+';')
                file.write(str(self.error[1])+';')
                # Phi2
                file.write(str(phi2)+';')
                file.write(str(self.error[(3*self.repetitions_index[i])+3]/(float(self.freqs[i].GetValue())*2*Pi)**2)+';')
                # Rex2
                file.write(str(phi2 * (2*Pi * float(self.freqs[0].GetValue()))**2/kex2)+';')
                file.write(str(';'))
                # chi2
                file.write(str(self.chi2_individual[i])+'\n')

        # model 5
        if int(self.model.GetSelection()) == 3:
            # write header
            file.write('Residue;R2 [1/s];err;kex A-B [1/s];err;pb;err;dw A-B [ppm];err;Rex A-B last exp. [rad/s];err;kex B-C [1/s];err;pc;err;dw B-C [ppm];err;Rex B-C last exp. [rad/s];err;Chi2\n')

            # loop over results
            for i in range(len(xy[0])):
                # Parameters
                kex = self.fit[0][0]
                kex2 = self.fit[0][1]
                pb = self.fit[0][2]
                pc = self.fit[0][3]
                dw = self.fit[0][4+(3*self.repetitions_index[i])]
                dw2 = self.fit[0][5+(3*self.repetitions_index[i])]
                R2 = self.fit[0][6+(3*i)]
                # errors
                kex_err = self.error[0]
                kex2_err = self.error[1]
                pb_err = self.error[2]
                pc_err = self.error[3]
                dw_err = self.error[4+(3*self.repetitions_index[i])]
                dw2_err = self.error[5+(3*self.repetitions_index[i])]
                R2_err = self.error[6+(3*i)]

                # Residue
                file.write(str(self.residue_container[i])+';')
                # R2
                file.write(str(R2)+';')
                file.write(str(R2_err)+';')
                # Kex
                file.write(str(kex)+';')
                file.write(str(kex_err)+';')
                # pb
                file.write(str(pb)+';')
                file.write(str(pb_err)+';')
                # dw
                file.write(str(dw)+';')
                file.write(str(dw_err/(float(self.freqs[i].GetValue())*2*Pi))+';')
                # Rex
                file.write(str((pb*(1-pb)*kex) / (1 + (kex/(dw* float(self.freqs[0].GetValue())*2*Pi))**2))+';')
                file.write(';')
                # Kex2
                file.write(str(kex2)+';')
                file.write(str(kex2_err)+';')
                # pc
                file.write(str(pc)+';')
                file.write(str(pc_err)+';')
                # dw2
                file.write(str(dw2)+';')
                file.write(str(dw2_err/(float(self.freqs[i].GetValue())*2*Pi))+';')
                # Rex2
                file.write(str((pc*(1-pc)*kex2) / (1 + (kex2/(dw2* float(self.freqs[0].GetValue())*2*Pi))**2))+';')
                file.write(';')
                # chi2
                file.write(str(self.chi2_individual[i])+'\n')

        # write global chi2
        file.write('\nGlobal chi2: '+str(self.chi2_global))

        # close file
        file.close()

        # add file to results tree
        self.main.tree_results.AppendItem (self.main.txt, directory+sep+'Cluster.csv', 0)

        # save entry
        self.main.results_txt.append(directory+sep+'Cluster.csv')


    def create_xy(self):
        """Function to create x and y pair."""
        # containers
        x = []
        y = []

        # loop over r2eff
        for i in range(len(self.r2eff_cluster)):
            # temporary containers
            x_tmp = []
            y_tmp = []

            # loop over entries
            for j in range(len(self.r2eff_cluster[i])):
                # store if data is present
                if self.r2eff_cluster[i][j]:
                    y_tmp.append(float(self.r2eff_cluster[i][j]))
                    x_tmp.append(float(self.cpmg_container[i][j]))

            # store item
            if not x_tmp == []:
                x.append(array(x_tmp))
                y.append(array(y_tmp))

        # return xy pair
        return [x, y]


    def read_resi(self):
        residues = []
        # loop over residues
        for resi in range(0, self.main.RESNO):
            if not str(self.main.data_grid[0].GetCellValue(resi, 0)) == '':
                residues.append(str(resi+1)+'\t'+str(self.main.data_grid[0].GetCellValue(resi, 0)))

        #self.residues.InsertItems(residues, 0)
        return residues


    def minimise(self, xy, p):
        """Function to minimize data."""
        wx.CallAfter(self.main.checkrun_label.SetLabel, 'Cluster analysis model '+str(int(self.model.GetSelection())+2))

        # Containers for Phi and dw to create color coded structures
        self.phi = []
        self.dw = []
        self.color_residue = []

        # model dictionary
        models = {'2':model_2_residuals, '3':model_3_residuals, '4':model_4_residuals, '5':model_5_residuals, '6':model_6_residuals, '7':model_7_residuals}

        # Selected model
        sel_model = str(int(self.model.GetSelection())+2)

        # convergence method
        if self.main.CONVERGENCE:
            # chi2 to compare
            chi2_old = 999
            chi2_current = 9999999999

            # repeat until convergence
            while not chi2_old == chi2_current:
                # minimise
                self.fit = leastsq(models[sel_model], p, args=((xy[1]), (xy[0]), self.variance_cluster, self.main.report_panel, True, self.freqs, self.repetitions_index), full_output = 1, col_deriv = 1, ftol = self.main.tolerance/2, xtol = self.main.tolerance/2, maxfev=2000000)

                # adjust ch2
                chi2_old = chi2_current
                chi2_current = sum(Chi2_container.chi2)

                # new estimation
                p_estimated = self.fit[0]

        # least square only or grid search minimisation method
        else:
            # fit
            self.fit = leastsq(models[sel_model], p, args=((xy[1]), (xy[0]), self.variance_cluster, self.main.report_panel, True, self.freqs, self.repetitions_index), full_output = 1, col_deriv = 1, ftol = self.main.tolerance, xtol = self.main.tolerance, maxfev=2000000)

        # calculate chi2
        chi2 = sum(Chi2_container.chi2)

        # Container for individual chi2
        self.chi2_individual = []

        # loop over cluster
        for i in range(len(xy[0])):
            # model 2
            if int(self.model.GetSelection()) == 0:
                # Parameters
                kex = self.fit[0][0]
                phi = self.fit[0][(2*self.repetitions_index[i])+1] * (float(self.freqs[i].GetValue()) * 2*Pi)**2
                R2 = self.fit[0][2+(2*i)]
                p_estimated = [R2, phi, kex]

                # Calculate values
                y_estimated = model_2(xy[0][i], p_estimated)

                # Calculate chi2
                chi2_tmp = sum((y_estimated - xy[1][i])**2/self.variance_cluster[i])

                # report summary
                # R2
                self.main.Model2_grid.SetCellValue(self.residue_container[i]-1, 0, str(R2))
                # Phi
                self.main.Model2_grid.SetCellValue(self.residue_container[i]-1, 3, str(phi))
                # kex
                self.main.Model2_grid.SetCellValue(self.residue_container[i]-1, 1, str(kex))
                #Rex
                self.main.Model2_grid.SetCellValue(self.residue_container[i]-1, 2, str(phi/kex))
                # Chi2
                self.main.Model2_grid.SetCellValue(self.residue_container[i]-1, 4, str(chi2_tmp))

                # store values for color coded structure
                self.phi.append(phi)
                self.color_residue.append(self.residue_container[i])

            # model 3
            if int(self.model.GetSelection()) == 1:
                # Parameters
                kex = self.fit[0][0]
                pb = self.fit[0][1]
                dw = self.fit[0][(2*self.repetitions_index[i])+2]*float(self.freqs[i].GetValue())*2*Pi
                R2 = self.fit[0][(2*i)+3]
                p_estimated = [R2, kex, dw, pb]

                # Calculate values
                y_estimated = model_3(xy[0][i], p_estimated)

                # Calculate chi2
                chi2_tmp = sum((y_estimated - xy[1][i])**2/self.variance_cluster[i])

                # report in summary
                # R2
                self.main.Model3_grid.SetCellValue(self.residue_container[i]-1, 0, str(R2))
                # kex
                self.main.Model3_grid.SetCellValue(self.residue_container[i]-1, 1, str(kex))
                # Rex
                self.main.Model3_grid.SetCellValue(self.residue_container[i]-1, 2, str((pb * (1 - pb) * kex) / (1 + (kex/dw)**2)))
                # dw
                self.main.Model3_grid.SetCellValue(self.residue_container[i]-1, 3, str(dw/(float(self.freqs[i].GetValue())*2*Pi)))
                # pb
                self.main.Model3_grid.SetCellValue(self.residue_container[i]-1, 4, str(pb))
                # Chi2
                self.main.Model3_grid.SetCellValue(self.residue_container[i]-1, 5, str(chi2_tmp))

                # store values for color coded structure
                self.dw.append(dw)
                self.color_residue.append(self.residue_container[i])

            # model 4
            if int(self.model.GetSelection()) == 2:
                # Parameters
                kex = self.fit[0][0]
                kex2 = self.fit[0][1]
                phi = self.fit[0][(3*self.repetitions_index[i])+2] * (float(self.freqs[i].GetValue()) * 2*Pi)**2
                phi2 = self.fit[0][(3*self.repetitions_index[i])+3] * (float(self.freqs[i].GetValue()) * 2*Pi)**2
                R2 = self.fit[0][4+(3*i)]
                p_estimated = [R2, phi, kex, phi2, kex2]

                # Calculate values
                y_estimated = model_4(xy[0][i], p_estimated)

                # Calculate chi2
                chi2_tmp = sum((y_estimated - xy[1][i])**2/self.variance_cluster[i])

                # report summary
                # R2
                self.main.Model4_grid.SetCellValue(self.residue_container[i]-1, 0, str(R2))
                # kex
                self.main.Model4_grid.SetCellValue(self.residue_container[i]-1, 1, str(kex))
                # Rex
                self.main.Model4_grid.SetCellValue(self.residue_container[i]-1, 2, str(phi/kex))
                # Phi
                self.main.Model4_grid.SetCellValue(self.residue_container[i]-1, 3, str(phi))
                # kex
                self.main.Model4_grid.SetCellValue(self.residue_container[i]-1, 4, str(kex2))
                # Rex
                self.main.Model4_grid.SetCellValue(self.residue_container[i]-1, 5, str(phi2/kex2))
                # Phi
                self.main.Model4_grid.SetCellValue(self.residue_container[i]-1, 6, str(phi2))
                # Chi2
                self.main.Model4_grid.SetCellValue(self.residue_container[i]-1, 7, str(chi2_tmp))

            # model 5
            if int(self.model.GetSelection()) == 3:
                # Parameters
                kex = self.fit[0][0]
                kex2 = self.fit[0][1]
                pb = self.fit[0][2]
                pc = self.fit[0][3]
                dw = self.fit[0][(3*self.repetitions_index[i])+4]*float(self.freqs[i].GetValue())*2*Pi
                dw2 = self.fit[0][(3*self.repetitions_index[i])+5]*float(self.freqs[i].GetValue())*2*Pi
                R2 = self.fit[0][(3*i)+6]
                p_estimated = [R2, kex, dw, pb, kex2, dw2, pc]

                # Calculate values
                y_estimated = model_5(xy[0][i], p_estimated)

                # Calculate chi2
                chi2_tmp = sum((y_estimated - xy[1][i])**2/self.variance_cluster[i])

                # report in summary
                # R2
                self.main.Model5_grid.SetCellValue(self.residue_container[i]-1, 0, str(R2))
                # kex
                self.main.Model5_grid.SetCellValue(self.residue_container[i]-1, 1, str(kex))
                # Rex
                self.main.Model5_grid.SetCellValue(self.residue_container[i]-1, 2, str((pb * (1 - pb) * kex) / (1 + (kex/dw)**2)))
                # dw
                self.main.Model5_grid.SetCellValue(self.residue_container[i]-1, 3, str(dw/(float(self.freqs[i].GetValue())*2*Pi)))   # in ppm
                # pb
                self.main.Model5_grid.SetCellValue(self.residue_container[i]-1, 4, str(pb))
                # kex2
                self.main.Model5_grid.SetCellValue(self.residue_container[i]-1, 5, str(kex2))
                # Rex2
                self.main.Model5_grid.SetCellValue(self.residue_container[i]-1, 6, str((pc * (1 - pc) * kex2) / (1 + (kex2/dw2)**2)))
                # dw2
                self.main.Model5_grid.SetCellValue(self.residue_container[i]-1, 7, str(dw2/(float(self.freqs[i].GetValue())*2*Pi)))  # in ppm
                # pb2
                self.main.Model5_grid.SetCellValue(self.residue_container[i]-1, 8, str(pc))
                # Chi2
                self.main.Model5_grid.SetCellValue(self.residue_container[i]-1, 9, str(chi2_tmp))

            # model 6
            if int(self.model.GetSelection()) == 4:
                # Parameters
                kex = self.fit[0][0]
                pb = self.fit[0][1]
                dw = self.fit[0][(2*self.repetitions_index[i])+2]*float(self.freqs[i].GetValue())*2*Pi
                R2 = self.fit[0][(2*i)+3]
                p_estimated = [R2, kex, dw, pb]

                # Calculate values
                y_estimated = model_6(xy[0][i], p_estimated)

                # Calculate chi2
                chi2_tmp = sum((y_estimated - xy[1][i])**2/self.variance_cluster[i])

                # report in summary
                # R2
                self.main.Model6_grid.SetCellValue(self.residue_container[i]-1, 0, str(R2))
                # kex
                self.main.Model6_grid.SetCellValue(self.residue_container[i]-1, 1, str(kex))
                # Rex
                self.main.Model6_grid.SetCellValue(self.residue_container[i]-1, 2, str((pb * (1 - pb) * kex) / (1 + (kex/dw)**2)))
                # dw
                self.main.Model6_grid.SetCellValue(self.residue_container[i]-1, 3, str(dw/(float(self.freqs[i].GetValue())*2*Pi)))
                # pb
                self.main.Model6_grid.SetCellValue(self.residue_container[i]-1, 4, str(pb))
                # Chi2
                self.main.Model6_grid.SetCellValue(self.residue_container[i]-1, 5, str(chi2_tmp))

            # model 7
            if int(self.model.GetSelection()) == 5:
                # Parameters
                kex = self.fit[0][0]
                pb = self.fit[0][1]
                dw = self.fit[0][(2*self.repetitions_index[i])+2]*float(self.freqs[i].GetValue())*2*Pi
                R2 = self.fit[0][(2*i)+3]
                p_estimated = [R2, kex, dw, pb]

                # Calculate values
                y_estimated = model_6(xy[0][i], p_estimated)

                # Calculate chi2
                chi2_tmp = sum((y_estimated - xy[1][i])**2/self.variance_cluster[i])

                # report in summary
                # R2
                self.main.Model7_grid.SetCellValue(self.residue_container[i]-1, 0, str(R2))
                # kex
                self.main.Model7_grid.SetCellValue(self.residue_container[i]-1, 1, str(kex))
                # Rex
                self.main.Model7_grid.SetCellValue(self.residue_container[i]-1, 2, str((pb * (1 - pb) * kex) / (1 + (kex/dw)**2)))
                # dw
                self.main.Model7_grid.SetCellValue(self.residue_container[i]-1, 3, str(dw/(float(self.freqs[i].GetValue())*2*Pi)))
                # pb
                self.main.Model7_grid.SetCellValue(self.residue_container[i]-1, 4, str(pb))
                # Chi2
                self.main.Model7_grid.SetCellValue(self.residue_container[i]-1, 5, str(chi2_tmp))

            # save individual chi2
            self.chi2_individual.append(chi2_tmp)

            # Sum up chi2
            #chi2 = chi2 + chi2_tmp

        # Save global chi2
        self.chi2_global = chi2


    def montecarlo(self, xy, model_sel):
        """Monte Carlo Simulation.

        Rex and Phi is calculated for last experiment.
        """
        # The model
        model = str(model_sel)

        # Dummy model selection container
        self.main.MODEL_SELECTION = []
        self.main.MODEL_SELECTION_ERROR = []

        # Update Status
        wx.CallAfter(self.main.checkrun_label.SetLabel, 'Monte Carlo Simulation...')
        wx.CallAfter(self.main.report_panel.AppendText, '\n\n----------------------------------------------------------\nMonte Carlo Simulation\n----------------------------------------------------------\n\n')

        # gauge
        wx.CallAfter(self.main.gauge_1.SetValue, 0)

        # maximum number of entries
        self.max_entries = len(self.r2eff_cluster)

        # reser progress bar
        wx.CallAfter(self.main.gauge_1.SetValue, 0)

        # dictionaries of functions
        func = {'2':model_2, '3':model_3, '4':model_4, '5':model_5, '6':model_6, '7':model_7}
        residuals = {'2':model_2_residuals, '3':model_3_residuals, '4':model_4_residuals, '5':model_5_residuals, '6':model_6_residuals, '7':model_7_residuals}

        # container of extracted parameters
        p = []

        # add fixed parameters
        if model == '2':
            p.append(self.fit[0][0])    # kex
        if model in ['3', '6', '7']:
            p = p + [self.fit[0][0], self.fit[0][1]]    # kex, pb
        if model == '4':
            p = p + [self.fit[0][0], self.fit[0][1]]    # kex1, kex2
        if model == '5':
            p = p + [self.fit[0][0], self.fit[0][1], self.fit[0][2], self.fit[0][3]]    # kex1, kex2, pb, pc

        # Read parameters
        for i in range(len(xy[0])):
            # model 2
            if model == '2':
                # Parameters
                phi = self.fit[0][(2*self.repetitions_index[i])+1] * (float(self.freqs[i].GetValue()) * 2*Pi)**2
                R2 = self.fit[0][2+(2*i)]
                p = p + [phi, R2]

            # model 3, 6 and 7
            if model in ['3', '6', '7']:
                # Parameters
                dw = self.fit[0][(2*self.repetitions_index[i])+2]*float(self.freqs[i].GetValue())*2*Pi
                R2 = self.fit[0][(2*i)+3]
                p = p + [dw, R2]

            # model 4
            if model == '4':
                # Parameters
                phi = self.fit[0][(3*self.repetitions_index[i])+2] * (float(self.freqs[i].GetValue()) * 2*Pi)**2
                phi2 = self.fit[0][(3*self.repetitions_index[i])+3] * (float(self.freqs[i].GetValue()) * 2*Pi)**2
                R2 = self.fit[0][4+(3*i)]
                p = p + [phi, phi2, R2]

            # model 5
            if int(self.model.GetSelection()) == 3:
                # Parameters
                dw = self.fit[0][(3*self.repetitions_index[i])+4]*float(self.freqs[i].GetValue())*2*Pi
                dw2 = self.fit[0][(3*self.repetitions_index[i])+5]*float(self.freqs[i].GetValue())*2*Pi
                R2 = self.fit[0][(3*i)+6]
                p = p + [dw, dw2, R2]

        # containers for error variables
        pooled_fit = [] #* len(self.fit[0])

        # empty continer
        for i in range(len(self.fit[0])):
            pooled_fit.append([])

        # Monte Carlo Simulation
        for mc in range(int(self.main.SETTINGS[1])):
            # Feedback
            wx.CallAfter(self.main.report_panel.AppendText, 'Monte Carlo Simulation ' + str(mc+1) +'\n' )
            time.sleep(0.001)

            # create synthetic y values
            y_synth = []

            # loop over experiments
            for exp in range(len(xy[0])):
                # parameters
                # model 2
                if model == '2':
                    # Parameters
                    kex = self.fit[0][0]
                    phi = self.fit[0][(2*self.repetitions_index[exp])+1] * (float(self.freqs[exp].GetValue()) * 2*Pi)**2
                    R2 = self.fit[0][2+(2*exp)]
                    p_estimated = [R2, phi, kex]

                # model 3, 6 and 7
                if model in ['3', '6', '7']:
                    # Parameters
                    kex = self.fit[0][0]
                    pb = self.fit[0][1]
                    dw = self.fit[0][(2*self.repetitions_index[exp])+2]*float(self.freqs[exp].GetValue())*2*Pi
                    R2 = self.fit[0][(2*exp)+3]
                    p_estimated = [R2, kex, dw, pb]

                # model 4
                if model == '4':
                    # Parameters
                    kex = self.fit[0][0]
                    kex2 = self.fit[0][1]
                    phi = self.fit[0][(3*self.repetitions_index[exp])+2] * (float(self.freqs[exp].GetValue()) * 2*Pi)**2
                    phi2 = self.fit[0][(3*self.repetitions_index[exp])+3] * (float(self.freqs[exp].GetValue()) * 2*Pi)**2
                    R2 = self.fit[0][4+(3*exp)]
                    p_estimated = [R2, phi, kex, phi2, kex2]

                # model 5
                if model == '5':
                    # Parameters
                    kex = self.fit[0][0]
                    kex2 = self.fit[0][1]
                    pb = self.fit[0][2]
                    pc = self.fit[0][3]
                    dw = self.fit[0][(3*self.repetitions_index[exp])+4]*float(self.freqs[exp].GetValue())*2*Pi
                    dw2 = self.fit[0][(3*self.repetitions_index[exp])+5]*float(self.freqs[exp].GetValue())*2*Pi
                    R2 = self.fit[0][(3*exp)+6]
                    p_estimated = [R2, kex, dw, pb, kex2, dw2, pc]

                # temporary y container (one experiment)
                y_sim = []

                # error
                error = sqrt(self.variance_cluster[exp])

                # loop over x values for particular experiment
                for sim in range(len(xy[0][exp])):
                    y_sim.append(func[model](xy[0][exp][sim], p_estimated)+uniform(-error, error))

                # store simulated y values
                y_synth.append(array(y_sim))

            # Minimise
            fit = leastsq(residuals[model], p, args=((y_synth), (xy[0]), self.variance_cluster, False, True, self.freqs, self.repetitions_index), full_output = 1, col_deriv = 1, ftol = self.main.tolerance, xtol = self.main.tolerance, maxfev=2000000)

            # store parameters
            for i in range(len(fit[0])):
                pooled_fit[i].append(fit[0][i])

            # update gauge
            wx.CallAfter(self.main.gauge_1.SetValue, min(100, int((mc+1)*100/int(self.main.SETTINGS[1]))))

        # error container
        error_container = []

        # calculate errors
        for i in range(len(pooled_fit)):
            error_container.append(sqrt(var(pooled_fit[i], ddof = 1)))

        # update progress bar
        per = 100
        wx.CallAfter(self.main.gauge_1.SetValue, min(100, per))

        # store error
        self.error = error_container


    def plot(self, xy):
        """Function to create plots."""

        # directory
        directory = str(self.main.proj_folder.GetValue())+sep+'cluster'
        try:
            makedirs(directory)
        except:
            a = 'dir exists'

        # Colors
        colors = ['BLUE', 'RED', 'GREEN', 'YELLOW', 'CYAN', 'GOLD', 'MAGENTA', 'NAVY', 'ORANGE', 'PINK', 'PURPLE', 'BLACK', 'GRAY', 'BLUE', 'RED', 'GREEN', 'YELLOW', 'CYAN', 'GOLD', 'MAGENTA', 'NAVY', 'ORANGE', 'PINK', 'PURPLE', 'BLACK', 'GRAY', 'BLUE', 'RED', 'GREEN', 'YELLOW', 'CYAN', 'GOLD', 'MAGENTA', 'NAVY', 'ORANGE', 'PINK', 'PURPLE', 'BLACK', 'GRAY', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK', 'BLACK' ]

        # Experiment
        experiment = {'1':'-', '2':'--', '3':'-.', '4':':', '5':'-', '6':'--', '7':'-.', '8':':'}

        # shape
        shape = {'1':'o', '2':'^', '3':'v', '4':'>', '5':'<', '6':'*', '7':'H', '8':'D'}

        # detect maximum cpmg frequency
        max = 0

        # loop over entries
        for i in range(len(self.cpmg_container)):
            # loop over entries
            for j in range(len(self.cpmg_container[i])):
                # compare to max
                if not str(self.cpmg_container[i][j]) == '':
                     if float(self.cpmg_container[i][j]) > max:
                        max = float(self.cpmg_container[i][j])

        # Set up
        # Frame width
        params={'axes.linewidth' : self.main.FRAMEWIDTH}
        pylab.rcParams.update(params)

        # selected model
        sel_model = int(self.model.GetSelection()) + 2

        # Rex container
        x_rex = []
        y_rex = []
        x_fit_rex = []
        y_fit_rex = []

        # add plots
        # loop over data
        for i in range(len(xy[0])):
            # csv text
            csv_text = ''

            # create xy plot
            pylab.errorbar(xy[0][i], xy[1][i], yerr = sqrt(self.variance_cluster[i]), color=colors[self.repetitions_index[i]], fmt =shape[str(self.experiment_cluster[i])])

            # create fit
            # craete data points
            x_values = linspace(0, max+(0.1 * max), num=500)

            # model 2
            if int(self.model.GetSelection()) == 0:
                # Parameters
                kex = self.fit[0][0]
                R2 = self.fit[0][(2*i)+2]
                phi = self.fit[0][(2*self.repetitions_index[i])+1]*(float(self.freqs[i].GetValue()) * 2*Pi)**2
                p_estimated = [R2, phi, kex]

                # Calculate values
                y_values = model_2(x_values, p_estimated)

            # model 3, 6 and 7
            if int(self.model.GetSelection()) in [1, 4, 5]:
                # Parameters
                kex = self.fit[0][0]
                pb = self.fit[0][1]
                dw = self.fit[0][2+(2*self.repetitions_index[i])]*float(self.freqs[i].GetValue()) * 2*Pi
                R2 = self.fit[0][3+(2*i)]
                p_estimated = [R2, kex, dw, pb]

                # Calculate values
                y_values = model_3(x_values, p_estimated)

            # model 4
            if int(self.model.GetSelection()) == 2:
                # Parameters
                kex = self.fit[0][0]
                kex2 = self.fit[0][1]
                phi = self.fit[0][(3*self.repetitions_index[i])+2]*(float(self.freqs[i].GetValue()) * 2*Pi)**2
                phi2 = self.fit[0][(3*self.repetitions_index[i])+3]*(float(self.freqs[i].GetValue()) * 2*Pi)**2
                R2 = self.fit[0][(3*i)+4]
                p_estimated = [R2, phi, kex, phi2, kex2]

                # Calculate values
                y_values = model_4(x_values, p_estimated)

            # model 5
            if int(self.model.GetSelection()) == 3:
                # Parameters
                kex = self.fit[0][0]
                kex2 = self.fit[0][1]
                pb = self.fit[0][2]
                pc = self.fit[0][3]
                dw = self.fit[0][4+(3*self.repetitions_index[i])]*float(self.freqs[i].GetValue()) * 2*Pi
                dw2 = self.fit[0][5+(3*self.repetitions_index[i])]*float(self.freqs[i].GetValue()) * 2*Pi
                R2 = self.fit[0][6+(3*i)]
                p_estimated = [R2, kex, dw, pb, kex2, dw2, pc]

                # Calculate values
                y_values = model_5(x_values, p_estimated)

            # Rex data
            x_rex.append([j - R2 for j in xy[0][i]])
            y_rex.append([j - R2 for j in xy[1][i]])
            x_fit_rex.append([j - R2 for j in x_values])
            y_fit_rex.append([j - R2 for j in y_values])

            # plot
            pylab.plot(x_values, y_values, experiment[str(self.experiment_cluster[i])], color=colors[self.repetitions_index[i]], label = 'Residue '+str(self.residue_container[i])+', Exp. '+str(self.experiment_cluster[i]))

        # Save file
        # Labels
        pylab.xlim(0, max+(0.1 * max))
        y_min = float(self.main.SETTINGS[5])
        y_max = float(self.main.SETTINGS[6])
        pylab.ylim(y_min, y_max)
        pylab.xlabel('v(CPMG) [Hz]', fontsize=19, weight='bold')
        pylab.ylabel('R2eff [1/s]', fontsize=19, weight='bold')
        pylab.xticks(fontsize=19)
        pylab.yticks(fontsize=19)
        pylab.legend()

        # save vector plot
        pylab.savefig(directory+sep+'Cluster.'+self.main.PLOTFORMAT)

        # Png
        if sel_model in [2, 3]:
            pylab.figtext(0.13, 0.11, 'kex: '+str(kex)+' 1/s')
        elif sel_model in [4, 5]:
            pylab.figtext(0.13, 0.11, 'kex(A-B): '+str(kex)+' 1/s, kex(B-C): '+str(kex2)+' 1/s')
        pylab.savefig(directory+sep+'Cluster.png', dpi = 72, transparent = True)

        # clear plot
        pylab.cla()
        pylab.close()

        # Store plot
        self.main.tree_results.AppendItem (self.main.plots2d, directory+sep+'Cluster.png', 0)
        self.main.plot2d.append(directory+sep+'Cluster.png')

        # Rex plots
        for i in range(len(x_rex)):
            # Data points
            pylab.errorbar(x_rex[i], y_rex[i], yerr = sqrt(self.variance_cluster[i]), color=colors[self.repetitions_index[i]], fmt =shape[str(self.experiment_cluster[i])])

            # Regression
            pylab.plot(x_fit_rex[i], y_fit_rex[i], experiment[str(self.experiment_cluster[i])], color=colors[self.repetitions_index[i]], label = 'Residue '+str(self.residue_container[i])+', Exp. '+str(self.experiment_cluster[i]))

        # Save plot
        # Labels
        pylab.xlim(0, max+(0.1 * max))
        y_min = float(self.main.SETTINGS[5])
        y_max = float(self.main.SETTINGS[6])
        #pylab.ylim(y_min, y_max)
        pylab.xlabel('v(CPMG) [Hz]', fontsize=19, weight='bold')
        pylab.ylabel('Rex [1/s]', fontsize=19, weight='bold')
        pylab.xticks(fontsize=19)
        pylab.yticks(fontsize=19)
        pylab.legend()

        # save vector plot
        pylab.savefig(directory+sep+'Cluster_Rex.'+self.main.PLOTFORMAT)

        # Png
        pylab.figtext(0.13, 0.11, 'kex: '+str(kex)+' 1/s')
        pylab.savefig(directory+sep+'Cluster_Rex.png', dpi = 72, transparent = True)

        # clear plot
        pylab.cla()
        pylab.close()

        # Store plot
        self.main.tree_results.AppendItem (self.main.plots2d, directory+sep+'Cluster_Rex.png', 0)
        self.main.plot2d.append(directory+sep+'Cluster_Rex.png')


    def pool(self):
        """Removes offset of effective R2eff."""
        # Detect number of experiments
        exp_no = self.main.NUMOFDATASETS

        # R2eff
        R2eff = []

        # self.R2eff_pooled
        self.R2eff_pooled = []

        # poooled variance storage
        self.pooled_variance_store = []

        # CPMG frequencies
        self.pooled_cpmg = []

        # loop over calculated experiments
        for exp in range(0, exp_no):

            # Calculate R2eff
            calc_R2eff(self.main, exp)

            # save R2eff without offset
            self.R2eff_pooled.append(self.main.R2eff)

            # Calculate pooled variance
            Pooled_variance(self.main, exp)

            # save pooled variance
            self.pooled_variance_store.append(self.main.R2eff_variance[exp])

            # CPMG freq
            self.pooled_cpmg.append(self.main.CPMGFREQ[exp])


    def select_all(self, event):
        for i in range(0, self.residues.GetCount()):
            self.residues.SetSelection(i, True)


    def start(self, event):
        # Sync selected residues
        self.sync()

        # Sow start analysis tab
        self.main.MainTab.SetSelection(self.main.MainTab.GetPageCount()-3)

        # start calculation
        try:
            _thread.start_new_thread(self.start_calc, ())

        except:
            a = 'something wrong'


    def start_calc(self):
        """Run calculation in thread."""
        # Calculate R2eff, variance, CPMG freq and heteronuc frequencies
        self.pool()

        # cluster R2eff
        self.cluster()

        # number of experiments == number of clustered data sets
        exp = len(self.r2eff_cluster) + 1

        # initial guess
        p = estimate(self, model=int(self.model.GetSelection())+2, cluster=exp)

        # create x and y data for fit
        xy = self.create_xy()

        # grid search
        if self.main.GRIDSEARCH:
            p_estimated = gridsearch(base_dir=str(self.main.proj_folder.GetValue()), data=xy, experiment='cpmg-cluster', output=self.main.report_panel, fileroot='Cluster_Model_'+str(int(self.model.GetSelection())+2)+'_Surface', frequencies=self.freqs, grid_size=self.main.GRID_INCREMENT, INI_R2=self.main.INI_R2, model=int(self.model.GetSelection())+2, variance=self.variance_cluster, output_tree=self.main.tree_results, savecont=self.main.plot3d, output1=self.main.plots3d, globalfit=False)

        # minimise
        self.minimise(xy, p)

        # create plots
        self.plot(xy)

        # Monte Carlo Simulation
        self.montecarlo(xy, int(self.model.GetSelection())+2)

        # Create csv summary
        self.create_csv(xy)

        # Create color coded structures
        self.color_code()

        # Feedback
        wx.CallAfter(self.main.checkrun_label.SetLabel, 'Done.')
        wx.CallAfter(self.main.report_panel.AppendText, '\n\n______________________________________________________\n\nFinished clustered fit!\nPlots are in 2D Plots.\n______________________________________________________\n')


    def sync(self):
        """Saves selected residues."""
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
