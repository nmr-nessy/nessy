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
import wx.grid

# NESSY modules
from conf.message import question, error_popup
from conf.path import NESSY_PIC
from conf.NESSY_grid import NESSY_grid



def add_experiment(self, dataset):
    """Function to add new experiment."""
    # add cpmg frequency and time container
    self.CPMGFREQ.append([])
    for i in range(0, int(self.SETTINGS[2])):
        self.CPMGFREQ[dataset-1].append('')

    # add constant cpmg time
    self.CPMG_DELAY.append('0.04')

    # add HD time and time container
    self.HD_TIME.append([])
    for i in range(0, int(self.SETTINGS[2])):
        self.HD_TIME[dataset-1].append('')

    # add HD noise
    self.HD_NOISE.append('1000')

    # reference spectrum
    self.referencedata.append([])

    # Number of data sets
    self.NUM_OF_DATASETS.append(0)
    self.NUM_OF_DATASET.append(0)

    # variance container
    self.R2eff_variance.append([])


def build_data_grid(self, index):
    """Building the Datagrid"""
    self.data_grid[index].CreateGrid(self.RESNO, (int(self.SETTINGS[2]) + 1))
    self.data_grid[index].EnableDragColSize(0)
    self.data_grid[index].EnableDragRowSize(0)
    self.data_grid[index].EnableDragGridSize(0)
    self.data_grid[index].SetColLabelValue(0, _("Sequence"))
    self.data_grid[index].SetColSize(0, 100)

    # Create initial data space
    for i in range(0, int(self.SETTINGS[2])):
        self.data_grid[index].SetColLabelValue((i+1), _("Data " + str(i+1)))
        self.data_grid[index].SetColSize((i+1), 100)


def build_off_resonance(self, exp):
    # Notebook
    notebook = self.data_grid_r1rho[exp][0]

    # Grid
    grid = self.data_grid_r1rho[exp][1]

    # Panels
    panel = []

    # Create Pages
    for i in range((int(self.SETTINGS[2]) + 1)):
        # Create Tab
        panel = wx.Panel(notebook, -1)

        # The sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Add the grid
        grid.append(NESSY_grid(panel, -1, size=(1, 1)))

        # Create the Grid
        grid[i].CreateGrid(self.RESNO, (int(self.SETTINGS[2]) + 1))
        for j in range((int(self.SETTINGS[2]) + 1)):
            # Residue
            if j == 0:
                grid[i].SetColLabelValue(j, 'Residue')

            # Spin Lock Time
            else:
                grid[i].SetColLabelValue(j, 'Data '+str(j))

        # Add grid to sizer
        sizer.Add(grid[i], -1, wx.EXPAND, 0)

        # Add sizer to panel
        panel.SetSizer(sizer)

        # Add new tab
        self.data_grid_r1rho[exp][2].append('')
        notebook.AddPage(panel, _('Offset '+str(i+1)))

        # Event when changing page
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, lambda evt, experiment=exp:self.sync_spinlock(evt, experiment), notebook)


def delete_experiment(self, current):
    # ask to delete
    q = question('Delete Experiment '+str(current)+' ?', self)

    if q:
        # delete tab
        self.MainTab.DeletePage(current)

        # delete parameters
        self.CPMGFREQ.pop(current-2)
        self.CPMG_DELAY.pop(current-2)
        self.referencedata.pop(current-2)
        self.NUM_OF_DATASETS.pop(current-2)
        self.NUM_OF_DATASET.pop(current-2)
        self.R2eff_variance.pop(current-2)
        self.sel_experiment.pop(current-2)

        # number of experiments
        self.NUMOFDATASETS = self.NUMOFDATASETS -1

        # check bitmap
        self.bitmap_setup.pop(current-2)

        # spectrometer frequency
        self.spec_freq.pop(current-2)

        # Static magnetic field B0
        self.B0.pop(current-2)

        # data grid
        self.data_grid.pop(current-2)

        # Heteronucleus
        #self.HETNUC.pop(current-2)


def sync_data(self, data_set_no=None, index=0):
    """Syncronize data entries with data storage"""

    # Workoround due to Windows incompatibiliy
    return

    # synchronize entire dataset
    if not data_set_no:
        # loop over residues
        for i in range(0, self.RESNO):
            self.data[i] = []

            # loop over data sets
            for j in range(0, int(self.SETTINGS[2])):
                self.data[i].append(str(self.data_grid[index].GetCellValue(j, i+1)))


