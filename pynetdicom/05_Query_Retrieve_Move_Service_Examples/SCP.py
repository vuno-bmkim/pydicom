"""
- 02_Storage_Service_Examples의 SCP도 port 11113으로 구동시키고 동작해야함. 
"""
import os

from pydicom import dcmread
from pydicom.data import get_testdata_files
from pydicom.dataset import Dataset

from pynetdicom import AE, StoragePresentationContexts
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelMove

# Create application entity
ae = AE()

# Add the requested presentation contexts (Storage SCU)
ae.requested_contexts = StoragePresentationContexts
# Add a supported presentation context (QR Move SCP)
ae.add_supported_context(PatientRootQueryRetrieveInformationModelMove)


def get_known_aet():
    return {b'STORE_SCP       ': ('127.0.0.1', 11113)}


# Implement the AE.on_c_move callback
def on_c_move(ds, move_aet, context, info):
    """Respond to a C-MOVE request Identifier `ds`.

    Parameters
    ----------
    ds : pydicom.dataset.Dataset
        The Identifier dataset sent by the peer.
    move_aet : bytes
        The destination AE title that matching SOP Instances will be sent
        to using C-STORE sub-operations. ``move_aet`` will be a correctly
        formatted AE title (16 chars, with trailing spaces as padding).
    context : presentation.PresentationContextTuple
        The presentation context that the C-MOVE message was sent under.
    info : dict
        A dict containing information about the current association.

    Yields
    ------
    addr, port : str, int or None, None
        The first yield should be the TCP/IP address and port number of the
        destination AE (if known) or ``(None, None)`` if unknown. If
        ``(None, None)`` is yielded then the SCP will send a C-MOVE
        response with a 'Failure' Status of ``0xA801`` (move destination
        unknown), in which case nothing more needs to be yielded.
    int
        The second yield should be the number of C-STORE sub-operations
        required to complete the C-MOVE operation. In other words, this is
        the number of matching SOP Instances to be sent to the peer.
    status : pydiom.dataset.Dataset or int
        The status returned to the peer AE in the C-MOVE response. Must be
        a valid C-MOVE status value for the applicable Service Class as
        either an ``int`` or a ``Dataset`` containing (at a minimum) a
        (0000,0900) *Status* element. If returning a ``Dataset`` then it
        may also contain optional elements related to the Status (as in
        DICOM Standard Part 7, Annex C).
    dataset : pydicom.dataset.Dataset or None
        If the status is 'Pending' then yield the ``Dataset``
        to send to the peer via a C-STORE sub-operation over a new
        association.

        If the status is 'Failed', 'Warning' or 'Cancel' then yield a
        ``Dataset`` with a (0008,0058) *Failed SOP Instance UID List*
        element containing the list of the C-STORE sub-operation SOP
        Instance UIDs for which the C-MOVE operation has failed.

        If the status is 'Success' then yield ``None``, although yielding a
        final 'Success' status is not required and will be ignored if
        necessary.
    """
    if 'QueryRetrieveLevel' not in ds:
        # Failure
        yield 0xC000, None
        return

    # Check move_aet is known
    # get_known_aet() is here to represent a user-implemented method of
    #   getting known AEs
    known_aet_dict = get_known_aet()
    if move_aet not in known_aet_dict:
        # Unknown destination AE
        yield (None, None)
        return

    # Assuming known_ae_dict is {b'STORE_SCP       ' : ('127.0.0.1', 11113)}
    (addr, port) = known_aet_dict[move_aet]

    # Yield the IP address and listen port of the destination AE
    yield (addr, port)

    # Import stored SOP Instances
    instances = []
    matching = []
    filename = get_testdata_files('CT_small.dcm')[0]
    filename2 = get_testdata_files("rtplan.dcm")[0]
    instances.append(dcmread(filename))
    instances.append(dcmread(filename2))
    """
    fdir = '/path/to/directory'
    for fpath in os.listdir(fdir):
        instances.append(dcmread(os.path.join(fdir, fpath)))
    """
    if ds.QueryRetrieveLevel == 'PATIENT':
        if 'PatientID' in ds:
            matching = [
                inst for inst in instances if inst.PatientID == ds.PatientID
            ]

        # Skip the other possible attributes...

    # Skip the other QR levels...
    # Yield the total number of C-STORE sub-operations required
    yield len(instances)
    # Yield the matching instances
    for instance in matching:
        # Pending
        yield (0xFF00, instance)


ae.on_c_move = on_c_move

# Start listening for incoming association requests
ae.start_server(('', 11112))
