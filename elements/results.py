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


#Python modules
from os import sep
import wx



def build_results(self):
        """Build results notebook GUI element"""
        self.results = wx.Panel(self.MainTab, -1)

        # Sizer
        sizer_results = wx.BoxSizer(wx.VERTICAL)

        #Header
        self.label_results = wx.StaticText(self.results, -1, _("Results"))
        self.label_results.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_results.Add(self.label_results, 0, wx.LEFT|wx.ADJUST_MINSIZE, 5)

        # Tree element
        self.tree_results = wx.TreeCtrl(self.results, -1, style=wx.TR_DEFAULT_STYLE|wx.TR_HAS_BUTTONS|wx.TR_LINES_AT_ROOT|wx.SUNKEN_BORDER)
        self.root = self.tree_results.AddRoot("Relaxation Dispersion")
        self.plots = self.tree_results.AppendItem (self.root, "Plots", 0)
        self.plots_intensities = self.tree_results.AppendItem (self.plots, "Intensities", 0)
        self.plots_plots = self.tree_results.AppendItem (self.plots, "R2eff/R1rho", 0)
        self.plots_model1 = self.tree_results.AppendItem (self.plots, "No Exchange (Model 1)", 0)
        self.plots_model2 = self.tree_results.AppendItem (self.plots, "Fast Exchange 2 state (Model 2)", 0)
        self.plots_model3 = self.tree_results.AppendItem (self.plots, "Slow Exchange 2 state (Model 3)", 0)
        self.plots_model4 = self.tree_results.AppendItem (self.plots, "Fast Exchange 3 state (Model 4)", 0)
        self.plots_model5 = self.tree_results.AppendItem (self.plots, "Slow Exchange 3 state (Model 5)", 0)
        self.plots_model6 = self.tree_results.AppendItem (self.plots, "Approximation 2 state (Model 6)", 0)
        self.plots_model7 = self.tree_results.AppendItem (self.plots, "Fast Exchange 2 state, all parameters (Model 7)", 0)
        self.plots_modelselection = self.tree_results.AppendItem (self.plots, "Final Results", 0)
        self.structures = self.tree_results.AppendItem (self.root, "Color Coded Structures", 0)
        self.txt = self.tree_results.AppendItem (self.root, "Text Files", 0)
        self.plots2d = self.tree_results.AppendItem (self.root, "2D Plots", 0)
        self.plots3d = self.tree_results.AppendItem (self.root, "3D Plots", 0)
        sizer_results.Add(self.tree_results, 1, wx.ALL|wx.EXPAND, 5)

        # Button
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.button_open_rsults = wx.Button(self.results, -1, _("Open"))
        sizer.Add(self.button_open_rsults, 0, wx.CENTER|wx.ADJUST_MINSIZE, 0)
        self.Bind(wx.EVT_BUTTON, self.open_results, self.button_open_rsults)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.open_results, self.tree_results, id=1)
        self.button_clear_rsults = wx.Button(self.results, -1, _("Clear"))
        sizer.Add(self.button_clear_rsults, 0, wx.CENTER|wx.ADJUST_MINSIZE, 0)
        self.Bind(wx.EVT_BUTTON, self.clear_results, self.button_clear_rsults)
        sizer_results.Add(sizer, 0, wx.CENTER, 0)

        # Pack notebook
        self.results.SetSizer(sizer_results)
        self.MainTab.AddPage(self.results, _("Results"))


def refresh_results(self):
    # deleting results

    # clear containers
    self.results_txt = []
    self.results_plot = []
    self.results_model1 = []
    self.results_model2 = []
    self.results_model3 = []
    self.results_model4 = []
    self.results_model5 = []
    self.results_model6 = []
    self.results_model7 = []
    self.COLOR_PDB = []
    self.plot2d = []
    self.plot3d = []
    self.INTENSITIES_PLOTS = []
    self.FINAL_RESULTS = []

    # clear entries
    self.tree_results.DeleteAllItems()

    # create new
    self.root = self.tree_results.AddRoot("Relaxation Dispersion")
    self.plots = self.tree_results.AppendItem (self.root, "Plots", 0)
    self.plots_intensities = self.tree_results.AppendItem (self.plots, "Intensities", 0)
    self.plots_plots = self.tree_results.AppendItem (self.plots, "R2eff/R1rho", 0)
    self.plots_model1 = self.tree_results.AppendItem (self.plots, "No Exchange (Model 1)", 0)
    self.plots_model2 = self.tree_results.AppendItem (self.plots, "Fast Exchange 2 state (Model 2)", 0)
    self.plots_model3 = self.tree_results.AppendItem (self.plots, "Slow Exchange 2 state (Model 3)", 0)
    self.plots_model4 = self.tree_results.AppendItem (self.plots, "Fast Exchange 3 state (Model 4)", 0)
    self.plots_model5 = self.tree_results.AppendItem (self.plots, "Slow Exchange 3 state (Model 5)", 0)
    self.plots_model6 = self.tree_results.AppendItem (self.plots, "Approximation 2 state (Model 6)", 0)
    self.plots_model7 = self.tree_results.AppendItem (self.plots, "Fast Exchange 2 state, all parameters (Model 7)", 0)
    self.plots_modelselection = self.tree_results.AppendItem (self.plots, "Final Results", 0)
    self.structures = self.tree_results.AppendItem (self.root, "Color Coded Structures", 0)
    self.txt = self.tree_results.AppendItem (self.root, "Text Files", 0)
    self.plots2d = self.tree_results.AppendItem (self.root, "2D Plots", 0)
    self.plots3d = self.tree_results.AppendItem (self.root, "3D Plots", 0)
