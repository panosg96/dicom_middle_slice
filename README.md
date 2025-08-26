# dicom_middle_slice

This program detects the middle slices of an exam series (e.g. CT Scan exam) in order to have the part of the series with the most useful clinical information for any potential applications.

Based on the detection of these slices, some DICOM tags are also extracted, in order to give more information regarding the files (e.g modality, SeriesInstanceUID or even SeriesDescription).

Finally these data are exported to a csv file for further potential analysis or use.

Notes: 
- In the main.py file, the variable *dicom_root_folder* contains the path of the directory that we want to read. There's no limitation, since the program reads every file and folder that is gonna be in that directory.
- The amount of middle slices can be easily selected through the variable *n* which determines the number of slices around the middle slice based on the formula 2x+1. For example, if n=2, then 5 slices are gonna be detected, the middle slice and the 2 neighbour slices (before and after the middle slice). That gives the option to have more slices in the middle part of the series
