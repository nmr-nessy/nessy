#################################################################################
#                                                                               #
#   (C) 2010 - 2011 Michael Bieri                                               #
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
import wx
from os import sep

# NESSY modules
from conf.data import add_experiment, build_data_grid, build_off_resonance
from conf.path import MISSING_PIC
from conf.NESSY_grid import NESSY_grid



def build_collect_data(self, dataset, off_resonance=False):
        """Build collect data notebook GUI element"""
        self.collect = wx.Panel(self.MainTab, -1)

        # Sizer
        self.datagrid_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        left_box = wx.BoxSizer(wx.VERTICAL)

        # Header
        self.header_1 = wx.StaticText(self.collect, -1, _("Collect Required Data #"+str(dataset)))
        self.header_1.SetMinSize((300, 25))
        self.header_1.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        left_box.Add(self.header_1, 0, wx.ADJUST_MINSIZE, 0)

        self.header_2 = wx.StaticText(self.collect, -1, _("Experiment Type:"))
        self.header_2.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        left_box.Add(self.header_2, 0, wx.ADJUST_MINSIZE, 0)

        # Selection
        select_box = wx.BoxSizer(wx.HORIZONTAL)
        self.sel_experiment.append(wx.ListBox(self.collect, -1, choices=[_("CPMG Relaxation Dispersion"), _("R1rho Dispersion (on-resonance)"), _("R1rho Dispersion (off-resonance)"), _("H/D Exchange")]))
        self.sel_experiment[dataset-1].SetMinSize((224, 100))
        self.sel_experiment[dataset-1].SetSelection(0)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.edit_exp, self.sel_experiment[dataset-1])
        self.Bind(wx.EVT_LISTBOX, lambda evt, selection=self.sel_experiment[dataset-1]: self.sync_exp(evt, selection), self.sel_experiment[dataset-1])
        select_box.Add(self.sel_experiment[dataset-1], 0, wx.BOTTOM|wx.ADJUST_MINSIZE, 10)

        # set up
        self.setup = wx.BoxSizer(wx.VERTICAL)
        self.edit_experiment = wx.Button(self.collect, -1, _("Set up"))
        self.edit_experiment.SetMinSize((60, 25))
        self.Bind(wx.EVT_BUTTON, self.edit_exp, self.edit_experiment)
        self.setup.Add(self.edit_experiment, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 0)
        self.bitmap_setup.append(wx.StaticBitmap(self.collect, -1, wx.Bitmap(MISSING_PIC, wx.BITMAP_TYPE_ANY)))
        self.setup.Add(self.bitmap_setup[dataset-1], 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE|wx.TOP, 10)
        select_box.Add(self.setup, 0, 0, 0)

        # pack box
        left_box.Add(select_box, 0, 0, 0)

        # Summary
        self.label_details = wx.StaticText(self.collect, -1, _("Heteronuclear Frequency [MHz]:"))
        self.label_details.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        left_box.Add(self.label_details, 0, wx.TOP|wx.BOTTOM|wx.ADJUST_MINSIZE, 5)

        self.spec_freq.append(wx.TextCtrl(self.collect, -1, ("60.77")))
        self.spec_freq[dataset-1].SetMinSize((224, 25))
        left_box.Add(self.spec_freq[dataset-1], 0, 0, 0)

        # Static Magnetic field B0
        self.label_B0 = wx.StaticText(self.collect, -1, _("Static Magnetic Field B(0) [T]:"))
        self.label_B0.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_B0.Hide()
        left_box.Add(self.label_B0, 0, wx.TOP|wx.BOTTOM|wx.ADJUST_MINSIZE, 5)

        self.B0.append(wx.TextCtrl(self.collect, -1, ("14.1")))
        self.B0[dataset-1].SetMinSize((224, 25))
        self.B0[dataset-1].Hide()
        left_box.Add(self.B0[dataset-1], 0, 0, 0)

        # Spin lock or Offset
        self.spinlock_offset_label.append(wx.StaticText(self.collect, -1, _("Offset [Hz]:")))
        self.spinlock_offset_label[dataset-1].SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        left_box.Add(self.spinlock_offset_label[dataset-1], 0, wx.TOP|wx.ADJUST_MINSIZE, 25)
        self.spinlock_offset_label[dataset-1].Hide()

        offset = wx.BoxSizer(wx.HORIZONTAL)
        self.spinlock_offset_value.append(wx.TextCtrl(self.collect, -1, (""), style=wx.TE_PROCESS_ENTER))
        self.Bind(wx.EVT_TEXT_ENTER, self.sync_spinlock_value, self.spinlock_offset_value[dataset-1])
        self.spinlock_offset_value[dataset-1].SetMinSize((224, 25))
        offset.Add(self.spinlock_offset_value[dataset-1], 0, wx.TOP, 5)
        self.spinlock_offset_value[dataset-1].Hide()

        self.set_offset = wx.Button(self.collect, -1, _("Set"))
        self.set_offset.SetMinSize((60, 25))
        self.Bind(wx.EVT_BUTTON, self.sync_spinlock_value, self.set_offset)
        offset.Add(self.set_offset, 0, wx.TOP, 5)
        self.set_offset.Hide()

        left_box.Add(offset, 0, 0, 0)

        self.spinlock_offset_label1.append(wx.StaticText(self.collect, -1, _("Assign value to actual data by\npressing enter.")))
        self.spinlock_offset_label1[dataset-1].SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        left_box.Add(self.spinlock_offset_label1[dataset-1], 0, wx.TOP|wx.BOTTOM|wx.ADJUST_MINSIZE, 5)
        self.spinlock_offset_label1[dataset-1].Hide()

        # data grid
        # CPMG relaxation dispersion and on-resonance R1rho
        self.data_grid.append(NESSY_grid(self.collect, -1, size=(1, 1)))
        build_data_grid(self, dataset-1)

        # Off-resonance R1rho
        self.data_grid_r1rho.append([wx.Notebook(self.collect, -1, style=wx.NB_TOP), [], []])   # [Notebook, Grid, Labels]
        build_off_resonance(self, dataset-1)

        # Pack main box
        self.datagrid_sizer[dataset-1].Add(left_box, 0, wx.LEFT, 5)

        # Pack data grid (default to CPMG dispersion)
        self.datagrid_sizer[dataset-1].Add(self.data_grid[dataset-1], -1, wx.EXPAND, 0)
        self.datagrid_sizer[dataset-1].Add(self.data_grid_r1rho[dataset-1][0], -1, wx.EXPAND, 0)

        if off_resonance:
            self.data_grid_r1rho[dataset-1][0].Show()
            self.data_grid[dataset-1].Hide()
        else:
            self.data_grid_r1rho[dataset-1][0].Hide()
            self.data_grid[dataset-1].Show()

        # Pack page
        self.collect.SetSizer(self.datagrid_sizer[dataset-1])
        self.MainTab.InsertPage(dataset, self.collect, _("Data Experiment #"+str(dataset)))

        # Build environment for new experiment
        add_experiment(self, dataset)
