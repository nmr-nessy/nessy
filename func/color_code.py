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


# script to create pymol macros

# Python modues
from os import mkdir, sep, makedirs
from scipy import log10, sqrt
from subprocess import PIPE, Popen
import wx
import wx.lib.agw.cubecolourdialog as CCD

# NESSY modules
from conf.filedialog import openfile, savefile
from conf.message import error_popup, message
from conf.path import NESSY_PIC, IMPORT_DATA_SIDE_PIC
from conf.NESSY_grid import NESSY_grid



class Color_code_from_file(wx.Dialog):
    """Class to produce custom color coded images."""
    def __init__(self, pdb_file, *args, **kwds):
        # connect variable
        self.pdb_filename = pdb_file

        # Create color variables
        self.start_color = [255, 255, 0]
        self.end_color = [255, 0, 0]
        self.tmp_end_color = wx.ColourData().SetColour((255, 0, 0))
        self.tmp_start_color = wx.ColourData().SetColour((255, 255, 0))

        # Build frame
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        # Background color
        self.SetBackgroundColour(wx.NullColour)

        # Build the frame
        self.build()


    def build(self):
        # Mainframe
        mainsizer = wx.BoxSizer(wx.HORIZONTAL)

        # The Image
        self.bitma = wx.StaticBitmap(self, -1, wx.Bitmap(IMPORT_DATA_SIDE_PIC, wx.BITMAP_TYPE_ANY))
        mainsizer.Add(self.bitma, 0, wx.ALL, 5)

        # Right sizer
        rightsizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        self.header = wx.StaticText(self, -1, "Create custom color- and width-coded sructures")
        self.header.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        rightsizer.Add(self.header, 0, wx.ALL, 5)

        # PDB file
        sizer_pdb = wx.BoxSizer(wx.HORIZONTAL)
        self.label_pdb = wx.StaticText(self, -1, "Select PDB File:")
        self.label_pdb.SetMinSize((150, 17))
        sizer_pdb.Add(self.label_pdb, 0, wx.LEFT|wx.TOP|wx.BOTTOM, 5)
        self.PDB_file = wx.TextCtrl(self, -1, self.pdb_filename)
        self.PDB_file.SetMinSize((200, 20))
        sizer_pdb.Add(self.PDB_file, 0, wx.TOP|wx.BOTTOM, 5)
        self.add_PDB = wx.Button(self, -1, "+")
        self.Bind(wx.EVT_BUTTON, self.load_pdb, self.add_PDB)
        self.add_PDB.SetMinSize((25, 23))
        sizer_pdb.Add(self.add_PDB, 0, wx.ALL, 5)
        rightsizer.Add(sizer_pdb, 0, wx.EXPAND, 0)

        # Output file
        sizer_file = wx.BoxSizer(wx.HORIZONTAL)
        self.label_file = wx.StaticText(self, -1, "Select Output File:")
        self.label_file.SetMinSize((150, 17))
        sizer_file.Add(self.label_file, 0, wx.LEFT, 5)
        self.savefile = wx.TextCtrl(self, -1, "")
        self.savefile.SetMinSize((200, 20))
        sizer_file.Add(self.savefile, 0, 0, 5)
        self.add_savefile = wx.Button(self, -1, "+")
        self.Bind(wx.EVT_BUTTON, self.savefile_add, self.add_savefile)
        self.add_savefile.SetMinSize((25, 23))
        sizer_file.Add(self.add_savefile, 0, wx.LEFT|wx.RIGHT, 5)
        rightsizer.Add(sizer_file, 0, wx.EXPAND, 0)

        # Data
        sizer_data = wx.BoxSizer(wx.HORIZONTAL)
        self.data_grid = NESSY_grid(self, -1, size=(1, 1))
        self.data_grid.CreateGrid(700, 2)
        self.data_grid.SetColLabelValue(0, "Residue")
        self.data_grid.SetColLabelValue(1, "Value")
        self.data_grid.SetMinSize((270, 300))
        sizer_data.Add(self.data_grid, 1, wx.EXPAND|wx.ALL, 5)

        sizer_databutton = wx.BoxSizer(wx.VERTICAL)
        self.button_load_file = wx.Button(self, -1, "Load Text File")
        self.Bind(wx.EVT_BUTTON, self.load_file, self.button_load_file)
        self.button_load_file.SetToolTipString("Text file containing Residue Number and Value.")
        self.button_load_file.SetMinSize((100, 25))
        sizer_databutton.Add(self.button_load_file, 0, wx.ALL, 5)
        self.button_clear = wx.Button(self, -1, "Clear")
        self.button_clear.SetMinSize((100, 25))
        self.Bind(wx.EVT_BUTTON, self.clear_grid, self.button_clear)
        sizer_databutton.Add(self.button_clear, -1, wx.ALL, 5)

        # Increasing/Decreasing
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mode_box = wx.RadioBox(self, -1, "Mode of coding", choices=["Ascending", "Descending"], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        self.mode_box.SetSelection(0)
        sizer_databutton.Add(self.mode_box, 0, wx.ALL, 5)
        self.multiply_box = wx.RadioBox(self, -1, "Multiplication", choices=["Exponential", "Linear", "Logarithmic"], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        self.multiply_box.SetSelection(0)
        sizer_databutton.Add(self.multiply_box, 0, wx.ALL, 5)

        sizer_data.Add(sizer_databutton, 0, 0, 0)
        rightsizer.Add(sizer_data, 0, wx.EXPAND, 0)

        # Choose Color
        self.static_line_1 = wx.StaticLine(self, -1)
        rightsizer.Add(self.static_line_1, 0, wx.EXPAND|wx.ALL, 5)
        sizer_color = wx.BoxSizer(wx.HORIZONTAL)
        self.color1 = wx.Button(self, -1, "Color #1")
        self.Bind(wx.EVT_BUTTON, self.choose_start_color, self.color1)
        sizer_color.Add(self.color1, 0, 0, 0)
        self.grad = wx.Panel(self, -1, size = (-1, -1), style = wx.BORDER_SUNKEN)
        self.grad.Bind(wx.EVT_PAINT, self.paint)
        self.grad.SetBackgroundColour('White')
        sizer_color.Add(self.grad, -1, wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        self.color2 = wx.Button(self, -1, "Color #2")
        self.Bind(wx.EVT_BUTTON, self.choose_end_color, self.color2)
        sizer_color.Add(self.color2, 0, 0, 0)
        rightsizer.Add(sizer_color, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 5)
        self.static_line_2 = wx.StaticLine(self, -1)
        rightsizer.Add(self.static_line_2, 0, wx.EXPAND|wx.ALL, 5)

        # Buttons
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        self.button_exe = wx.Button(self, -1, "Create")
        self.button_close = wx.Button(self, -1, "Close")
        self.Bind(wx.EVT_BUTTON, self.execute, self.button_exe)
        self.Bind(wx.EVT_BUTTON, self.close, self.button_close)
        sizer_2.Add(self.button_exe, 0, wx.ALL, 5)
        sizer_2.Add(self.button_close, 0, wx.ALL, 5)
        rightsizer.Add(sizer_2, 0, 0, 0)

        # Pack window
        mainsizer.Add(rightsizer, 0, wx.EXPAND, 0)
        self.SetSizer(mainsizer)
        mainsizer.Fit(self)
        self.Layout()
        self.Centre()


    def choose_end_color(self, event):
        # Create the dialog
        color = wx.ColourDialog(self, self.tmp_end_color)
        color.GetColourData().SetChooseFull(True)

        # Save color
        if color.ShowModal() == wx.ID_OK:
            self.end_color = color.GetColourData().GetColour().Get()
            self.tmp_end_color = color.GetColourData()
            self.paint(1)

        # Close dialog
        color.Destroy()


    def choose_start_color(self, event):
        # Create the dialog
        color = wx.ColourDialog(self, self.tmp_start_color)
        color.GetColourData().SetChooseFull(True)

        # Save color
        if color.ShowModal() == wx.ID_OK:
            self.start_color = color.GetColourData().GetColour().Get()
            self.tmp_start_color = color.GetColourData()
            self.paint(1)
 
        # Close dialog
        color.Destroy()


    def clear_grid(self, event):
        for i in range(700):
            self.data_grid.SetCellValue(i, 0, '')
            self.data_grid.SetCellValue(i, 1, '')


    def close(self, event):
        self.Destroy()


    def execute(self, event):
        # read residue and values
        residue = []
        value = []

        # Read values
        try:
            for i in range(700):
                if not str(self.data_grid.GetCellValue(i, 0)) == '' and not str(self.data_grid.GetCellValue(i, 1)) == '':
                    residue.append(str(self.data_grid.GetCellValue(i, 0)))
                    value.append(float(self.data_grid.GetCellValue(i, 1)))
        except:
            error_popup('At least one of the entered values are incorrect!', self)
            return

        # Detect minimum and maximum
        min = value[0]
        for i in range(1, len(value)):
            if value[i] < min:
                min = value[i]

        max = value[0]
        for i in range(1, len(value)):
            if value[i] > max:
                max = value[i]

        # detect negative values
        if min < 0:
            # shift data
            value = [i - min for i in value]
            max = max - min
            min = 0

        # lower lowest value to 0
        else:
            # shift data
            value = [i - min for i in value]
            max = max - min
            min = 0

        # Calculate percentage
        value = [ i / max for i in value]

        # Create the macros
        filename = str(self.savefile.GetValue())
        if filename == '':
            error_popup('No outputfile selected!', self)
            return

        # add corect extension
        if not '.pml' in filename:
            filename = filename + '.pml'

        # Write the file
        file = open(filename, 'w')
        file1 = open(filename.replace('.pml', '.sphere.pml'), 'w')      # The sphere representation

        # Load structure file.
        if not str(self.PDB_file.GetValue()) == '':
            file.write('load '+str(self.PDB_file.GetValue())+'\n')
            file1.write('load '+str(self.PDB_file.GetValue())+'\n')

        # Hide everything
        file.write('hide all\n')
        file1.write('hide all\n')

        # set white background
        file.write('bg_color white\n')
        file1.write('bg_color white\n')

        # colour molecule in gray
        file.write('color gray90\n')
        file1.write('color gray90\n')

        # show backbone
        file.write('show sticks, name C+N+CA\nset stick_quality, 10\n')
        file1.write('show spheres, name N\nset sphere_transparency, 0.2\n')

        # Write color coding
        e = 2.71828

        # Color difference between min and max
        r_diff = self.end_color[0] - self.start_color[0]
        g_diff = self.end_color[1] - self.start_color[1]
        b_diff = self.end_color[2] - self.start_color[2]

        # ascending
        if self.mode_box.GetSelection() == 0:
            # Set thickness to 0.2
            file.write('set_bond stick_radius, 0.2, all\n')
            file1.write('show cartoon\nalter all, vdw=0\nrebuild\n')

            for i in range(0, len(value)):
                # exponential
                if self.multiply_box.GetSelection() == 0:
                    #thickness
                    file.write('set_bond stick_radius, '+str((0.2 + value[i])**2)+', resi '+str(residue[i])+'\n')
                    file1.write('alter resi '+str(residue[i])+', vdw='+str((1.2 + value[i])**2)+'\nrebuild\n')

                    # color
                    r = str((self.start_color[0] + value[i]**2 * r_diff))
                    g = str((self.start_color[1] + value[i]**2 * g_diff))
                    b = str((self.start_color[2] + value[i]**2 * b_diff))

                    # Write
                    file.write('set_color resicolor'+str(residue[i])+', ['+r+', '+g+', '+b+']\n')
                    file.write('color resicolor'+str(residue[i])+', resi '+str(residue[i])+'\n')
                    file1.write('set_color resicolor'+str(residue[i])+', ['+r+', '+g+', '+b+']\n')
                    file1.write('color resicolor'+str(residue[i])+', resi '+str(residue[i])+'\n')

                # linear
                elif self.multiply_box.GetSelection() == 1:
                    #thickness
                    file.write('set_bond stick_radius, '+str(0.2 + value[i])+', resi '+str(residue[i])+'\n')
                    file1.write('alter resi '+str(residue[i])+', vdw='+str((1.2 + value[i]))+'\nrebuild\n')

                    # color
                    r = str((self.start_color[0] + value[i] * r_diff))
                    g = str((self.start_color[1] + value[i] * g_diff))
                    b = str((self.start_color[2] + value[i] * b_diff))

                    # Write
                    file.write('set_color resicolor'+str(residue[i])+', ['+r+', '+g+', '+b+']\n')
                    file.write('color resicolor'+str(residue[i])+', resi '+str(residue[i])+'\n')
                    file1.write('set_color resicolor'+str(residue[i])+', ['+r+', '+g+', '+b+']\n')
                    file1.write('color resicolor'+str(residue[i])+', resi '+str(residue[i])+'\n')

                # logarithmic
                else:
                    #thickness
                    file.write('set_bond stick_radius, '+str(log10(10 ** (0.2 + value[i])))+', resi '+str(residue[i])+'\n')
                    file1.write('alter resi '+str(residue[i])+', vdw='+str(log10(10 ** (1.2 + value[i])))+'\nrebuild\n')

                    # color
                    r = str((self.start_color[0] + log10(10**value[i]) * r_diff))
                    g = str((self.start_color[1] + log10(10**value[i]) * g_diff))
                    b = str((self.start_color[2] + log10(10**value[i]) * b_diff))

                    # Write
                    file.write('set_color resicolor'+str(residue[i])+', ['+r+', '+g+', '+b+']\n')
                    file.write('color resicolor'+str(residue[i])+', resi '+str(residue[i])+'\n')
                    file1.write('set_color resicolor'+str(residue[i])+', ['+r+', '+g+', '+b+']\n')
                    file1.write('color resicolor'+str(residue[i])+', resi '+str(residue[i])+'\n')

        # descending
        else:
            # Set thickness to 1
            file.write('set_bond stick_radius, 0.2, all\n')

            for i in range(0, len(value)):
                # exponential
                if self.multiply_box.GetSelection() == 0:
                    #thickness
                    file.write('set_bond stick_radius, '+str((1 - value[i])**2)+', resi '+str(residue[i])+'\n')
                    file1.write('alter resi '+str(residue[i])+', vdw='+str((1 - value[i])**2)+'\nrebuild\n')

                    # color
                    r = str((self.end_color[0] - (value[i])**2 * r_diff))
                    g = str((self.end_color[1] - (value[i])**2 * g_diff))
                    b = str((self.end_color[2] - (value[i])**2 * b_diff))

                    # Write
                    file.write('set_color resicolor'+str(residue[i])+', ['+r+', '+g+', '+b+']\n')
                    file.write('color resicolor'+str(residue[i])+', resi '+str(residue[i])+'\n')
                    file1.write('set_color resicolor'+str(residue[i])+', ['+r+', '+g+', '+b+']\n')
                    file1.write('color resicolor'+str(residue[i])+', resi '+str(residue[i])+'\n')

                # linear
                elif self.multiply_box.GetSelection() == 1:
                    #thickness
                    file.write('set_bond stick_radius, '+str(1 - value[i])+', resi '+str(residue[i])+'\n')
                    file1.write('alter resi '+str(residue[i])+', vdw='+str((1 - value[i]))+'\nrebuild\n')

                    # color
                    r = str((self.end_color[0] - (value[i]) * r_diff))
                    g = str((self.end_color[1] - (value[i]) * g_diff))
                    b = str((self.end_color[2] - (value[i]) * b_diff))

                    # Write
                    file.write('set_color resicolor'+str(residue[i])+', ['+r+', '+g+', '+b+']\n')
                    file.write('color resicolor'+str(residue[i])+', resi '+str(residue[i])+'\n')
                    file1.write('set_color resicolor'+str(residue[i])+', ['+r+', '+g+', '+b+']\n')
                    file1.write('color resicolor'+str(residue[i])+', resi '+str(residue[i])+'\n')

                # logarithmic
                else:
                    #thickness
                    file.write('set_bond stick_radius, '+str(log10(10 ** (1 - value[i])))+', resi '+str(residue[i])+'\n')
                    file1.write('alter resi '+str(residue[i])+', vdw='+str(log10(10 ** (1 - value[i])))+'\nrebuild\n')

                    # color
                    r = str((self.end_color[0] - log10(10 ** value[i]) * r_diff))
                    g = str((self.end_color[1] - log10(10 ** value[i]) * g_diff))
                    b = str((self.end_color[2] - log10(10 ** value[i]) * b_diff))

                    # Write
                    file.write('set_color resicolor'+str(residue[i])+', ['+r+', '+g+', '+b+']\n')
                    file.write('color resicolor'+str(residue[i])+', resi '+str(residue[i])+'\n')
                    file1.write('set_color resicolor'+str(residue[i])+', ['+r+', '+g+', '+b+']\n')
                    file1.write('color resicolor'+str(residue[i])+', resi '+str(residue[i])+'\n')

        # raytrace structure
        file.write('ray\n')
        file1.write('rebuild\nray\n')

        # close file
        file.close()
        file1.close()

        # Message
        message('Successfully Created PyMol macros!', self)

        # open in Pymol, if installed
        try:
            # BAckbone model
            # Open Pymol
            pymol1 = Popen(['pymol', '-qpK -q -i -x'], stdin=PIPE).stdin

            # Execute macros
            pymol1.write('@' + filename + '\n')

            # Sphere model
            # Open Pymol
            pymol1 = Popen(['pymol', '-qpK -q -i -x'], stdin=PIPE).stdin

            # Execute macros
            pymol1.write('@' + filename.replace('.pml', '.sphere.pml') + '\n')

        except:
            a = 'no pymol installed.'


    def load_file(self, event):
        filename = openfile('Select text file to open.', str(self.PDB_file.GetValue()), '', 'All files (*.*)|*', self)

        if filename:
            # index
            index = 0

            # open file
            file = open(filename, 'r')

            # read lines
            for line in file:
                # Replace enter
                line = line.replace('\n', '')

                # Empty line
                if line == '':
                    continue

                # split line
                if ',' in line:
                    entries = line.split(',')
                elif ';' in line:
                    entries = line.split(';')
                if '\t' in line:
                    entries = line.split('\t')
                else:
                    entries = line.split()

                # No entries
                if len(entries) < 2:
                    continue
                if isinstance(entries, basestring):
                    continue

                # Import
                self.data_grid.SetCellValue(index, 0, str(entries[0]))
                self.data_grid.SetCellValue(index, 1, str(entries[1]))

                # increase index
                index = index + 1


    def load_pdb(self, event):
        filename = openfile('Select PDB file to open.', str(self.PDB_file.GetValue()), '', 'PDB files (*.pdb)|*.pdb|all files (*.*)|*', self)

        # Set the PDB file
        if filename:
            self.PDB_file.SetValue(filename)


    def paint(self, evt):
        # this is the wx drawing surface/canvas
        dc = wx.PaintDC(self.grad)
        dc.Clear()
        dc.GradientFillLinear((0, 0, self.grad.GetSize()[0], self.grad.GetSize()[1]), self.start_color, self.end_color)


    def savefile_add(self, event):
        filename = savefile('Select output file.', str(self.PDB_file.GetValue()), '', 'PyMol macros (*.pml)|*.pml|all files (*.*)|*', self)

        # Set the PDB file
        if filename:
            self.savefile.SetValue(filename)



class Model_code():
    """Class to create macro to color code the model on the structure"""
    def __init__(self, main, exp_index):
        self.main = main

        # File prefix
        self.prefix = 'Exp_'+str(exp_index+1)+'_'
        # Global fit
        if self.main.ISGLOBAL:
            self.prefix = 'Global_fit_'


        # craete folder
        folder = str(self.main.proj_folder.GetValue())+sep+'pymol_macros'
        try:
            mkdir(folder)
        except:
            a = 12

        # create file
        filename = folder+sep+self.prefix+'model_selection.pml'
        file = open(filename, 'w')

        # create entries
        # Load structure file.
        if not str(self.main.pdb_file.GetValue()) == '':
            file.write('load '+str(self.main.pdb_file.GetValue())+'\n')

        # Hide everything
        file.write('hide all\n')

        # set white background
        file.write('bg_color white\n')

        # colour molecule in gray
        file.write('color black\n')

        # show cartoon
        file.write('show cartoon\n')

        # colour code residues
        for i in range (0, len(self.main.MODEL_SELECTION)):
            if self.main.MODEL_SELECTION[i]['model'] == 1:
                file.write('color gray90, resi '+str(self.main.MODEL_SELECTION[i]['residue'])+'\n')
            if self.main.MODEL_SELECTION[i]['model'] == 2:
                file.write('color red, resi '+str(self.main.MODEL_SELECTION[i]['residue'])+'\n')
            if self.main.MODEL_SELECTION[i]['model'] == 3:
                file.write('color orange, resi '+str(self.main.MODEL_SELECTION[i]['residue'])+'\n')
            if self.main.MODEL_SELECTION[i]['model'] == 4:
                file.write('color cyan, resi '+str(self.main.MODEL_SELECTION[i]['residue'])+'\n')
            if self.main.MODEL_SELECTION[i]['model'] == 5:
                file.write('color marine, resi '+str(self.main.MODEL_SELECTION[i]['residue'])+'\n')
            if self.main.MODEL_SELECTION[i]['model'] == 6:
                file.write('color green, resi '+str(self.main.MODEL_SELECTION[i]['residue'])+'\n')

        # raytrace structure
        file.write('ray\n')

        # close file
        file.close()

        # Add file to results tree
        self.main.tree_results.AppendItem (self.main.structures, filename, 0)
        self.main.COLOR_PDB.append(filename)



class Kex_code():
    """Class to generate kex color coded pymaol macros"""

    """Class to create macro to color code the model on the structure"""
    def __init__(self, main, exp_index):
        self.main = main
        self.coding = []    # [Residue, color, thikness]

        # File prefix
        self.prefix = 'Exp_'+str(exp_index+1)+'_'

        # Global fit
        if self.main.ISGLOBAL:
            self.prefix = 'Global_fit_'

        # craete folder
        folder = str(self.main.proj_folder.GetValue())+sep+'pymol_macros'
        try:
            mkdir(folder)
        except:
            a = 12

        # create file
        filename = folder+sep+self.prefix+'kex.pml'
        file = open(filename, 'w')

        # create entries
        # Load structure file.
        if not str(self.main.pdb_file.GetValue()) == '':
            file.write('load '+str(self.main.pdb_file.GetValue())+'\n')

        # Hide everything
        file.write('hide all\n')

        # set white background
        file.write('bg_color white\n')

        # colour molecule in gray
        file.write('color gray90\n')

        # show backbone
        file.write('show sticks, name C+N+CA\nset stick_quality, 10\n')

        # calculate coloru coding
        self.color_coding()

        # color coded entries
        for i in range(0, len(self.coding)):
            #thickness
            file.write('set_bond stick_radius, '+str(self.coding[i][2])+', resi '+str(self.coding[i][0])+'\n')

            # color
            file.write('set_color resicolor'+str(self.coding[i][0])+', '+str(self.coding[i][1])+'\n')
            file.write('color resicolor'+str(self.coding[i][0])+', resi '+str(self.coding[i][0])+'\n')

        # ray trace structure
        file.write('ray\n')

        # close file
        file.close()

        # Add file to results tree
        self.main.tree_results.AppendItem (self.main.structures, filename, 0)
        self.main.COLOR_PDB.append(filename)


    def color_coding(self):
        """Function to convert kex values into colors"""

        # detect max kex
        max = 0
        for i in range(0, len(self.main.MODEL_SELECTION)):
            try:
                if self.main.MODEL_SELECTION[i]['Rex']:
                    if self.main.MODEL_SELECTION[i]['Rex'] > max:
                        max = self.main.MODEL_SELECTION[i]['Rex']
            except:
                continue

        # create coding
        for i in range(0, len(self.main.MODEL_SELECTION)):
            try:
                if self.main.MODEL_SELECTION[i]['kex']:
                    width = (self.main.MODEL_SELECTION[i]['kex'] / max) + 0.1
                    if width > 1:
                        width = 1
                    color = [1, 1 - width, 0] # [red, green, blue] --> higher kex, from yellow to red
                    self.coding.append([self.main.MODEL_SELECTION[i]['residue'], color, width])
            except:
                continue


class Rex_code():
    """Class to generate kex color coded pymaol macros"""

    """Class to create macro to color code the model on the structure"""
    def __init__(self, main, exp_index):
        self.main = main
        self.coding = []    # [Residue, color, thikness]

        # File prefix
        self.prefix = 'Exp_'+str(exp_index+1)+'_'
        # Global fit
        if self.main.ISGLOBAL:
            self.prefix = 'Global_fit_'

        # craete folder
        folder = str(self.main.proj_folder.GetValue())+sep+'pymol_macros'
        try:
            mkdir(folder)
        except:
            a = 12

        # create file
        filename = folder+sep+self.prefix+'Rex.pml'
        file = open(filename, 'w')

        # create entries
        # Load structure file.
        if not str(self.main.pdb_file.GetValue()) == '':
            file.write('load '+str(self.main.pdb_file.GetValue())+'\n')

        # Hide everything
        file.write('hide all\n')

        # set white background
        file.write('bg_color white\n')

        # colour molecule in gray
        file.write('color gray90\n')

        # show backbone
        file.write('show sticks, name C+N+CA\nset stick_quality, 10\n')

        # calculate coloru coding
        self.color_coding()

        # color coded entries
        for i in range(0, len(self.coding)):
            #thickness
            file.write('set_bond stick_radius, '+str(self.coding[i][2])+', resi '+str(self.coding[i][0])+'\n')

            # color
            file.write('set_color resicolor'+str(self.coding[i][0])+', '+str(self.coding[i][1])+'\n')
            file.write('color resicolor'+str(self.coding[i][0])+', resi '+str(self.coding[i][0])+'\n')

        # ray trace structure
        file.write('ray\n')

        # close file
        file.close()

        # Add file to results tree
        self.main.tree_results.AppendItem (self.main.structures, filename, 0)
        self.main.COLOR_PDB.append(filename)


    def color_coding(self):
        """Function to convert kex values into colors"""

        # detect max kex
        max = 0
        for i in range(0, len(self.main.MODEL_SELECTION)):
            try:
                if self.main.MODEL_SELECTION[i]['Rx']:
                    if self.main.MODEL_SELECTION[i]['Rex'] > max:
                        max = self.main.MODEL_SELECTION[i]['Rex']
            except:
                continue

        # create coding
        for i in range(0, len(self.main.MODEL_SELECTION)):
            try:
                if self.main.MODEL_SELECTION[i]['Rex']:
                    width = (self.main.MODEL_SELECTION[i]['Rex'] / max) + 0.1
                    if width > 1:
                        width = 1
                    color = [1, 1 - width, 0] # [red, green, blue] --> higher kex, from yellow to red
                    self.coding.append([self.main.MODEL_SELECTION[i]['residue'], color, width])
            except:
                continue


def color_code(residue, value, output_file, directory, pdb_file=None):
    """Function to create color coded pymol macros.

    residue:        list of residue numbers (int)
    value:          list value (float)
    output_file:    name of output file (str)
    directory:      output directory (str)
    pdb_file:       PDB file (str, None if not specified)
    """

    # detect maximum and minimum
    max = 0
    min = 0
    for i in range(len(value)):
        # maximum
        if max < value[i]:
            max = value[i]
        # minimum
        if min > value[i]:
            min = value[i]

    # calculate relative value
    value = [i / max for i in value]

    # Square root values
    value = [sqrt(i) for i in value]

    # normalize to 80% (allow minimum width of 0.2
    value = [0.8 * i for i in value]

    # Create directory
    try:
        makedirs(directory)
    except:
        a = 'dir exists'

    # create file
    file = open(directory+sep+output_file, 'w')

    # Load structure file.
    if pdb_file:
        file.write('load '+pdb_file+'\n')

    # Hide everything
    file.write('hide all\n')

    # set white background
    file.write('bg_color white\n')

    # colour molecule in gray
    file.write('color gray90\n')

    # show backbone
    file.write('show sticks, name C+N+CA\nset stick_quality, 10\n')

    # set general width to 0.2
    file.write('set_bond stick_radius, 0.2, all\n')

    # write codings
    for i in range(len(residue)):
        #thickness
        file.write('set_bond stick_radius, '+str(0.2 + value[i])+', resi '+str(residue[i])+'\n')

        # color
        file.write('set_color resicolor'+str(residue[i])+', [1, '+str(1 - value[i])+', 0]\n')
        file.write('color resicolor'+str(residue[i])+', resi '+str(residue[i])+'\n')

    # ray trace structure
    file.write('ray\n')

    # close file
    file.close()


def color_code_model(residue, value, output_file, directory, pdb_file=None):
    """Function to create color coded pymol macros.

    residue:        list of residue numbers (int)
    value:          list selected models (int)
    output_file:    name of output file (str)
    directory:      output directory (str)
    pdb_file:       PDB file (str, None if not specified)
    """

    # craete folder
    try:
        makedirs(directory)
    except:
        a = 12

    # create file
    filename = directory+sep+output_file
    file = open(filename, 'w')

    # create entries
    # Load structure file.
    if pdb_file:
        file.write('load '+pdb_file+'\n')

    # Hide everything
    file.write('hide all\n')

    # set white background
    file.write('bg_color white\n')

    # colour molecule in gray
    file.write('color black\n')

    # show cartoon
    file.write('show cartoon\n')

    # colour code residues
    for i in range (0, len(residue)):
        if value[i] == 1:
            file.write('color gray90, resi '+str(residue[i])+'\n')
        if value[i] == 2:
            file.write('color red, resi '+str(residue[i])+'\n')
        if value[i] == 3:
            file.write('color orange, resi '+str(residue[i])+'\n')
        if value[i] == 4:
            file.write('color cyan, resi '+str(residue[i])+'\n')
        if value[i] == 5:
            file.write('color marine, resi '+str(residue[i])+'\n')
        if value[i] == 6:
            file.write('color green, resi '+str(residue[i])+'\n')
        if value[i] == 7:
            file.write('color hotpink, resi '+str(residue[i])+'\n')

    # raytrace structure
    file.write('ray\n')

    # close file
    file.close()
