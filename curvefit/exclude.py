#################################################################################
#                                                                               #
#   (C) 2010 Michael Bieri                                                      #
#   (C) 2013 Edward d'Auvergne                                                  #
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

# Function to estimnate if exchange is present



def exclude(r2effs, cpmgfreqs, min_diff, prior=False):
        '''Function to exclude if difference betweendata is not big enougt.

        r2effs:     List of R2eff values
        cpmgfreqs:  List of CPMG values
        min_diff:   Minimal difference between R2eff of lowest and highest CPMG frequency as STRING'''

        # Minimal difference is twice the error.
        if min_diff in ['error', 'Error']:
            min_diff = 0.1

        # No minimal difference criteria
        elif min_diff in ['0', 'None']:
            return False

        # value was specified
        else:
            min_diff = float(min_diff)

        # excange is expected, if at least 1 experiment has bigger difference
        has_exchange = False

        # detect max R2eff
        max_index = 0

        # avoid beeing empty
        while cpmgfreqs[max_index] == '':
            max_index = max_index + 1

        # loop over cpmg freqs
        for freq in range(0, len(cpmgfreqs)):
            # stop if cpmg freq is not set
            if str(cpmgfreqs[freq]) == '':
                continue

            # compare highest cpmg freq so far with actual cpmg freq
            if float(cpmgfreqs[max_index]) < float(cpmgfreqs[freq]):
                # adjust index of bigger cpmg freq, only is r2eff is present
                if cpmgfreqs[freq]:
                    max_index = freq

        # detect min R2eff
        min_index = 0

        # avoid beeing reference spectrum
        while float(cpmgfreqs[min_index]) == 0.0:
            min_index = min_index + 1

        # loop over cpmg freqs
        for freq in range(0, len(cpmgfreqs)):
            # stop if cpmg freq is not set or reference spectrum
            if str(cpmgfreqs[freq]) in ['0', '']:
                continue

            # compare highest cpmg freq so far with actual cpmg freq
            if float(cpmgfreqs[min_index]) > float(cpmgfreqs[freq]):
                # adjust index of smaller cpmg freq, only is r2eff is present
                if cpmgfreqs[freq]:
                    min_index = freq

        # read R2effs
        r2eff_max = r2effs[max_index]
        r2eff_min = r2effs[min_index]

        # difference
        diff = r2eff_min - r2eff_max

        # compare difference
        if diff > min_diff:
            # has exchnage, don't exclude
            return False

        # no exhcnage expected, exclude
        else:
            return True
