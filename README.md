


# PyEQD2
Convert a DICOM-RT dose distribution to its Linear Quadratic Equivalent Dose (LQED2, EQD2).

<br />

#### Example (Main Functions)
```
dicompath = '/Users/macuser/Downloads/testfile.dcm'
a = RTDose(dicompath)
a.plot()
a.plot_legend()
fractions = 8   #number of fractions
abratio = 3   #alpha/beta ratio
a.make_EQD2(fractions, abratio)
a.export()
```

#### Example (Other Commands)
```
# For an easy way to multiply the entire dose distribution before or after conversion to EQD2:
factor = 8
a.multiply(factor)
```

<br />

#### Credit: 
Based on Darcy Mason's pydicom (http://www.pydicom.org) – thank you for your hard work!
