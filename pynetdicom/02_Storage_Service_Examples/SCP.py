"""
    - SCU에서 전송한 dcm 파일을 SCP가 받아서 File Meta Information, meta, transfer_syntax 등을 정하여 새로운 파일을 저장함. 
"""
from pydicom.dataset import Dataset

from pynetdicom import (
    AE,
    StoragePresentationContexts,
    PYNETDICOM_IMPLEMENTATION_UID,
    PYNETDICOM_IMPLEMENTATION_VERSION
)

import tempfile

# Initialise the Application Entity and specify the listen port
ae = AE()

# Add the supported presentation contexts
ae.supported_contexts = StoragePresentationContexts


# Implement the AE.on_c_store callback
def on_c_store(ds, context, info):
    """Store the pydicom Dataset `ds`.

    Parameters
    ----------
    ds : pydicom.dataset.Dataset
        The dataset that the peer has requested be stored.
    context : namedtuple
        The presentation context that the dataset was sent under.
    info : dict
        Information about the association and storage request.

    Returns
    -------
    status : int or pydicom.dataset.Dataset
        The status returned to the peer AE in the C-STORE response. Must be
        a valid C-STORE status value for the applicable Service Class as
        either an ``int`` or a ``Dataset`` object containing (at a
        minimum) a (0000,0900) *Status* element.
    """
    # Add the DICOM File Meta Information
    meta = Dataset()
    meta.MediaStorageSOPClassUID = ds.SOPClassUID
    meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID
    meta.ImplementationClassUID = PYNETDICOM_IMPLEMENTATION_UID
    meta.ImplementationVersionName = PYNETDICOM_IMPLEMENTATION_VERSION
    meta.TransferSyntaxUID = context.transfer_syntax

    # Add the file meta to the dataset
    ds.file_meta = meta

    # Set the transfer syntax attributes of the dataset
    ds.is_little_endian = context.transfer_syntax.is_little_endian
    ds.is_implicit_VR = context.transfer_syntax.is_implicit_VR

    suffix = '.dcm'
    filename = tempfile.NamedTemporaryFile(suffix=suffix, dir="").name
    # Save the dataset using the SOP Instance UID as the filename
    ds.save_as(filename, write_like_original=False)

    # Return a 'Success' status
    return 0x0000


ae.on_c_store = on_c_store

# Start listening for incoming association requests in blocking mode
ae.start_server(('', 11112), block=True)
