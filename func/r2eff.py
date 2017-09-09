#################################################################################
#                                                                               #
#   (C) 2010 Michael Bieri                                                      #
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


# scipt to calculate R2eff

'''
Calculations:

Error of Intensities:

Calculated according to pooled standard deviation (McNaught, A.D; Wilkinson, A; IUPAC Compendium of Chemical Termonology, 2nd Edition; Royal Society of Chemistry; Cambridge, UK, 1997

sigma[I] ^ 2 = std^2 / 2


R2eff Values:

R2eff = ( -1 / Tcpmg ) * ln( I[cpmg] / I[0] )

Standard Error of R2eff

sigma[r2eff(vCPMG)] = ( sigma[I] * I[0] ) / ( Tcpmg * I[vCPMG] )

'''


# Python modules
import math
import wx
import time
from scipy import mean, array, sqrt, std, var

# NESSY modules
from math_fns.r2eff import R2eff_cpmg, On_resonance


class R2_eff():
    """Class to calculate R2eff."""
    def __init__(self, self_main, exp_index, exp_mode=0):
        """Calculation of R2eff.

        restrict:       If None, then all residues will be calculated.
                        If a number, only this residue will be calculated

                        This is used in n-state model.
        """

        # Connect variables
        self.main = self_main

        # index of experiment
        self.exp_index = exp_index

        # update program status
        if exp_mode == 0:
            wx.CallAfter(self.main.checkrun_label.SetLabel, 'Running R2eff calculation...')
            report = "\nCalculating R2eff...\n"
        else:
            wx.CallAfter(self.main.checkrun_label.SetLabel, 'Running R1rho calculation...')
            report = "\nCalculating R1rho...\n"
        wx.CallAfter(self.main.report_panel.AppendText, report)

        # residues included having data
        self.main.include = []

        # informations for progress bar
        maximum = 0.0
        current_calc = 1.0

        # Calculate maximum
        for i in range(0, self.main.RESNO):
            if not str(self.main.data_grid[self.exp_index].GetCellValue(i, self.main.referencedata[self.exp_index])) == '':
                maximum = maximum + 1.0

        maximum = (maximum * (self.main.NUM_OF_DATASET[self.exp_index]-1))

        # Container for R2eff by increasing residue number
        r2eff = []
        for i in range(self.main.RESNO):
            r2eff.append([])

        # Index of reference dataset
        self.ref_index = self.main.referencedata[self.exp_index]

        # loop over residue
        for residue in range(0, self.main.RESNO):

            # Loop over data sets
            for dataset in range(1, self.main.NUM_OF_DATASET[self.exp_index]+1):

                # skip if no data or reference dataset
                skip = False

                # Reference dataset
                if float(self.main.CPMGFREQ[self.exp_index][dataset-1]) == 0.0:
                    skip = True
                # No data present
                if self.main.data_grid[self.exp_index].GetCellValue(residue, dataset) == '':
                    skip = True
                # Residue is disabled for calculation
                if not self.main.INCLUDE_RES[residue]:
                    skip = True
                # Reference spectrum is set up
                if self.main.data_grid[self.exp_index].GetCellValue(residue, self.ref_index) == '':
                    skip = True

                # add none if no data
                if skip:
                    r2eff[residue].append(None)

                # if data is present, calculate R2eff
                else:
                    # current intensity
                    I = float(self.main.data_grid[self.exp_index].GetCellValue(residue, dataset))

                    # Reference intensity
                    I0 = float(self.main.data_grid[self.exp_index].GetCellValue(residue, self.ref_index))

                    # CPMG delay
                    T = float(self.main.CPMG_DELAY[self.exp_index])

                    # calculate value

                    ####################################### Calculation ##################################

                    #          calculate R2eff according to: R2eff = (-ln{I(v[CPMG])/I(O)}) / T          #

                    ######################################################################################

                    #calc_r2eff = (1/T)*math.log(I0/I)
                    if exp_mode == 0:
                        calc_r2eff = R2eff_cpmg(T, I0, I)

                    # On resonance R1rho
                    if exp_mode == 1:
                        calc_r2eff = On_resonance(T, I0, I)

                    # store r2eff
                    r2eff[residue].append(calc_r2eff)

                    # uptdate progress bar
                    # set current number of calculation
                    current_calc = current_calc + 1

                    # get percentage
                    percentage = current_calc / maximum * 100

                    # update gauge
                    p = round(percentage)
                    pr = int(p)
                    wx.CallAfter(self.main.gauge_1.SetValue, min(100, pr))

                    # writing the log
                    if exp_mode == 0:
                        report = "\nCalculated R2eff for Residue " + str(residue+1) + ' of Dataset ' + str(dataset) + ' (R2eff = ' + str(r2eff[residue][dataset-1])+ ')'
                    if exp_mode == 1:
                        report = "\nCalculated R1rho for Residue " + str(residue+1) + ' of Dataset ' + str(dataset) + ' (R1rho = ' + str(r2eff[residue][dataset-1])+ ')'

                    wx.CallAfter(self.main.report_panel.AppendText, report)
                    time.sleep(0.01)

                    # add residue to include in further calcs
                    self.main.include.append(residue)

                    # Add to summary
                    self.main.R2eff_grid.SetCellValue(residue, dataset-1, str(r2eff[residue][dataset-1]))

        # store entry
        self.main.R2eff = r2eff

