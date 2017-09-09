#################################################################################
#                                                                               #
#   (C) 2010 Michael Bieri                                                      #
#   (C) 2016 Edward d'Auvergne                                                  #
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
from conf.filedialog import openfile
from conf.message import question, message, error_popup
from conf.filedialog import openfile, multi_openfile
from conf.data import sync_data
from conf.cpmg import Setup_experiment
from conf.project import stringtolist
from conf.path import NESSY_PIC, IMPORT_DATA_SIDE_PIC



class Bruker_project(wx.Dialog):
    """Import of Bruker Dynamic Center Project."""
    def __init__(self, gui, *args, **kwds):
        # link parameters
        self.main = gui

        # draw the frame
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")
        self.SetTitle("NESSY")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        # build frame
        self.build()


    def build(self):
        # Image
        self.topsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(IMPORT_DATA_SIDE_PIC, wx.BITMAP_TYPE_ANY))
        self.bitmap.SetMinSize((100, 180))
        self.topsizer.Add(self.bitmap, 0, wx.ALL, 5)

        # Mainsizer
        mainsizer = wx.BoxSizer(wx.VERTICAL)

        # Header
        self.header = wx.StaticText(self, -1, "Import of BRUKER Protein Dynamic Center Project")
        self.header.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        mainsizer.Add(self.header, 0, wx.ALL|wx.ALIGN_LEFT, 5)

        # File
        sizer_file = wx.BoxSizer(wx.HORIZONTAL)
        self.title_file = wx.StaticText(self, -1, "BRUKER Protein Dynamic Center Export File:")
        self.title_file.SetMinSize((250, 17))
        mainsizer.Add(self.title_file, 0, wx.LEFT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5)

        self.bruker_file = wx.TextCtrl(self, -1, "")
        self.bruker_file.SetMinSize((200, 23))
        sizer_file.Add(self.bruker_file, 0, wx.LEFT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL, 5)

        self.button_add_file = wx.Button(self, -1, "+")
        self.button_add_file.SetMinSize((30, 23))
        self.Bind(wx.EVT_BUTTON, self.open_file, self.button_add_file)
        sizer_file.Add(self.button_add_file, 0, wx.LEFT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL, 5)
        mainsizer.Add(sizer_file, 0, wx.EXPAND, 0)

        # Experiment
        sizer_experiment = wx.BoxSizer(wx.HORIZONTAL)
        self.title_experiment = wx.StaticText(self, -1, "Add to Experiment no:")
        self.title_experiment.SetMinSize((250, 17))
        mainsizer.Add(self.title_experiment, 0, wx.LEFT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5)

        self.exp_no = wx.SpinCtrl(self, -1, "", min=1, max=self.main.NUMOFDATASETS)
        sizer_experiment.Add(self.exp_no, 0, wx.LEFT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL, 5)
        mainsizer.Add(sizer_experiment, 0, wx.EXPAND, 0)

        # Buttons
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.button_ok = wx.Button(self, -1, "Import")
        self.Bind(wx.EVT_BUTTON, self.do_import, self.button_ok)
        sizer_buttons.Add(self.button_ok, 0, wx.ALL, 10)
        self.button_cancel = wx.Button(self, -1, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.cancel, self.button_cancel)
        sizer_buttons.Add(self.button_cancel, 0, wx.ALL, 10)
        mainsizer.Add(sizer_buttons, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        # Pack dialog
        self.topsizer.Add(mainsizer, 0, 0, 0)
        self.SetSizer(self.topsizer)
        self.topsizer.Fit(self)
        self.Layout()


    def cancel(self, event):
        self.Destroy()


    def do_import(self, event):
        """Reads the file."""
        # Flag for intensity entries
        is_intensity = False

        # experiment index
        exp_index = int(self.exp_no.GetValue())-1

        # Filename
        filename = str(self.bruker_file.GetValue())
        if filename == '':
            error_popup('No file selected!')
            return

        # Datacontainer
        entries = []

        # open file
        file = open(filename)

        for line in file:
            entry = line
            entry = line.strip()
            entry = entry.split('\t')

            # Check project
            if 'Project:' in entry[0]:
                if not 'Dynamic method/Rex' in entry[1]:
                    error_popup('This is not a "REX" BRUKER File')
                    return

            # read CPMG delay
            if 'Total mixing time[s]:' in entry[0]:
                self.main.CPMG_DELAY[exp_index] = entry[1]

            # Proton frequency
            if 'Proton frequency[MHz]:' in entry[0]:
                self.main.spec_freq[exp_index].SetValue(str(float(entry[1])))


            # Detect intensity section
            if 'SECTION:' in entry[0]:
                if 'original integrals' in entry[1]:
                    # Change Flag
                    is_intensity = True

                else:
                    is_intensity = False

            # Read intensities and CPMG delay
            if is_intensity:
                # CPMG delay
                if 'Rf field [1/s]:' in entry[0]:
                    # loop over CPMG frequencies
                    for i in range(1, len(entry)):
                        self.main.CPMGFREQ[exp_index][i-1] = str(int(round(float(entry[i]))))

                elif entry[0] == '':
                    continue

                elif 'SECTION:' in entry[0]:
                    continue

                elif 'Peak name' in entry[0]:
                    continue

                # Intensity
                else:
                    self.fill_in_intensity(entry, exp_index)

        # Close file
        file.close()

        # Feedback
        message('Successfully imported BRUKER Dynamic Center Project:\n'+str(self.bruker_file.GetValue())+'\n\nPlease Select Project Folder.', self)

        # close dialog
        self.Destroy()


    def fill_in_intensity(self, entry, exp_index):
        """Fills intensities in Data Grid."""
        # Residue number
        resno = 0

        # find start of number
        start = 0
        while entry[0][start].isdigit()==False: start = start+1

        # find end of number
        end = start
        while end < len(entry[0]) and entry[0][end].isdigit()==True: end = end+1

        # Residue Number
        resno = int(entry[0][start:end]) - 1

        # Sequence
        self.main.data_grid[exp_index].SetCellValue(resno, 0, entry[0][0:3])

        # Data
        # loop over entries
        for dataset in range(1, len(entry)):
            self.main.data_grid[exp_index].SetCellValue(resno, dataset, entry[dataset])



    def open_file(self, event): # wxGlade: Bruker.<event_handler>
        # Read file
        filename = openfile('Select Bruker Dynamic Center export', self.main.PROJFOLDER, '', 'all files (*.*)|*', self)

        if filename:
            self.bruker_file.SetValue(filename)




class Erase_dataset(wx.Dialog):
    def __init__(self, gui, *args, **kwds):
        # connect gui
        self.main = gui

        # The frame
        kwds["style"] = wx.CAPTION
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        # max
        max = self.main.MainTab.GetPageCount()

        # Current page
        self.current = self.main.MainTab.GetSelection()
        self.exp = self.current-1

        # on settings tab
        if self.current < 1:
            self.Destroy()
            return

        # on result or analysis tab
        if self.current > (max-3):
            self.Destroy()
            return

        # Build window
        self.build()


    def build(self):
        # main sizer
        mainsizer = wx.BoxSizer(wx.VERTICAL)

        # title
        self.label_1 = wx.StaticText(self, -1, 'Erase Data Set in Experiment'+str(self.current)+':', style=wx.ALIGN_CENTRE)
        self.label_1.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        mainsizer.Add(self.label_1, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 10)

        # Select Data set
        datasizer = wx.BoxSizer(wx.HORIZONTAL)
        label_dataset = wx.StaticText(self, -1, 'Data Set to Erase:', style=wx.ALIGN_CENTRE)
        label_dataset.SetMinSize((150, 17))
        datasizer.Add(label_dataset, 0, wx.ADJUST_MINSIZE|wx.LEFT, 5)

        self.datasetnumber = wx.SpinCtrl(self, -1, '1', min=1, max=int(self.main.SETTINGS[2]))
        self.datasetnumber.SetMinSize((95, 20))
        datasizer.Add(self.datasetnumber, 0, wx.ADJUST_MINSIZE|wx.RIGHT, 5)

        mainsizer.Add(datasizer, 0, wx.ADJUST_MINSIZE, 0)

        # Buttons
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        # Apply
        self.ok_button = wx.Button(self, -1, "Apply")
        self.Bind(wx.EVT_BUTTON, self.apply_erase, self.ok_button)
        sizer_buttons.Add(self.ok_button, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 10)
        # cancel
        self.cancel_button = wx.Button(self, -1, "Close")
        self.Bind(wx.EVT_BUTTON, self.abort_erase, self.cancel_button)
        sizer_buttons.Add(self.cancel_button, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 10)

        mainsizer.Add(sizer_buttons, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_HORIZONTAL, 0)

        # Pack window
        self.SetSizer(mainsizer)
        mainsizer.Fit(self)
        self.Layout()


    def apply_erase(self, event):
        dataset = str(self.datasetnumber.GetValue())
        q = question('Really erase Dataset ' +  dataset + ' ?', self)
        if q:
            for i in range(0, self.main.RESNO):
                self.main.data_grid[self.exp].SetCellValue(i, int(dataset), '')


    def abort_erase(self, event):
        self.Destroy()




class import_data(wx.Dialog):
    def __init__(self, gui, multi, peaklist, *args, **kwds):
        # The frame
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        # connect data
        self.main = gui

        # multi or single file
        self.multi = multi

        # Import peaklist
        self.ispeaklist = peaklist

        # Labels
        if not peaklist:
            if multi:
                self.title = 'Import Multiple Peak Lists'
                self.datafile_text = 'Start of Data Sets:'
            else:
                self.title = 'Import Peak List'
                self.datafile_text = 'Data Set Number:'
        else:
            self.multi = False
            self.title = 'Import Data for Residue'
            self.datafile_text = 'Residue:'

        # Data file columns
        self.resnum = str( int(self.main.DATAFILEPROPERTY[0]) + 1)
        self.data_int = str( int(self.main.DATAFILEPROPERTY[1]) + 1)
        self.file_type = self.main.DATAFILEPROPERTY[2]

        # file name(s)
        self.filenames = ''

        # Image
        self.topsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(IMPORT_DATA_SIDE_PIC, wx.BITMAP_TYPE_ANY))
        self.topsizer.Add(self.bitmap, 0, wx.ALL, 5)

        # Main Sizer
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)

        # Header
        self.header()

        # Load data file(s)
        self.load_file()

        # Specify start of dataset
        self.dataset_no()

        # select residue number column
        self.rescol()

        # select intensity number column
        self.int_col()

        # filetype of peak file
        self.filetype()

        # Experiment number
        self.exp_no()

        # Buttons
        self.buttons()

        # Pack window
        self.topsizer.Add(self.mainsizer, 0, 0, 0)
        self.SetSizer(self.topsizer)
        self.topsizer.Fit(self)
        self.Layout()


    def header(self):
        # Title
        self.label_1 = wx.StaticText(self, -1, self.title, style=wx.ALIGN_CENTRE)
        self.label_1.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_1.SetMinSize((300, 20))
        self.mainsizer.Add(self.label_1, 0, wx.ALL|wx.BOTTOM|wx.ALIGN_LEFT, 5)


    def load_file(self):
        # Build load datafile(s)
        # Sizer
        sizer_datafiles = wx.BoxSizer(wx.HORIZONTAL)

        # Datafile label
        self.label_datafile = wx.StaticText(self, -1, "Datafile:")
        self.label_datafile.SetMinSize((60, 17))
        sizer_datafiles.Add(self.label_datafile, 0, wx.LEFT|wx.ADJUST_MINSIZE|wx.TOP, 5)

        # Datafile
        self.filename = wx.TextCtrl(self, -1, "")
        self.filename.SetMinSize((200, 20))
        sizer_datafiles.Add(self.filename, 0, wx.BOTTOM|wx.ADJUST_MINSIZE|wx.TOP, 5)

        # Add data file button
        self.add_data = wx.Button(self, -1, "+")
        self.add_data.SetMinSize((30, 20))
        self.Bind(wx.EVT_BUTTON, self.add_data_file, self.add_data)
        sizer_datafiles.Add(self.add_data, 0, wx.ADJUST_MINSIZE|wx.TOP, 5)

        # Pack sizer
        self.mainsizer.Add(sizer_datafiles, 0, 0, 0)


    def dataset_no(self):
        # Build data file number / start of data files
        # sizer
        sizer_dataset = wx.BoxSizer(wx.HORIZONTAL)

        # data file number text
        self.datafile_text = wx.StaticText(self, -1, self.datafile_text)
        self.datafile_text.SetMinSize((195, 17))
        sizer_dataset.Add(self.datafile_text, 0, wx.LEFT|wx.ADJUST_MINSIZE|wx.TOP, 5)

        # Data file number selector
        self.datafilenum = wx.SpinCtrl(self, -1, "1", min=1, max=20)
        self.datafilenum.SetMinSize((95, 20))
        self.datafilenum.SetToolTipString("Number of data set")
        sizer_dataset.Add(self.datafilenum, 0, wx.ADJUST_MINSIZE|wx.TOP, 5)

        # Pack sizer
        self.mainsizer.Add(sizer_dataset, 0, 0, 0)


    def exp_no(self):
        # Build data file number / start of data files
        # sizer
        sizer_exp = wx.BoxSizer(wx.HORIZONTAL)

        # data file number text
        self.experiment_text = wx.StaticText(self, -1, "Experiment No.:")
        self.experiment_text.SetMinSize((195, 17))
        sizer_exp.Add(self.experiment_text, 0, wx.LEFT|wx.ADJUST_MINSIZE|wx.TOP, 5)

        # Data file number selector
        # Detect experiment
        # on settings tab
        if self.main.MainTab.GetSelection() < 0:
            page = 1

        # on start or results tab
        elif self.main.MainTab.GetSelection() > (self.main.MainTab.GetPageCount()-2):
            page = 1

        # experiment tab
        else:
            page = self.main.MainTab.GetSelection()

        self.exp_no = wx.SpinCtrl(self, -1, str(page), min=1, max=self.main.NUMOFDATASETS)
        self.exp_no.SetMinSize((95, 20))
        self.exp_no.SetToolTipString("Number of experiment")
        sizer_exp.Add(self.exp_no, 0, wx.ADJUST_MINSIZE|wx.TOP, 5)

        # Pack sizer
        self.mainsizer.Add(sizer_exp, 0, 0, 0)


    def rescol(self):
        # Build residue number column
        # sizer
        sizer_resicol = wx.BoxSizer(wx.HORIZONTAL)

        # residue number colum text
        self.label_resicol = wx.StaticText(self, -1, "Residue Number Column:")
        self.label_resicol.SetMinSize((195, 17))
        sizer_resicol.Add(self.label_resicol, 0, wx.LEFT|wx.ADJUST_MINSIZE|wx.TOP, 5)

        # residue column selector
        self.resi_col = wx.SpinCtrl(self, -1, self.resnum, min=0, max=100)
        self.resi_col.SetMinSize((95, 20))
        self.resi_col.SetToolTipString("Column Numbering start with 1")
        sizer_resicol.Add(self.resi_col, 0, wx.ADJUST_MINSIZE|wx.TOP, 5)

        # Pack sizer
        self.mainsizer.Add(sizer_resicol, 0, 0, 0)


    def int_col(self):
        # Build intensity column
        # sizer
        sizer_intcol = wx.BoxSizer(wx.HORIZONTAL)

        # Intensity column text
        if not self.ispeaklist: self.label_intcol = wx.StaticText(self, -1, "Data Hight Column:")
        else:                   self.label_intcol = wx.StaticText(self, -1, "Data is in Raw:")
        self.label_intcol.SetMinSize((195, 17))
        sizer_intcol.Add(self.label_intcol, 0, wx.LEFT|wx.ADJUST_MINSIZE|wx.TOP|wx.BOTTOM, 5)

        # intensity column selector
        self.data_hight_col = wx.SpinCtrl(self, -1, self.data_int, min=0, max=100)
        self.data_hight_col.SetMinSize((95, 20))
        self.data_hight_col.SetToolTipString("Column Numbering start with 1")
        sizer_intcol.Add(self.data_hight_col, 0, wx.ADJUST_MINSIZE|wx.TOP|wx.BOTTOM, 5)

        # Pack sizer
        self.mainsizer.Add(sizer_intcol, 0, 0, 0)


    def filetype(self):
        # Type of peakfile
        # Sizer
        sizer_filetype = wx.BoxSizer(wx.HORIZONTAL)

        # Peak File selector text
        self.label_filetype = wx.StaticText(self, -1, "Data Separator:")
        self.label_filetype.SetMinSize((145, 17))
        sizer_filetype.Add(self.label_filetype, 0, wx.LEFT|wx.ADJUST_MINSIZE, 5)

        # Peak File selector
        self.peakfile_type = wx.ListBox(self, -1, choices=["Tabulator", "Space", "Comma", "Semicolon"])
        if self.file_type == "Tabulator":
            sele = 0
        elif self.file_type == "Space":
            sele = 1
        elif self.file_type == 'Comma':
            sele = 2
        elif self.file_type == 'Semicolon':
            sele = 3
        else:
            sele = 0
        self.peakfile_type.SetSelection(sele)
        self.peakfile_type.SetMinSize((145, 80))
        sizer_filetype.Add(self.peakfile_type, 0, wx.ADJUST_MINSIZE, 20)

        # Pack sizer
        self.mainsizer.Add(sizer_filetype, 0, 0, 0)


    def buttons(self):
        # Build buttons
        # sizer
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)

        # OK
        self.ok_button = wx.Button(self, -1, "Import")
        self.Bind(wx.EVT_BUTTON, self.do_add_data, self.ok_button)
        sizer_buttons.Add(self.ok_button, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 10)

        # cancel
        self.cancel_button = wx.Button(self, -1, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.abort_import, self.cancel_button)
        sizer_buttons.Add(self.cancel_button, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 10)

        # Pack sizer
        self.mainsizer.Add(sizer_buttons, 0, wx.ALIGN_CENTER_HORIZONTAL| wx.ALIGN_CENTER_VERTICAL, 0)


    def add_data_file(self, event):
        # open file multiple files
        if self.multi:
            newfile = multi_openfile('Select file to open', self.main.PROJFOLDER, '', 'all files (*.*)|*', self)
            if not newfile == False:
                self.filename.SetValue(str(len(newfile)) + ' Files Selected')
                self.filenames = newfile

        # open file multiple files
        else:
            newfile = openfile('Select file to open', self.main.PROJFOLDER, '', 'all files (*.*)|*', self)
            if not newfile == False:
                self.filename.SetValue(newfile)
                self.filenames = newfile


    def do_add_data(self, event): # add data
        # add selected datafiles

        # Is spin lock experiments
        if self.main.sel_experiment[0].GetSelection() in [1, 2]:    self.spinlock = True
        else:                                                       self.spinlock = False

        # Residue Number Column
        self.resnum = str( int(self.resi_col.GetValue())-1)

        # Intensity column
        self.data_int = str(int(self.data_hight_col.GetValue())-1)

        # file type
        self.file_type = str(self.peakfile_type.GetStringSelection())

        # Create separator
        if self.file_type == "Tabulator":       self.separator = '\t'
        elif self.file_type == "Space":         self.separator = ' '
        elif self.file_type == "Coma":          self.separator = ','
        elif self.file_type == "Semicolon":     self.separator = ';'
        else:                                   self.separator = ' '

        # data set no / starting point of data sets
        self.data_start = str(self.datafilenum.GetValue())

        # Store entries
        self.main.DATAFILEPROPERTY = [self.resnum, self.data_int, self.file_type]

        # Is file(s) selected
        if self.filenames == '':
            message('Missing Data File!', self)
            return

        else:
            q = question('Import Data?', self)
            if q:
                # Import data for on eresidue
                if self.ispeaklist: self.fill_in_residue(self.filenames, self.data_start)

                # Import peak list(s)
                else:
                    if self.multi:
                        for i in range(0, len(self.filenames)):
                            self.fill_in_values(self.filenames[i], int(self.data_start)+i)
                    else:
                        self.fill_in_values(self.filenames, self.data_start)

        # synchronize data sets
        sync_data(self.main)

        # Close window
        self.Destroy()


    def fill_in_residue(self, filename, residue):
        # Fill in values for residue
        residue = int(residue)

        # experiment index
        index = int(self.exp_no.GetValue())-1

        # read file
        file = open(filename, 'r')

        # Index
        raw = 0

        # loop over residues
        for line in file:
            # correct raw
            if raw == int(self.data_int):
                # abort criteria
                if line in ['', '\n']:          continue

                # Split
                if self.separator == ' ':       entries = line.split()
                else:                           entries = line.split(self.separator)

                # read residue number
                resnum = entries[residue-1]

                # find start of number
                start = 0
                while resnum[start].isdigit()==False: start = start+1

                # find end of number
                end = start
                while end < len(resnum) and resnum[end].isdigit()==True: end = end+1

                # cut out residue number integer
                resnum = resnum[start:end]

                # Fill in values
                exp = 1
                for i in range(len(entries)):
                    # don't read residue
                    print(str(self.main.data_grid_r1rho[index][0].GetSelection()))

                    # Fill in CPMG or H/D data
                    if not self.spinlock:   self.main.data_grid[index].SetCellValue(int(resnum)-1, int(exp), str(float(entries[i])))

                    # Fill in spin lock data
                    else:                   self.main.data_grid_r1rho[index][1][self.main.data_grid_r1rho[index][0].GetSelection()].SetCellValue(int(resnum)-1, int(exp), str(float(entries[i])))

                    # next experiment
                    exp = exp + 1

            # next raw
            raw = raw + 1


    def fill_in_values(self, datafile, datasetno):
        # reads data files and fills values in dataset

        # experiment index
        index = int(self.exp_no.GetValue())-1

        # read file
        file = open(datafile, 'r')
        for line in file:
            line = line.replace('\n', '')

            # Split
            if self.separator == ' ':       entry = line.split()
            else:                           entry = line.split(self.separator)

            if not entry in ['', []]: # empty line
                if not entry[0] in ['Assignment', '', 'Assign', 'Assign', None, '\n']:
                  try:

                    # set residue number form corresponding column
                    resnum = str(entry[int(self.resnum)])

                    # find start of number
                    start = 0
                    while resnum[start].isdigit()==False: start = start+1

                    # find end of number
                    end = start
                    while end < len(resnum) and resnum[end].isdigit()==True: end = end+1

                    # cut out residue number integer
                    resnum = resnum[start:end]

                    # fill values in grid
                    if not self.spinlock:   self.main.data_grid[index].SetCellValue(int(resnum)-1, int(datasetno), str(float(entry[int(self.data_int)])))
                    else:                   self.main.data_grid_r1rho[index][1][self.main.data_grid_r1rho[index][0].GetSelection()].SetCellValue(int(resnum)-1, int(datasetno), str(float(entry[int(self.data_int)])))
                  except:
                      continue

        # Close file
        file.close()


    def abort_import(self, event):
        # cancel
        self.Destroy()



