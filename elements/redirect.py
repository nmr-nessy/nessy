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
try:
    import thread as _thread
except ImportError:
    import _thread
from conf.path import ERROR_PIC



class NESSY_error(wx.Frame):
    def __init__(self, *args, **kwds):
        # open flag
        self.is_open = False

        # begin wxGlade: error.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP
        wx.Frame.__init__(self, *args, **kwds)
        self.SetTitle("NESSY Error")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(ERROR_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        # Sizer
        mainsizer = wx.BoxSizer(wx.VERTICAL)

        # Header
        self.Header = wx.StaticText(self, -1, "The following error occured:")
        self.Header.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        mainsizer.Add(self.Header, 0, wx.ALL, 5)

        # Message
        self.text = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)
        self.text.SetMinSize((500, 250))
        mainsizer.Add(self.text, 0, wx.ALL, 5)

        # Button
        self.ok_button = wx.Button(self, -1, "Ok")
        self.Bind(wx.EVT_BUTTON, self.close, self.ok_button)
        mainsizer.Add(self.ok_button, 0, wx.ALL, 5)

        # Pack frame
        self.SetSizer(mainsizer)
        mainsizer.Fit(self)
        self.Layout()
        self.Center()


    def close(self, event):
        # Clear entry
        self.text.SetValue('')

        # open flag
        self.is_open = False

        # Hide Frame
        self.Hide()



class Redirect_text(object):
    """Class to redirect error in report panel"""
    def __init__(self, object):
        self.error_message = object[0]
        self.report = object[1]
        self.max = object[2]
        self.pageno = object[3]


    def write(self, string):
        # Go to report tab
        self.report.SetSelection(self.max-self.pageno)

        # Write error message
        wx.CallAfter(self.error_message.AppendText, 'NESSY error> '+string.replace('\n', '')+'\n')
