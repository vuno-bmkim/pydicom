import os

from pydicom import dcmread
from pydicom.dataset import Dataset

from pynetdicom import AE
from pynetdicom.sop_class import GeneralRelevantPatientInformationQuery

# Initialise the Application Entity and specify the listen port
ae = AE()

# Add a requested presentation context
ae.add_supported_context(GeneralRelevantPatientInformationQuery)

# Implement the AE.on_c_store callback
def on_c_find(ds, context, info):
    """Respond to a C-FIND request Identifier `ds`.

    Parameters
    ----------
    ds : pydicom.dataset.Dataset
       The Identifier dataset send by the peer.
    context : namedtuple
       The presentation context that the dataset was sent under.
    info : dict
       Information about the association and relevant patient info request.

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
    fdir = '/path/to/directory'
    for fpath in os.listdir(fdir):
       instances.append(dcmread(os.path.join(fdir, fpath)))

    # Not a good example of how to match
    matching = [
        inst for inst in instances if inst.PatientID == ds.PatientID
    ]

    # There must either be no match or 1 match, everything else
    #   is a failure
    if len(matching) == 1:
        # User-defined function to create the identifier based off a
        #   template, outside the scope of the current example
        identifier = create_template(matching[0], ds)
        yield (0xFF00, identifier)
    elif len(matching) > 1:
        # More than 1 match found
        yield (0xC100, None)

ae.on_c_find = on_c_find

# Start listening for incoming association requests
ae.start_server(('', 11112))