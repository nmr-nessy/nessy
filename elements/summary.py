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

# NESSY imports
from conf.NESSY_grid import NESSY_grid



def build_summary(self):
        """Build summary notebook GUI element"""
        self.summary = wx.Panel(self.MainTab, -1)

        # Sizer
        sizer_summary = wx.BoxSizer(wx.VERTICAL)

        #Header
        self.label_summary = wx.StaticText(self.summary, -1, _("Summary"))
        self.label_summary.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_summary.Add(self.label_summary, 0, wx.LEFT|wx.ADJUST_MINSIZE, 5)

        # Sizer for notebook
        self.notebook_summary = wx.BoxSizer(wx.VERTICAL)

        # Create Notebook
        self.Summary = wx.Notebook(self.summary, -1, style=wx.NB_LEFT)

        # Craeate R2eff tab
        self.R2eff_tab = wx.Panel(self.Summary, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.R2eff_grid = NESSY_grid(self.R2eff_tab, -1, size=(1, 1))
        self.R2eff_grid.CreateGrid(self.RESNO, 1000)
        for i in range(1000):
            self.R2eff_grid.SetColLabelValue(i, '')
        sizer.Add(self.R2eff_grid, -1, wx.EXPAND, 0)
        self.R2eff_tab.SetSizer(sizer)
        self.Summary.AddPage(self.R2eff_tab, _("R2eff"))

        # Craeate Model 1 tab
        self.Model1_tab = wx.Panel(self.Summary, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.Model1_grid = NESSY_grid(self.Model1_tab, -1, size=(1, 1))
        self.Model1_grid.CreateGrid(self.RESNO, 1)
        self.Model1_grid.SetColLabelValue(0, "Chi2")
        sizer.Add(self.Model1_grid, -1, wx.EXPAND, 0)
        self.Model1_tab.SetSizer(sizer)
        self.Summary.AddPage(self.Model1_tab, _("Model 1"))

        # Craeate Model 2 tab
        self.Model2_tab = wx.Panel(self.Summary, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.Model2_grid = NESSY_grid(self.Model2_tab, -1, size=(1, 1))
        self.Model2_grid.CreateGrid(self.RESNO, 4)
        self.Model2_grid.SetColLabelValue(0, "kex")
        self.Model2_grid.SetColLabelValue(1, "Rex")
        self.Model2_grid.SetColLabelValue(2, "Phi")
        self.Model2_grid.SetColLabelValue(3, "Chi2")
        sizer.Add(self.Model2_grid, -1, wx.EXPAND, 0)
        self.Model2_tab.SetSizer(sizer)
        self.Summary.AddPage(self.Model2_tab, _("Model 2"))

        # Craeate Model 3 tab
        self.Model3_tab = wx.Panel(self.Summary, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.Model3_grid = NESSY_grid(self.Model3_tab, -1, size=(1, 1))
        self.Model3_grid.CreateGrid(self.RESNO, 6)
        self.Model3_grid.SetColLabelValue(0, "kex")
        self.Model3_grid.SetColLabelValue(1, "Rex")
        self.Model3_grid.SetColLabelValue(2, "dw")
        self.Model3_grid.SetColLabelValue(3, "pb")
        self.Model3_grid.SetColLabelValue(4, "Chi2")
        self.Model3_grid.SetColLabelValue(5, "dG [kJ/mol]")
        sizer.Add(self.Model3_grid, -1, wx.EXPAND, 0)
        self.Model3_tab.SetSizer(sizer)
        self.Summary.AddPage(self.Model3_tab, _("Model 3"))

        # Craeate Model 4 tab
        self.Model4_tab = wx.Panel(self.Summary, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.Model4_grid = NESSY_grid(self.Model4_tab, -1, size=(1, 1))
        self.Model4_grid.CreateGrid(self.RESNO, 7)
        self.Model4_grid.SetColLabelValue(0, "kex 1")
        self.Model4_grid.SetColLabelValue(1, "Rex 1")
        self.Model4_grid.SetColLabelValue(2, "Phi 1")
        self.Model4_grid.SetColLabelValue(3, "kex 2")
        self.Model4_grid.SetColLabelValue(4, "Rex 2")
        self.Model4_grid.SetColLabelValue(5, "Phi 2")
        self.Model4_grid.SetColLabelValue(6, "Chi2")
        sizer.Add(self.Model4_grid, -1, wx.EXPAND, 0)
        self.Model4_tab.SetSizer(sizer)
        self.Summary.AddPage(self.Model4_tab, _("Model 4"))

        # Craeate Model 5 tab
        self.Model5_tab = wx.Panel(self.Summary, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.Model5_grid = NESSY_grid(self.Model5_tab, -1, size=(1, 1))
        self.Model5_grid.CreateGrid(self.RESNO, 9)
        self.Model5_grid.SetColLabelValue(0, "kex 1")
        self.Model5_grid.SetColLabelValue(1, "Rex 2")
        self.Model5_grid.SetColLabelValue(2, "dw 1")
        self.Model5_grid.SetColLabelValue(3, "pb")
        self.Model5_grid.SetColLabelValue(4, "kex 2")
        self.Model5_grid.SetColLabelValue(5, "Rex 2")
        self.Model5_grid.SetColLabelValue(6, "dw 2")
        self.Model5_grid.SetColLabelValue(7, "pc")
        self.Model5_grid.SetColLabelValue(8, "Chi2")
        sizer.Add(self.Model5_grid, -1, wx.EXPAND, 0)
        self.Model5_tab.SetSizer(sizer)
        self.Summary.AddPage(self.Model5_tab, _("Model 5"))

        # Craeate Model 6 tab
        self.Model6_tab = wx.Panel(self.Summary, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.Model6_grid = NESSY_grid(self.Model6_tab, -1, size=(1, 1))
        self.Model6_grid.CreateGrid(self.RESNO, 6)
        self.Model6_grid.SetColLabelValue(0, "kex")
        self.Model6_grid.SetColLabelValue(1, "Rex")
        self.Model6_grid.SetColLabelValue(2, "dw")
        self.Model6_grid.SetColLabelValue(3, "pb")
        self.Model6_grid.SetColLabelValue(4, "Chi2")
        self.Model6_grid.SetColLabelValue(5, "dG [kJ/mol]")
        sizer.Add(self.Model6_grid, -1, wx.EXPAND, 0)
        self.Model6_tab.SetSizer(sizer)
        self.Summary.AddPage(self.Model6_tab, _("Model 6"))

        # Craeate Model 7 tab
        self.Model7_tab = wx.Panel(self.Summary, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.Model7_grid = NESSY_grid(self.Model7_tab, -1, size=(1, 1))
        self.Model7_grid.CreateGrid(self.RESNO, 6)
        self.Model7_grid.SetColLabelValue(0, "kex")
        self.Model7_grid.SetColLabelValue(1, "Rex")
        self.Model7_grid.SetColLabelValue(2, "dw")
        self.Model7_grid.SetColLabelValue(3, "pb")
        self.Model7_grid.SetColLabelValue(4, "Chi2")
        self.Model7_grid.SetColLabelValue(5, "dG [kJ/mol]")
        sizer.Add(self.Model7_grid, -1, wx.EXPAND, 0)
        self.Model7_tab.SetSizer(sizer)
        self.Summary.AddPage(self.Model7_tab, _("Model 7"))

        # Craeate Final tab
        self.Final_tab = wx.Panel(self.Summary, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.Final_grid = NESSY_grid(self.Final_tab, -1, size=(1, 1))
        labels = ['Model', 'Rex (tot)', 'err', 'kex', 'err', 'dw', 'err', 'pb', 'err', 'kex 2', 'err', 'dw 2', 'err', 'pc', 'err', 'Alpha', 'dG [kJ/mol]', 'dG* [kJ/mol]']
        self.Final_grid.CreateGrid(self.RESNO, len(labels))
        for i in range(len(labels)):
            self.Final_grid.SetColLabelValue(i, labels[i])
        sizer.Add(self.Final_grid, -1, wx.EXPAND, 0)
        self.Final_tab.SetSizer(sizer)
        self.Summary.AddPage(self.Final_tab, _("Final"))

        # Add Notebook
        sizer_summary.Add(self.Summary, -1, wx.EXPAND|wx.ALL, 5)

        # Text for unit
        unit_text = wx.StaticText(self.summary, -1, _("Units: Shift difference (dw) are in ppm, populations in relation, Phi in (ppm)**2, kex in 1/s, R2 in 1/s and Rex in rad/s."))
        unit_text.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        sizer_summary.Add(unit_text, 0, wx.ALIGN_RIGHT|wx.RIGHT, 5)

        # Pack notebook
        self.summary.SetSizer(sizer_summary)
        self.MainTab.AddPage(self.summary, _("Summary"))
