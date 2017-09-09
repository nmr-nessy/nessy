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


# Selection of residues to calculate

# Python modules
import wx

# NESSY modules
from conf.path import NESSY_PIC, IMPORT_DATA_SIDE_PIC
from conf.message import question, message



class Select_residues(wx.Dialog):
    def __init__(self, main, *args, **kwds):
        # assign parameters
        self.main = main

        # running flag
        self.running = False

        # Create Window
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        # Build Elements
        self.build()


    def build(self):
        # Image
        self.topsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(IMPORT_DATA_SIDE_PIC, wx.BITMAP_TYPE_ANY))
        self.topsizer.Add(self.bitmap, 0, wx.ALL, 5)

        # Mainsizer
        mainsizer = wx.BoxSizer(wx.VERTICAL)

        # Header
        self.header = wx.StaticText(self, -1, "Select Residues for Calculation")
        self.header.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        mainsizer.Add(self.header, 0, wx.ALL|wx.ALIGN_LEFT, 5)

        # Line
        self.static_line_2 = wx.StaticLine(self, -1)
        mainsizer.Add(self.static_line_2, 0, wx.EXPAND, 0)

        # Text
        self.header = wx.StaticText(self, -1, "Only selected residues will be included in curve fitting.")
        mainsizer.Add(self.header, 0, wx.ALL|wx.ALIGN_LEFT, 5)

        # Line
        self.static_line_1 = wx.StaticLine(self, -1)
        mainsizer.Add(self.static_line_1, 0, wx.EXPAND, 0)

        # Residues
        sizer_resi = wx.BoxSizer(wx.HORIZONTAL)
        self.label_resi = wx.StaticText(self, -1, "Include residues:")
        self.label_resi.SetMinSize((150, 17))
        sizer_resi.Add(self.label_resi, 0, 0, 0)

        self.residues = wx.ListBox(self, -1, choices=self.read_resi(), style = wx.LB_MULTIPLE)
        self.residues.SetMinSize((150, 250))
        sizer_resi.Add(self.residues, 0, 0, 0)
        # Select according to settings
        for i in range(0, self.residues.GetCount()):
            self.residues.SetSelection(i, self.main.INCLUDE_RES[i])

        self.button_all = wx.Button(self, -1, "Select all")
        self.Bind(wx.EVT_BUTTON, self.select_all, self.button_all)
        sizer_resi.Add(self.button_all, 0, 0, 0)
        mainsizer.Add(sizer_resi, 1, wx.ALL|wx.EXPAND, 5)

        # Buttons
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.button_start = wx.Button(self, -1, "Save")
        self.Bind(wx.EVT_BUTTON, self.save, self.button_start)
        sizer_buttons.Add(self.button_start, 0, 0, 0)

        self.button_close = wx.Button(self, -1, "Close")
        self.Bind(wx.EVT_BUTTON, self.close, self.button_close)
        sizer_buttons.Add(self.button_close, 0, 0, 0)
        mainsizer.Add(sizer_buttons, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)

        # Pack dialog
        self.topsizer.Add(mainsizer, 0, 0, 0)
        self.SetSizer(self.topsizer)
        self.topsizer.Fit(self)
        self.Layout()
        self.Center()


    def close(self, event):
        self.Destroy()


    def read_resi(self):
        residues = []
        # loop over residues
        for resi in range(0, self.main.RESNO):
            if not str(self.main.data_grid[0].GetCellValue(resi, 0)) == '':
                residues.append(str(resi+1)+'\t'+str(self.main.data_grid[0].GetCellValue(resi, 0)))

        #self.residues.InsertItems(residues, 0)
        return residues


    def select_all(self, event):
        for i in range(0, self.residues.GetCount()):
            self.residues.SetSelection(i, True)


    def save(self, event):
        for i in range(0, self.residues.GetCount()):
            # detect residue no
            tmp = str(self.residues.GetString(i))
            tmp = tmp.split('\t')
            res_index = int(tmp[0])-1

            # is selected
            if self.residues.IsSelected(i):
                self.main.INCLUDE_RES[res_index] = True

            # is not selected
            else:
                self.main.INCLUDE_RES[res_index] = False

        # close dialog
        self.Destroy()
