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


# Grid search

# Python modules
from scipy import sum
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.mlab import griddata
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import pylab
from numpy import meshgrid, linspace, array
from os import sep, makedirs
from time import sleep
import wx


# NESSY modules
from curvefit.chi2 import Chi2_container
from elements.variables import Pi, Constraints_container
from math_fns.models import limit_entries, model_2, model_3, model_4, model_5, model_6





def gridsearch(base_dir='', data=None, experiment='cpmg', output=None, fileroot=None, frequencies=None, grid_size=[0.2, 5, 0.005, 0.002, 0.001], INI_R2=None, model=3, output_tree=None, output1=None, savecont=None, variance=None, globalfit=False):
    """Function to perform grid search to find initial parameters.

    data:               Data as list of x and y values  ([[x], [y]).
    experiment:         Type of experiment: 'cpmg' for CPMG relaxation dispersion; 'r1p' for R1rhi spin lock experiments.
    grid_size:          Increment steps of data grid. List of floats: [R2, kex, dw, pb].
    """

    # FIXME
    if model in [1]: return

    # chi2 container as dictionary
    chi2 = {'chi2':[], 'kex':[], 'dw':[], 'pb':[], 'phi':[], 'kex2':[], 'phi2':[], 'dw2':[], 'pc':[]}

    # function container
    func = {'2':model_2, '3':model_3, '4':model_4, '5':model_5, '6':model_6}

    # Number of grid points
    kex_points = int((Constraints_container.kex[model-1][1] - Constraints_container.kex[model-1][0]) / grid_size[1])
    dw_points = int((Constraints_container.dw[model-1][1] - Constraints_container.dw[model-1][0]) / grid_size[2])
    pb_points = int((Constraints_container.pb[model-1][1] - Constraints_container.pb[model-1][0]) / grid_size[3])
    phi_points = int((Constraints_container.phi[model-1][1] - Constraints_container.phi[model-1][0]) / grid_size[4])
    phi2_points = int((Constraints_container.phi2[model-1][1] - Constraints_container.phi2[model-1][0]) / grid_size[4])
    kex2_points = int((Constraints_container.kex2[model-1][1] - Constraints_container.kex2[model-1][0]) / grid_size[1])
    pc_points = int((Constraints_container.pc[model-1][1] - Constraints_container.pc[model-1][0]) / grid_size[3])
    dw2_points = int((Constraints_container.dw2[model-1][1] - Constraints_container.dw2[model-1][0]) / grid_size[2])

    # R2 independant
    r2_points = 1

    # Remove offset of R2
    y = []
    for i in range(len(data[1])):
        y.append([])
        for j in range(len(data[1][i])):
            y[i].append(data[1][i][j] - min(data[1][i]))

    # convert to arrays
    for i in range(len(y)):     y[i] = array(y[i])

    # Output
    wx.CallAfter(output.AppendText, '\n\n------------------------------\n       GRID SEARCH\n------------------------------\n')

    # loop over R2
    for l_r2 in range(r2_points):
        # R2 value
        r2 = 0.0      # fit only Rex

        # loop over kex
        for l_kex in range(kex_points):
            # kex value
            kex = Constraints_container.kex[model-1][0] + l_kex * grid_size[1]

            # Models 3 and 6

            # loop over dw
            for l_dw in range(dw_points):
                # dw value
                dw = Constraints_container.dw[model-1][0] + l_dw * grid_size[2]

                # loop over pb
                for l_pb in range(pb_points):
                    # pb value
                    pb = Constraints_container.pb[model-1][0] + l_pb * grid_size[3]

                    # error container
                    error = []

                    # model 3 and 5
                    if model in [3, 6]:
                        # skip if 0 is in p
                        if 0 in [kex, dw, pb]: continue

                        # feedback
                        wx.CallAfter(output.AppendText, 'Grid search (kex, dw, pb): '+str(kex)[0:9]+', '+str(dw)[0:7]+', '+str(pb)[0:7]+'\n')
                        sleep(0.0001)
                        limit_entries(output)

                        # calculate chi2
                        # loop over experiments
                        for i in range(len(data[0])):
                            # parameters
                            # Individual fit
                            if frequencies == None:     p = [r2, kex, dw, pb]

                            # global and cluster fit
                            else:                       p = [r2, kex, dw*float(frequencies[i].GetValue()) * 2 * Pi, pb]

                            #Chi2 function
                            if 'cpmg' in experiment:
                                # individual fit
                                if frequencies == None:     err_tmp = ((y[i]-func[str(model)](data[0][i], p))/variance)**2

                                # global and cluster fit
                                else:                       err_tmp = ((y[i]-func[str(model)](data[0][i], p))/variance[i])**2


                            # combine errors
                            error.extend(err_tmp)

                        # calculate chi2
                        chi2_tmp = sum(error)

                        # save chi2 and parameters
                        chi2['chi2'].append(chi2_tmp)
                        chi2['kex'].append(kex)
                        chi2['dw'].append(dw)
                        chi2['pb'].append(pb)

                    # model 5
                    if model == 5:
                        # loop over dw
                        for l_dw2 in range(dw2_points):
                            # dw2 value
                            dw2 = Constraints_container.dw2[model-1][0] + l_dw2 * grid_size[2]

                            # loop over kex2
                            for l_kex2 in range(kex2_points):
                                # kex value
                                kex2 = Constraints_container.kex2[model-1][0] + l_kex2 * grid_size[1]

                                # loop over pb
                                for l_pc in range(pc_points):
                                    # pb value
                                    pc = Constraints_container.pc[model-1][0] + l_pc * grid_size[3]

                                    # skip if 0 is in p
                                    if 0 in [kex, dw, pb, kex2, dw2, pc]: continue

                                    # feedback
                                    wx.CallAfter(output.AppendText, 'Grid search (kex, dw, pb, kex2, dw2, pc): '+str(kex)[0:9]+', '+str(dw)[0:7]+', '+str(pb)[0:7]+', '+str(kex2)[0:9]+', '+str(dw2)[0:7]+', '+str(pc)[0:7]+'\n')
                                    sleep(0.0001)
                                    limit_entries(output)

                                    # calculate chi2
                                    # loop over experiments
                                    for i in range(len(data[0])):
                                        # parameters
                                        # Individual fit
                                        if frequencies == None:     p = [r2, kex, dw, pb, kex2, dw2, pc]

                                        # global and cluster fit
                                        else:                       p = [r2, kex, dw*float(frequencies[i].GetValue()) * 2 * Pi, pb, kex2, dw2*float(frequencies[i].GetValue()) * 2 * Pi, pc]

                                        #Chi2 function
                                        if 'cpmg' in experiment:
                                            # individual fit
                                            if frequencies == None:     err_tmp = ((y[i]-func[str(model)](data[0][i], p))/variance)**2

                                            # global and cluster fit
                                            else:                       err_tmp = ((y[i]-func[str(model)](data[0][i], p))/variance[i])**2


                                        # combine errors
                                        error.extend(err_tmp)

                                    # calculate chi2
                                    chi2_tmp = sum(error)

                                    # save chi2 and parameters
                                    chi2['chi2'].append(chi2_tmp)
                                    chi2['kex'].append(kex)
                                    chi2['dw'].append(dw)
                                    chi2['pb'].append(pb)
                                    chi2['kex2'].append(kex2)
                                    chi2['dw2'].append(dw2)
                                    chi2['pc'].append(pc)

            # Models 2 and 4
            for l_phi in range(phi_points):
                # phi value
                phi = Constraints_container.phi[model-1][0] + l_phi * grid_size[4]

                # error container
                error = []

                # skip if 0 is in p
                if 0 in [phi, kex]: continue

                if model == 2:
                    # feedback
                    wx.CallAfter(output.AppendText, 'Grid search (phi, kex): '+str(phi)[0:9]+', '+str(kex)[0:9]+'\n')
                    sleep(0.0001)
                    limit_entries(output)

                    # calculate chi2
                    # loop over experiments
                    for i in range(len(data[0])):
                        # Individual fit
                        if frequencies == None:     p = [r2, phi, kex]

                        # global and cluster fit
                        else:                       p = [r2, phi*float(frequencies[i].GetValue()) * 2 * Pi*float(frequencies[i].GetValue()) * 2 * Pi, kex]


                        #Chi2 function
                        if 'cpmg' in experiment:
                            # individual fit
                            if frequencies == None:     err_tmp = ((y[i]-func[str(model)](data[0][i], p))/variance)**2

                            # global and cluster fit
                            else:                       err_tmp = ((y[i]-func[str(model)](data[0][i], p))/variance[i])**2

                        # combine errors
                        error.extend(err_tmp)

                    # calculate chi2
                    chi2_tmp = sum(error)

                    # save chi2 and parameters
                    chi2['chi2'].append(chi2_tmp)
                    chi2['kex'].append(kex)
                    chi2['phi'].append(phi)

                # model 4
                if model == 4:
                    for l_phi in range(phi_points):
                        # phi value
                        phi = Constraints_container.phi[model-1][0] + l_phi * grid_size[4]

                        # phi2 value
                        for l_phi2 in range(phi2_points):
                            # phi value
                            phi2 = Constraints_container.phi2[model-1][0] + l_phi2 * grid_size[4]

                            # kex2 value
                            for l_kex2 in range(kex2_points):
                                # kex2 value
                                kex2 = Constraints_container.kex2[model-1][0] + l_kex2 * grid_size[1]

                                # feedback
                                wx.CallAfter(output.AppendText, 'Grid search (phi, kex, phi2, kex2): '+str(phi)[0:9]+', '+str(kex)[0:9]+', '+str(phi2)[0:9]+', '+str(kex2)[0:9]+'\n')
                                sleep(0.0001)
                                limit_entries(output)

                                # calculate chi2
                                # loop over experiments
                                for i in range(len(data[0])):
                                    # Individual fit
                                    if frequencies == None:     p = [r2, phi, kex, phi2, kex2]

                                    # global and cluster fit
                                    else:                       p = [r2, phi*float(frequencies[i].GetValue()) * 2 * Pi*float(frequencies[i].GetValue()) * 2 * Pi, kex, phi2*float(frequencies[i].GetValue()) * 2 * Pi*float(frequencies[i].GetValue()) * 2 * Pi, kex2]


                                    #Chi2 function
                                    if 'cpmg' in experiment:
                                        # individual fit
                                        if frequencies == None:     err_tmp = ((y[i]-func[str(model)](data[0][i], p))/variance)**2

                                        # global and cluster fit
                                        else:                       err_tmp = ((y[i]-func[str(model)](data[0][i], p))/variance[i])**2

                                    # combine errors
                                    error.extend(err_tmp)

                                # calculate chi2
                                chi2_tmp = sum(error)

                                # save chi2 and parameters
                                chi2['chi2'].append(chi2_tmp)
                                chi2['kex'].append(kex)
                                chi2['phi'].append(phi)
                                chi2['kex2'].append(kex2)
                                chi2['phi2'].append(phi2)

    # select best parameters
    min_chi2 = 10000000000000000000000
    index = 0

    # loop over chi2
    for i in range(len(chi2['chi2'])):
        if chi2['chi2'][i] < min_chi2:
            min_chi2 = chi2['chi2'][i]
            index = i

    # create parameters
    if globalfit:
        # global fit
        p = []

        # Models 3 and 6
        if model in [3, 6]:
            p.append(chi2['kex'][index])
            p.append(chi2['pb'][index])
            p.append(chi2['dw'][index])
            for i in range(0, len(data[0])):
                p.append(INI_R2[model-1])

        # Model 2
        if model == 2:
            p.append(chi2['kex'][index])
            p.append(chi2['phi'][index])
            for i in range(0, len(data[0])):
                p.append(INI_R2[model-1])

        # Model 4
        if model == 4:
            p.append(chi2['kex'][index])
            p.append(chi2['kex2'][index])
            p.append(chi2['phi'][index])
            p.append(chi2['phi2'][index])
            for i in range(0, len(data[0])):
                p.append(INI_R2[model-1])

        # Model 5
        if model == 5:
            p.append(chi2['kex'][index])
            p.append(chi2['kex2'][index])
            p.append(chi2['pb'][index])
            p.append(chi2['pc'][index])
            p.append(chi2['dw'][index])
            p.append(chi2['dw2'][index])
            for i in range(0, len(data[0])):
                p.append(INI_R2[model-1])

    else:
        # Individual fit
        if not 'cluster' in experiment:

            # models 3 and 5:
            if model in [3, 6]:     p = [INI_R2[model-1], chi2['kex'][index], chi2['dw'][index], chi2['pb'][index]]

            # model 2
            if model == 2:          p = [INI_R2[model-1], chi2['phi'][index], chi2['kex'][index]]

            # model 4
            if model == 4:          p = [INI_R2[model-1], chi2['phi'][index], chi2['kex'][index], chi2['phi2'][index], chi2['kex2'][index]]

            # model 5
            if model == 5:          p = [INI_R2[model-1], chi2['kex'][index], chi2['dw'][index], chi2['pb'][index], chi2['kex2'][index], chi2['dw2'][index], chi2['pc'][index]]

        # cluster analysis
        else:
            p = []

            # models 3 and 6
            if model in [3, 6]:
                p = [chi2['kex'][index], chi2['pb'][index]]
                for i in range(len(data[0])):
                    p.append(chi2['dw'][index])
                    p.append(INI_R2[model-1])

            # model 2
            if model == 2:
                p = [chi2['kex'][index]]
                for i in range(len(data[0])):
                    p.append(chi2['phi'][index])
                    p.append(INI_R2[model-1])

            # model 4
            if model == 4:
                p = [chi2['kex'][index], chi2['kex2'][index]]
                for i in range(len(data[0])):
                    p.append(chi2['phi'][index])
                    p.append(chi2['phi2'][index])
                    p.append(INI_R2[model-1])

            # model 5
            if model == 5:
                p = [chi2['kex'][index], chi2['kex2'][index], chi2['pb'][index], chi2['pc'][index]]
                for i in range(len(data[0])):
                    p.append(chi2['dw'][index])
                    p.append(chi2['dw2'][index])
                    p.append(INI_R2[model-1])

    # output
    if model == 2:          wx.CallAfter(output.AppendText, '\n\n------------------------------\nCompleted.\n('+str(chi2['phi'][index])[0:6]+', '+str(chi2['kex'][index])[0:6]+')\n------------------------------\n\n')
    elif model == 4:        wx.CallAfter(output.AppendText, '\n\n------------------------------\nCompleted.\n('+str(chi2['phi'][index])[0:6]+', '+str(chi2['kex'][index])[0:6]+str(chi2['phi2'][index])[0:6]+', '+str(chi2['kex2'][index])[0:6]+')\n------------------------------\n\n')
    elif model in [3, 6]:   wx.CallAfter(output.AppendText, '\n\n------------------------------\nCompleted.\n('+str(chi2['kex'][index])[0:6]+', '+str(chi2['dw'][index])[0:5]+', '+str(chi2['pb'][index])[0:5]+')\n------------------------------\n\n')
    elif model == 5:        wx.CallAfter(output.AppendText, '\n\n------------------------------\nCompleted.\n('+str(chi2['kex'][index])[0:6]+', '+str(chi2['dw'][index])[0:5]+', '+str(chi2['pb'][index])[0:5]+', '+str(chi2['kex2'][index])[0:6]+', '+str(chi2['dw2'][index])[0:5]+', '+str(chi2['pc'][index])[0:5]+')\n------------------------------\n\n')

    # only create surface plot for models 2, 3, 6 (2 state models)
    if not model in [2, 3, 6]:  return p

    # create surface plot
    # read optimal index
    x = []
    y = []
    z = []
    for i in range(len(chi2['chi2'])):
            # match pb
            if model in [3, 6]:
                if not chi2['pb'][i] == chi2['pb'][index]:  continue

            # Store entries
            x.append(chi2['kex'][i])
            if model == 2:  y.append(chi2['phi'][i])
            else:           y.append(chi2['dw'][i])
            z.append(chi2['chi2'][i])

    # create plot
    chi2_surface_plot(x, y, z, fileroot, 'svg', base_dir, output_tree, output1, savecont)

    # return value
    return p



