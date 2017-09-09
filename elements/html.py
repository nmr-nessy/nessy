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
from os import sep
import wx
import wx.html
import wx.lib.printout as printer


# NESSY modules
from conf.path import NESSY_PIC, ROOT, PRINT



class Html(wx.Frame):
    def __init__(self, filename, *args, **kwds):
        self.filename = filename

        # Build frame
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetSize((940, 600))
        self.Centre()

        # toolbar
        self.toolbar = wx.ToolBar(self, -1, style=wx.TB_HORIZONTAL|wx.TB_FLAT)
        self.SetToolBar(self.toolbar)
        self.toolbar.AddLabelTool(1, _("Refresh"), wx.Bitmap(PRINT, wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, _("Refresh"), "")
        self.Bind(wx.EVT_TOOL, self.print_window, id=1)

        # Add a sizer box.
        box = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(box)

        # The HTML window.
        self.html = wx.html.HtmlWindow(self, -1, size=(-1, -1))
        box.Add(self.html, 1, wx.GROW)

        # Load manual.html
        self.html.LoadFile(filename)

        # For printing
        self.printer = wx.html.HtmlEasyPrinting()


    def print_window(self, event):
        file = open(self.filename, 'r')
        data = ''
        for line in file:
            data = data + line
        file.close()
        
        #self.printer.GetPrintData().SetPaperId(wx.PAPER_LETTER)
        self.printer.PrintFile(self.filename)
        
