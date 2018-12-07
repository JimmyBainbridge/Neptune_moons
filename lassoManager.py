#!/usr/bin/env python
from __future__ import print_function
#=============================================================================#
#                                                                             #
# NAME:     lassoManager.py                                                   #
#                                                                             #
# PURPOSE:  Class to allow selection of points in a scatter plot via a lasso  #
#           tool. Assigns points to five (or fewer) catagories.               #
#                                                                             #
# MODIFIED: 28-Jun-2018 by C. Purcell                                         #
#                                                                             #
#=============================================================================#

import numpy as np
import pickle
import matplotlib.pyplot as plt
from matplotlib.widgets import LassoSelector
from matplotlib.widgets import RadioButtons
from matplotlib.path import Path
from mpl_toolkits.axes_grid1 import make_axes_locatable

#-----------------------------------------------------------------------------#
class LassoManager(object):
    """Use a lasso selector to select points on a scatter plot and assign
    to up to four labeled catagories. An integer mask of the final selection
    can be accessed via LassoManager.selMsk."""

    def __init__(self, ax, collection, labels=('a', 'b')):

        # Store the axis and data collection
        self.canvas = ax.figure.canvas
        self.collection = collection
        self.xys = collection.get_offsets()
        self.Npts = len(self.xys)

        # Store the labels and set the colours (limit to 5 labels)
        self.labels = labels[:5]
        self.rgbLst = [[0.75, 0.75, 0.0, 1.0],
                       [0.0, 0.0, 1.0, 1.0],
                       [0.0, 1.0, 0.0, 1.0],
                       [1.0, 0.0, 0.0, 1.0],
                       [1.0, 1.0, 1.0, 1.0]]
        self.fcCurrent = self.rgbLst[0]
        self.labIndxCurrent = 0

        # Array to store the final selection mask
        self.selMsk = np.ones((self.Npts), dtype=np.integer) * -1

        # Ensure that we have separate colors for each object
        self.fc = collection.get_facecolors()
        self.fc = np.tile(self.fc, self.Npts).reshape(self.Npts, -1)

        # Initialise the lasso selector
        self.lasso = LassoSelector(ax, onselect=self.onSelect)

        # Put the radio-buttons to the right
        self.divider = make_axes_locatable(ax)
        self.rax = self.divider.append_axes("right", size="30%")
        self.radio = RadioButtons(self.rax, labels=self.labels, activecolor="k")
        self.radio.on_clicked(self.onRadioClicked)

    def onSelect(self, verts):
        """Set the colours and label index mask of the current selection."""

        # Determine indices of selection
        path = Path(verts)
        indices = np.nonzero([path.contains_point(xy) for xy in self.xys])[0]

        # Set the colours and the mask
        self.fc[indices] = self.fcCurrent
        self.collection.set_facecolors(self.fc)
        self.selMsk[indices] = self.labIndxCurrent

        # Redraw
        self.canvas.draw_idle()

    def onRadioClicked(self, label):
        """Store the index and colour of the currently active label."""

        # Determine the index of currently selected label
        self.labIndxCurrent = self.labels.index(label)

        # Set the point colour for the label
        self.fcCurrent = self.rgbLst[self.labIndxCurrent]
        #self.radio.activecolor = self.rgbLst[self.labIndxCurrent]

        # Redraw
        self.canvas.draw()

if __name__ == '__main__':

    # Make the plot interactive
    plt.ion()

    # Load the saved coordinates
    coords = pickle.load( open( "coords.pkl", "rb" ) )
    (frmNumLst, xJupLst_pix, yJupLst_pix,
     xMoonLst_pix, yMoonLst_pix) = coords

    # Unpack the moon coordinates and add an ID column
    frmMoon = []
    xMoon = []
    yMoon = []
    ID = []
    for i, frm in enumerate(frmNumLst):
        for j in range(len(xMoonLst_pix[i])):
            frmMoon.append(frm)
            xMoon.append(xMoonLst_pix[i][j])
            yMoon.append(yMoonLst_pix[i][j])
            ID.append(0)

    # Transpose the moon coordinates into an array with two columns
    data = np.array([xMoon, yMoon]).T

    # Create the figure
    fig = plt.figure()
    ax = fig.add_subplot(111)
    collection = ax.scatter(data[:, 0], data[:, 1], s=20, color='k')
    labels = ('Io', 'Europa', 'Ganymede', 'Calisto', 'Flagged')
    laso = LassoManager(ax, collection, labels)
    plt.draw()

    # Pause for plotting to finish
    input('Press Enter to finish plotting')
    print("\nYou created the following mask:")
    print(laso.selMsk)
