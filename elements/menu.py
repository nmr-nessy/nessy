#################################################################################
#                                                                               #
#   (C) 2010-2011 Michael Bieri                                                 #
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


# Python module
import wx
import sys
from os import sep
from conf.path import *
from conf.settings import VERSION

# NESSY module
from conf.project import open_project


def openproject(evt, self, st):
    open_project(self, st.replace('\n', ''))


def create_submenu(self):
    # projects submenu
    projects = wx.Menu()

    # read list and append menu
    file = open(self.homefolder+sep+'projects.nessy')
    i = 90
    for line in file:
        if not line in ['', '\n']:
            projects.Append(i, line.replace('\n', ''))
            self.Bind(wx.EVT_MENU, lambda evt, filename=line: openproject(evt, self, filename), id=i)
            i +=1
    file.close()

    return projects


def build_menubar(self):
        """Build menubar"""

        # Menu Bar
        self.menubar = wx.MenuBar()

        # File
        main_menu = wx.Menu()
        self.menu_item(main_menu, id = 1, text = "&New\tCtrl+N", tooltip = "", pic = REFRESH_PIC)
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 2, _("&Open\tCtrl+O"), "", pic = OPEN_PIC)
        #main_menu.AppendSeparator()
        #main_menu.AppendMenu(-1, 'Opened Projects', create_submenu(self))
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 5, _("&Save\tCtrl+S"), "", SAVE_PIC)
        self.menu_item(main_menu, 3, _("&Save as...\tCtrl+Shift+S"), "", SAVE_PIC)
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 4, _("&Quit\tCtrl+Q"), "", QUIT_PIC)
        self.menubar.Append(main_menu, _("&File"))
        self.Bind(wx.EVT_MENU, self.new, id=1)
        self.Bind(wx.EVT_MENU, self.open, id=2)
        self.Bind(wx.EVT_MENU, self.save_as, id=3)
        self.Bind(wx.EVT_MENU, self.quit, id=4)
        self.Bind(wx.EVT_MENU, self.save, id=5)

        # Import
        main_menu = wx.Menu()
        self.menu_item(main_menu, 12, _("Load S&tructure File\tF6"), "", LOAD_PDB_PIC)
        self.menu_item(main_menu, 16, _("Load &FASTA sequence\tF7"), "", FASTA_PIC)
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 13, _("Import &Data from Single Peak List\tF8"), "", IMPORT_DATA_PIC)
        self.menu_item(main_menu, 14, _("Import Data from &Multiple Peak Lists\tF9"), "", MULTI_IMPORT_DATA_PIC)
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 19, _("Import Data for Residue\tR"), "", MULTI_IMPORT_DATA_PIC)
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 20, _("Import Shift Differences\tS"), "", SHIFT_DIFF_PIC)
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 15, _("Import &VD List\tF10"), "", LIST_PIC)
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 17, _("Import Bruker Protein Dynamic Center Project\tCtrl+B"), "", LIST_PIC)
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 18, _("Import NMR View Table\tCtrl+Shift+V"), "", LIST_PIC)
        self.menubar.Append(main_menu, _("&Import"))
        self.Bind(wx.EVT_MENU, self.select_pdb_file, id=12)
        self.Bind(wx.EVT_MENU, self.import_data_from_file, id=13)
        self.Bind(wx.EVT_MENU, self.multi_import_data_from_file, id=14)
        self.Bind(wx.EVT_MENU, self.import_vd, id=15)
        self.Bind(wx.EVT_MENU, self.fasta_import, id=16)
        self.Bind(wx.EVT_MENU, self.bruker_dynamics_center_import, id=17)
        self.Bind(wx.EVT_MENU, self.nmrview_import, id=18)
        self.Bind(wx.EVT_MENU, self.import_residue, id=19)
        self.Bind(wx.EVT_MENU, self.shift_diff, id=20)

        # Data
        main_menu = wx.Menu()
        self.menu_item(main_menu, 32, _("Correction of &Residue Numbering\tCtrl+R"), "", CORRECTION_PIC)
        self.menu_item(main_menu, 33, _("Correction of &Data Assignment\tCtrl+D"), "", CORRECTION_PIC)
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 35, _("Erase Data Set\tCtrl+E"), "", EXIT_PIC)
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 136, _("&Add Experiment"), "", ADD_DATASET)
        self.menu_item(main_menu, 137, _("Delete Current &Experiment"), "", ERROR_PIC)
        self.Bind(wx.EVT_MENU, self.shift_resno, id=32)
        self.Bind(wx.EVT_MENU, self.shift_data, id=33)
        self.Bind(wx.EVT_MENU, self.erase, id=35)
        self.Bind(wx.EVT_TOOL, self.add_dataset, id=136)
        self.Bind(wx.EVT_TOOL, self.delete_dataset, id=137)
        self.menubar.Append(main_menu, _("&Data"))

        # Settings
        main_menu = wx.Menu()
        self.menu_item(main_menu, 23, _("Select &Residues to include in calculation\tCtrl+Alt+R"), "", N_STATE_PIC)
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 22, _("&Select Models"), "", N_STATE_PIC)
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 24, _("&Manual Model Selection / Alpha Analysis"), "", N_STATE_PIC)
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 25, _("&Boundaries / Initial guess"), "", N_STATE_PIC)
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 21, _("&NESSY Settings\tF12"), "", SETTINGS_PIC)
        self.menubar.Append(main_menu, _("&Settings"))
        self.Bind(wx.EVT_MENU, self.nessy_settings, id=21)
        self.Bind(wx.EVT_MENU, self.models, id=22)
        self.Bind(wx.EVT_MENU, self.select_res, id=23)
        self.Bind(wx.EVT_MENU, self.manual_selection, id=24)
        self.Bind(wx.EVT_MENU, self.constraints, id=25)

        # n-state model
        main_menu = wx.Menu()
        self.menu_item(main_menu, 61, _("n-States Model Fast Exchange\tCTRL+ALT+N"), "", N_STATE_PIC)
        self.menu_item(main_menu, 62, _("n-States Model Slow Exchange\tCTRL+ALT+M"), "", N_STATE_PIC)
        self.menubar.Append(main_menu, _("&n-States"))
        self.Bind(wx.EVT_MENU, self.n_state, id=61)
        self.Bind(wx.EVT_MENU, self.n_state_slow, id=62)
        # disable if not running on Mac of Windows ('darwin', 'win32', 'cygwin')
        if not 'win' in sys.platform:
            self.menubar.EnableTop(4, False)

        # Cluster
        main_menu = wx.Menu()
        self.menu_item(main_menu, 71, _("Cluster &Residues for Simultaneous Fit\tCTRL+SHIFT+C"), "", N_STATE_PIC)
        self.Bind(wx.EVT_MENU, self.cluster, id=71)
        self.menubar.Append(main_menu, _("&Cluster"))

        # Extras
        main_menu = wx.Menu()
        self.menu_item(main_menu, 31, _("&PEAKY\tCtrl+P"), "", PEAKY_PIC)
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 34, _("&Back calculate Intensities\tCtrl+B"), "", BACKCALC_PIC)
        self.menu_item(main_menu, 37, _("&Create Synthetic Data\tCtrl+Alt+C"), "", BACKCALC_PIC)
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 38, _("&Calculate Free Energy dG\tCtrl+G"), "", BACKCALC_PIC)
        self.menu_item(main_menu, 39, _("&van't Hoff Analysis\tCtrl+ALT+V"), "", BACKCALC_PIC)
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 36, _("Export / Save log\tCtrl+Alt+S"), "", SAVE_PIC)
        self.Bind(wx.EVT_MENU, self.back_calc_int, id=34)
        self.Bind(wx.EVT_MENU, self.export_log, id=36)
        self.Bind(wx.EVT_MENU, self.create_synthetic_data, id=37)
        self.Bind(wx.EVT_MENU, self.free_energy, id=38)
        self.Bind(wx.EVT_MENU, self.vant_hoff, id=39)
        self.menubar.Append(main_menu, _("&Extras"))

        # Plotting
        main_menu = wx.Menu()
        self.menu_item(main_menu, 50, _("Create 2D Plots\tCtrl+Alt+P"), "", PLOT2D_PIC)
        self.menu_item(main_menu, 51, _("Create 3D Plots\tCtrl+Shift+P"), "", PLOT_PIC)
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 52, _("Create Multiple Alignment of Plots\tCtrl+Shift+A"), "", N_STATE_PIC)
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 53, _("Create Color Coded Structures\tCtrl+Shift+U"), "", COLORCODE_PIC)
        self.Bind(wx.EVT_MENU, self.ddd_plot, id=51)
        self.Bind(wx.EVT_MENU, self.dd_plot, id=50)
        self.Bind(wx.EVT_MENU, self.create_csv, id=52)
        self.Bind(wx.EVT_MENU, self.color_code, id=53)
        self.menubar.Append(main_menu, _("&Plotting"))

        # Help
        main_menu = wx.Menu()
        self.menu_item(main_menu, 41, _("&Manual\tF1"), "", MANUAL_PIC)
        self.menu_item(main_menu, 42, _("&Tutorial\tF2"), "", TUTORIAL_PIC)
        self.menu_item(main_menu, 47, _("&Equations\tCTRL+ALT+E"), "", EQUATION_PIC)
        self.menu_item(main_menu, 48, _("SI &Units\tCTRL+ALT+U"), "", EQUATION_PIC)
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 44, _("&GNU GPL License\tCTRL+ALT+L"), "", GNU_PIC)
        main_menu.AppendSeparator()
        self.menu_item(main_menu, 46, _("&NESSY Mailing Lists"), "", CONTACT_PIC)
        self.menu_item(main_menu, 45, _("&Contact NESSY (nessy-users@gna.org)\tCTRL+ALT+C"), "", CONTACT_PIC)
        main_menu.AppendSeparator()
        #if 'svn' in VERSION:
        #    self.menu_item(main_menu, 47, _("&Update\tCTRL+ALT+U"), "", N_STATE_PIC)
        #    self.Bind(wx.EVT_MENU, self.update, id=47)
        #    main_menu.AppendSeparator()
        self.menu_item(main_menu, 43, _("&About NESSY\tF3"), "", ABOUT_PIC)
        self.Bind(wx.EVT_MENU, self.manual, id=41)
        self.Bind(wx.EVT_MENU, self.tutorial, id=42)
        self.Bind(wx.EVT_MENU, self.about, id=43)
        self.Bind(wx.EVT_MENU, self.license, id=44)
        self.Bind(wx.EVT_MENU, self.contact, id=45)
        self.Bind(wx.EVT_MENU, self.mailing_lists, id=46)
        self.Bind(wx.EVT_MENU, self.equations, id=47)
        self.Bind(wx.EVT_MENU, self.units, id=48)
        self.menubar.Append(main_menu, _("&Help"))
        self.SetMenuBar(self.menubar)
