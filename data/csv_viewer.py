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


# python modules
import os
from os import sep
import wx

# NESSY modules
from conf.path import NESSY_PIC, PLOT_SIDE_PIC


def open_csv_viewer(gui, item, sel):
    """opens csv viewer"""

    viewer = csv_viewer(gui, item, sel, None, -1, "")
    viewer.Show()



class csv_viewer(wx.Frame):
    def __init__(self, gui, item, sel, *args, **kwds):

        # connect parameters
        self.main = gui
        self.csv_file = item
        self.selection = sel

        # Build window
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        # Set title
        t = item.split(sep)
        t = t[len(t)-1]
        t = t.replace('_', ' ').replace('.csv', '')
        self.SetTitle('NESSY - CSV Viewer - '+t)
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        self.new_item = ''

        # Image
        self.topsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(PLOT_SIDE_PIC, wx.BITMAP_TYPE_ANY))
        self.topsizer.Add(self.bitmap, 0, wx.ALL, 5)

        # Main box
        main_box = wx.BoxSizer(wx.VERTICAL)

        # header
        self.header = wx.StaticText(self, -1, "Residue")
        self.header.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        main_box.Add(self.header, 0, wx.ALL|wx.ALIGN_LEFT, 10)

        self.build_name(self.csv_file)

        #list
        self.list = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.list.SetMinSize((500, 400))
        main_box.Add(self.list, -1, wx.LEFT|wx.RIGHT|wx.EXPAND, 5)
        # add entries
        self.add_list_entries()

        # button
        self.button_box = wx.BoxSizer(wx.HORIZONTAL)

        #Previous
        self.button_prev = wx.Button(self, -1, "Previous")
        self.Bind(wx.EVT_BUTTON, self.previous_csv, self.button_prev)
        self.button_box.Add(self.button_prev, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 0)

        #close
        self.button_close = wx.Button(self, -1, "Close")
        self.Bind(wx.EVT_BUTTON, self.close, self.button_close)
        self.button_box.Add(self.button_close, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 0)

        #Next
        self.button_next = wx.Button(self, -1, "Next")
        self.Bind(wx.EVT_BUTTON, self.next_csv, self.button_next)
        self.button_box.Add(self.button_next, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 0)

        # Pack buttons
        main_box.Add(self.button_box, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)

        # Pack dialog
        self.topsizer.Add(main_box, -1, wx.EXPAND, 0)
        self.SetSizer(self.topsizer)
        self.topsizer.Fit(self)
        self.Layout()


    def add_list_entries(self):
        """Fills entries in List"""

        # read file
        istitle = True
        entries = 0
        file = open(self.csv_file, 'r')
        for line in file:
            line = line.replace('\n', '')
            line = line.replace('None', '  ')
            entry= line.split(';')

            # Build header
            if istitle:
                istitle = False

                for v in range(0, len(entry)):

                    self.list.InsertColumn(v, entry[v]+':')
                    entries = len(entry)

            # Build entries
            else:
                if not entry[0] == '':
                    # Insert items
                    for v in range(0, len(entry)):
                        if v == 0:
                            self.list.InsertStringItem(self.list.GetItemCount(), entry[v])
                        else:
                            self.list.SetStringItem(self.list.GetItemCount()-1, v, entry[v])

        file.close()


    def build_name(self, csv_name, model = False):
        """Create header of plot"""

        # residue number
        name = csv_name.split(sep)
        csv = name[len(name)-1]

        # Delete Exp name and file ending
        csv = csv.replace('_', ' ')
        csv = csv.replace('.csv', '')

        # Split filename
        text = csv.split(sep)

        # Update header
        self.header.SetLabel(text[len(text)-1])


    def close(self, event): # close
        self.Destroy()
        event.Skip()


    def next_csv(self, event):
        """open next plot"""

        # get selection
        item = self.new_item
        if str(self.new_item) == '':
            self.new_item = self.main.tree_results.GetNextSibling(self.selection)
        else:
            self.new_item = self.main.tree_results.GetNextSibling(item)

        # read entry
        new_csv = self.main.tree_results.GetItemText(self.new_item)

        if new_csv == '':
            self.new_item = item

        else:
            # get header
            self.build_name(new_csv)

            # display plot
            self.csv_file = new_csv
            self.list.ClearAll()
            self.add_list_entries()

            # Set title
            t = new_csv.split(sep)
            t = t[len(t)-1]
            t = t.replace('_', ' ').replace('.csv', '')
            self.SetTitle('NESSY - CSV Viewer - '+t)


    def previous_csv(self, event):
        """open next plot"""

        # get selection
        item = self.new_item
        if str(self.new_item) == '':
            self.new_item = self.main.tree_results.GetPrevSibling(self.selection)
        else:
            self.new_item = self.main.tree_results.GetPrevSibling(item)

        # read entry
        new_csv = self.main.tree_results.GetItemText(self.new_item)

        if new_csv == '':
            self.new_item = item

        else:
            # get header
            self.build_name(new_csv)

            # display plot
            self.csv_file = new_csv
            self.list.ClearAll()
            self.add_list_entries()

            # Set title
            t = new_csv.split(sep)
            t = t[len(t)-1]
            t = t.replace('_', ' ').replace('.csv', '')
            self.SetTitle('NESSY - CSV Viewer - '+t)
