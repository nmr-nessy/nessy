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
import pylab
from scipy import sqrt
from os import sep
import wx

# NESSY modules
from conf.filedialog import openfile, savefile
from conf.message import error_popup, message
from conf.path import NESSY_PIC, PLOT2D_SIDE_PIC, SYNTHETIC_PIC
from conf.NESSY_grid import NESSY_grid




class DD_Plot_draw(wx.Frame):
    """Class to create 3d plots."""
    def __init__(self, gui, *args, **kwds):
        self.test = [[1, 2], [2, 2], [1, 1]]
        # link GUI
        self.main = gui

        # Build frame
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX
        wx.Frame.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.Centre()

        # Build dialog
        self.build()


    def build(self):
        # main sizer
        mainsizer = wx.BoxSizer(wx.VERTICAL)

        # Subsizer
        subsizer = wx.BoxSizer(wx.HORIZONTAL)

        # Image
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(PLOT2D_SIDE_PIC, wx.BITMAP_TYPE_ANY))
        subsizer.Add(self.bitmap, 0, wx.ALL, 5)

        # right sizer
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        self.label_title = wx.StaticText(self, -1, "2D Plot Generator")
        self.label_title.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        right_sizer.Add(self.label_title, 0, wx.ALL, 5)

        # Table title
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_file = wx.StaticText(self, -1, "NESSY - .csv File to plot:")
        title_file.SetMinSize((280, 17))
        title_sizer.Add(title_file, 0, wx.LEFT|wx.RIGHT, 5)

        title_label = wx.StaticText(self, -1, "Label:")
        title_label.SetMinSize((160, 17))
        title_sizer.Add(title_label, 0, wx.LEFT|wx.RIGHT, 5)

        title_format = wx.StaticText(self, -1, "Plot style:")
        title_format.SetMinSize((110, 17))
        title_sizer.Add(title_format, 0, wx.LEFT|wx.RIGHT, 5)

        title_color = wx.StaticText(self, -1, "Plot color:")
        title_color.SetMinSize((110, 17))
        title_sizer.Add(title_color, 0, wx.LEFT|wx.RIGHT, 5)

        title_column = wx.StaticText(self, -1, "X / Y / Error column:")
        title_column.SetMinSize((150, 17))
        title_sizer.Add(title_column, 0, wx.LEFT|wx.RIGHT, 5)

        right_sizer.Add(title_sizer, 0, 0, 0)


        # Data
        self.data = []
        self.x_col = []
        self.y_col = []
        self.err_col = []
        self.buttons = []
        self.label = []
        self.style = []
        self.color = []
        self.edit = []
        self.dataset = []
        for i in range(0, 10):
            # Sizer
            sizer_data1 = wx.BoxSizer(wx.HORIZONTAL)

            # Text box
            self.data.append(wx.TextCtrl(self, -1, ""))
            self.data[i].SetMinSize((180, 25))
            self.data[i].SetToolTipString("Select .csv generated by NESSY to plot.")
            sizer_data1.Add(self.data[i], 0, wx.LEFT, 5)

            # Add button
            self.buttons.append(wx.Button(self, -1, "+"))
            self.buttons[i].SetMinSize((23, 25))
            self.Bind(wx.EVT_BUTTON, lambda evt, datano=i: self.add_data(evt, datano), self.buttons[i])
            sizer_data1.Add(self.buttons[i], 0, wx.LEFT, 5)

            # Add edit button
            self.edit.append(wx.Button(self, -1, "Edit"))
            self.edit[i].SetMinSize((60, 25))
            self.Bind(wx.EVT_BUTTON, lambda evt, datano=i: self.edit_data(evt, datano), self.edit[i])
            sizer_data1.Add(self.edit[i], 0, wx.RIGHT, 5)

            # append dataset container
            self.dataset.append([[], [], []])   # x, y and error values

            # Label box
            self.label.append(wx.TextCtrl(self, -1, ""))
            self.label[i].SetMinSize((150, 25))
            sizer_data1.Add(self.label[i], 0, wx.LEFT|wx.RIGHT, 15)

            # Plot style
            self.style.append(wx.ComboBox(self, -1, choices=["Scatter plot + error", "Scatter plot", "Bar plot", "Bar plot + error", "Line plot", "Landscape mode"], style=wx.CB_DROPDOWN | wx.CB_READONLY))
            self.style[i].SetMinSize((100, 25))
            self.style[i].SetSelection(0)
            # Line plot for regression
            if i == 1:
                self.style[i].SetSelection(4)
            sizer_data1.Add(self.style[i], 0, wx.LEFT, 5)

            # Plot color
            self.color.append(wx.ComboBox(self, -1, choices=['BLACK', 'BLUE', 'RED', 'GREEN', 'VIOLET', 'YELLOW', 'CYAN', 'MAGENTA', 'ORANGE', 'PINK', 'PURPLE', 'GRAY', 'WHITE'], style=wx.CB_DROPDOWN | wx.CB_READONLY))
            self.color[i].SetMinSize((100, 25))
            self.color[i].SetSelection(i)
            sizer_data1.Add(self.color[i], 0, wx.LEFT, 20)

            # X column
            self.x_col.append(wx.TextCtrl(self, -1, '1'))
            self.x_col[i].SetMinSize((50, 25))
            sizer_data1.Add(self.x_col[i], 0, wx.LEFT, 20)

            # Y column
            self.y_col.append(wx.TextCtrl(self, -1, '2'))
            self.y_col[i].SetMinSize((50, 25))
            sizer_data1.Add(self.y_col[i], 0, wx.LEFT, 5)

            # Error column
            self.err_col.append(wx.TextCtrl(self, -1, '3'))
            self.err_col[i].SetMinSize((50, 25))
            sizer_data1.Add(self.err_col[i], 0, wx.LEFT|wx.RIGHT, 5)

            # add entry
            right_sizer.Add(sizer_data1, 0, 0, 0)

        # static line
        self.static_line_1 = wx.StaticLine(self, -1)
        right_sizer.Add(self.static_line_1, 0, wx.ALL, 5)

        # x label
        sizer_xlabel = wx.BoxSizer(wx.HORIZONTAL)
        self.label_xlabel = wx.StaticText(self, -1, "Label of x-axis (in 2D plot):")
        self.label_xlabel.SetMinSize((230, 17))
        sizer_xlabel.Add(self.label_xlabel, 0, wx.LEFT|wx.RIGHT, 5)

        self.xlabel = wx.TextCtrl(self, -1, "v(CPMG) [Hz]")
        self.xlabel.SetMinSize((230, 20))
        sizer_xlabel.Add(self.xlabel, 0, 0, 5)

        self.hint = wx.StaticText(self, -1, "(For Greek symbols, write: '$\{Symbol}$'. Eg. for Delta, add '$\Delta$'.)")
        self.hint.SetFont(wx.Font(8, wx.DEFAULT, wx.ITALIC, wx.NORMAL, 0, ""))
        sizer_xlabel.Add(self.hint, 0, wx.LEFT|wx.ALIGN_BOTTOM, 5)

        right_sizer.Add(sizer_xlabel, 0, 0, 0)

        # y label
        sizer_ylabel = wx.BoxSizer(wx.HORIZONTAL)
        self.label_ylabel = wx.StaticText(self, -1, "Label of y-axis (in 2D plot):")
        self.label_ylabel.SetMinSize((230, 17))
        sizer_ylabel.Add(self.label_ylabel, 0, wx.LEFT|wx.RIGHT, 5)

        self.ylabel = wx.TextCtrl(self, -1, "R2eff [1/s]")
        self.ylabel.SetMinSize((230, 20))
        sizer_ylabel.Add(self.ylabel, 0, 0, 0)
        right_sizer.Add(sizer_ylabel, 0, 0, 0)

        # Another line
        self.static_line_2 = wx.StaticLine(self, -1)
        right_sizer.Add(self.static_line_2, 0, wx.ALL, 5)

        # x axis range
        sizer_xlim = wx.BoxSizer(wx.HORIZONTAL)
        self.label_xlim = wx.StaticText(self, -1, "Range of x-axis:")
        self.label_xlim.SetMinSize((230, 17))
        sizer_xlim.Add(self.label_xlim, 0, wx.LEFT|wx.RIGHT, 5)

        self.xlim = wx.SpinCtrl(self, -1, "0", min=-100000, max=100000)
        self.xlim.SetMinSize((80, 20))
        sizer_xlim.Add(self.xlim, 0, 0, 0)

        self.label_xlim1 = wx.StaticText(self, -1, "to")
        self.label_xlim1.SetMinSize((20, 17))
        sizer_xlim.Add(self.label_xlim1, 0, wx.LEFT|wx.RIGHT, 5)

        self.xlim_end = wx.SpinCtrl(self, -1, "1600", min=-100000, max=100000)
        self.xlim_end.SetMinSize((80, 20))
        sizer_xlim.Add(self.xlim_end, 0, 0, 0)

        right_sizer.Add(sizer_xlim, 0, 0, 0)

        # y axis range
        sizer_ylim = wx.BoxSizer(wx.HORIZONTAL)
        self.label_ylim = wx.StaticText(self, -1, "Range of y-axis:")
        self.label_ylim.SetMinSize((230, 17))
        sizer_ylim.Add(self.label_ylim, 0, wx.LEFT|wx.RIGHT, 5)

        self.ylim = wx.SpinCtrl(self, -1, "10", min=-100000, max=100000)
        self.ylim.SetMinSize((80, 20))
        sizer_ylim.Add(self.ylim, 0, 0, 0)

        self.label_ylim1 = wx.StaticText(self, -1, "to")
        self.label_ylim1.SetMinSize((20, 17))
        sizer_ylim.Add(self.label_ylim1, 0, wx.LEFT|wx.RIGHT, 5)

        self.ylim_end = wx.SpinCtrl(self, -1, "40", min=-100000, max=100000)
        self.ylim_end.SetMinSize((80, 20))
        sizer_ylim.Add(self.ylim_end, 0, 0, 0)

        right_sizer.Add(sizer_ylim, 0, 0, 0)

        # Another line
        self.static_line_3 = wx.StaticLine(self, -1)
        right_sizer.Add(self.static_line_3, 0, wx.ALL, 5)

        # Dimensions of plot
        sizer_dimension = wx.BoxSizer(wx.HORIZONTAL)
        self.label_dimension = wx.StaticText(self, -1, "Hight of Plot [%]:")
        self.label_dimension.SetMinSize((230, 17))
        sizer_dimension.Add(self.label_dimension, 0, wx.LEFT|wx.RIGHT, 5)

        self.dimension = wx.TextCtrl(self, -1, "100")
        self.dimension.SetMinSize((230, 20))
        sizer_dimension.Add(self.dimension, 0, 0, 0)

        right_sizer.Add(sizer_dimension, 0, 0, 0)

        # Size font Lable
        sizer_size_font = wx.BoxSizer(wx.HORIZONTAL)
        self.label_size_font = wx.StaticText(self, -1, "Size of Axis Label [points]:")
        self.label_size_font.SetMinSize((230, 17))
        sizer_size_font.Add(self.label_size_font, 0, wx.LEFT|wx.RIGHT, 5)

        self.size_font = wx.TextCtrl(self, -1, "19")
        self.size_font.SetMinSize((230, 20))
        sizer_size_font.Add(self.size_font, 0, 0, 0)

        right_sizer.Add(sizer_size_font, 0, 0, 0)

        # Size font Lable
        sizer_size_tick = wx.BoxSizer(wx.HORIZONTAL)
        self.label_size_tick = wx.StaticText(self, -1, "Size of Tick Label [points]:")
        self.label_size_tick.SetMinSize((230, 17))
        sizer_size_tick.Add(self.label_size_tick, 0, wx.LEFT|wx.RIGHT, 5)

        self.size_tick = wx.TextCtrl(self, -1, "19")
        self.size_tick.SetMinSize((230, 20))
        sizer_size_tick.Add(self.size_tick, 0, 0, 0)

        right_sizer.Add(sizer_size_tick, 0, 0, 0)

        # Another line
        self.static_line_31 = wx.StaticLine(self, -1)
        right_sizer.Add(self.static_line_31, 0, wx.ALL, 5)

        # Save file
        sizer_savefile = wx.BoxSizer(wx.HORIZONTAL)
        self.label_savefile = wx.StaticText(self, -1, "Select output file root:")
        self.label_savefile.SetMinSize((230, 17))
        sizer_savefile.Add(self.label_savefile, 0, wx.LEFT|wx.RIGHT, 5)

        self.savefile = wx.TextCtrl(self, -1, "")
        self.savefile.SetMinSize((230, 20))
        sizer_savefile.Add(self.savefile, 0, 0, 0)

        self.button_savefile = wx.Button(self, -1, "+")
        self.button_savefile.SetMinSize((23, 20))
        self.Bind(wx.EVT_BUTTON, self.add_savefile, self.button_savefile)
        sizer_savefile.Add(self.button_savefile, 0, wx.LEFT|wx.RIGHT, 5)

        right_sizer.Add(sizer_savefile, 0, 0, 0)

        # Another line
        self.static_line_4 = wx.StaticLine(self, -1)
        right_sizer.Add(self.static_line_4, 0, wx.ALL, 5)

        # Show legend
        sizer_legend = wx.BoxSizer(wx.HORIZONTAL)
        self.legend_text = wx.StaticText(self, -1, "Show legend ?")
        self.legend_text.SetMinSize((230, 17))
        sizer_legend.Add(self.legend_text, 0, wx.LEFT, 5)

        self.radio_yes = wx.RadioButton(self, -1, "Yes")
        self.radio_yes.SetMinSize((60, 19))
        sizer_legend.Add(self.radio_yes, 0, 0, 0)

        self.radio_no = wx.RadioButton(self, -1, "No")
        self.radio_no.SetMinSize((60, 19))
        sizer_legend.Add(self.radio_no, 0, 0, 0)

        right_sizer.Add(sizer_legend, 0, 0, 0)

        # Another line
        self.static_line_10 = wx.StaticLine(self, -1)
        right_sizer.Add(self.static_line_10, 0, wx.ALL, 5)

        # Another line
        self.static_line_9 = wx.StaticLine(self, -1)
        right_sizer.Add(self.static_line_9, 0, wx.ALL, 5)

        # Buttons
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        self.button_create = wx.Button(self, -1, "Create 2D plot")
        self.button_create.SetMinSize((110, 29))
        self.Bind(wx.EVT_BUTTON, self.create, self.button_create)
        sizer_1.Add(self.button_create, 0, wx.LEFT|wx.BOTTOM, 5)

        self.button_close = wx.Button(self, -1, "Close")
        self.button_close.SetMinSize((110, 29))
        self.Bind(wx.EVT_BUTTON, self.close, self.button_close)
        sizer_1.Add(self.button_close, 0, 0, 0)

        right_sizer.Add(sizer_1, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        # Add right sizer
        subsizer.Add(right_sizer, 0, 0, 0)
        mainsizer.Add(subsizer, 0, 0, 0)

        # Pack dialog
        self.SetSizer(mainsizer)
        mainsizer.Fit(self)
        self.Layout()


    def add_data(self, event, dataset_no):
        # select data to import
        filename = openfile('Select NESSY - .csv file to open', '', '', 'NESSY CSV File (*.csv)|*.csv|all files (*.*)|*', self)
        if filename:
            self.data[dataset_no].SetValue(filename)


    def add_savefile(self, event):
        # select file to save
        filename = savefile('Select file to save 3D plot (file ending will be automatically created!)', '', '', 'all files (*.*)|*', self)
        if filename:
            self.savefile.SetValue(filename)

        # brings dialog to top
        self.Raise()


    def create(self, event):
        # create 3d plot
        # evalute entries
        check = False

        # data sets
        for i in range(0, len(self.data)):
            if not str(self.data[i].GetValue()) == '':
                check = True

        if not check:
            error_popup('No data to plot!\nSelect at least one .csv file.', self)
            return

        # Savefile
        if str(self.savefile.GetValue()) == "":
            error_popup('No output file selected!', self)
            return

        # prepare data
        self.prepare_data()

        # sort data
        self.sort()

        # plot 3d plot
        output = str(self.savefile.GetValue())
        xlabel = str(self.xlabel.GetValue())
        zlabel = str(self.ylabel.GetValue())
        xlim = [str(self.xlim.GetValue()), str(self.xlim_end.GetValue())]
        ylim = [str(self.ylim.GetValue()), str(self.ylim_end.GetValue())]
        showlegend = self.radio_yes.GetValue()
        xy_dimension = float(self.dimension.GetValue())
        label = int(self.size_font.GetValue())
        tick = int(self.size_tick.GetValue())

        # create
        self.plot(output, self.plotdata, xlabel=xlabel, zlabel=zlabel, xlim=xlim, ylim=ylim, dimension=xy_dimension, label=label, tick=tick, show_legend=showlegend)


    def close(self, event):
        # close dialog
        self.Destroy()


    def edit_data(self, evt, datano):
        """Opens edit dialog."""
        # read file if present
        if not str(self.data[datano].GetValue()) in ['', 'Custom.']:
            # container
            data_tmp = [[], [], []]

            # read values
            # open file
            file = open(str(self.data[datano].GetValue()), 'r')

            # Column numbers
            x_index = int(self.x_col[datano].GetValue())-1
            y_index = int(self.y_col[datano].GetValue())-1
            err_index = int(self.err_col[datano].GetValue())-1

            # Header flag
            isheader = True

            # read and split lines
            for line in file:
                    entries = line
                    entries = entries.replace('\n', '')
                    # Semicolon separated
                    if ';' in entries:
                        entries = entries.split(';')
                    # Coma separated
                    elif ',' in entries:
                        entries = entries.split(',')
                    # Tabulator separated
                    elif '\t' in entries:
                        entries = entries.split('\t')
                    # Whitespace separated
                    else:
                        entries = entries.split()

                    # empty lines
                    if len(entries) < 2:
                        continue

                    # header
                    if 'x' in entries[x_index]:
                        continue

                    # header
                    if 'x' in entries[x_index]:
                        continue

                    # x values
                    data_tmp[0].append(float(entries[x_index]))

                    # y values
                    data_tmp[1].append(float(entries[y_index]))

                     # error
                    try:    # error value present
                        data_tmp[2].append(float(entries[err_index]))
                    except: # no error value present
                        data_tmp[2].append(0.0)

            # Save values
            self.dataset[datano] = data_tmp

        # open dialog
        edit = Data_editor(self, self.data[datano], datano, self, -1, "")
        edit.ShowModal()


    def plot(self, output, data, xlabel='v(CPMG) [Hz]', ylabel='', zlabel='R2eff [1/s]', xlim=[0, 1600], ylim=[10, 40], dimension=100, label=19, tick=19, show_legend=True):
        """Function to create 3d plots.

        output:         Output file.
        data:           List of 2d data sets, label and plane no.
                        [[x_dataset1, y_dataset1, yerr_dataset, label_dataset1, style1, color1], ...]
        xlabel:         Lable of x axis.
        ylabel:         Label of y axis.
        zlabel:         Label of z axis.
        xlim:           Range of x axes (of 2d plot).
        ylim:           Range of y axes (od 2d plot).
        dimension:      The dimension of the plot (% of hight).
        label:          Size of the axis label font.
        tick:           Size of the tick font.
        show_legend:    True for add legend to plot.
        """

        # Frame width
        params={'axes.linewidth' : self.main.FRAMEWIDTH}
        pylab.rcParams.update(params)

        # The dimension of the plot
        hight = dimension*0.8/100
        pylab.axes([0.125, 0.1, 0.775, hight])

        # loop over datasets
        for y in range(0, len(data)):
            # x
            x_value = data[y][0]

            # y
            y_value = data[y][1]

            # err
            err = data[y][2]

            # label
            label1 = data[y][3][0]
            if not label1:
                label1 = 'n/a'

            # color
            color = data[y][5][0]

            # style
            plotformat = data[y][4][0]

            # error bar
            if plotformat == "Scatter plot + error":
                pylab.errorbar(x_value, y_value, yerr = err, color=color, fmt ='o')

            # scatter plot
            if plotformat == 'Scatter plot':
                pylab.scatter(x_value, y_value, c = color, marker = 'o')

            # line plot
            if plotformat == 'Line plot':
                pylab.plot(x_value, y_value, '-', color=color, label = label1)

            # bar plot
            if plotformat == "Bar plot":
                pylab.bar(x_value, [i-float(ylim[0]) for i in y_value], bottom = float(ylim[0]), color=color, alpha=0.6, label = label1)

            # bar plot with error bar
            if plotformat == "Bar plot + error":
                pylab.bar(x_value, [i-float(ylim[0]) for i in y_value], bottom = float(ylim[0]), color=color, alpha=0.6, yerr = err, ecolor='k', label = label1)

            # Landscape mode
            if plotformat == "Landscape mode":
                pylab.plot(x_value, y_value, '_', color=color, label = label1, markersize=70, markeredgewidth= 5)

                # craete baseline
                pylab.plot([float(xlim[0])-0.5, float(xlim[1])+0.5], [0, 0], 'k--')

        # label of axis
        pylab.xlabel(xlabel, fontsize=label, weight='bold')
        pylab.ylabel(zlabel, fontsize=label, weight='bold')

        # Size of axis labels
        pylab.xticks(fontsize=tick)
        pylab.yticks(fontsize=tick)

        # range of axis
        if plotformat == "Landscape mode":
            pylab.xlim(float(xlim[0])-0.5, float(xlim[1])+0.5)
        else:
            pylab.xlim(float(xlim[0]), float(xlim[1]))
        pylab.ylim(float(ylim[0]), float(ylim[1]))

        # save file names
        file_png = output+'.png'
        file_svg = output+self.main.PLOTFORMAT

        # Legend
        try:
            if show_legend:
                pylab.legend()
        except:
            a = 'bar plot selected...'

        pylab.savefig(file_svg)
        pylab.savefig(file_png, dpi = 72, transparent = True)

        # clear graph
        pylab.cla()
        pylab.close()

        # Add 3d plot to results
        self.main.tree_results.AppendItem (self.main.plots2d, file_png, 0)

        # Store 3d plots
        self.main.plot2d.append(file_png)

        # Feedback
        message('2D Plot created!\nPlot is listed in results tab.', self)


    def prepare_data(self):
        # reads csv files and stores entries in self.plotdata
        self.plotdata = []      # [[x_dataset1, y_dataset1, yerr_dataset, label_dataset1, style1, color1], ...]

        number_of_plot = 0

        # loop over data sets
        for i in range(0, len(self.data)):

            # data set is selected as file and was not manipulated
            if not str(self.data[i].GetValue()) in ['', 'Custom.']:
                # create new dataset
                self.plotdata.append([[], [], [], [], [], [], [], []])

                # Column numbers
                x_index = int(self.x_col[i].GetValue())-1
                y_index = int(self.y_col[i].GetValue())-1
                err_index = int(self.err_col[i].GetValue())-1

                # open and read file
                file = open(str(self.data[i].GetValue()), 'r')

                # read lines
                for line in file:
                    entries = line
                    entries = entries.replace('\n', '')
                    # Semicolon separated
                    if ';' in entries:
                        entries = entries.split(';')
                    # Coma separated
                    elif ',' in entries:
                        entries = entries.split(',')
                    # Tabulator separated
                    elif '\t' in entries:
                        entries = entries.split('\t')
                    # Whitespace separated
                    else:
                        entries = entries.split()

                    # empty lines
                    if len(entries) < 2:
                        continue

                    # header
                    if 'x' in entries[x_index]:
                        continue

                    # Not a list
                    if isinstance(entries, basestring):
                        continue

                    # save entries
                    # x value
                    self.plotdata[number_of_plot][0].append(float(entries[x_index]))
                    # y value
                    self.plotdata[number_of_plot][1].append(float(entries[y_index]))
                    # error
                    try:    # error value present
                        self.plotdata[number_of_plot][2].append(float(entries[err_index]))
                    except: # no error value present
                        self.plotdata[number_of_plot][2].append(0.0)
                    # label
                    self.plotdata[number_of_plot][3].append(str(self.label[i].GetValue()))
                    # style
                    self.plotdata[number_of_plot][4].append(str(self.style[i].GetValue()))
                    # color
                    self.plotdata[number_of_plot][5].append(str(self.color[i].GetValue()))

                # next plot
                number_of_plot = number_of_plot + 1

                file.close()

            # Custom
            if str(self.data[i].GetValue()) == 'Custom.':
                # add entries
                self.plotdata.append([[], [], [], [], [], [], [], []])

                # x values
                xvalues = self.dataset[i][0]
                xvalues = [float(v) for v in xvalues]
                self.plotdata[len(self.plotdata)-1][0].extend(xvalues)

                # y vlalues
                yvalues = self.dataset[i][1]
                yvalues = [float(v) for v in yvalues]
                self.plotdata[len(self.plotdata)-1][1].extend(yvalues)

                # error
                # loop over errors
                err = []
                for k in range(len(self.dataset[i][2])):
                    if self.dataset[i][2][k] == '':
                        err.append(0.0)
                    else:
                        err.append(float(self.dataset[i][2][k]))
                self.plotdata[len(self.plotdata)-1][2].extend(err)

                # label, style and color
                for k in range(len(self.dataset[i][0])):
                    # label
                    self.plotdata[len(self.plotdata)-1][3].append(str(self.label[i].GetValue()))
                    # style
                    self.plotdata[len(self.plotdata)-1][4].append(str(self.style[i].GetValue()))
                    # color
                    self.plotdata[len(self.plotdata)-1][5].append(str(self.color[i].GetValue()))


    def sort(self):
        """Sort list of list."""

        # loop over datasets
        for i in range(0, len(self.plotdata)):
            # extract data
            x = self.plotdata[i][0]
            y = self.plotdata[i][1]
            err = self.plotdata[i][2]

            # sort entries
            # loop over x values
            for j in range(0, len(x)):
                # compare next values:
                for v in range(0, len(x)):
                    if not j == v:
                        if x[j] > x[v]:
                            # sort x values
                            x_temp = x[j]
                            x[j] = x[v]
                            x[v] = x_temp

                            # sort y values
                            y_temp = y[j]
                            y[j] = y[v]
                            y[v] = y_temp

                            # sort error
                            err_temp = err[j]
                            err[j] = err[v]
                            err[v] = err_temp

                # store new values
                self.plotdata[i][0] = x
                self.plotdata[i][1] = y
                self.plotdata[i][2] = err



class Data_editor(wx.Dialog):
    """Dialog to edit data to plot."""
    def __init__(self, gui, label, datano, *args, **kwds):
        """Data to plot can be manipulated or inserted.

        data:       List container of x, y and error values.
        label:      TextXtrl object with filename.
        datano:     Number of dataset.
        """

        # link data
        self.main = gui
        self.data = self.main.dataset[datano]
        self.label = label
        self.datano = datano

        # Build the GUI
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.Centre()

        # Build dialog
        self.build()

        # Read entries
        self.read()


    def build(self):
        """Build the dialog."""
        # Mainsizer
        mainsizer = wx.BoxSizer(wx.HORIZONTAL)

        # The image
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(SYNTHETIC_PIC, wx.BITMAP_TYPE_ANY))
        mainsizer.Add(self.bitmap, 0, wx.ALL, 5)

        # Right sizer
        rightsizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        self.Header = wx.StaticText(self, -1, "Edit Data of Layer "+str(self.datano+1))
        self.Header.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        rightsizer.Add(self.Header, 0, wx.ALL, 5)

        # Data grid
        self.data_grid = NESSY_grid(self, -1, size=(1, 1))
        self.data_grid.CreateGrid(1000, 3)
        self.data_grid.SetColLabelValue(0, "X")
        self.data_grid.SetColLabelValue(1, "Y")
        self.data_grid.SetColLabelValue(2, "Error")
        self.data_grid.SetMinSize((400, 300))
        rightsizer.Add(self.data_grid, 0, wx.ALL|wx.EXPAND, 5)

        # Buttons
        button_box = wx.BoxSizer(wx.HORIZONTAL)
        self.button_save = wx.Button(self, -1, "Save")
        button_box.Add(self.button_save, 0, wx.ALL, 10)
        self.Bind(wx.EVT_BUTTON, self.save, self.button_save)
        self.button_cancel = wx.Button(self, -1, "Cancel")
        button_box.Add(self.button_cancel, 0, wx.ALL, 10)
        self.Bind(wx.EVT_BUTTON, self.cancel, self.button_cancel)
        rightsizer.Add(button_box, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        # Pack dialog
        mainsizer.Add(rightsizer, 0, wx.EXPAND, 0)
        self.SetSizer(mainsizer)
        mainsizer.Fit(self)
        self.Layout()


    def cancel(self, event):
        self.Destroy()


    def read(self):
        # empty file
        if self.label == '':
            return

        # Custom saved entry or given file
        else:
            # fill in values
            for i in range(len(self.data[0])):
                # x values
                self.data_grid.SetCellValue(i, 0, str(self.data[0][i]))

                # y values
                self.data_grid.SetCellValue(i, 1, str(self.data[1][i]))

                # errors
                self.data_grid.SetCellValue(i, 2, str(self.data[2][i]))


    def save(self, event):
        # set 'file name'
        self.label.SetValue('Custom.')

        # Reset data container
        self.data = [[], [], []]

        # read data
        for i in range(0, 1000):
            if not str(self.data_grid.GetCellValue(i, 0)) == '' and not str(self.data_grid.GetCellValue(i, 1)) == '':
                # x value
                self.data[0].append(str(self.data_grid.GetCellValue(i, 0)))

                # y value
                self.data[1].append(str(self.data_grid.GetCellValue(i, 1)))

                # error value
                self.data[2].append(str(self.data_grid.GetCellValue(i, 2)))

        # close dialog
        self.main.dataset[self.datano] = self.data
        self.Destroy()