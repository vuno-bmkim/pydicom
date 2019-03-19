import os

from pydicom import dcmread
from pydicom.data import get_testdata_files
from pydicom.dataset import Dataset

from pynetdicom import AE
from pynetdicom.sop_class import ModalityWorklistInformationFind

# Initialise the Application Entity and specify the listen port
ae = AE()

# Add a requested presentation context
ae.add_supported_context(ModalityWorklistInformationFind)


# Implement the AE.on_c_store callback
def on_c_find(ds, context, info):
    print(ds)
    """Respond to a C-FIND request Identifier `ds`.

    Parameters
    ----------
    ds : pydicom.dataset.Dataset
        The Identifier dataset send by the peer.
    context : namedtuple
        The presentation context that the dataset was sent under.
    info : dict
        Information about the association and query/retrieve request.

    Yields
    ------
    status : int or pydicom.dataset.Dataset
        The status returned to the peer AE in the C-FIND response. Must be
        a valid C-FIND status value for the applicable Service Class as
        either an ``int`` or a ``Dataset`` object containing (at a
        minimum) a (0000,0900) *Status* element.
    identifier : pydicom.dataset.Dataset
        If the status is 'Pending' then the *Identifier* ``Dataset`` for a
        matching SOP Instance. The exact requirements for the C-FIND
        response *Identifier* are Service Class specific (see the
        DICOM Standard, Part 4).

        If the status is 'Failure' or 'Cancel' then yield ``None``.

        If the status is 'Success' then yield ``None``, however yielding a
        final 'Success' status is not required and will be ignored if
        necessary.
    """
    # Import stored SOP Instances
    instances = []
    matching = []
    filename = get_testdata_files('CT_small.dcm')[0]
    filename2 = get_testdata_files("rtplan.dcm")[0]
    instances.append(dcmread(filename))
    instances.append(dcmread(filename2))
    print(dcmread(filename))
    """
    print(filename)
    fdir = '/path/to/directory'
    for fpath in os.listdir(fdir):
        instances.append(dcmread(os.path.join(fdir, fpath)))
    """

    if 'QueryRetrieveLevel' not in ds:
        # Failure
        yield 0xC000, None
        return

    if ds.QueryRetrieveLevel == 'PATIENT':
        if 'PatientName' in ds:
            if ds.PatientName not in ['*', '', '?']:
                matching = [
                    inst for inst in instances if inst.PatientName == ds.PatientName
                ]

            # Skip the other possibile values...

        # Skip the other possible attributes...

    # Skip the other QR levels...

    for instance in matching:
        identifier = Dataset()
        identifier.PatientName = instance.PatientName
        identifier.QueryRetrieveLevel = ds.QueryRetrieveLevel

        # Pending
        yield (0xFF00, identifier)


ae.on_c_find = on_c_find

# Start listening for incoming association requests
ae.start_server(('', 11112))
