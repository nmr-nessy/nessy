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
import math
from os import sep
import wx

# NESSY modules
from conf.filedialog import openfile, savefile
from conf.message import error_popup, message
from conf.path import NESSY_PIC, IMPORT_DATA_SIDE_PIC



class Back_calc_gui(wx.Dialog):
    """Class to back calculate Intensities."""
    def __init__(self, main, *args, **kwds):

        # The frame
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("NESSY - Back calc tool")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        # link parameters
        self.main = main

        # build window
        self.build_gui()


    def build_gui(self):
        """Build the gui."""

        # Image
        self.topsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(IMPORT_DATA_SIDE_PIC, wx.BITMAP_TYPE_ANY))
        #self.bitmap.SetMinSize((100,180))
        self.topsizer.Add(self.bitmap, 0, wx.ALL, 5)

        # Main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        self.header = wx.StaticText(self, -1, "Back Calculation Tool of Intensities", style=wx.ALIGN_CENTRE)
        self.header.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.header.SetMinSize((540, 20))
        main_sizer.Add(self.header, 0, wx.ALL|wx.ALIGN_LEFT, 5)

        # Reference peak file
        sizer_reference = wx.BoxSizer(wx.HORIZONTAL)
        self.label_reference = wx.StaticText(self, -1, "Select new reference peak list:")
        self.label_reference.SetMinSize((210, 17))
        sizer_reference.Add(self.label_reference, 0, wx.LEFT, 5)
        self.reference_peaklist = wx.TextCtrl(self, -1, "")
        self.reference_peaklist.SetMinSize((300, 19))
        sizer_reference.Add(self.reference_peaklist, 0, 0, 0)
        self.add_reference = wx.Button(self, -1, "+")
        self.add_reference.SetMinSize((25, 19))
        self.Bind(wx.EVT_BUTTON, self.add_referencefile, self.add_reference)
        sizer_reference.Add(self.add_reference, 0, 0, 0)
        # add to main sizer
        main_sizer.Add(sizer_reference, 0, wx.EXPAND, 0)

        # Peak list
        sizer_peaklist = wx.BoxSizer(wx.HORIZONTAL)
        self.label_peaklist = wx.StaticText(self, -1, "Select peak list:")
        self.label_peaklist.SetMinSize((210, 17))
        sizer_peaklist.Add(self.label_peaklist, 0, wx.LEFT, 5)
        self.peaklist = wx.TextCtrl(self, -1, "")
        self.peaklist.SetMinSize((300, 19))
        sizer_peaklist.Add(self.peaklist, 0, 0, 0)
        self.add_peaklist = wx.Button(self, -1, "+")
        self.add_peaklist.SetMinSize((25, 19))
        self.Bind(wx.EVT_BUTTON, self.load_list, self.add_peaklist)
        sizer_peaklist.Add(self.add_peaklist, 0, 0, 0)
        # add to main sizer
        main_sizer.Add(sizer_peaklist, 0, wx.EXPAND, 0)

        # Save file
        sizer_save = wx.BoxSizer(wx.HORIZONTAL)
        self.label_save = wx.StaticText(self, -1, "Select output peak list:")
        self.label_save.SetMinSize((210, 17))
        sizer_save.Add(self.label_save, 0, wx.LEFT, 5)
        self.save_file = wx.TextCtrl(self, -1, "")
        self.save_file.SetMinSize((300, 19))
        sizer_save.Add(self.save_file, 0, 0, 0)
        self.select_savefile = wx.Button(self, -1, "+")
        self.select_savefile.SetMinSize((25, 19))
        self.Bind(wx.EVT_BUTTON, self.select_save, self.select_savefile)
        sizer_save.Add(self.select_savefile, 0, 0, 0)
        # add to main sizer
        main_sizer.Add(sizer_save, 0, wx.EXPAND, 0)

        # Help text
        self.hepl_text = wx.StaticText(self, -1, "Back calc tool will calculate intensities of new experiments  normalized gainst existing data.\n\nThis tool is suitable for adding additional data points measured independently.\n\nNew peak lists are generated in Sparky format.", style=wx.ALIGN_CENTRE)
        self.hepl_text.SetMinSize((400, 120))
        main_sizer.Add(self.hepl_text, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 10)

        # Buttons
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.button_calc = wx.Button(self, -1, "Calculate")
        self.Bind(wx.EVT_BUTTON, self.calc, self.button_calc)
        sizer_buttons.Add(self.button_calc, 0, 0, 0)
        self.button_1 = wx.Button(self, -1, "Close")
        self.Bind(wx.EVT_BUTTON, self.close, self.button_1)
        sizer_buttons.Add(self.button_1, 0, 0, 0)
        main_sizer.Add(sizer_buttons, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)

        # Pack dialog
        self.topsizer.Add(main_sizer, 0, 0, 0)
        self.SetSizer(self.topsizer)
        self.topsizer.Fit(self)
        self.Layout()


    def add_referencefile(self, event):
        # New reference peak list
        reference = openfile('Select new referece peak list', '', '', 'all files (*.*)|*.*', self)
        if reference:
            self.reference_peaklist.SetValue(reference)
        event.Skip()


    def calc(self, event):
        # Calculate

        # Experiment index
        if self.main.MainTab.GetSelection() < 0:
            page = 0

        # on start or results tab
        elif self.main.MainTab.GetSelection() > (self.main.MainTab.GetPageCount()-2):
            page = 0

        # experiment tab
        else:
            page = self.main.MainTab.GetSelection()-1

        # Check input
        self.check_arguments()

        # Read reference peak file
        ref_entries = []
        file = open(str(self.reference_peaklist.GetValue()), 'r')
        for line in file:
            entry = line.replace('\n', '').split()
            ref_entries.append(entry)
        file.close()

        # Read peaklist
        list_entries = []
        file = open(str(self.peaklist.GetValue()), 'r')
        for line in file:
            entry = line.replace('\n', '').split()
            list_entries.append(entry)
        file.close()

        # Calculate R2
        r2eff = []
        Tcpmg = float(self.main.CPMG_DELAY[page])

        # loop over entries of list
        for i in range(0, len(list_entries)):
            r2eff_tmp = None
            if len(list_entries[i]) > 2:
                if not str(list_entries[i][0]) == 'Assignment':
                    rel_int = float(list_entries[i][3])

                    # detect reference
                    ref_int = None
                    for j in range(0, len(ref_entries)):
                        if len(ref_entries[j]) > 2:
                            if str(list_entries[i][0]) == str(ref_entries[j][0]):
                                ref_int = float(ref_entries[j][3])

                    # Calculate R2eff
                    if ref_int:
                        r2eff_tmp = (1/Tcpmg)*math.log(ref_int/rel_int)

            # Add r2eff
            r2eff.append(r2eff_tmp)

        # Original references
        # detect reference data set
        ref_index = None
        for i in range(0, len(self.main.CPMGFREQ[page])):
            if float(self.main.CPMGFREQ[page][i]) == 0.0:
                ref_index = i

        # read original intensities of main session
        orig_ref_int = []   # [Residue, intensity]

        if not ref_index == None:
                if not r2eff == []:
                    for i in range(0, self.main.RESNO):
                        tmp_intensity = str(self.main.data_grid[page].GetCellValue(i, ref_index+1))
                        if not tmp_intensity == '':
                            tmp_intensity = float(tmp_intensity)
                            orig_ref_int.append([i+1, tmp_intensity])
        else:
                error_popup('No reference peak list found in main session!')
                return

        # Back calculate intensity

        # create new peak file
        file = open(str(self.save_file.GetValue()), 'w')

        # loop over selected peak list
        for i in range(0, len(list_entries)):
                new_intensity = None

                if r2eff[i]:
                    residue_information = list_entries[i][0]

                    # index for residue number
                    end_of_residue = 0
                    start_of_residue = 0

                    #find start of residue number
                    for j in range(0, len(residue_information)):
                        isinteger = residue_information[j].isdigit()
                        if isinteger == True:
                            start_of_residue = j
                            break

                    #find end of residue number
                    for j in range((start_of_residue + 1), len(residue_information)):
                        isinteger2 = residue_information[j].isdigit()
                        if isinteger2 == False:
                            end_of_residue = j
                            break

                    # cut out residue number integer
                    resnum = residue_information[start_of_residue: end_of_residue]

                    # detect reference intensity
                    reference_intensity = None
                    for k in range(0, len(orig_ref_int)):
                        if int(orig_ref_int[k][0]) == int(resnum):
                            reference_intensity = float(orig_ref_int[k][1])
                            break

                    # detect r2eff
                    r2eff_tmp = r2eff[i]

                    # calculate intensity
                    if reference_intensity:
                        new_intensity = reference_intensity / (math.exp(Tcpmg*r2eff_tmp))


                # write entry
                # spaceing
                s = '    '
                if r2eff[i]:
                    entrystring = s+list_entries[i][0]+s+list_entries[i][1]+s+list_entries[i][2]+s+str(int(new_intensity))+'\n'
                    file.write(entrystring)


        # Close the file
        file.close()

        # feedback
        message('Successfully converted peak list!', self)


    def check_arguments(self):
        """check arguments."""
        if str(self.reference_peaklist.GetValue()) == '':
            error_popup('No reference peak list selected!', self)
            return
        if str(self.peaklist.GetValue()) == '':
            error_popup('No peak list to convert selected!', self)
            return
        if str(self.save_file.GetValue()) == '':
            error_popup('No file to save new peak list selected!', self)
            return


    def close(self, event):
        # close tool
        self.Destroy()
        event.Skip()


    def select_save(self, event):
        # save file
        save_file = savefile('Select file to save', '', '', 'all files (*.*)|*.*', self)
        if save_file:
            self.save_file.SetValue(save_file)
        event.Skip()


    def load_list(self, event):
        # Select peak list to convert
        peaklist = openfile('Select peak list to convert', '', '', 'all files (*.*)|*.*', self)
        if peaklist:
            self.peaklist.SetValue(peaklist)
            save_file_tmp = peaklist
            save_file_tmp = save_file_tmp.replace('.', '_backcalc.')
            self.save_file.SetValue(save_file_tmp)
        event.Skip()
