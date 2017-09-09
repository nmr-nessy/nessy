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


# Python import
import traceback
import sys
import wx

# NESSY modules
from curvefit.calc_R1rho_models import Run_spinlock
from curvefit.calc_cpmg_models import CPMG_fit




class Run_dispersion_calc():
    """Class to execute single stepts of dispersion analysis."""
    def __init__(self, self_main):

        # Connect variables.
        self.main = self_main

        try:
            # Experiment mode
            self.exp_mode = self.main.sel_experiment[0].GetSelection()
            if self.exp_mode == 0:
                mode = 'CPMG relaxation dispersion'
            if self.exp_mode == 1:
                mode = 'On resonance R1rho relaxation dispersion'
            if self.exp_mode == 2:
                mode = 'Off resonance R1rho relaxation dispersion'
            wx.CallAfter(self.main.report_panel.AppendText,  '\nExperiment mode: '+mode+'.\n')

            # Start calcuation
            # CPMG relaxation dispersion
            if self.exp_mode == 0:
                CPMG_fit(self.main, self.exp_mode)

            # on resonance
            elif self.exp_mode == 1:
                Run_spinlock(self.main, globalfit=True, onresonance=True)

            # off resonance
            elif self.exp_mode == 2:
                Run_spinlock(self.main, globalfit=True, onresonance=False)

        # Proper error handling in the thread.
        except Exception:
            wx.Yield()
            sys.__stderr__.write("%s\n" % traceback.format_exc())
            wx.CallAfter(self.main.report_panel.AppendText, '\n\n%s\n' % traceback.format_exc())
