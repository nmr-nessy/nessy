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


# python modules
import os
from os import sep
import pylab
import wx

# NESSY modules
from conf.path import NESSY_PIC, PLOT_SIDE_PIC


class view_plots(wx.Frame):
    '''Plot Viewer'''
    def __init__(self, gui, plot, selection, *args, **kwds):

        # Link parameters
        self.main = gui
        self.plot = plot
        self.selection = selection

        #window
        kwds["style"] = wx.CAPTION | wx.MINIMIZE_BOX
        wx.Frame.__init__(self, *args, **kwds)
        # Set title
        t = plot.split(sep)
        t = t[len(t)-1]
        t = t.replace('_', ' ').replace('.png', '')
        self.SetTitle('NESSY - Plot Viewer - '+t)
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        # Temporary item
        self.new_item = ''

        # Image
        self.topsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(PLOT_SIDE_PIC, wx.BITMAP_TYPE_ANY))
        self.topsizer.Add(self.bitmap, 0, wx.ALL, 5)

        # Main sizer
        main_box = wx.BoxSizer(wx.VERTICAL)

        # Plot
        self.plot_bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(plot, wx.BITMAP_TYPE_ANY))
        #self.plot_bitmap.SetMinSize((540, 432))
        main_box.Add(self.plot_bitmap, wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 0)

        # Buttons
        self.button_box = wx.BoxSizer(wx.HORIZONTAL)

        # Previous
        self.button_prev = wx.Button(self, -1, "Previous")
        self.Bind(wx.EVT_BUTTON, self.previous_plot, self.button_prev)
        self.button_box.Add(self.button_prev, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)

        # close
        self.button_close = wx.Button(self, -1, "Close")
        self.Bind(wx.EVT_BUTTON, self.close_viewer, self.button_close)
        self.button_box.Add(self.button_close, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)

        # next
        self.button_next = wx.Button(self, -1, "Next")
        self.Bind(wx.EVT_BUTTON, self.next_plot, self.button_next)
        self.button_box.Add(self.button_next, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5)

        # Pack Buttons
        main_box.Add(self.button_box, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        # Pack dialog
        self.topsizer.Add(main_box, 0, 0, 0)
        self.SetSizer(self.topsizer)
        self.topsizer.Fit(self)
        self.Layout()


    def close_viewer(self, event): # close plot viewer
        self.Destroy()
        event.Skip()


    def next_plot(self, event):
        """open next plot"""
        # get selection
        item = self.new_item
        if str(self.new_item) == '':
            self.new_item = self.main.tree_results.GetNextSibling(self.selection)
        else:
            self.new_item = self.main.tree_results.GetNextSibling(item)

        # read entry
        new_plot = self.main.tree_results.GetItemText(self.new_item)

        if new_plot == '':
            self.new_item = item

        else:
            # display plot
            self.plot_bitmap.SetBitmap(wx.Bitmap(new_plot, wx.BITMAP_TYPE_ANY))

            # Set title
            t = new_plot.split(sep)
            t = t[len(t)-1]
            t = t.replace('_', ' ').replace('.png', '')
            self.SetTitle('NESSY - Plot Viewer - '+t)


    def previous_plot(self, event):
        """open next plot"""
        # get selection
        item = self.new_item
        if str(self.new_item) == '':
            self.new_item = self.main.tree_results.GetPrevSibling(self.selection)
        else:
            self.new_item = self.main.tree_results.GetPrevSibling(item)

        # read entry
        new_plot = self.main.tree_results.GetItemText(self.new_item)

        if new_plot == '':
            self.new_item = item

        else:
            # display plot
            self.plot_bitmap.SetBitmap(wx.Bitmap(new_plot, wx.BITMAP_TYPE_ANY))

            # Set title
            t = new_plot.split(sep)
            t = t[len(t)-1]
            t = t.replace('_', ' ').replace('.png', '')
            self.SetTitle('NESSY - Plot Viewer - '+t)
