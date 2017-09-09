#################################################################################
#                                                                               #
#   (C) 2010 Michael Bieri                                                      #
#   (C) 2013-2016 Edward d'Auvergne                                             #
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
from conf import message
from conf.message import question, message
from os import sep
import sys

# NESSY modules
from conf.message import question, error_popup
from conf.path import NESSY_PIC, FREQ_PIC, CHECKED_PIC


class Setup_HD(wx.Dialog):
    def __init__(self, gui, *args, **kwds):
        # link parameters
        self.main = gui

        # Index
        self.index = self.main.MainTab.GetSelection()-1

        # Build window
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        #  Build boxes
        self.topsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_box = wx.BoxSizer(wx.VERTICAL)
        self.button_box = wx.BoxSizer(wx.HORIZONTAL)

        # add image
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(FREQ_PIC, wx.BITMAP_TYPE_ANY))
        self.topsizer.Add(self.bitmap, 0, wx.ALL, 5)

        # Build header
        self.build_header()

        # Add HD times
        self.build_entries()
        
        # Noise
        self.build_noise()

        # Initial Guess
        self.build_initial_guess()

        # Build buttons
        self.build_buttons()
        self.main_box.Add(self.button_box, 1, wx.ALIGN_LEFT|wx.LEFT, 5)

        # add mainbox
        self.topsizer.Add(self.main_box, 0, 0, 0)
        self.SetSizer(self.topsizer)
        self.topsizer.Fit(self)
        self.Layout()


    def build_buttons(self):
        # Create buttons
        self.button_ok = wx.Button(self, -1, "Save")
        self.button_1 = wx.Button(self, -1, "Cancel")
        self.button_box.Add(self.button_ok, 0, wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 10)
        self.button_box.Add(self.button_1, 0, wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 10)
        self.Bind(wx.EVT_BUTTON, self.save_hd, self.button_ok)
        self.Bind(wx.EVT_BUTTON, self.cancel, self.button_1)


    def build_entries(self):
        # Build interface.
        self.frequency_box = wx.BoxSizer(wx.VERTICAL)

        self.data = []
        self.label = []

        # Frequencies
        self.sizer_freq = wx.GridSizer(0, 4, 0, 0)

        # loop over frequencies
        for i in range(0, int(self.main.SETTINGS[2])):
            # The label
            self.label.append(wx.StaticText(self, -1, "Data "+str(i+1)+':'))
            self.label[i].SetMinSize((60, 17))
            self.sizer_freq.Add(self.label[i], 0, wx.LEFT|wx.ADJUST_MINSIZE, 20)

            # The text field
            self.data.append(wx.TextCtrl(self, -1, ""))
            self.data[i].SetMinSize((60, 20))
            self.data[i].SetValue(self.main.HD_TIME[self.index][i])
            self.sizer_freq.Add(self.data[i], 0, wx.ADJUST_MINSIZE|wx.RIGHT, 20)

        # add frequencies
        self.frequency_box.Add(self.sizer_freq, 0, 0, 0)
        self.main_box.Add(self.frequency_box, 0, 0, 0)


    def build_header(self):
        self.label_header = wx.StaticText(self, -1, "Set up H/D Exchange Experiment:")
        self.label_header.SetMinSize((350, 25))
        self.label_header.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_subheader = wx.StaticText(self, -1, "Enter incubation time below [s]:")
        self.label_subheader.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.main_box.Add(self.label_header, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        self.main_box.Add(self.label_subheader, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)


    def build_initial_guess(self):
        label =  wx.StaticText(self, -1, "Initial Guess:")
        label.SetMinSize((350, 25))
        label.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.main_box.Add(label, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)

        # guess
        sizer_guess = wx.BoxSizer(wx.HORIZONTAL)

        # I0
        self.I0_header = wx.StaticText(self, -1, "I0 [%]:")
        self.I0_header.SetMinSize((50, 23))
        sizer_guess.Add(self.I0_header, 0, wx.ALL, 5)
        self.I0 = wx.TextCtrl(self, -1, self.main.INITIAL_HD[0])
        self.I0.SetMinSize((70, 25))
        sizer_guess.Add(self.I0, 0, 0, wx.ALL, 5)

        # C
        self.C_header = wx.StaticText(self, -1, "C:")
        self.C_header.SetMinSize((20, 23))
        sizer_guess.Add(self.C_header, 0, wx.ALL, 5)
        self.C = wx.TextCtrl(self, -1, self.main.INITIAL_HD[1])
        self.C.SetMinSize((70, 25))
        sizer_guess.Add(self.C, 0, 0, wx.ALL, 5)

        # kex
        self.kex_header = wx.StaticText(self, -1, "kex [1/s]:")
        self.kex_header.SetMinSize((70, 23))
        sizer_guess.Add(self.kex_header, 0, wx.ALL, 5)
        self.kex = wx.TextCtrl(self, -1, self.main.INITIAL_HD[2])
        self.kex.SetMinSize((70, 25))
        sizer_guess.Add(self.kex, 0, 0, wx.ALL, 5)

        self.main_box.Add(sizer_guess, 0, 0, 0)


    def build_noise(self):
        """Create noise GUI element"""

        # CPMG delay
        self.label_noise = wx.StaticText(self, -1, "\nBackground noise: ")
        self.label_noise.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_noise.SetMinSize((350, 35))
        self.main.hd_noise = wx.TextCtrl(self, -1, self.main.HD_NOISE[self.index])
        self.main.hd_noise.SetMinSize((100, 20))
        self.main_box.Add(self.label_noise, 0, wx.LEFT|wx.TOP|wx.ADJUST_MINSIZE|wx.ALIGN_BOTTOM, 5)
        #self.cpmg_delay_field.SetValue(cpmg_delay)
        self.main_box.Add(self.main.hd_noise, 0, wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 10)


    def save_hd(self, event): # save new frequencies
        # collect new values
        for i in range(0, int(self.main.SETTINGS[2])):
            self.main.HD_TIME[self.index][i] = str(self.data[i].GetValue())

        # Number of data sets
        entry = ''
        self.main.NUM_OF_DATASET[self.index] = 0
        for i in range(0, (len(self.main.HD_TIME[self.index]))):
             if not self.main.HD_TIME[self.index][i] == '':
                value = str(self.main.HD_TIME[self.index][i])
                isinteger = value.isdigit()
                if isinteger:
                    self.main.NUM_OF_DATASET[self.index] = self.main.NUM_OF_DATASET[self.index] + 1
                    entry = entry + 'Dataset ' + str(i+1) + ': ' + str(self.main.HD_TIME[self.index][i]) + ' Hz\n'
                    self.main.data_grid[self.index].SetColLabelValue((i+1), _(str((float(self.main.HD_TIME[self.index][i])/3600))[0:6] + ' h'))
                else:
                    error_popup('Incubation time has to be in Numbers!\n\nError in data set '+str(i+1))
                    return

        # set up reference spectrum
        for i in range(0, len(self.main.HD_TIME[self.index])):
            if float(self.main.HD_TIME[self.index][i]) == 0.0:
                self.main.referencedata[self.index] = i + 1
                self.main.data_grid[self.index].SetColLabelValue((i+1), _('Reference'))

        # Number of dataset
        self.main.NUM_OF_DATASETS[self.index] = 0
        for i in range(0, len(self.main.HD_TIME[self.index])):
            if not self.main.HD_TIME[self.index][i] == '':
                self.main.NUM_OF_DATASETS[self.index] = self.main.NUM_OF_DATASETS[self.index] + 1

        # Noise
        self.main.HD_NOISE[self.index] = str(self.main.hd_noise.GetValue())

        # Change image
        self.main.bitmap_setup[self.index].SetBitmap(wx.Bitmap(CHECKED_PIC, wx.BITMAP_TYPE_ANY))#CHECKED_PIC)

        # save initial guess
        self.main.INITIAL_HD[0] = str(self.I0.GetValue())
        self.main.INITIAL_HD[1] = str(self.C.GetValue())
        self.main.INITIAL_HD[2] = str(self.kex.GetValue())

        # Close dialog
        self.Destroy()


    def cancel(self, event): # abort
        self.Destroy()
