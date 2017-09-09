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
from conf.path import *


def build_toolbar(self):
        """Build Tool Bar"""

        self.toolbar = wx.ToolBar(self, -1, style=wx.TB_HORIZONTAL|wx.TB_FLAT)
        self.SetToolBar(self.toolbar)
        self.toolbar.AddLabelTool(101, _("Refresh"), wx.Bitmap(REFRESH_PIC, wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _("Refresh"), "")
        self.toolbar.AddLabelTool(102, _("Open"), wx.Bitmap(OPEN_PIC, wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _("Open"), "")
        self.toolbar.AddLabelTool(103, _("Save"), wx.Bitmap(SAVE_PIC, wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _("Save Project as..."), "")
        self.Bind(wx.EVT_TOOL, self.new, id=101)
        self.Bind(wx.EVT_TOOL, self.open, id=102)
        self.Bind(wx.EVT_TOOL, self.save, id=103)

        self.toolbar.AddSeparator()

        self.toolbar.AddLabelTool(104, _("Back"), wx.Bitmap(BACK_ICON, wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _("Previous Step"), "")
        self.toolbar.AddLabelTool(105, _("Forward"), wx.Bitmap(FORWARD_PIC, wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _("Next Step"), "")
        self.Bind(wx.EVT_TOOL, self.previous, id=104)
        self.Bind(wx.EVT_TOOL, self.next, id=105)

        self.toolbar.AddSeparator()

        self.toolbar.AddLabelTool(106, _("Select Project Folder"), wx.Bitmap(SELECT_PROJ_FOLDER, wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _("Select Project Folder"), "")
        self.toolbar.AddLabelTool(107, _("Load Protein Structure"), wx.Bitmap(LOAD_PDB_PIC, wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _("Load Protein Structure"), "")
        self.toolbar.AddLabelTool(108, _("Load Protein Sequence"), wx.Bitmap(FASTA_PIC, wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _("Load Protein Sequence"), "")
        self.toolbar.AddLabelTool(109, _("Import Data File"), wx.Bitmap(IMPORT_DATA_PIC, wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _("Import Data from Peak File"), "")
        self.toolbar.AddLabelTool(113, _("Import Multiple Data File"), wx.Bitmap(MULTI_IMPORT_DATA_PIC, wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _("Import Data from multiple Peak Files"), "")
        self.Bind(wx.EVT_TOOL, self.select_proj_folder, id=106)
        self.Bind(wx.EVT_TOOL, self.select_pdb_file, id=107)
        self.Bind(wx.EVT_TOOL, self.fasta_import, id=108)
        self.Bind(wx.EVT_TOOL, self.import_data_from_file, id=109)
        self.Bind(wx.EVT_TOOL, self.multi_import_data_from_file, id=113)

        self.toolbar.AddSeparator()

        self.toolbar.AddLabelTool(114, _("Add Experiment"), wx.Bitmap(ADD_DATASET, wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _("Add Experiment"), "")
        self.Bind(wx.EVT_TOOL, self.add_dataset, id=114)
        self.toolbar.AddLabelTool(115, _("Delete Experiment"), wx.Bitmap(ERROR_PIC, wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _("Delete Current Experiment"), "")
        self.Bind(wx.EVT_TOOL, self.delete_dataset, id=115)

        self.toolbar.AddSeparator()

        self.toolbar.AddLabelTool(120, _("2D Plot Generator"), wx.Bitmap(PLOT2D_PIC, wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _("2D Plot Generator"), "")
        self.toolbar.AddLabelTool(121, _("3D Plot Generator"), wx.Bitmap(PLOT_PIC, wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _("3D Plot Generator"), "")
        self.toolbar.AddLabelTool(122, _("Color-coded Structure Generator"), wx.Bitmap(COLORCODE_PIC, wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _("Create color-coded structures."), "")
        self.Bind(wx.EVT_TOOL, self.dd_plot, id=120)
        self.Bind(wx.EVT_TOOL, self.ddd_plot, id=121)
        self.Bind(wx.EVT_TOOL, self.color_code, id=122)

        self.toolbar.AddSeparator()

        self.toolbar.AddLabelTool(112, _("Settings"), wx.Bitmap(SETTINGS_PIC, wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _("Settings"), "")
        self.toolbar.AddLabelTool(110, _("About"), wx.Bitmap(ABOUT_PIC, wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _("About NESSY"), "")
        self.Bind(wx.EVT_TOOL, self.about, id=110)
        self.Bind(wx.EVT_TOOL, self.nessy_settings, id=112)


        self.toolbar.AddSeparator()

        self.toolbar.AddLabelTool(111, _("Quit"), wx.Bitmap(QUIT_PIC, wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _("Quit NESSY"), "")
        self.Bind(wx.EVT_TOOL, self.quit, id=111)

