#################################################################################
#                                                                               #
#   (C) 2012 Michael Bieri                                                      #
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


# Python import
import wx
import wx.grid



class NESSY_grid(wx.grid.Grid):
    """ A Copy&Paste enabled grid class

    Script adapted from:    http://wxpython-users.1045709.n5.nabble.com/copy-and-pasting-selections-in-wx-grid-cells-td2353289.html
    """

    def __init__(self, *args, **kwds):
        # Initialise wxGrid
        wx.grid.Grid.__init__(self, *args, **kwds)

        # Catch key event handlers
        wx.EVT_KEY_DOWN(self, self.OnKey)

        # Color
        self.SetDefaultCellBackgroundColour('White')
        self.SetDefaultCellTextColour('Black')
        self.SetLabelBackgroundColour('Lightgray')
        self.SetLabelTextColour('Black')

    def OnKey(self, event):
        # If Ctrl+C is pressed...copy to clipboard
        if event.ControlDown() and event.GetKeyCode() == 67:
            # Call copy method
            self.copy()
           
        # If Ctrl+V is pressed... paste from clipboard
        if event.ControlDown() and event.GetKeyCode() == 86:
            # Call paste method
            self.paste()
           
        # If Supr is presed
        if event.GetKeyCode() == 127:
            # Call delete method
            try:
                self.delete()
            except:
                return
           
        # Skip other Key events
        if event.GetKeyCode():
            event.Skip()
            return

    def copy(self):
        # Number of rows and cols
        rows = self.GetSelectionBlockBottomRight()[0][0] - self.GetSelectionBlockTopLeft()[0][0] + 1
        cols = self.GetSelectionBlockBottomRight()[0][1] - self.GetSelectionBlockTopLeft()[0][1] + 1
       
        # data variable contain text that must be set in the clipboard
        data = ''
       
        # For each cell in selected range append the cell value in the data variable
        # Tabs '\t' for cols and '\r' for rows
        for r in range(rows):
            for c in range(cols):
                data = data + str(self.GetCellValue(self.GetSelectionBlockTopLeft()[0][0] + r, self.GetSelectionBlockTopLeft()[0][1] + c))
                if c < cols - 1:
                    data = data + '\t'
            data = data + '\n'
        # Create text data object
        clipboard = wx.TextDataObject()
        # Set data object value
        clipboard.SetText(data)
        # Put the data in the clipboard
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(clipboard)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox("Can't open the clipboard", "Error")
           
    def paste(self):
        clipboard = wx.TextDataObject()
        if wx.TheClipboard.Open():
            wx.TheClipboard.GetData(clipboard)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox("Can't open the clipboard", "Error")
        data = clipboard.GetText()
        table = []
        y = -1
        # Convert text in a array of lines
        for r in data.splitlines():
            y = y +1
            x = -1
            # Convert c in a array of text separated by tab
            for c in r.split('\t'):
                x = x +1
                self.SetCellValue(self.GetGridCursorRow() + y, self.GetGridCursorCol() + x, c)
               
    def delete(self):
        # Number of rows and cols
        rows = self.GetSelectionBlockBottomRight()[0][0] - self.GetSelectionBlockTopLeft()[0][0] + 1
        cols = self.GetSelectionBlockBottomRight()[0][1] - self.GetSelectionBlockTopLeft()[0][1] + 1
        # Clear cells contents
        for r in range(rows):
            for c in range(cols):
                self.SetCellValue(self.GetSelectionBlockTopLeft()[0][0] + r, self.GetSelectionBlockTopLeft()[0][1] + c, '')
