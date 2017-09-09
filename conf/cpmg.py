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


class Setup_experiment(wx.Dialog):
    def __init__(self, gui, exp, *args, **kwds):
        # link parameters
        self.main = gui

        # The experiment type
        self.exptyp = exp

        # Index
        self.index = self.main.MainTab.GetSelection()-1

        # Read experiment environment of spin lock experiments
        if self.exptyp in ['on', 'off']:
            self.spinlock_exp = self.main.data_grid_r1rho[self.index][0].GetSelection()

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

        # Add CPMG frequencies
        self.build_entries()

        # Add constant time
        self.build_constant_time()

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
        self.Bind(wx.EVT_BUTTON, self.save_cpmg, self.button_ok)
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
            self.data[i].SetValue(str(self.main.CPMGFREQ[self.index][i]))
            self.sizer_freq.Add(self.data[i], 0, wx.ADJUST_MINSIZE|wx.RIGHT, 20)

        # add frequencies
        self.frequency_box.Add(self.sizer_freq, 0, 0, 0)

        self.main_box.Add(self.frequency_box, 0, 0, 0)


    def build_constant_time(self):
        """Create CPMG constant time GUI element"""

        # Constant values
        if self.exptyp == 'CPMG':
            self.label_cpmg_freq = wx.StaticText(self, -1, "\nConstant CPMG relaxation Delay [s]: ")
            self.cpmg_delay_field = wx.TextCtrl(self, -1, self.main.CPMG_DELAY[self.index])
        elif self.exptyp == 'on':
            self.label_cpmg_freq = wx.StaticText(self, -1, "\nSpin lock power [Hz]: ")
            self.label_cpmg_freq.Hide()
            self.cpmg_delay_field = wx.TextCtrl(self, -1, "0")
            self.cpmg_delay_field.Hide()
        elif self.exptyp == 'off':
            self.label_cpmg_freq = wx.StaticText(self, -1, "\nSpin Lock Power [Hz]: ")
            self.cpmg_delay_field = wx.TextCtrl(self, -1, self.main.CPMG_DELAY[self.index])

        self.label_cpmg_freq.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_cpmg_freq.SetMinSize((350, 35))

        self.cpmg_delay_field.SetMinSize((100, 20))
        self.main_box.Add(self.label_cpmg_freq, 0, wx.LEFT|wx.TOP|wx.ADJUST_MINSIZE|wx.ALIGN_BOTTOM, 5)
        self.main_box.Add(self.cpmg_delay_field, 0, wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 10)


    def build_header(self):
        # CPMG
        if self.exptyp == 'CPMG':
            self.label_header = wx.StaticText(self, -1, "Set up CPMG Relaxation Experiment:")
            self.label_subheader = wx.StaticText(self, -1, "CPMG Field Strength [Hz]:")

        # On resonance
        elif self.exptyp == 'on':
            self.label_header = wx.StaticText(self, -1, "Set up R1rho Relaxation Experiment\n(on-resonance):")
            self.label_subheader = wx.StaticText(self, -1, "Spin-lock time [s]:")

        # Off resonance
        elif self.exptyp == 'off':
            self.label_header = wx.StaticText(self, -1, "Set up R1rho Relaxation Experiment\n(off-resonance):")
            self.label_subheader = wx.StaticText(self, -1, "Spin-lock time [s]:")

        # Settings and add headers
        self.label_header.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_subheader.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.main_box.Add(self.label_header, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)
        self.main_box.Add(self.label_subheader, 0, wx.ALL|wx.ADJUST_MINSIZE, 5)


    def save_cpmg(self, event): # save new frequencies
        # collect new values
        for i in range(0, int(self.main.SETTINGS[2])):
            self.main.CPMGFREQ[self.index][i] = str(self.data[i].GetValue())

        # CPMG Relkaxation Delay
        self.main.CPMG_DELAY[self.index] = str(self.cpmg_delay_field.GetValue())

        # Number of data sets
        self.main.NUM_OF_DATASET[self.index] = 0

        # Loop over entries (future x values)
        for i in range(0, (len(self.main.CPMGFREQ[self.index]))):
             # Is field used
             if not self.main.CPMGFREQ[self.index][i] == '':
                # The value
                value = str(self.main.CPMGFREQ[self.index][i])

                # Check if the entry is a number
                try:
                    value = float(value)
                    isinteger = True
                except:
                    isinteger = False

                # Store, if number
                if isinteger:
                    # Count of x values
                    self.main.NUM_OF_DATASET[self.index] = self.main.NUM_OF_DATASET[self.index] + 1

                    # CPMG
                    if self.exptyp == 'CPMG':
                        # Data grid
                        self.main.data_grid[self.index].SetColLabelValue((i+1), _(str(self.main.CPMGFREQ[self.index][i]) + ' Hz'))
                        # Summary
                        self.main.R2eff_grid.SetColLabelValue(len(self.main.CPMGFREQ[self.index])*self.index+i, str(self.main.CPMGFREQ[self.index][i]) + ' Hz')

                    # On resonance
                    if self.exptyp in ['on', 'off']:
                        # Data Grid
                        for dim2 in range(int(self.main.SETTINGS[2])):
                            self.main.data_grid_r1rho[self.index][1][dim2].SetColLabelValue((i+1), _(str(self.main.CPMGFREQ[self.index][i]) + ' s'))
                        # Summary
                        self.main.R2eff_grid.SetColLabelValue(len(self.main.CPMGFREQ[self.index])*self.index+i, str(self.main.CPMGFREQ[self.index][i]) + ' s')

                # Not a number, throw error
                else:
                    error_popup('CPMG frequencies have to be Numbers!\n\nError in data set '+str(i+1))
                    return

        # set up reference spectrum
        for i in range(0, len(self.main.CPMGFREQ[self.index])):
            # No value.
            if self.main.CPMGFREQ[self.index][i] == '':
                continue

            if float(self.main.CPMGFREQ[self.index][i]) == 0.0:
                self.main.referencedata[self.index] = i + 1
                self.main.data_grid[self.index].SetColLabelValue((i+1), _('Reference'))

        # Change image
        self.main.bitmap_setup[self.index].SetBitmap(wx.Bitmap(CHECKED_PIC, wx.BITMAP_TYPE_ANY))#CHECKED_PIC)

        # Close dialog
        self.Destroy()


    def cancel(self, event): # abort
        self.Destroy()
