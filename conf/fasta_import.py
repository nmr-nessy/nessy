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
try:
    from urllib import urlopen
except ImportError:
    from urllib.request import urlopen
import wx

# NESSY import
from conf.path import NESSY_PIC, IMPORT_DATA_SIDE_PIC



class Import_FASTA(wx.Dialog):
    def __init__(self, gui, *args, **kwds):
        # link parameters
        self.main = gui

        # Build window
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX
        wx.Dialog.__init__(self, *args, **kwds)
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetTitle("NESSY")

        # Image
        self.topsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(IMPORT_DATA_SIDE_PIC, wx.BITMAP_TYPE_ANY))
        self.topsizer.Add(self.bitmap, 0, wx.ALL, 5)

        # main sizer
        mainsizer = wx.BoxSizer(wx.VERTICAL)

        # header
        self.label_header = wx.StaticText(self, -1, "FASTA Sequence Import", style=wx.ALIGN_CENTRE)
        self.label_header.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        mainsizer.Add(self.label_header, 0, wx.ALL|wx.ALIGN_LEFT, 5)

        # UniProt/SwissProt Name
        sizer_swissprot = wx.BoxSizer(wx.HORIZONTAL)
        self.label_swissprot = wx.StaticText(self, -1, "UniProtKB/Swiss-Prot Code:")
        self.label_swissprot.SetMinSize((215, 17))
        sizer_swissprot.Add(self.label_swissprot, 0, wx.LEFT|wx.RIGHT|wx.TOP, 5)

        self.prot_code = wx.TextCtrl(self, -1, "")
        self.prot_code.SetMinSize((200, 20))
        sizer_swissprot.Add(self.prot_code, 0, wx.LEFT|wx.RIGHT|wx.TOP, 5)

        self.button_prot = wx.Button(self, -1, "Retreive")
        self.button_prot.SetMinSize((70, 20))
        self.button_prot.SetFont(wx.Font(7, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.Bind(wx.EVT_BUTTON, self.load_swissprot, self.button_prot)
        sizer_swissprot.Add(self.button_prot, 0, wx.RIGHT|wx.TOP, 5)

        mainsizer.Add(sizer_swissprot, 1, 0, 0)

        # Sequence box
        self.sequence = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)
        self.sequence.SetMinSize((600, 200))
        mainsizer.Add(self.sequence, 0, wx.LEFT|wx.RIGHT|wx.BOTTOM, 5)

        # Start of numbering
        sizer_start = wx.BoxSizer(wx.HORIZONTAL)
        self.label_start = wx.StaticText(self, -1, "Sequence start with residue no.:")
        self.label_start.SetMinSize((215, 17))
        sizer_start.Add(self.label_start, 0, wx.LEFT|wx.RIGHT, 5)

        self.start_seq = wx.SpinCtrl(self, -1, "", min=1, max=450, style=wx.TE_READONLY)
        self.start_seq.SetMinSize((95, 25))
        sizer_start.Add(self.start_seq, 0, wx.LEFT|wx.RIGHT, 5)
        mainsizer.Add(sizer_start, 1, 0, 0)

        # Buttons
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.button_Load = wx.Button(self, -1, "Import")
        sizer_buttons.Add(self.button_Load, 0, 0, 0)
        self.Bind(wx.EVT_BUTTON, self.load_seq, self.button_Load)
        self.button_Clear = wx.Button(self, -1, "Clear")
        sizer_buttons.Add(self.button_Clear, 0, 0, 0)
        self.Bind(wx.EVT_BUTTON, self.clear_seq, self.button_Clear)
        self.button_cancel = wx.Button(self, -1, "Close")
        self.Bind(wx.EVT_BUTTON, self.cancel, self.button_cancel)
        sizer_buttons.Add(self.button_cancel, 0, 0, 0)
        mainsizer.Add(sizer_buttons, 1, wx.BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 5)

        # Pack dialog
        self.topsizer.Add(mainsizer, 0, 0, 0)
        self.SetSizer(self.topsizer)
        self.topsizer.Fit(self)
        self.Layout()


    def add_entries(self):
        # converts fasta format to three letter code and adds sequence to data grid

        # Table of amino acid codes
        amino_acid_table = [ ['R', 'Arg'], ['H', 'His'], ['K', 'Lys'], ['D', 'Asp'], ['E', 'Glu'], ['S', 'Ser'], ['T', 'Thr'], ['N', 'Asn'], ['Q', 'Gln'], ['C', 'Cys'], ['U', 'Sec'], ['G', 'Gly'], ['P', 'Pro'],  ['A', 'Ala'], ['I', 'Ile'], ['L', 'Leu'], ['M', 'Met'], ['F', 'Phe'], ['W', 'Trp'], ['Y', 'Tyr'], ['V', 'Val'] ]

        # loop over sequence
        for i in range(0, len(self.seq)):
            code = ''
            # loop over amino acid table to identify 3 letter code
            for j in range(0, len(amino_acid_table)):
                if self.seq[i] == amino_acid_table[j][0]:
                    code = amino_acid_table[j][1]

            # keep original fasta code if not found in table
            if code == '':
                code = self.seq[i]

            # add sequence to data grid
            # loop over experiments
            for exp in range(0, self.main.NUMOFDATASETS):
                self.main.data_grid[exp].SetCellValue(i-1+int(self.start_seq.GetValue()), 0, code)


    def cancel(self, event):
        # Close dialog
        self.Destroy()
        event.Skip()


    def clear_seq(self, event):
        # clear sequence
        for i in range(0, self.main.RESNO):
            for exp in range(0, self.main.NUMOFDATASETS):
                self.main.data_grid[exp].SetCellValue(i, 0, '')


    def load_seq(self, event):
        # Import FASTA sequence
        entry = self.sequence.GetValue()

        # split entries according to lines
        entries = entry.split('\n')

        # connect sequence
        self.seq = ''
        for i in range(0, len(entries)):
            if not '>' in entries[i]:
                self.seq = self.seq + str(entries[i])

        # remove any whitespace
        self.seq = self.seq.strip()

        # convert sequence to upper case
        self.seq = self.seq.upper()

        # add entries to data grid
        self.add_entries()

        event.Skip()


    def load_swissprot(self, event):
        # load FASTA sequence from SwissProt/UniProt database
        f = urlopen('http://www.uniprot.org/uniprot/'+str(self.prot_code.GetValue())+'.fasta')
        entry = f.read()

        # Load to text box
        self.sequence.SetValue(entry)
