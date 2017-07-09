'''
Version:    1.0
Status:     finished
Date:       Jun 22, 2017
Author:     ***REMOVED***
Summary:    Plotting function for dose distribution. Legend. Custom colormap.
'''


### Preamble ###
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np


### Plotting ###
# defining a custom colormap
# Cf. [A] for creation of custom colormaps; the following code is based on this source.
# generate a jet colormap with 10 values:
jet = plt.cm.get_cmap("jet", 10)
# extract those values as an array:
jet_vals = jet(np.arange(10))
# change the first value to white (4th item: transparency; 0 is 100% transparency):
jet_vals[0] = [1, 1, 1, 0]
# change the last value to purple:
jet_vals[9] = [0.47, 0.17, 0.35, 1]
# save as new colormap:
newjet = colors.LinearSegmentedColormap.from_list("newjet", jet_vals) 


def legend(colormap):
    # generate data:
    # Cf. [B] für the following four line of code 
    m = np.zeros((1,1000))
    for i in range(1000):
        m[0,i] = i
    # setup figure:
    plt.imshow(m, colormap, aspect=100)
    plt.yticks([])
    plt.xticks([])
    plt.xlabel('0 – 100% (of maximum dose)',fontsize=14)
    plt.title('Color Legend',fontsize=14)
    plt.savefig('Legend.png')
    plt.show()

''' Test
legend(newjet)
\Test '''   


def rtdose_plot(pixelarray, name, colormap):
    numslices, numrows, numcols = pixelarray.shape
    # pick 16 slices from dose matrix:
    subset = np.linspace(0,numslices-1,16)
    subset = np.around(subset, decimals=0)
    subset = subset.astype(int)
    subset = subset.tolist()
    # initiate figure:
    figrows, figcols = (4,4)
    fig, axes = plt.subplots(figrows, figcols, figsize=(9,9))
    title = ('''Samples of '%s.dcm'
(Total Number of Slices: %d)''' %(name,numslices))
    fig.suptitle(title, fontsize=14, fontweight='bold', verticalalignment='top')
    plt.setp(axes, xticks=[], xticklabels=[],   # Cf. [C] for axis labeling
        yticks=[], yticklabels=[], aspect=1) 
    # populate figure with slices:
    counter = 0
    for r in range(0,figrows):
        for c in range(0,figcols):
            curr_slice_index = subset[counter]
            curr_slice_data = pixelarray[curr_slice_index]
            swapped = np.swapaxes(curr_slice_data,0,1)   # Cf. [D] for axis swap prior to plotting
            rotated = np.rot90(swapped, k=1)
            axes[r,c].pcolormesh(rotated, cmap=colormap, vmin=0) 
            axes[r,c].set_title('Slice #%d' % (curr_slice_index+1), fontsize=9)
            counter += 1
    plt.savefig("Samples_of_%s" % name, bbox_inches="tight")
    plt.show()

''' Test
dicompath = '/Users/macuser/Downloads/testfile.dcm'
dcmfile = import_dcm(dicompath)
rtdose_plot(dcmfile.pixel_array, 'RTDOSE', newjet)
\Test '''


### References ###
# [A] http://matplotlib.1069221.n5.nabble.com/get-colorlist-and-values-from-existing-matplotlib-colormaps-td23788.html
# [B] https://stackoverflow.com/questions/2451264/creating-a-colormap-legend-in-matplotlib
# [C] https://stackoverflow.com/questions/19626530/python-xticks-in-subplots
# [D] https://stackoverflow.com/questions/36483060/typeerror-dimensions-of-c-are-incompatible-with-x-y