def chi2_surface_plot(x, y, z, fileroot, vec, base_dir, output, output1, savecont):
    """Function to create Chi2 surface plot after grid search."""

    # Create folders
    # png
    pngdir = base_dir+sep+'chi2_surface'+sep+'png'
    try:
        makedirs(pngdir)
    except:
        a = 0

    # vector
    vecdir = base_dir+sep+'chi2_surface'+sep+vec
    try:
        makedirs(vecdir)
    except:
        a = 0

    # cvs
    csvdir = base_dir+sep+'chi2_surface'+sep+'csv'
    try:
        makedirs(csvdir)
    except:
        a = 0

    # draw plot
    # Create 3d axes
    fig = pylab.figure()
    ax = Axes3D(fig)

    # Prepare grid
    xi = linspace(min(x), max(x))
    yi = linspace(min(y), max(y))

    # create grid
    X, Y = meshgrid(xi, yi)
    Z = griddata(x, y, z, xi, yi)

    # plot
    #ax.plot(x, y, z, '.')
    surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.jet, linewidth=0, antialiased=False)

    # limit
    ax.set_zlim3d(min(z), max(z))

    # labels
    ax.set_xlabel('kex [1/s]', fontsize=13, weight='bold')
    ax.set_ylabel('dw [ppm]', fontsize=13, weight='bold')
    ax.set_zlabel('chi2', fontsize=13, weight='bold')

    # color bar
    fig.colorbar(surf, shrink=0.5, aspect=20)

    # save plot
    pylab.savefig(pngdir+sep+fileroot+'.png', dpi = 72, transparent = True)

    # Create vector plot
    pylab.savefig(vecdir+sep+fileroot+'.'+vec)

    # Crear plot
    pylab.cla()     # clear the axes
    pylab.close()   #clear figure

    # Store 3D plots
    output.AppendItem (output1, pngdir+sep+fileroot+'.png', 0)

    # Store 3d plots
    savecont.append(pngdir+sep+fileroot+'.png')

    # csv file
    file = open(csvdir+sep+fileroot+'.csv', 'w')

    # header
    file.write('kex [1/s],dw [ppm],chi2\n')

    # frite entries
    for i in range(len(x)):
        file.write(str(x[i])+';'+str(y[i])+';'+str(z[i])+'\n')

    # close file
    file.close()


