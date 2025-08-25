import os
import gzip
import csv
import pydicom
import numpy as np
from io import BytesIO
from collections import defaultdict

# Configuration
dicom_root_folder = '/Desktop/dcm_img_tests'
output_csv = 'middle_slices_summary3.csv'
n = 1  # Number of slices in each side of the middle slice (2n+1)

# Read DICOM path
def readDicomFile(file_path):
    try:
        if file_path.endswith('.gz'):
            with gzip.open(file_path, 'rb') as f:
                raw = f.read()
            return pydicom.dcmread(BytesIO(raw), stop_before_pixels=False) # to include the pixel data as well
        else:
            return pydicom.dcmread(file_path, stop_before_pixels=False)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

# Group DICOM archives based on SeriesInstanceUID
series_dict = defaultdict(list)

for root, _, files in os.walk(dicom_root_folder):
    for f in files:
        if f.endswith('.dcm') or f.endswith('.dcm.gz'):
            full_path = os.path.join(root, f)
            ds = readDicomFile(full_path)
            if ds and hasattr(ds, 'PixelData'):
                series_uid = getattr(ds, 'SeriesInstanceUID', 'Unknown')
                series_dict[series_uid].append((ds, full_path))


# Tags to be extracted
tags_to_extract = [
    'StudyInstanceUID', 'SeriesInstanceUID', 'SOPInstanceUID',
    'Modality', 'WindowCenter', 'WindowWidth', 'RescaleIntercept', 'RescaleSlope',
    'ImagePositionPatient', 'ImageOrientationPatient', 'PhotometricInterpretation',
    'ImageType', 'ScanOptions', 'ProtocolName', 'RequestedProcedureDescription',
    'SeriesDescription', 'BodyPartExamined'
]

# Go through series and save middle slices
rows = []

for series_uid, items in series_dict.items():
    items.sort(key=lambda x: getattr(x[0], 'ImagePositionPatient', [0, 0, 0])[2] # sort based on the ImagePositionPaient or with InstanceNumber
               if hasattr(x[0], 'ImagePositionPatient') else getattr(x[0], 'InstanceNumber', 0))
    
    total_slices = len(items)
    
    # Skip the process if there is 0 files or invalid files in a series
    if total_slices < 1:
        continue

    middle_index = total_slices // 2
    start = max(0, middle_index - n)
    end = min(total_slices, middle_index + n + 1)

    selected = items[start:end]

    for ds, file_path in selected:
        ds.decode()

        row = {
            'FilePath': file_path,
            'FileName': os.path.basename(file_path)
        }
        for tag in tags_to_extract:
            value = getattr(ds, tag, 'N/A')
            if isinstance(value, (list, pydicom.multival.MultiValue)):
                value = str(list(value))
            row[tag] = value
        rows.append(row)

# CSV export
fieldnames = ['FilePath', 'FileName'] + tags_to_extract
with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
