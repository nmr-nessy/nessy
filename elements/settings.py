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


# Python modules
import wx
from os import sep

# NESSY modules
from conf.path import FRONT_PIC


def build_settings(self):
        """Build settings notebook GUI element"""

        self.settings = wx.Panel(self.MainTab, -1)

        # Sizer
        settings_main = wx.FlexGridSizer(2, 2, 0, 0)
        left_box = wx.BoxSizer(wx.VERTICAL)

        # Header
        self.welcome = wx.StaticText(self.settings, -1, _("Welcome to NESSY"))
        self.welcome.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        left_box.Add(self.welcome, 0, wx.ADJUST_MINSIZE, 0)

        self.nessy = wx.StaticText(self.settings, -1, _("NMR Relaxation Dispersion Spectroscopy Analysis Software\n"))
        self.nessy.SetMinSize((635, 50))
        left_box.Add(self.nessy, 0, wx.ADJUST_MINSIZE, 0)

        self.set_up = wx.StaticText(self.settings, -1, _("Project Set up:"))
        left_box.Add(self.set_up, 0, wx.ADJUST_MINSIZE, 0)
        self.set_up.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))

        # Project folder
        folder_box = wx.BoxSizer(wx.HORIZONTAL)
        self.label_folder = wx.StaticText(self.settings, -1, _("Select Project Folder *:"))
        self.label_folder.SetMinSize((200, 17))
        self.proj_folder = wx.TextCtrl(self.settings, -1, "")
        self.proj_folder.SetMinSize((400, 20))
        self.select_folder = wx.Button(self.settings, -1, _("+"))
        self.select_folder.SetMinSize((30, 20))
        self.Bind(wx.EVT_BUTTON, self.select_proj_folder, self.select_folder)
        folder_box.Add(self.label_folder, 0, wx.ADJUST_MINSIZE, 0)
        folder_box.Add(self.proj_folder, 0, wx.ADJUST_MINSIZE, 0)
        folder_box.Add(self.select_folder, 0, 0, 0)
        # Pack left box
        left_box.Add(folder_box, 0, wx.TOP, 5)

        # PDB file
        pdb_box = wx.BoxSizer(wx.HORIZONTAL)
        self.label_pdb = wx.StaticText(self.settings, -1, _("Select PDB File:"))
        self.label_pdb.SetMinSize((200, 17))
        self.pdb_file = wx.TextCtrl(self.settings, -1, "")
        self.pdb_file.SetMinSize((400, 20))
        self.select_pdb = wx.Button(self.settings, -1, _("+"))
        self.select_pdb.SetMinSize((30, 20))
        self.Bind(wx.EVT_BUTTON, self.select_pdb_file, self.select_pdb)
        pdb_box.Add(self.label_pdb, 0, wx.ADJUST_MINSIZE, 0)
        pdb_box.Add(self.pdb_file, 0, wx.ADJUST_MINSIZE, 0)
        pdb_box.Add(self.select_pdb, 0, 0, 0)
        # Pack left box
        left_box.Add(pdb_box, 0, wx.TOP, 5)

        # Text
        text = wx.StaticText(self.settings, -1, _("NESSY is an open source software to analyze CPMG and R1rho NMR relaxation dispersion experiments.\n\nMain features include:\n\n\t- Fully automated analysis of CPMG and R1rho NMR data\n\t- Curvefit to different relaxation dispersion models\n\t- Grid search for robust parameter estimation\n\t- Model-selection using AICc/AIC/F-test\n\t- Monte Carlo simulations for error estimation\n\t- van't Hoff analysis\n\t- Creation of 2D and 3D plots and color coded structures\n\t- Analysis of H/D exchange experiments\n\n\nIf you are using NESSY, please cite the followin article:\n\nAutomated NMR relaxation dispersion data analysis using NESSY, M. Bieri and P. Gooley, BMC Bioinformatics 2011, 12:421\n\nhttp://home.gna.org/nessy/ or http://www.nessy.biochem.unimelb.edu.au"))
        text.SetMinSize((600, 400))
        text.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        # Pack left box
        left_box.Add(text, 0, wx.TOP, 40)

        # right image
        self.waver = wx.StaticBitmap(self.settings, -1, wx.Bitmap(FRONT_PIC, wx.BITMAP_TYPE_ANY))

        # Pack notebook
        settings_main.Add(left_box, 1, wx.LEFT|wx.SHAPED, 5)
        settings_main.Add(self.waver, 0, wx.LEFT|wx.TOP|wx.ADJUST_MINSIZE, 20)
        self.settings.SetSizer(settings_main)
        self.MainTab.AddPage(self.settings, _("Settings"))
        self.settings.SetMinSize((1440, 518))
