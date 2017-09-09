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


# Path of images

# Python module imports.
import __main__
from os import getenv, sep
from sys import path

# Root path
# Python files
ROOT = __main__.install_path +sep
# Compiled programe in one file
#ROOT = ''#str(path[len(path)-1]).split('?')[0].replace('nessy', '') + sep

# GUI image path

NESSY_PIC = ROOT+"pics"+sep+"NESSY.png"
FRONT_PIC = ROOT+"pics"+sep+"wave.png"

# Icons

OPEN_PIC = ROOT+"pics"+sep+"Open.png"
SAVE_PIC = ROOT+"pics"+sep+"Save_As.png"
REFRESH_PIC = ROOT+"pics"+sep+"Add.png"
BACK_ICON = ROOT+"pics"+sep+"Back.png"
FORWARD_PIC = ROOT+"pics"+sep+"Forward.png"
SELECT_PROJ_FOLDER = ROOT+"pics"+sep+"Project_folder.png"
LOAD_PDB_PIC = ROOT+"pics"+sep+"Protein.png"
IMPORT_DATA_PIC = ROOT+"pics"+sep+"Import_data.png"
MULTI_IMPORT_DATA_PIC = ROOT+"pics"+sep+"multi_Import_data.png"
ABOUT_PIC = ROOT+"pics"+sep+"Help.png"
ERROR_PIC = ROOT+"pics"+sep+"Error.png"
EXIT_PIC = ROOT+"pics"+sep+"Error.png"
QUIT_PIC = ROOT+"pics"+sep+"exit.png"
MANUAL_PIC = ROOT+"pics"+sep+"menu_icon"+sep+"help-contents.png"
SETTINGS_PIC = ROOT+"pics"+sep+"menu_icon"+sep+"preferences-system.png"
SPLASH_PIC = ROOT+"pics"+sep+"NESSY_SPLASH.png"
SPLASH_EXIT_PIC = ROOT+"pics"+sep+"NESSY_SPLASH_EXIT.png"
PEAKY_PIC = ROOT+"pics"+sep+"menu_icon"+sep+"peaky.png"
LIST_PIC = ROOT+"pics"+sep+"menu_icon"+sep+"list.png"
CORRECTION_PIC = ROOT+"pics"+sep+"menu_icon"+sep+"correction.png"
BACKCALC_PIC = ROOT+"pics"+sep+"menu_icon"+sep+"back_calc.png"
PLOT_PIC = ROOT+"pics"+sep+"menu_icon"+sep+"3dplot.png"
PLOT2D_PIC = ROOT+"pics"+sep+"menu_icon"+sep+"2dplot.png"
TUTORIAL_PIC = ROOT+"pics"+sep+"menu_icon"+sep+"tutorial.png"
GNU_PIC = ROOT+"pics"+sep+"menu_icon"+sep+"GNU.png"
CONTACT_PIC = ROOT+"pics"+sep+"menu_icon"+sep+"mail.png"
COLLECT_PIC = ROOT+"pics"+sep+"Import.png"
FASTA_PIC = ROOT+"pics"+sep+"menu_icon"+sep+"fasta.png"
ADD_DATASET = ROOT+"pics"+sep+"toolbar_icon"+sep+"add_dataset.png"
N_STATE_PIC = ROOT+"pics"+sep+"menu_icon"+sep+"NESSY.png"
N_STATE_FORMULA = ROOT+"pics"+sep+"r2eff.png"
N_STATE_FORMULA_SLOW = ROOT+"pics"+sep+"r2eff_model3.png"
SYNTHETIC_PIC = ROOT+"pics"+sep+"synthetic_data.png"
SETTINGS_SIDE_PIC = ROOT+"pics"+sep+"settings.png"
PLOT3D_SIDE_PIC = ROOT+"pics"+sep+"3dplot.png"
PLOT2D_SIDE_PIC = ROOT+"pics"+sep+"2dplot.png"
FREQ_PIC = ROOT+"pics"+sep+"freq.png"
IMPORT_DATA_SIDE_PIC = ROOT+"pics"+sep+"import_data_side.png"
PLOT_SIDE_PIC = ROOT+"pics"+sep+"plot_side.png"
MISSING_PIC = ROOT+"pics"+sep+"missing.png"
CHECKED_PIC = ROOT+"pics"+sep+"checked.png"
PAPB = ROOT+"pics"+sep+"papb.png"
dG =ROOT+"pics"+sep+"dG.png"
dG_tr =ROOT+"pics"+sep+"dG_tr.png"
PRINT = ROOT+"pics"+sep+'toolbar_icon'+sep+'print.png'
COLORCODE_PIC = ROOT+"pics"+sep+"menu_icon"+sep+"color_code.png"
EQUATION_PIC = ROOT+"pics"+sep+"menu_icon"+sep+"equation.png"
SHIFT_DIFF_PIC = ROOT+"pics"+sep+"menu_icon"+sep+"Shift_diff.png"
