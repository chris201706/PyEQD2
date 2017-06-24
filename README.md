


# PyEQD2
Convert a DICOM-RT dose distribution to its Linear Quadratic Equivalent Dose (LQED2, EQD2).

<br />

#### Example (Main Functions)
```
dicompath = '/Users/macuser/Downloads/testfile.dcm'
a = RTDose(dicompath)
a.plot()
a.plot_legend()
a.make_EQD2(8,3)
a.make_EQD2(1,3)
a.export()
```

#### Example (Other Commands)
```
# For an easy way to multiply the entire dose distribution before or after conversion to EQD2:
a.multiply(8)
```

<br />

#### Credit: 
Based on Darcy Mason's pydicom (http://www.pydicom.org) – thank you for your hard work!
