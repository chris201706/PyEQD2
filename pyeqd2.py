'''
Version:    1.0
Status:     finished
Date:       Jun 22, 2017
Author:     ***REMOVED***
Summary:    Import/Export DICOM RT-DOSE, convert to EQD2, plot dose distribution and legend. Object-Oriented.
'''


### Preamble ###
from corefunctions import *
from plotting import *


### Class Definition ###
class RTDose:
    def __init__(self, filepath):
        self.dcmfile = import_dcm(filepath)
        self.name, self.ext = os.path.splitext(os.path.basename(filepath))
        if is_modality(self.dcmfile,'RTDOSE'):
            self.pixelarray, self.shape = read_dose(self.dcmfile)
            self.pixelspacing = self.dcmfile.PixelSpacing
            self.raw_maxval = np.amax(self.pixelarray)
            self.scalefactor = self.dcmfile.DoseGridScaling
            self.precision = self.dcmfile.BitsAllocated
            self.signedness = self.dcmfile.PixelRepresentation # Cf. [A] for PixelRepresentation: 0 is unsigned, 1 is signed
            print("––New instance of Class RTDose has been initiated.")
        else:
            raise ValueError("Input file is not of modality 'RTDOSE'.(Returning False.)")
    def make_eqd2(self, fn, abratio):
        self.pixelarray, self.scalefactor = dcm_to_eqd2(self.pixelarray, self.scalefactor, self.precision, self.signedness, self.raw_maxval, fn, abratio)
    def multiply(self, factor):
        self.pixelarray, self.scalefactor = dcm_multiply(self.pixelarray, self.scalefactor, self.precision, self.signedness, self.raw_maxval, factor)
    def plot(self):
        rtdose_plot(self.pixelarray, self.name, newjet)
    def plot_legend(self):
        legend(newjet)
        pass
    def export(self):
        export_dcm(self.dcmfile, self.name)   # simply exports to current directory (where plots and legends are also saved – consistency!)

''' Test
dicompath = '/Users/macuser/Downloads/testfile.dcm'
a = RTDose(dicompath)
a.name
a.plot_legend()
a.plot()
a.make_eqd2(8,3)
a.multiply(8)
a.make_eqd2(1,3)
a.export()
\Test '''


### References ###
# [A] http://dicomiseasy.blogspot.de/2012/08/chapter-12-pixel-data.html
