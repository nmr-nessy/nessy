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
import os
import sys
from os import sep
from scipy import mean, array, sqrt, std, var
import time
import wx

# NESSY modules
from conf.data import sync_data



class Pooled_variance():
    """Calculate pooled variance of R2eff values."""
    def __init__(self, gui, exp_index):
        # link parameters
        self.main = gui

        # index of experiment
        self.exp_index = exp_index

        # Detect reference dataset
        for i in range(0, len(self.main.CPMGFREQ[self.exp_index])):
            if float(self.main.CPMGFREQ[self.exp_index][i]) == 0.0:
                self.reference_index = i
                break

        # detect repetitions
        self.detect_reps()

        # calculate individual variances
        self.calc_variances()

        # Calculate pooled variance
        self.calc_pooled_var()


    def detect_reps(self):
        # new line
        wx.CallAfter(self.main.report_panel.AppendText, '\n\n')

        # Detect repetitions
        self.repetitions_index = []
        for frequency in range(0, len(self.main.CPMGFREQ[self.exp_index])):
            # if there is an entry
            if not str(self.main.CPMGFREQ[self.exp_index][frequency]) == '':
                # frequence to compare with
                freq = frequency

                # temporary entry
                temp_entry = [freq]

                # compare frequency with other entries
                for i in range(frequency+1, len(self.main.CPMGFREQ[self.exp_index])):
                    # matching frequency found
                    if str(self.main.CPMGFREQ[self.exp_index][i]) == self.main.CPMGFREQ[self.exp_index][freq]:
                        temp_entry.append(i)

                # store entry if repetition was detected
                if len(temp_entry) > 1:
                    self.repetitions_index.append(temp_entry)

                    # output
                    wx.CallAfter(self.main.report_panel.AppendText, str(len(temp_entry)) + ' repetitions detected at ' + str(self.main.CPMGFREQ[self.exp_index][frequency]) + ' Hz\n')

        # new line
        wx.CallAfter(self.main.report_panel.AppendText, '\n')


    def calc_variances(self):
        # collect entries of repetitions and store variances

        # Loop over residues
        self.variances = []  # None, if no data / 0.1 if no repetition / list of variances if repetitions. Format: [variance, num of repetitions n]
        for residue in range(0, self.main.RESNO):
            # temporary list of variance
            variance_temp = []

            #loop over repeted frequencies
            for freq in range(0, len(self.repetitions_index)):
                #loop over repetitions of this frequency
                temp_entry = []

                # Check whether data is present for residue

                # loop over repetitions of same frequency
                for i in range(0, len(self.repetitions_index[freq])):
                    # Store R2eff is present for residue and data set
                    if self.main.R2eff[residue][self.repetitions_index[freq][i]]:
                        temp_entry.append(float(str(self.main.R2eff[residue][self.repetitions_index[freq][i]])))

                # repetitions have data
                if len(temp_entry) > 1:
                    variance_temp.append([var(temp_entry, ddof = 1), len(temp_entry)])

                    # output
                    wx.CallAfter(self.main.report_panel.AppendText, 'Variance for residue '+str(residue+1)+' at ' + str(self.main.CPMGFREQ[self.exp_index][self.repetitions_index[freq][0]]) + ' Hz is '+str(var(temp_entry, ddof = 1)) +'\n')


            # Store variance for each residue

            # no data
            if str(self.main.data_grid[self.exp_index].GetCellValue(residue, self.reference_index+1)) == '':
                self.variances.append(None)

            # no repetitions for this residue (due to missing data)
            elif variance_temp ==[]:
                self.variances.append(0.1)

            # repetitions are present for this residue
            else:
                self.variances.append(variance_temp)

        # new line
        wx.CallAfter(self.main.report_panel.AppendText, '\n')


    def calc_pooled_var(self):
            """Calculate pooled variance."""

            # Parameter list
            self.pooled_variance = []

            # loop over residues
            for residue in range(0, self.main.RESNO):

                # No data
                if self.variances[residue] == None:
                    self.pooled_variance.append(None)

                # No repetitions for residue
                elif self.variances[residue] == 0.1:
                    self.pooled_variance.append(0.1)

                # Data is present
                else:
                    enumerator = 0
                    dominator = 0

                    # loop over variances
                    for variance in range(0, len(self.variances[residue])):
                        var = self.variances[residue][variance][0]
                        n = self.variances[residue][variance][1]

                        # Summ up variances
                        enumerator = enumerator + ( (n-1) * var )
                        dominator = dominator + (n-1)

                    # Calculate pooled variance and store it
                    self.pooled_variance.append(enumerator/dominator)

                    # Output
                    wx.CallAfter(self.main.report_panel.AppendText, 'Pooled variance for residue '+str(residue+1)+' is ' + str((enumerator/dominator)) +'\n')

            # Store pooled variance in main GUI
            self.main.R2eff_variance[self.exp_index] = self.pooled_variance