def sync_exp1(self, event, selection):
        # On resonance
        if selection.GetSelection() == 1:
            self.isoffresonance = True
            self.set_offset.Show()

            # Loop over experiments
            for i in range(self.NUMOFDATASETS):
                self.data_grid_r1rho[i][0].Show()
                self.data_grid[i].Hide()
                self.spinlock_offset_label[i].Show()
                self.spinlock_offset_label[i].SetLabel('Spin Lock Power [Hz]')
                self.spinlock_offset_value[i].Show()
                self.spinlock_offset_label1[i].Show()

                # Change Labels of grid
                for j in range((int(self.SETTINGS[2]) + 1)):
                     # No value was added
                    if self.data_grid_r1rho[i][2][j] == '':
                        self.data_grid_r1rho[i][0].SetPageText(j, "Spin Lock " + str(j+1))

                    # Value was set
                    else:
                        self.data_grid_r1rho[i][0].SetPageText(j, str(self.data_grid_r1rho[i][2][j])+' Hz')

                    # Tool tip
                    self.data_grid_r1rho[i][0].SetToolTipString("On-resonance experiment.\n\nValues in tabs represent spin lock power.\n\nSpin lock power can be set in the text field on the left side by confirming with 'enter'.")

                # Update layout
                self.datagrid_sizer[i].Layout()

        # Off resonance R1rho
        elif selection.GetSelection() == 2:
            self.isoffresonance = True
            self.set_offset.Show()

            # Loop over experiments
            for i in range(self.NUMOFDATASETS):
                self.data_grid_r1rho[i][0].Show()
                self.data_grid[i].Hide()
                self.spinlock_offset_label[i].Show()
                self.spinlock_offset_label[i].SetLabel('Offset [Hz]')
                self.spinlock_offset_value[i].Show()
                self.spinlock_offset_label1[i].Show()

                # Change Labels of grid
                for j in range((int(self.SETTINGS[2]) + 1)):
                    # No value was added
                    if self.data_grid_r1rho[i][2][j] == '':
                        self.data_grid_r1rho[i][0].SetPageText(j, "Offset " + str(j+1))

                    # Value was set
                    else:
                        self.data_grid_r1rho[i][0].SetPageText(j, str(self.data_grid_r1rho[i][2][j])+' Hz')

                    # Tool tip
                    self.data_grid_r1rho[i][0].SetToolTipString("Off-resonance experiment.\n\nValues in tabs represent offset.\n\nOffset can be set in the text field on the left side by confirming with 'enter'.")

                # Update layout
                self.datagrid_sizer[i].Layout()

        # CPMG or HD exchange
        else:
            self.isoffresonance = False
            self.set_offset.Hide()

            # Loop over experiments
            for i in range(self.NUMOFDATASETS):
                self.data_grid_r1rho[i][0].Hide()
                self.data_grid[i].Show()
                self.spinlock_offset_label[i].Hide()
                self.spinlock_offset_value[i].Hide()
                self.spinlock_offset_label1[i].Hide()

                # Update layout
                self.datagrid_sizer[i].Layout()

        # Syncing experiment
        for i in range(len(self.sel_experiment)):
            self.sel_experiment[i].SetSelection(selection.GetSelection())


def sync_spinlock1(self, event, experiment=0):
        try:
            # Page was changed
            page = self.data_grid_r1rho[experiment][0].GetSelection()
            # Synchronize spin locks
            self.spinlock_offset_value[experiment].SetValue(self.data_grid_r1rho[experiment][2][page])
        except:
            a='Page was not added yet'


def sync_spinlock_value1(self, event):
        # Experiment
        experiment_no = self.MainTab.GetSelection() -1

        # Tab of spin lock
        page = self.data_grid_r1rho[experiment_no][0].GetSelection()

        # check if entered value is a number
        try:
            a = float(self.spinlock_offset_value[experiment_no].GetValue())
        except:
            error_popup('Entered value has to be a number.', self)
            return

        # Save value
        self.data_grid_r1rho[experiment_no][2][page] = str(self.spinlock_offset_value[experiment_no].GetValue())

        # Lable grid
        self.data_grid_r1rho[experiment_no][0].SetPageText(page, str(self.spinlock_offset_value[experiment_no].GetValue()) +' Hz')




