"""
- CTImage example data 받아서 하니
    "No suitable presentation context for the SCU role has been accepted
    by the peer for the SOP Class 'CT Image Storage' with a transfer syntax of 'JPEG 2000 Image Compression'"
    가 뜨며 안됨. testdata로 하니까 됨
"""

from pydicom import dcmread
from pydicom.data import get_testdata_files

from pynetdicom import AE
from pynetdicom.sop_class import CTImageStorage

# Initialise the Application Entity
ae = AE()

# Add a requested presentation context
ae.add_requested_context(CTImageStorage)
# Read in our DICOM CT dataset
filename = get_testdata_files('CT_small.dcm')[0]
print(filename)
ds = dcmread(filename)

# Associate with peer AE at IP 127.0.0.1 and port 11112
assoc = ae.associate('127.0.0.1', 11112)

if assoc.is_established:
    # Use the C-STORE service to send the dataset
    # returns a pydicom Dataset
    status = assoc.send_c_store(ds)

    # Check the status of the storage request
    if status:
        # If the storage request succeeded this will be 0x0000
        print('C-STORE request status: 0x{0:04x}'.format(status.Status))
    else:
        print('Connection timed out, was aborted or received invalid response')

    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')
