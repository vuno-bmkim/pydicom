import os

from pydicom import dcmread
from pydicom.dataset import Dataset

from pynetdicom import AE, StoragePresentationContexts
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelGet

# Create application entity
ae = AE()

# Add the supported presentation contexts (Storage SCU)
ae.supported_contexts = StoragePresentationContexts

# Accept the association requestor's proposed SCP role in the
#   SCP/SCU Role Selection Negotiation items
for cx in ae.supported_contexts:
    cx.scp_role = True
    cx.scu_role = False

# Add a supported presentation context (QR Get SCP)
ae.add_supported_context(PatientRootQueryRetrieveInformationModelGet)

# Implement the AE.on_c_get callback
def on_c_get(ds, context, info):
    """Respond to a C-GET request Identifier `ds`.

    Parameters
    ----------
    ds : pydicom.dataset.Dataset
        The Identifier dataset sent by the peer.
    context : presentation.PresentationContextTuple
        The presentation context that the C-GET message was sent under.
    info : dict
        A dict containing information about the current association.

    Yields
    ------
    int
        The first yielded value should be the total number of C-STORE
        sub-operations necessary to complete the C-GET operation. In other
        words, this is the number of matching SOP Instances to be sent to
        the peer.
    status : pydicom.dataset.Dataset or int
        The status returned to the peer AE in the C-GET response. Must be a
        valid C-GET status value for the applicable Service Class as either
        an ``int`` or a ``Dataset`` object containing (at a minimum) a
        (0000,0900) *Status* element. If returning a Dataset object then
        it may also contain optional elements related to the Status (as in
        DICOM Standard Part 7, Annex C).
    dataset : pydicom.dataset.Dataset or None
        If the status is 'Pending' then yield the ``Dataset`` to send to
        the peer via a C-STORE sub-operation over the current association.

        If the status is 'Failed', 'Warning' or 'Cancel' then yield a
        ``Dataset`` with a (0008,0058) *Failed SOP Instance UID List*
        element containing a list of the C-STORE sub-operation SOP Instance
        UIDs for which the C-GET operation has failed.

        If the status is 'Success' then yield ``None``, although yielding a
        final 'Success' status is not required and will be ignored if
        necessary
    """
    if 'QueryRetrieveLevel' not in ds:
        # Failure
        yield 0xC000, None
        return

    # Import stored SOP Instances
    instances = []
    matching = []
    fdir = '/path/to/directory'
    for fpath in os.listdir(fdir):
        instances.append(dcmread(os.path.join(fdir, fpath)))

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


ae.on_c_get = on_c_get

# Start listening for incoming association requests
ae.start_server(('', 11112))