def pdb_to_sequence(self):
    """Extract protein sequence from PDB file"""

    sequence = [] # create empty sequence
    residue_num = []

    file = open(self.PDB, 'r')  #open pdb file for reading


    for line in file:
        entries = []

        # extract lines from file
        entry = str(line.strip().split('\n'))
        entry = entry[2: (len(entry)-2)]

        #extract columns from line
        entries = entry.split()

        # Skip is empty line
        if len(entries) < 5:
            continue

        # add sequence to list
        if entries[0] == 'ATOM':

            #write sequence to grid
            # loop over experiments
            for exp in range(0, self.NUMOFDATASETS):
                try:
                    self.data_grid[exp].SetCellValue(int(entries[5]) - 1, 0, entries[3])
                except:
                    a = 'Dummy for PDB version differences'


        # stop if protein sequence is finished
        if entries[0] == 'TER':
            break

    #close file
    file.close()



class NMRView_project_import(wx.Dialog):
    """Import of Bruker Dynamic Center Project."""
    def __init__(self, gui, *args, **kwds):
        # link parameters
        self.main = gui

        # draw the frame
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")
        self.SetTitle("NESSY")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        # build frame
        self.build()


    def build(self):
        # Image
        self.topsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(IMPORT_DATA_SIDE_PIC, wx.BITMAP_TYPE_ANY))
        self.bitmap.SetMinSize((100, 210))
        self.topsizer.Add(self.bitmap, 0, wx.ALL, 5)

        # Mainsizer
        mainsizer = wx.BoxSizer(wx.VERTICAL)

        # Header
        self.header = wx.StaticText(self, -1, "Import of NMR View Table")
        self.header.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        mainsizer.Add(self.header, 0, wx.ALL|wx.ALIGN_LEFT, 5)

        # File
        sizer_file = wx.BoxSizer(wx.HORIZONTAL)
        self.title_file = wx.StaticText(self, -1, "NMR View Table File:")
        self.title_file.SetMinSize((250, 17))
        mainsizer.Add(self.title_file, 0, wx.LEFT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5)

        self.bruker_file = wx.TextCtrl(self, -1, "")
        self.bruker_file.SetMinSize((200, 23))
        sizer_file.Add(self.bruker_file, 0, wx.LEFT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL, 5)

        self.button_add_file = wx.Button(self, -1, "+")
        self.button_add_file.SetMinSize((30, 23))
        self.Bind(wx.EVT_BUTTON, self.open_file, self.button_add_file)
        sizer_file.Add(self.button_add_file, 0, wx.LEFT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL, 5)
        mainsizer.Add(sizer_file, 0, wx.EXPAND, 0)

        # Assign to Residue or Peak
        peakres = wx.BoxSizer(wx.HORIZONTAL)
        self.title_peakres = wx.StaticText(self, -1, "Assign Data to:")
        self.title_peakres.SetMinSize((250, 17))
        mainsizer.Add(self.title_peakres, 0, wx.LEFT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5)

        self.peak_residue = wx.Choice(self, -1, choices=["Residue", "Peak"])
        self.peak_residue.SetSelection(0)
        self.peak_residue.SetMinSize((150, 25))
        mainsizer.Add(self.peak_residue, 0, 0, 0)


        # Experiment
        sizer_experiment = wx.BoxSizer(wx.HORIZONTAL)
        self.title_experiment = wx.StaticText(self, -1, "Add to Experiment no:")
        self.title_experiment.SetMinSize((250, 17))
        mainsizer.Add(self.title_experiment, 0, wx.LEFT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5)

        self.exp_no = wx.SpinCtrl(self, -1, "", min=1, max=self.main.NUMOFDATASETS)
        sizer_experiment.Add(self.exp_no, 0, wx.LEFT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL, 5)
        mainsizer.Add(sizer_experiment, 0, wx.EXPAND, 0)

        # Buttons
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.button_ok = wx.Button(self, -1, "Import")
        self.Bind(wx.EVT_BUTTON, self.do_import, self.button_ok)
        sizer_buttons.Add(self.button_ok, 0, wx.ALL, 10)
        self.button_cancel = wx.Button(self, -1, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.cancel, self.button_cancel)
        sizer_buttons.Add(self.button_cancel, 0, wx.ALL, 10)
        mainsizer.Add(sizer_buttons, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        # Pack dialog
        self.topsizer.Add(mainsizer, 0, 0, 0)
        self.SetSizer(self.topsizer)
        self.topsizer.Fit(self)
        self.Layout()


    def cancel(self, event):
        self.Destroy()


    def do_import(self, event):
        """Reads the file."""
        # experiment index
        exp_index = int(self.exp_no.GetValue())-1

        # selection of Peak or Residue
        self.selection = int(self.peak_residue.GetSelection())

        # Filename
        filename = str(self.bruker_file.GetValue())
        if filename == '':
            error_popup('No file selected!')
            return

        # Datacontainer
        entries = []
        header = []
        residue = []
        peak = []

        # Index
        residue_index = 0
        peak_index = 0

        # open file
        file = open(filename)

        for line in file:
            entry = line
            entry = entry.replace('\n', '')

            # Split the line
            entry = entry.split('\t')

            # Skip if empty line
            if len(entry) < 2:
                continue

            # read index
            if 'Peak' in entry:
                # read Peak index
                while not entry[peak_index] == 'Peak': peak_index = peak_index + 1

                # read residue index
                while not entry[residue_index] == 'Residue': residue_index = residue_index + 1

                # save the header
                header = entry

                # exclude index
                exclude_index = []
                for i in range(len(entry)):
                    if entry[i] in ['Peak', 'N', 'Residue', 'a', 'asigma', 'b', 'bsigma', 'rmsd']:
                        exclude_index.append(i)

            # save data
            else:
                # append residue
                residue.append(entry[residue_index])

                # append peak
                peak.append(entry[peak_index])

                # append data
                entries.append([])
                for i in range(len(entry)):
                    # exclude
                    if i in exclude_index:
                        continue

                    entries[len(entries)-1].append(entry[i])

        # Close file
        file.close()

        # fill in values
        self.fill_in_intensity(exp_index, entries, residue, peak, self.selection)

        # Feedback
        message('Successfully imported BRUKER Dynamic Center Project:\n'+str(self.bruker_file.GetValue())+'\n\nPlease Select Project Folder.', self)

        # close dialog
        self.Destroy()


    def fill_in_intensity(self, exp_index, entries, residue, peak, selection):
        """Fills intensities in Data Grid."""
        # Peak number was selected
        if selection == 1:
            # fill in values
            for i in range(len(peak)):
                # loop over entries
                for e in range(len(entries[i])):
                    self.main.data_grid[exp_index].SetCellValue(int(peak[i]), e+1, entries[i][e])

        # residue number was selected
        if selection == 0:
            # fill in values
            for i in range(len(residue)):
                # abort if peak is not assigned
                if residue[i] == '':
                    continue

                # extract residue number
                # Residue number
                resno = 0

                # find start of number
                start = 0
                while residue[i][start].isdigit()==False: start = start+1

                # find end of number
                end = start
                while end < len(residue[i]) and residue[i][end].isdigit()==True: end = end+1

                # Residue Number
                resno = int(residue[i][start:end]) - 1

                # loop over entries
                for e in range(len(entries[i])):
                    self.main.data_grid[exp_index].SetCellValue(resno, e+1, entries[i][e])


    def open_file(self, event): # wxGlade: Bruker.<event_handler>
        # Read file
        filename = openfile('Select Bruker Dynamic Center export', self.main.PROJFOLDER, '', 'all files (*.*)|*', self)

        if filename:
            self.bruker_file.SetValue(filename)




class vd_import():
    """Class to import CPMG frequencies from VD list (Bruker only)"""

    def __init__(self, main):

        # connect main frame
        self.main = main

        # current tab
        current_tab = self.main.MainTab.GetSelection()

        # is tab experimen?
        if self.main.MainTab.GetSelection() < 1:
            index = 0
        elif self.main.MainTab.GetSelection() > (self.main.MainTab.GetPageCount()-2):
            index = 0

        # actual tab is experiment
        else:
            index = self.main.MainTab.GetSelection()-1

        # clean CPMGFREQ
        self.main.CPMGFREQ[index] = []
        for i in range(0, int(self.main.SETTINGS[2])):
            self.main.CPMGFREQ[index].append('')

        # select file to open
        vd_file = openfile('Select VD List', self.main.PROJFOLDER, 'vdlist.list', 'all files (*)|*', self.main)
        if not vd_file:
            return

        # read entries and set CPMG frequencies
        i = 0
        if vd_file:
            file = open(vd_file, 'r')
            for line in file:
                entry = str(line.strip().split('\n'))
                entry = entry[2: (len(entry)-2)]

                # set CPMGFREQ
                if i <= int(self.main.SETTINGS[2]):
                    self.main.CPMGFREQ[index][i] = str(entry)
                    i = i +1

        # Open set up Panel.
        self.main.MainTab.SetSelection(index+1)
        exp_mode = self.main.sel_experiment[index].GetSelection()
        if exp_mode == 0:
            cpmg_setup = Setup_experiment(self.main, 'CPMG', None, -1, "")
        if exp_mode == 1:
            cpmg_setup = Setup_experiment(self.main, 'on', None, -1, "")
        if exp_mode == 2:
            cpmg_setup = Setup_experiment(self.main, 'off', None, -1, "")
        cpmg_setup.ShowModal()
