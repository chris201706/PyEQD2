'''
Version:    1.0
Status:     finished
Date:       Jun 22, 2017
Author:     ***REMOVED***
Summary:    Import/Export DICOM RT-DOSE, convert to EQD2, multiply dose distribution by an arbitrary factor.
'''


################
### Preamble ###
################

# Import modules
import numpy as np
import os
import pydicom as dcm   # the pydicom module
import time

# Interpreter configuration
# np.set_printoptions(threshold=None)   # let NumPy print arrays in full size


######################
### Core Functions ###
######################

def import_dcm(filepath):
    try:
        dcmfile = dcm.read_file(filepath, force=True)
        print("——Successfully imported the following DICOM file:\n %s" % filepath)
        return dcmfile
    except:
        raise RuntimeError("An error occured while importing the DICOM file.")

''' Test
dicompath = '/Users/macuser/Downloads/testfile.dcm'
dcmfile = import_dcm(dicompath)
\Test '''


def is_modality(dicom, modality_str):
    if dicom.Modality == modality_str:
        print("––Input file is of modality %s. (Returning True.)" % modality_str)
        return True
    else:
        return False


def read_dose(dicom):
    try:
        if not hasattr(dicom.file_meta, 'TransferSyntaxUID'):   # Cf. [A] for setting the TransferSyntaxUID before reading the PixelArray
            dicom.file_meta.TransferSyntaxUID = dcm.uid.ImplicitVRLittleEndian   # Cf. [B] for default Transfer Syntax for DICOM: Implicit VR Endian (==ImplicitVRLittleEndian)
            print("––The input file has no tag 'TransferSyntaxUID'. The tag has been added and its value set to the default '1.2.840.10008.1.2' (Implicit VR Little Endian).")
        pixelarray = dicom.pixel_array   # Cf. [C] for reading the PixelArray
        shape = pixelarray.shape
        [numslices, numrows, numcolumns] = shape
        print("——Pixel array has been read from input file.\n",
            "Shape (slices x rows x columns): %d x %d x %d." % (numslices, numrows, numcolumns))
        return pixelarray, shape
    except:
        raise RuntimeError("An error occured while reading the pixelarray from the DICOM RTDOSE file.")

''' Test
array_uint, shape = read_dose(dcmfile)
\Test '''


def scale_for_use(array_uint, scalefactor):   # Cf. [D] for the mechanics of RT-DICOM's DoseGridScaling as a scalefactor
    array_float = array_uint.astype(np.float)
    array_scaled = array_float * scalefactor
    print("——Array scaled for use/modification. Log:\n",
          "Original scalefactor (DICOM DoseGridScaling): approx. %.9E\n" % scalefactor,
          "Mininum / Maximum values of raw input array:\n %d / %d\n" % (np.amin(array_uint), np.amax(array_uint)),
          "Mininum / Maximum array values after conversion to floating-point format:\n %f / %f\n" % (np.amin(array_float), np.amax(array_float)),
          "Mininum / Maximum array values after scaling:\n %f / %f" % (np.amin(array_scaled), np.amax(array_scaled)))
    return array_scaled

''' Test
print(dcmfile.DoseGridScaling)
array_scaled = scale_for_use(array_uint, dcmfile.DoseGridScaling)
\Test '''


def LQED2(Di,fn,abratio):   # Cf. [E] for the LQED2 formula
    LQED2i = Di * (abratio+(Di/fn)) / (abratio+2)  
    return LQED2i


def equalize(array,fn,abratio):
    tic = time.time()
    equalized = LQED2(array,fn,abratio)
    toc = time.time()
    print("——Array equalized. Log:\n",
        "Running time: approx. %.3f seconds.\n" % (toc-tic),   # Cf. [F] for Python equivalent of MATLAB's tic-toc feature
        "Mininum / Maximum values before equalization",
        "(displaying 6 decimals):\n %.6f / %.6f\n" % (np.amin(array), np.amax(array)),
        "Mininum / Maximum values after equalization",
        "(displaying 6 decimals):\n %.6f / %.6f" % (np.amin(equalized), np.amax(equalized)))
    return equalized

''' Test
testarray = np.array([[1, 0, 5], [0, 4, 0], [3, 0, 2]])
testarray_equalized = equalize(testarray,1,3)
print(testarray_equalized)
array_equalized = equalize(array_scaled,1,3)
\Test '''

def multiply(array,factor):
    tic = time.time()
    multiplied = array * factor
    toc = time.time()
    print("——Array multiplied. Log:\n",
          "Factor specified for multiplication (displaying 10 decimals): %.10f\n" % factor,
          "Running time: approx. %.3f seconds.\n" % (toc-tic),
          "Mininum / Maximum values before multiplication",
          "(displaying 6 decimals):\n %.6f / %.6f\n" % (np.amin(array), np.amax(array)),
          "Mininum / Maximum values after multiplication",
          "(displaying 6 decimals):\n %.6f / %.6f" % (np.amin(multiplied), np.amax(multiplied)))
    return multiplied

''' Test
array_multiplied = multiply(array_scaled,(1/33))
\Test '''


