from pydicom.dataset import Dataset

from pynetdicom import (
    AE,
    PYNETDICOM_IMPLEMENTATION_UID,
    PYNETDICOM_IMPLEMENTATION_VERSION
)
from pynetdicom.pdu_primitives import SCP_SCU_RoleSelectionNegotiation
from pynetdicom.sop_class import (
    PatientRootQueryRetrieveInformationModelGet,
    CTImageStorage
)

# Initialise the Application Entity
ae = AE()

# Add the requested presentation contexts (QR SCU)
ae.add_requested_context(PatientRootQueryRetrieveInformationModelGet)
# Add the requested presentation context (Storage SCP)
ae.add_requested_context(CTImageStorage)

# Add an SCP/SCU Role Selection Negotiation item for CT Image Storage
role = SCP_SCU_RoleSelectionNegotiation()
role.sop_class_uid = CTImageStorage
# We will be acting as an SCP for CT Image Storage
role.scu_role = False
role.scp_role = True

# Extended negotiation items
ext_neg = [role]

# Create our Identifier (query) dataset
# We need to supply a Unique Key Attribute for each level above the
#   Query/Retrieve level
ds = Dataset()
ds.QueryRetrieveLevel = 'SERIES'
# Unique key for PATIENT level
ds.PatientID = '1234567'
# Unique key for STUDY level
ds.StudyInstanceUID = '1.2.3'
# Unique key for SERIES level
ds.SeriesInstanceUID = '1.2.3.4'

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

    # Save the dataset using the SOP Instance UID as the filename
    ds.save_as(ds.SOPInstanceUID, write_like_original=False)

    # Return a 'Success' status
    return 0x0000

ae.on_c_store = on_c_store

# Associate with peer AE at IP 127.0.0.1 and port 11112
assoc = ae.associate('127.0.0.1', 11112, ext_neg=ext_neg)

if assoc.is_established:
    # Use the C-GET service to send the identifier
    # A query_model value of 'P' means use the 'Patient Root Query Retrieve
    #     Information Model - Get' presentation context
    responses = assoc.send_c_get(ds, query_model='P')

    for (status, identifier) in responses:
        if status:
            print('C-GET query status: 0x{0:04x}'.format(status.Status))

            # If the status is 'Pending' then `identifier` is the C-GET response
            if status.Status in (0xFF00, 0xFF01):
                print(identifier)
        else:
            print('Connection timed out, was aborted or received invalid response')

    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')