class Reassign_data(wx.Dialog):
    """Function to renumber residue numbering."""
    def __init__(self, main, *args, **kwds):
        self.main = main

        # max
        max = self.main.MainTab.GetPageCount()

        # Current page
        current = self.main.MainTab.GetSelection()
        self.exp = current

        # Create Window
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        # on settings tab
        if current < 1:
            self.Destroy()
            return

        # on result or analysis tab
        if current > (max-3):
            self.Destroy()
            return

        # Main sizer
        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        # Title
        self.label_title = wx.StaticText(self, -1, "Correction of Data\nAssignment, Experiment "+ str(current), style=wx.ALIGN_CENTRE)
        self.label_title.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_1.Add(self.label_title, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)

        # Renumbering section
        sizer_factor = wx.BoxSizer(wx.HORIZONTAL)
        self.label_correction = wx.StaticText(self, -1, "Shift Assignment:")
        self.label_correction.SetMinSize((150, 17))
        sizer_factor.Add(self.label_correction, 0, wx.LEFT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL, 5)
        self.shift = wx.SpinCtrl(self, -1, "0", min=-500, max=500)
        sizer_factor.Add(self.shift, 0, wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_1.Add(sizer_factor, 1, 0, 0)

        # Buttons
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.button_close = wx.Button(self, -1, "Close")
        self.Bind(wx.EVT_BUTTON, self.close, self.button_close)
        sizer_buttons.Add(self.button_close, 0, 0, 10)
        self.button_apply = wx.Button(self, -1, "Apply")
        self.Bind(wx.EVT_BUTTON, self.apply, self.button_apply)
        sizer_buttons.Add(self.button_apply, 0, 0, 5)
        sizer_1.Add(sizer_buttons, 1, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)

        # Pack Window
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()


    def close(self, event):
        self.Destroy()
        event.Skip()


    def apply(self, event): # renumber data

        numofdata = int(self.main.SETTINGS[2])
        exp = self.exp-1

        # Read data
        data = []
        for dataset in range(0, numofdata):     # loop over data sets
            data.append([])

            for residue in range(0, self.main.RESNO):       # loop over residue
                data[dataset].append(str(self.main.data_grid[exp].GetCellValue(residue, dataset+1)))

        # clear data grid
        for i in range(0, self.main.RESNO):     # loop over residue
            for j in range(0, numofdata):       # loop over dataset
                self.main.data_grid[exp].SetCellValue(i, j+1, '')

        # insert new data
        shift = int(self.shift.GetValue())

        for dataset in range(0, numofdata):     # loop over dataset
            for j in range(0, self.main.RESNO):             # loop over residue
                if (j + shift) >= 0:
                    if (j + shift) < self.main.RESNO:
                        self.main.data_grid[exp].SetCellValue((j+shift), dataset+1, data[dataset][j])



class Renumber_residues(wx.Dialog):
    def __init__(self, gui, *args, **kwds):
        self.main = gui

        # max
        max = self.main.MainTab.GetPageCount()

        # Current page
        current = self.main.MainTab.GetSelection()
        self.exp = current-1

        # Create Window
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        # on settings tab
        if current < 1:
            self.Destroy()
            return

        # on result or analysis tab
        if current > (max-3):
            self.Destroy()
            return

        # Main sizer
        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        # Title
        self.label_title = wx.StaticText(self, -1, "Correction of Residue\nNumbering, Experiment "+str(current), style=wx.ALIGN_CENTRE)
        self.label_title.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_1.Add(self.label_title, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)

        # Renumbering section
        sizer_factor = wx.BoxSizer(wx.HORIZONTAL)
        self.label_correction = wx.StaticText(self, -1, "Shift Residues:")
        self.label_correction.SetMinSize((150, 17))
        sizer_factor.Add(self.label_correction, 0, wx.LEFT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL, 5)
        self.shift = wx.SpinCtrl(self, -1, "0", min=-500, max=500)
        sizer_factor.Add(self.shift, 0, wx.RIGHT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_1.Add(sizer_factor, 1, 0, 0)

        # Buttons
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.button_close = wx.Button(self, -1, "Close")
        self.Bind(wx.EVT_BUTTON, self.close, self.button_close)
        sizer_buttons.Add(self.button_close, 0, 0, 10)
        self.button_apply = wx.Button(self, -1, "Apply")
        self.Bind(wx.EVT_BUTTON, self.apply, self.button_apply)
        sizer_buttons.Add(self.button_apply, 0, 0, 5)
        sizer_1.Add(sizer_buttons, 1, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)

        # Pack Window
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()


    def close(self, event):
        self.Destroy()
        event.Skip()


    def apply(self, event): # renumber residues
        exp = self.exp

        # Read sequence
        seq = []
        for i in range(0, self.main.RESNO):
            seq.append(str(self.main.data_grid[exp].GetCellValue(i, 0)))

        # clear data grid
        for i in range(0, self.main.RESNO):
            self.main.data_grid[exp].SetCellValue(i, 0, '')

        # insert new sequence
        shift = int(self.shift.GetValue())
        for j in range(0, self.main.RESNO):
            if (j + shift) >= 0:
                if (j + shift) < self.main.RESNO:
                    self.main.data_grid[exp].SetCellValue((j+shift), 0, seq[j])



class sort_datasets():
    """Class to sort the data sets."""
    def __init__(self, gui):
        # link main frame
        self.main = gui

        # Parameters
        self.datasets = []      # [Number of dataset, CPMG frequence, is there data]
        self.has_sorted = False

        # Check frequencies
        self.check_freq()

        # Check is data is present
        self.check_datasets()

        # Sort datasets
        self.sort_data()

        # Sync datasets
        sync_data(self.main)

        # Feedback
        if self.has_sorted:
            # feedback in log panel
            self.main.report_panel.AppendText('\nDatasets have been sorted.\n')

            # Experiment summary
            self.summary()


    def check_datasets(self):
        """Check if data is present."""

        # loop over datasets
        for dataset in range(0, len(self.datasets)):
            # checkpoint
            checkpoint = False

            #loop over residues
            for residue in range(0, self.main.RESNO):
                if not str(self.main.data_grid.GetCellValue(residue, dataset+1)) == '':
                    checkpoint = True

            # Store if data is present
            if checkpoint:
                if self.datasets[dataset][1]:
                    self.datasets[dataset][2] = True


    def check_freq(self):
        """Check if frequency is specified."""

        # loop over datasets
        for i in range(0, int(self.main.SETTINGS[2])):
            # frequence specified
            if self.main.CPMGFREQ[i] == '':
                self.datasets.append([i+1, False, False])
            else:
                self.datasets.append([i+1, True, False])


    def sort_data(self):
        """Function to sort data."""

        # Loop over dataset
        for dataset in range(0, len(self.datasets)):
            # Shift datasets if data is not complete
            if not self.datasets[dataset][2]:
                # shift datasets
                for i in range(self.datasets[dataset][0], len(self.datasets)):
                    # CPMG freq
                    if i > len(self.datasets):
                        new_cpmg = ''
                    else:
                        new_cpmg = self.main.CPMGFREQ[i]

                    self.main.CPMGFREQ[i-1] = new_cpmg

                    # loop over residue
                    for residue in range(0, self.main.RESNO):
                        # last entry
                        if i == len(self.datasets):
                            new_value = ''
                        # read next dataset entry
                        else:
                            new_value = str(self.main.data_grid.GetCellValue(residue, i+1))

                        # Fill in new value
                        self.main.data_grid.SetCellValue(residue, i, new_value)

                        # Data has been sorted
                        self.has_sorted = True


    def summary(self):
        """write experiment summary."""
        entry = ''

        # loop over frequencies
        for i in range(0, len(self.main.CPMGFREQ)):
            if not str(self.main.CPMGFREQ[i]) == '':
                entry = entry + 'Dataset ' + str(i+1) + ': ' + str(self.main.CPMGFREQ[i]) + ' Hz\n'

        # Write entry
        entry = entry + '\nConstant CPMG relaxation delay:\n' + str(self.main.CPMG_DELAY) + ' [s]'
        self.main.label_summary.SetLabel(entry)