def scale_for_storage(array_float, orig_precision, orig_signedness, orig_maxval):
    precision_maxval = 0
    if orig_precision == 8 and orig_signedness == 0:
        precision_maxval = (2**8)-1  # highest value in unsigned quarter precision (= 255)
        precision_arrayfunc = np.uint8
    elif orig_precision == 16 and orig_signedness == 0:
        precision_maxval = (2**16)-1  # highest value in unsigned half precision (= 65535)
        precision_arrayfunc = np.uint16
    elif orig_precision == 32 and orig_signedness == 0:
        precision_maxval = (2**32)-1  # highest value in unsigned single precision (= 4,294,967,295)
        precision_arrayfunc = np.uint32
    else:
        raise ValueError("DICOM metadata tag 'BitsAllocated' (i.e. floating-point precision)",
                         "has to be 8 (quarter), 16 (half) or 32 (single).",
                         "Also, metadata tag 'PixelRepresentation' (i.e. signedness) has to be 0 (unsigned)",
                         "These limitations may easily be overcome by adding a few lines of code.")
    ##
    def scale_array(array):
        scalefactor = np.amax(array) / orig_maxval
        scaled = array / scalefactor
        return scaled, scalefactor
    ##
    scaled, scalefactor = scale_array(array_float)
    rounded = np.around(scaled, decimals=0) # round before simply truncating all decimals via 'astype:'
    converted = rounded.astype(precision_arrayfunc)
    print("——Array scaled for storage. Log:\n",
          "Floating-point precision of original file: unsigned %d-bit." % orig_precision,
          "Theoretical maximum value: %d.\n" % precision_maxval,
          "Actual maximum value in original file: %d\n" % orig_maxval,
          "New scalefactor (DICOM DoseGridScaling): approx. %.9E\n" % scalefactor,
          "Minimum / Maximum values of input array before any modifications",
          "(displaying 6 decimals):\n %.6f / %.6f\n" % (np.amin(array_float),np.amax(array_float)),
          "Minimum / Maximum array values after scaling",
          "(displaying 6 decimals):\n %.6f / %.6f\n" % (np.amin(scaled), np.amax(scaled)),
          "Minimum / Maximum array values after rounding to zero decimals:\n %.1f / %.1f\n" % (np.amin(rounded), np.amax(rounded)),
          "Minimum / Maximum array values after conversion to uint:\n %d / %d" % (np.amin(converted), np.amax(converted)))
    return converted, scalefactor

''' Test
array_uint, new_scalefactor = scale_for_storage(array_equalized)
array_uint, new_scalefactor = scale_for_storage(array_multiplied)
\Test '''


def export_dcm(dcmfile, name):
    path = os.getcwd()+'/'
    dcmfile.save_as(path+name+'.dcm')
    print("——Exported the DICOM file to current working directory.\n",
        "Location: %s\n" % path,
        "Name: %s" % (name+'.dcm'))

''' Test
export_dcm(array_uint,new_scalefactor,'_EQD2')
export_dcm(array_uint,new_scalefactor,'_multiplied')
\Test '''


def dcm_to_eqd2(orig_pixelarray, orig_scalefactor, orig_precision, orig_signedness, orig_maxval, fn, abratio):
    try:
        scaled = scale_for_use(orig_pixelarray, orig_scalefactor)
        equalized = equalize(scaled,1,3)
        new_pixelarray, new_scalefactor = scale_for_storage(equalized, orig_precision, orig_signedness, orig_maxval)
        return new_pixelarray, new_scalefactor
    except:
        RuntimeError("An error occured while converting the input pixelarray to EQD2.")

''' Test
array_equalized, new_scalefactor = dcm_to_eqd2(array_uint, dcmfile.DoseGridScaling, dcmfile.BitsAllocated, dcmfile.PixelRepresentation, np.amax(array_uint), 1, 3)
\Test '''


def dcm_multiply(orig_pixelarray, orig_scalefactor, orig_precision, orig_signedness, orig_maxval, factor):
    try:
        scaled = scale_for_use(orig_pixelarray,orig_scalefactor)
        multiplied = multiply(scaled,factor)
        new_pixelarray, new_scalefactor = scale_for_storage(multiplied, orig_precision, orig_signedness, orig_maxval)
        return new_pixelarray, new_scalefactor
    except:
        RuntimeError("An error occured while multiplying the input pixelarray.")

''' Test
array_multiplied, new_scalefactor = dcm_multiply(array_uint, dcmfile.DoseGridScaling, dcmfile.BitsAllocated, dcmfile.PixelRepresentation, np.amax(array_uint), 8)
\Test '''

##################
### References ###
##################
# [A] https://stackoverflow.com/questions/44492420/pydicom-dataset-object-has-no-attribute-transfersyntaxuid
# [B] https://www.dicomlibrary.com/dicom/transfer-syntax/)
# [C] http://pydicom.readthedocs.io/en/stable/working_with_pixel_data.html
# [D] https://ushik.ahrq.gov/ViewItemDetails?system=mdr&itemKey=79808000
# [E] American Association of Physicists in Medicine (AAPM), »The Use and QA of Biologically Related Models for Treatment Planning«, 2012
# [F] https://stackoverflow.com/questions/5849800/tic-toc-functions-analog-in-python


