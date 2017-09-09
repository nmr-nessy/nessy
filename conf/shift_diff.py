#################################################################################
#                                                                               #
#   (C) 2012 Michael Bieri                                                      #
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


# Loading shift differences

# Python modules
import wx

# NESSY modules
from conf.path import NESSY_PIC, IMPORT_DATA_SIDE_PIC
from conf.filedialog import openfile, savefile
from conf.message import error_popup, message
from conf.NESSY_grid import NESSY_grid



class Shift_difference(wx.Frame):
    def __init__(self, main, *args, **kwds):
        # assign parameters
        self.main = main

        # Create Window
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX
        wx.Frame.__init__(self, *args, **kwds)
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
        self.header = wx.StaticText(self, -1, "Load Shift Differences")
        self.header.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        mainsizer.Add(self.header, 0, wx.ALL|wx.ALIGN_LEFT, 5)

        # text
        text = wx.StaticText(self, -1, "Shift differences will be used as constants in model 3 and model 6.\nShift differences can be obtained by comparing HSQC spectra in apo\nand saturated state.\n")
        text.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        mainsizer.Add(text, 0, wx.ALL|wx.ALIGN_LEFT, 5)

        # data grid
        self.data_grid = NESSY_grid(self, -1, size=(1, 1))
        self.data_grid.CreateGrid(self.main.RESNO, 2)
        self.data_grid.SetColLabelValue(0, "Residue")
        self.data_grid.SetColSize(0, 100)
        self.data_grid.SetColLabelValue(1, "Shift difference [ppm]")
        self.data_grid.SetColSize(1, 270)
        self.data_grid.SetMinSize((400, 300))
        self.data_grid.SetRowLabelSize(0)
        mainsizer.Add(self.data_grid, 0, wx.ALL|wx.EXPAND, 5)

        # buttons
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        import_button = wx.Button(self, -1, "Import from file")
        import_button.SetMinSize((115, 30))
        sizer.Add(import_button, 0, wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.load_from_file, import_button)
        clear_button = wx.Button(self, -1, "Clear")
        clear_button.SetMinSize((115, 30))
        self.Bind(wx.EVT_BUTTON, self.clear, clear_button)
        sizer.Add(clear_button, 0, wx.ALL, 5)
        mainsizer.Add(sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        # buttons 2
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        cancel_button = wx.Button(self, -1, "Cancel")
        cancel_button.SetMinSize((115, 30))
        sizer.Add(cancel_button, 0, wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.close, cancel_button)
        save_button = wx.Button(self, -1, "Save")
        save_button.SetMinSize((115, 30))
        self.Bind(wx.EVT_BUTTON, self.sync, save_button)
        sizer.Add(save_button, 0, wx.ALL, 5)
        mainsizer.Add(sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        # Pack dialog
        self.topsizer.Add(mainsizer, 0, 0, 0)
        self.SetSizer(self.topsizer)
        self.topsizer.Fit(self)
        self.Layout()
        self.Center()

        # load from data
        self.sync(False)


    def clear(self, event):
        # clear shift diff
        for i in range(self.main.RESNO):
            # clear entries
            self.data_grid.SetCellValue(i, 0, '')
            self.data_grid.SetCellValue(i, 1, '')

            # clear container
            self.main.SHIFT_DIFFERENCE[i] = None


    def close(self, event):
        # Destroy dialog
        self.Destroy()


    def load_from_file(self, event):
        # containers
        residues = []
        difference = []

        # select file
        filename = openfile('Select file to open', '', '', 'all files (*.*)|*', self)

        # read file
        if filename:
            # clear data grid
            self.clear(True)

            # open file
            file = open(filename, 'r')

            # read lines
            for line in file:
                # split
                if ';' in line:     entries = line.split(';')
                elif ',' in line:   entries = line.split(',')
                else:               entries = line.split()

                # read residue and value
                try:
                    res = str(int(entries[0]))
                    diff = str(float(entries[1]))

                    # save
                    residues.append(res)
                    difference.append(diff)

                except:
                    continue

            # write values
            for i in range(len(residues)):
                self.data_grid.SetCellValue(i, 0, residues[i])
                self.data_grid.SetCellValue(i, 1, difference[i])


    def sync(self, save):
        # Synchronising data

        # save data
        if save:
            # set each shift difference to None
            for i in range(self.main.RESNO):    self.main.SHIFT_DIFFERENCE[i] = None

            # loop over grid
            for i in range(self.main.RESNO):
                # data is present
                if not str(self.data_grid.GetCellValue(i, 0)) == '' or not str(self.data_grid.GetCellValue(i, 1)) == '':
                    res = int(self.data_grid.GetCellValue(i, 0)) - 1
                    self.main.SHIFT_DIFFERENCE[res] = str(self.data_grid.GetCellValue(i, 1))

            # close dialog
            self.close(True)

        # read data
        else:
            current_row = 0

            for i in range(self.main.RESNO):
                # if value is present
                if self.main.SHIFT_DIFFERENCE[i]:
                    # residue
                    self.data_grid.SetCellValue(current_row, 0, str(i+1))

                    # data
                    self.data_grid.SetCellValue(current_row, 1, str(self.main.SHIFT_DIFFERENCE[i]))

                    # next row
                    current_row = current_row + 1
