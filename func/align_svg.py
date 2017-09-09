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

# script to craete multiple alignment svg image


# Python modules
from os import sep
import wx

# NESSY modules
from conf.path import NESSY_PIC, IMPORT_DATA_SIDE_PIC
from conf.filedialog import savefile
from conf.message import error_popup, message


class MyTextTarget(wx.TextDropTarget):
    def __init__(self, target_widget, choices):
        wx.TextDropTarget.__init__(self)
        self.target_widget = target_widget

        # choices list
        self.choices = choices

        self.text_obj = wx.TextDataObject()
        self.SetDataObject(self.text_obj)

    def OnData(self, x, y, default):  #called automatically on drop
        self.GetData()
        text = self.text_obj.GetText()
        text = text.replace('file:'+sep+sep, '')
        text = text.replace('\n', '')
        text = text.replace('\r', '')

        # append choices
        self.choices.append(str(text))

        end_of_list = self.target_widget.GetCount()
        self.target_widget.InsertItems([text], end_of_list)

        return default


class Align_svg(wx.Frame):

    def __init__(self, main, *args, **kwds):
        # connect
        self.main = main

        # choices
        self.choices = self.main.results_model1+self.main.results_model2+self.main.results_model3+self.main.results_model4+self.main.results_model5
        # replace png
        for i in range(0, len(self.choices)):
            self.choices[i] = self.choices[i].replace('png', self.main.PLOTFORMAT.replace('.', ''))

        # override choices if added upon start up
        if self.main.align_svg_files:
            self.choices = self.main.align_svg_files

        # build dialog
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.Centre()
        self.build()

        # image size
        self.size = [576, 432]


    def add_file(self, event):
        file = savefile('Select output file.', str(self.main.proj_folder), '', 'svg files (*.svg)|*.svg', self)
        if file:
            self.filename.SetValue(file)

        # brings dialog to top
        self.Raise()


    def build(self):
        # mainframe
        mainframe = wx.BoxSizer(wx.HORIZONTAL)

        # Image
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(IMPORT_DATA_SIDE_PIC, wx.BITMAP_TYPE_ANY))
        mainframe.Add(self.bitmap, 0, wx.ALL, 5)

        # right sizer
        rightframe = wx.BoxSizer(wx.VERTICAL)

        # title
        self.title = wx.StaticText(self, -1, "Create SVG Image of multiple plots")
        self.title.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        rightframe.Add(self.title, 0, wx.ALL, 5)

        # columns
        sizer_col = wx.BoxSizer(wx.HORIZONTAL)
        self.label_col = wx.StaticText(self, -1, "Numbers of columns:")
        self.label_col.SetMinSize((170, 17))
        sizer_col.Add(self.label_col, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)

        self.num_col = wx.SpinCtrl(self, -1, "1", min=1, max=100)
        self.num_col.SetMinSize((70, 23))
        sizer_col.Add(self.num_col, 0, wx.RIGHT, 5)
        rightframe.Add(sizer_col, 0, 0, 0)

        # selection
        sizer_files = wx.BoxSizer(wx.HORIZONTAL)
        self.label_files = wx.StaticText(self, -1, "Select plots to combine:")
        self.label_files.SetMinSize((170, 17))
        sizer_files.Add(self.label_files, 0, wx.LEFT, 5)
        self.files = wx.ListBox(self, -1, choices=self.choices, style = wx.LB_MULTIPLE)
        target = MyTextTarget(self.files, self.choices)  #MyTextTarget defined below
        self.files.SetDropTarget(target)
        self.files.SetMinSize((500, 200))
        sizer_files.Add(self.files, 0, wx.RIGHT, 5)
        rightframe.Add(sizer_files, 0, 0, 0)

        # outputfile
        sizer_out = wx.BoxSizer(wx.HORIZONTAL)
        self.label_out = wx.StaticText(self, -1, "Output file:")
        self.label_out.SetMinSize((170, 17))
        sizer_out.Add(self.label_out, 0, wx.LEFT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5)
        folder = ''
        if not str(self.main.proj_folder.GetValue()) == '':
            folder = str(self.main.proj_folder.GetValue())+sep+'ensemble.svg'
        self.filename = wx.TextCtrl(self, -1, folder)
        self.filename.SetMinSize((470, 23))
        sizer_out.Add(self.filename, 0, wx.RIGHT|wx.TOP, 5)
        self.add_button = wx.Button(self, -1, "+")
        self.add_button.SetMinSize((25, 23))
        self.Bind(wx.EVT_BUTTON, self.add_file, self.add_button)
        sizer_out.Add(self.add_button, 0, wx.TOP, 5)
        rightframe.Add(sizer_out, 0, 0, 0)

        # buttons
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.button_create = wx.Button(self, -1, "Create")
        self.Bind(wx.EVT_BUTTON, self.create, self.button_create)
        sizer_buttons.Add(self.button_create, 0, wx.ALL, 5)
        self.button_close = wx.Button(self, -1, "Close")
        self.Bind(wx.EVT_BUTTON, self.close, self.button_close)
        sizer_buttons.Add(self.button_close, 0, wx.ALL, 5)
        rightframe.Add(sizer_buttons, 0, wx.LEFT, 0)

        # pack frame
        mainframe.Add(rightframe, 0, 0, 0)
        self.SetSizer(mainframe)
        mainframe.Fit(self)
        self.Layout()


    def create(self, event):
        # outputname
        if str(self.filename.GetValue()) == '':
            error_popup('No output file selected!', self)
            return
        else:
            outputname = str(self.filename.GetValue())

        # read selections
        selections = self.files.GetSelections()

        # nothing selected
        if len(selections) < 1:
            error_popup('No plots selected!', self)
            return
        else:
            files = []
            for i in range(0, len(selections)):
                files.append(self.choices[selections[i]])

        # sort files
        try:
            files = self.sort_list(files)
        except:
            a = 'THIS WAS NOT A NESSY FILE! WHO CARES!'

        # rows (which are the columns!!!)
        rows = int(self.num_col.GetValue())

        # create file
        file = open(outputname, 'w')

        # calculate columns
        columns = len(files) / rows

        # avoid not enough columns
        a = float(len(files)) / float(rows)
        if columns < a:
            columns += 1

        # print header
        header = '<?xml version="1.0" standalone="no"?>\n<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"\n  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n<!-- Created by NESSY -->\n<svg width="'+str(self.size[0]*rows)+'pt" height="'+str(self.size[1]*columns)+'pt" viewBox="0 0 '+str(self.size[0]*rows)+' '+str(self.size[1]*columns)+'"\n   xmlns="http://www.w3.org/2000/svg"\n   xmlns:xlink="http://www.w3.org/1999/xlink"\n   version="1.1"\n   id="svg1">\n'
        file.write(header)

        # craete white background
        bg = '<g id="patch1">\n<path style="fill: #ffffff; stroke: #ffffff; stroke-width: 1.000000; stroke-linejoin: round; stroke-linecap: square;  opacity: 1.000000"  d="M0.000000 '+str(self.size[1]*columns)+'.000000L'+str(self.size[0]*rows)+'.000000 '+str(self.size[1]*columns)+'.000000L'+str(self.size[0]*rows)+'.000000 0.000000\nL0.000000 0.000000L0.000000 '+str(self.size[1]*columns)+'.000000"/>\n</g>\n'
        file.write(bg)

        # create alignment
        # coordinates
        x = 0
        y = 0

        # loop over images
        for im in range(0, len(files)):

            # read file
            data = self.readfile(files[im])

            # write entries
            write_flag = False
            for i in range(0, len(data)):

                # replace identity
                if 'figure1' in data[i]:
                    data[i]=data[i].replace('<g id="figure1">', '<g transform="translate('+str(x)+', '+str(y)+')"\n   id="figure'+str(im)+'">')

                # is not header
                if 'id="' in data[i] and not write_flag:
                    write_flag = True
                    continue

                # avoid termination of svg
                if '</svg>' in data[i]:
                    continue

                # skip entry if it is from header
                if not write_flag:
                    continue

                # write entry
                file.write(data[i])

            # add coordinates
            x = x + (self.size[0]-20)

            # start new line
            if x >= rows * (self.size[0]-20):
                x = 0
                y = y + self.size[1]

        # end svg
        file.write('</svg>')

        # close file
        file.close()

        # report
        message('Succesfully created file:\n\n'+outputname, self)


    def close(self, event): # wxGlade: Align_csv.<event_handler>
        self.Destroy()


    def readfile(self, filename):
        # open file and read entries
        file = open(filename, 'r')

        # read and store entries
        entries = []
        skip = False    # skip flag
        for line in file:
            if line == '' or line == '\n':
                continue

            # remove background
            if '<g id="patch1">' in line:
                skip = True
                continue

            # reactivate
            if '</g>' in line and skip:
                skip = False
                continue

            # skip
            if skip:
                continue

            # store entries
            entries.append(line)

            # read imagesize
            if '<svg width="' in line:
                tmp = line.split('"')
                width = int(tmp[1].replace('pt', ''))
                height = int(tmp[3].replace('pt', ''))
                self.size = [width, height]

        # close file
        file.close()

        return entries


    def sort_list(self, files):
        # sort file list
        for i in range(0, len(files)):
            # detect residue
            filenamepath = files[i].split(sep)
            filename = filenamepath[len(filenamepath)-1]
            residue = filename.split('_')[4]

            # compare to other entries
            for j in range(i, len(files)):
                # detect residue
                filenamepath1 = files[j].split(sep)
                filename1 = filenamepath1[len(filenamepath1)-1]
                residue1 = filename1.split('_')[4]

                # compare
                if int(residue) > int(residue1):
                    save = files[i]
                    files[i] = files[j]
                    files[j] = save

        return files
