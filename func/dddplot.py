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
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from scipy import sqrt
from os import sep
import wx

# NESSY modules
from conf.filedialog import openfile, savefile
from conf.message import error_popup, message
from conf.path import NESSY_PIC, PLOT3D_SIDE_PIC
from conf.NESSY_grid import NESSY_grid



class DDD_Plot_draw(wx.Frame):
    """Class to create 3d plots."""
    def __init__(self, gui, *args, **kwds):
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
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(PLOT3D_SIDE_PIC, wx.BITMAP_TYPE_ANY))
        subsizer.Add(self.bitmap, 0, wx.ALL, 5)

        # right sizer
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        self.label_title = wx.StaticText(self, -1, "3D Plot Generator")
        self.label_title.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        right_sizer.Add(self.label_title, 0, wx.ALL, 5)

        # Table title
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_file = wx.StaticText(self, -1, "NESSY - .csv File to plot:")
        title_file.SetMinSize((220, 17))
        title_sizer.Add(title_file, 0, wx.LEFT|wx.RIGHT, 5)

        title_label = wx.StaticText(self, -1, "Label:")
        title_label.SetMinSize((155, 17))
        title_sizer.Add(title_label, 0, wx.LEFT|wx.RIGHT, 5)

        title_plane = wx.StaticText(self, -1, "Plane no.:")
        title_plane.SetMinSize((75, 17))
        title_sizer.Add(title_plane, 0, wx.LEFT|wx.RIGHT, 5)

        title_format = wx.StaticText(self, -1, "Plot style:")
        title_format.SetMinSize((110, 17))
        title_sizer.Add(title_format, 0, wx.LEFT|wx.RIGHT, 5)

        title_color = wx.StaticText(self, -1, "Plot color:")
        title_color.SetMinSize((110, 17))
        title_sizer.Add(title_color, 0, wx.LEFT|wx.RIGHT, 5)

        title_column = wx.StaticText(self, -1, "X / Y column:")
        title_column.SetMinSize((100, 17))
        title_sizer.Add(title_column, 0, wx.LEFT|wx.RIGHT, 5)

        right_sizer.Add(title_sizer, 0, 0, 0)


        # Data
        self.data = []
        self.x_col = []
        self.y_col = []
        self.buttons = []
        self.label = []
        self.plane = []
        self.style = []
        self.color = []
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
            sizer_data1.Add(self.buttons[i], 0, wx.LEFT|wx.RIGHT, 5)

            # Label box
            self.label.append(wx.TextCtrl(self, -1, ""))
            self.label[i].SetMinSize((150, 25))
            sizer_data1.Add(self.label[i], 0, wx.LEFT|wx.RIGHT, 15)

            # Plane text field
            self.plane.append(wx.TextCtrl(self, -1, str(i+1)))
            self.plane[i].SetMinSize((50, 25))
            sizer_data1.Add(self.plane[i], 0, wx.LEFT|wx.RIGHT, 5)

            # Plot style
            self.style.append(wx.ComboBox(self, -1, choices=["Line plot", "Scatter plot", "Bar plot", "Line and Dots"], style=wx.CB_DROPDOWN | wx.CB_READONLY))
            self.style[i].SetMinSize((100, 25))
            self.style[i].SetSelection(0)
            sizer_data1.Add(self.style[i], 0, wx.LEFT, 25)

            # Plot color
            self.color.append(wx.ComboBox(self, -1, choices=['BLUE', 'RED', 'GREEN', 'VIOLET', 'YELLOW', 'CYAN', 'MAGENTA', 'ORANGE', 'PINK', 'PURPLE', 'BLACK', 'GRAY'], style=wx.CB_DROPDOWN | wx.CB_READONLY))
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
            sizer_data1.Add(self.y_col[i], 0, wx.LEFT|wx.RIGHT, 5)

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
        self.button_create = wx.Button(self, -1, "Create 3D plot")
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
        filename = openfile('Select NESSY - .csv file to open', '', '', 'all files (*.*)|*', self)
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

        # create
        self.plot(output, self.plotdata, xlabel=xlabel, zlabel=zlabel, xlim=xlim, ylim=ylim, show_legend=showlegend)


    def close(self, event):
        # close dialog
        self.Destroy()


    def plot(self, output, data, xlabel='v(CPMG) [Hz]', ylabel='', zlabel='R2eff [1/s]', xlim=[0, 1600], ylim=[10, 40], show_legend=True):
        """Function to create 3d plots.

        output:         Output file.
        data:           List of 2d data sets, label and plane no.
                        [[x_dataset1, y_dataset1, label_dataset1, plane_dataset1, style1, color1], ...]
        xlabel:         Lable of x axis.
        ylabel:         Label of y axis.
        zlabel:         Label of z axis.
        xlim:           Range of x axes (of 2d plot).
        ylim:           Range of y axes (od 2d plot).
        show_legend:    True for add legend to plot.
        """

        # Frame width
        params={'axes.linewidth' : self.main.FRAMEWIDTH}
        plt.rcParams.update(params)

        # Create 3d axes
        fig = plt.figure()
        ax = Axes3D(fig)

        # loop over datasets
        for y in range(0, len(data)):
            # x
            x_value = data[y][0]

            # y
            y_value = []
            for i in range(0, len(data[y][0])):
                y_value.append(int(data[y][3][0])-1)

            # z
            z_value = data[y][1]

            # label
            label1 = data[y][2][0]
            if not label1:
                label1 = 'n/a'

            # color
            color = data[y][5][0]

            # style
            plotformat = data[y][4][0]

            # scatter plot
            if plotformat == 'Scatter plot':
                ax.plot(x_value, y_value, z_value, zs = 'y', c = color, marker = 'o', lw = 0, label = label1)

            # line plot
            if plotformat == 'Line plot':
                ax.plot(x_value, y_value, z_value, zs = 'y', c = color, marker = '', label = label1)

            # bar plot
            if plotformat == 'Bar plot':
                ax.bar(x_value, z_value, [i-float(ylim[0]) for i in y_value], zdir = 'y', bottom = float(ylim[0]), color=color, alpha=0.8, label = label1)

            # line and dott
            if plotformat == 'Line and Dots':
                ax.plot(x_value, y_value, z_value, zs = 'y', c = color, marker = 'o', label = label1)

            # label of axis
            ax.set_xlabel(xlabel, fontsize=19, weight='bold')
            ax.set_ylabel(ylabel, fontsize=19, weight='bold')
            ax.set_zlabel(zlabel, fontsize=19, weight='bold')

            # range of axis
            ax.set_xlim3d(float(xlim[0]), float(xlim[1]))
            ax.set_zlim3d(float(ylim[0]), float(ylim[1]))

            max = int(data[len(data)-1][3][0]) - 1
            delta = 0.3
            ax.set_ylim3d(delta*(-1), max + delta)

        # save file names
        file_png = output+'.png'
        file_svg = output+self.main.PLOTFORMAT

        # Legend
        try:
            if show_legend:
                plt.legend()
        except:
            a = 'no legend can be plotted as bar plot was specified'

        plt.savefig(file_svg)
        plt.savefig(file_png, dpi = 72, transparent = True)

        # clear graph
        plt.cla()
        plt.close()

        # Add 3d plot to results
        self.main.tree_results.AppendItem (self.main.plots3d, file_png, 0)

        # Store 3d plots
        self.main.plot3d.append(file_png)

        # Feedback
        message('3D Plot created!\nPlot is listed in results tab.', self)


    def prepare_data(self):
        # reads csv files and stores entries in self.plotdata
        self.plotdata = []      # [[x_dataset1, y_dataset1, label_dataset1, plane_dataset1, style1, color1], ...]

        number_of_plot = 0

        # loop over data sets
        for i in range(0, len(self.data)):

            # data set is selected
            if not str(self.data[i].GetValue()) == '':
                # create new dataset
                self.plotdata.append([[], [], [], [], [], [], [], []])

                # Column numbers
                x_index = int(self.x_col[i].GetValue())-1
                y_index = int(self.y_col[i].GetValue())-1

                # open and read file
                file = open(str(self.data[i].GetValue()), 'r')

                # read lines
                # Header flag
                isheader = True

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

                    # skip header
                    if isheader:
                        isheader = False
                        continue

                    # save entries
                    # x value
                    self.plotdata[number_of_plot][0].append(float(entries[x_index]))
                    # y value
                    self.plotdata[number_of_plot][1].append(float(entries[y_index]))
                    # label
                    self.plotdata[number_of_plot][2].append(str(self.label[i].GetValue()))
                    # plane
                    self.plotdata[number_of_plot][3].append(str(self.plane[i].GetValue()))
                    # style
                    self.plotdata[number_of_plot][4].append(str(self.style[i].GetValue()))
                    # color
                    self.plotdata[number_of_plot][5].append(str(self.color[i].GetValue()))

                # next plot
                number_of_plot = number_of_plot + 1

                file.close()


    def sort(self):
        """Sort list of list."""

        # loop over datasets
        for i in range(0, len(self.plotdata)):
            # extract data
            x = self.plotdata[i][0]
            y = self.plotdata[i][1]

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

                # store new values
                self.plotdata[i][0] = x
                self.plotdata[i][1] = y
