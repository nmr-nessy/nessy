#################################################################################
#                                                                               #
#   (C) 2011 Michael Bieri                                                      #
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
from scipy import array


def estimate(self, model=None, isglobal=None, cluster=None, factor=1):
    """Function, which returns initial guess for curve fit to models 1 - 6.

    self:           container of referring NESSY dialog, which contains NESSY main frame as self.main.
    model:          Model number (1-6).
    isglobal:       If single fit: None or False.
                    If global fit: Number of experiments (int).
    factor:         Product of 2 * Pi * Heteronucleus Frequency
    """

    # No model selected
    if not model:
        print('\nNo model selected. Aborting estimation.\n')
        return

    # Global fit
    if isglobal and not cluster:
        # estimation container
        estimation = []

        # [R2(i)]
        if model == 1:
            for i in range(0, isglobal):
                estimation.append(float(self.main.INI_R2[model-1]))

        # [kex, Phi, R2(i)]
        if model == 2:
            estimation.append(self.main.INI_kex[model-1])
            estimation.append(float(self.main.INI_phi[model-1]))
            for i in range(0, isglobal):
                estimation.append(float(self.main.INI_R2[model-1]))

        # [kex1, pb, dw, R2(i)]
        if model == 3:
            estimation.append(self.main.INI_kex[model-1])
            estimation.append(self.main.INI_pb[model-1])
            estimation.append(self.main.INI_dw[model-1])
            for i in range(0, isglobal):
                estimation.append(float(self.main.INI_R2[model-1]))

        # [kex1, kex2, r2(i), phi1(i), ph2(i)]
        if model == 4:
            estimation.append(self.main.INI_kex[model-1])
            estimation.append(self.main.INI_kex2[model-1])
            estimation.append(float(self.main.INI_phi[model-1]))
            estimation.append(float(self.main.INI_phi2[model-1]))
            for i in range(0, isglobal):
                estimation.append(float(self.main.INI_R2[model-1]))

        # [kex1, pb1, kex2, pb2, dw1(i), dw1(i), R2(i)]
        if model == 5:
            estimation.append(self.main.INI_kex[model-1])
            estimation.append(self.main.INI_kex2[model-1])
            estimation.append(self.main.INI_pb[model-1])
            estimation.append(self.main.INI_pc[model-1])
            estimation.append(self.main.INI_dw[model-1])
            estimation.append(self.main.INI_dw2[model-1])
            for i in range(0, isglobal):
                estimation.append(float(self.main.INI_R2[model-1]))

        # [kex1, pb, dw, R2(i)]
        if model in [6, 7]:
            estimation.append(self.main.INI_kex[6-1])
            estimation.append(self.main.INI_pb[6-1])
            estimation.append(self.main.INI_dw[6-1])
            for i in range(0, isglobal):
                estimation.append(float(self.main.INI_R2[6-1]))

    # Cluster analysis
    if cluster:
        # Model 2
        if model == 2:
            estimation = [float(self.main.INI_kex[model-1])]
            for i in range(cluster):
                estimation.append(float(self.main.INI_phi[model-1]))
                estimation.append(float(self.main.INI_R2[model-1]))

        # model 3
        elif model == 3:
            estimation = [float(self.main.INI_kex[model-1]), float(self.main.INI_pb[model-1])]
            for i in range(cluster):
                estimation.append(float(self.main.INI_dw[model-1]))
                estimation.append(float(self.main.INI_R2[model-1]))

        # model 4
        elif model == 4:
            estimation = [float(self.main.INI_kex[model-1]), float(self.main.INI_kex2[model-1])]
            for i in range(cluster):
                estimation.append(float(self.main.INI_phi[model-1]))
                estimation.append(float(self.main.INI_phi2[model-1]))
                estimation.append(float(self.main.INI_R2[model-1]))

        # model 5
        elif model == 5:
            estimation = [float(self.main.INI_kex[model-1]), float(self.main.INI_kex2[model-1]), float(self.main.INI_pb[model-1]), float(self.main.INI_pc[model-1])]
            for i in range(cluster):
                estimation.append(float(self.main.INI_dw[model-1]))
                estimation.append(float(self.main.INI_dw[model-1]))
                estimation.append(float(self.main.INI_R2[model-1]))

        # model 6
        elif model in [6, 7]:
            estimation = [float(self.main.INI_kex[6-1]), float(self.main.INI_pb[6-1])]
            for i in range(cluster):
                estimation.append(float(self.main.INI_dw[6-1]))
                estimation.append(float(self.main.INI_R2[6-1]))

    # return estimation
    return array(estimation)
