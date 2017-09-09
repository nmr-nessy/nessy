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


# python modules
import os
from os import sep
import sys
try:
    import thread as _thread
except ImportError:
    import _thread
import wx
from conf.message import NESSY_error

from data.csv_viewer import csv_viewer
from data.plot_viewer import view_plots

def open_selected_results(self, item, sel):
    '''Opens selected result of results tab'''

    #grace plots
    if '.agr' in item:
        os.system('xmgrace ' + item + ' &')

    # png plots
    elif '.png' in item:
        plot_viewer = view_plots(self, item, sel, None, -1, "")
        plot_viewer.Show()

    # csv
    elif '.csv' in item:
        viewer = csv_viewer(self, item, sel, None, -1, "")
        viewer.Show()
        #open_csv_viewer(self, item, sel)

    #pymol macro
    elif '.pml' in item:
        os.system('pymol ' + item + ' &')
