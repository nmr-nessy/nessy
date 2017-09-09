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


# Python Imports
import wx
import sys
try:
    import thread as _thread
except ImportError:
    import _thread
from time import sleep

# NESSY imports
from conf.data import sort_datasets



def checkinput(self):
    _thread.start_new_thread(check, (self,))
    sleep(0.5)
    _thread.start_new_thread(pulsing, (self.gauge_1, self.report_panel))


def check(self):
    self.error_flag = False

    # disable 'Start Calculation' button and set progress bar to 0 %
    wx.CallAfter(self.start_calc.Enable, (False))
    wx.CallAfter(self.gauge_1.SetValue, 0)
    wx.CallAfter(self.report_panel.AppendText, ('\nEvaluating Datasets and Experiments:\n==================================================\n\n'))

    # numbers of experiments
    num_exp = self.NUMOFDATASETS

    # max number of datasets
    num_data = int(self.SETTINGS[2])

    # Experiment index to analyse
    self.SET_UP_EXPERIMENT = []

    # debugging mode
    if self.debug:
        # add experiments without testing
        for i in range(0, num_exp):
            self.SET_UP_EXPERIMENT.append(i)

        # enable if not running on mac
        if not 'darwin' in sys.platform:
            self.menubar.EnableTop(4, True)

        # enable 'Start Calculation' button
        wx.CallAfter(self.start_calc.Enable, (True))
        self.isrunning = False

        # return
        Checking.check = False
        sleep(1)
        return

    # check if project folder is set
    wx.CallAfter(self.report_panel.AppendText, ('\nChecking if project folder is set up...\t\t\t'))
    checkpoint = False
    if str(self.proj_folder.GetValue()) == '':
        wx.CallAfter(self.report_panel.AppendText, '\nNo project folder specified.\n')
        self.isrunning = False
        Checking.check = False
        sleep(1)
        return False
    else: wx.CallAfter(self.report_panel.AppendText, '[Ok]\n\n')

    # Value for progress bar
    pbar = 1

    # Loop over experiment
    for experiment in range(0, num_exp):
        # Report
        wx.CallAfter(self.report_panel.AppendText, ('Evaluating Experiment '+str(experiment+1)+'.....\n=============================================\n\n'))

        # CPMG and HD experiment
        if self.sel_experiment[0].GetSelection() in [0, 3]:

            # check if several datasets are specified
            wx.CallAfter(self.report_panel.AppendText, 'Checking if datasets are set up...\t\t\t\t')
            checkpoint = False
            if not self.NUM_OF_DATASET[experiment] > 1:
                wx.CallAfter(self.report_panel.AppendText, '\nDatasets are not set up.\n')
                Checking.check = False
                sleep(1)
                return False
            else: wx.CallAfter(self.report_panel.AppendText, '[Ok]\n\n')

            # check if data is present and positive
            wx.CallAfter(self.report_panel.AppendText, 'Checking if values are entered correctly...\t\t')
            checkpoint_exp = False
            # loop over residue
            for residue in range(0, self.RESNO):
                # loop over datasets
                for dataset in range(1, num_data+1):
                    for residue in range(0, self.RESNO):
                        # adjust progress bar
                        pbar = pbar + 1
                        #wx.CallAfter(self.gauge_1.SetValue, min(100, int(pbar/100)))
                        #sleep(0.000001)
                        if pbar == 10000: pbar = 0

                        # Data is present
                        if not str(self.data_grid[experiment].GetCellValue(residue, dataset)) == '':
                            checkpoint_exp = True

                            # Value is a number
                            try:
                                float(self.data_grid[experiment].GetCellValue(residue, dataset))
                            except:
                                checkpoint_exp = False
                                wx.CallAfter(self.report_panel.AppendText, ('\nEntered value in dataset '+str(dataset)+' for residue '+str(residue+1)+' in experiment '+str(experiment+1)+' is not a number.\n'))
                                Checking.check = False
                                sleep(1)
                                return False

                            # Value is positive
                            if float(self.data_grid[experiment].GetCellValue(residue, dataset)) < 0:
                                checkpoint_exp = False
                                wx.CallAfter(self.report_panel.AppendText, ('\nNegative value found in dataset '+str(dataset)+' for residue '+str(residue+1)+' in experiment '+str(experiment+1)+'.\n'))
                                Checking.check = False
                                sleep(1)
                                return False

            if checkpoint_exp == False:
                wx.CallAfter(self.report_panel.AppendText, ('\nMissing data in experiment '+str(experiment+1)+'.\n'))
                Checking.check = False
                sleep(1)
                return False
            else: wx.CallAfter(self.report_panel.AppendText, '[Ok]\n\n')

        # check if reference is set upin CPMG dispersion
        if self.sel_experiment[0].GetSelection() == 0:
            wx.CallAfter(self.report_panel.AppendText, 'Checking if reference spectrum is set up...\t\t')
            checkpoint = False
            if '0' in self.CPMGFREQ[experiment]: checkpoint = True
            if not checkpoint:
                wx.CallAfter(self.report_panel.AppendText, '\nNo reference spectrum is set up in experiment '+str(experiment+1)+'.\n')
                self.isrunning = False
                Checking.check = False
                sleep(1)
                return False
            else: wx.CallAfter(self.report_panel.AppendText, '[Ok]\n\n')

        # Report
        wx.CallAfter(self.report_panel.AppendText, ('\n Experiment '+str(experiment+1)+ ' checked.\n'))

        # Add experiment index to enable calculation
        self.SET_UP_EXPERIMENT.append(experiment)

    # Number of residues
    seq = 0
    for i in range(0, self.RESNO):
          if not str(self.data_grid[0].GetCellValue(i, 0)) == '':
                seq = seq + 1

    # write summary
    output = 'Experiment:\n' + str(self.sel_experiment[experiment].GetStringSelection()) + '\n\nProject Folder:\n' + str(self.proj_folder.GetValue())  + '\n\nMolecule has ' + str(seq) + ' Residues'  + '\n\nNumber of experiments to calculate ' + str(len(self.SET_UP_EXPERIMENT))

    wx.CallAfter(self.text_ctrl_1.SetValue, (output))

    # enable 'Start Calculation' button
    wx.CallAfter(self.start_calc.Enable, (True))
    self.isrunning = False

    # Feedback
    if len(self.SET_UP_EXPERIMENT) == 1:
        output = str(len(self.SET_UP_EXPERIMENT)) + ' experiment'
    else:
        output = str(len(self.SET_UP_EXPERIMENT)) + ' experiments'
    wx.CallAfter(self.report_panel.AppendText, ('\n-----------------------------------------------------------------\n'+output+' will be analyzed.\n-----------------------------------------------------------------\n\n'))

    # enable if not running on mac
    if not 'darwin' in sys.platform:
        self.menubar.EnableTop(4, True)

    # release pulsing gauge
    Checking.check = False
    sleep(1)



def pulsing(gauge, panel):
    # pulsing gauge

    # timer
    timer = 0

    # pulse until finished pulsing
    while Checking.check == True:
            # pulse gauge
            wx.CallAfter(gauge.Pulse)
            sleep(0.05)

            # add timer
            timer = timer + 1

            if timer > (120/0.05):
                wx.CallAfter(panel.AppendText, '\n\nAn error occurred....\n\n')
                break

    # set gauge to 0
    wx.CallAfter(gauge.SetValue, 0)



class Checking():
    '''Class for checking flag.'''
    check = True
