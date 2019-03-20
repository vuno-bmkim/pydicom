from pydicom.dataset import Dataset
from pynetdicom import AE
from pynetdicom.sop_class import DisplaySystemSOPClass

# Initialise the Application Entity and specify the listen port
ae = AE()

# Add the supported presentation context
ae.add_supported_context(DisplaySystemSOPClass)


def create_attribute_list(attr):
    ds = Dataset()
    ds.SOPClassUID = '1.2.840.10008.5.1.1.40'
    ds.SOPInstanceUID = '1.2.840.10008.5.1.1.40.1'
    return ds


def on_n_get(attr, context, info):
    """Callback for when an N-GET request is received.

    Parameters
    ----------
    attr : list of pydicom.tag.Tag
        The value of the (0000,1005) *Attribute Idenfier List* element
        containing the attribute tags for the N-GET operation.
    context : presentation.PresentationContextTuple
        The presentation context that the N-GET message was sent under.
    info : dict
        A dict containing information about the current association.

    Returns
    -------
    status : pydicom.dataset.Dataset or int
        The status returned to the peer AE in the N-GET response. Must be a
        valid N-GET status value for the applicable Service Class as either
        an ``int`` or a ``Dataset`` object containing (at a minimum) a
        (0000,0900) *Status* element. If returning a Dataset object then
        it may also contain optional elements related to the Status (as in
        DICOM Standard Part 7, Annex C).
    dataset : pydicom.dataset.Dataset or None
        If the status category is 'Success' or 'Warning' then a dataset
        containing elements matching the request's Attribute List
        conformant to the specifications in the corresponding Service
        Class.

        If the status is not 'Successs' or 'Warning' then return None.
    """
    # User defined function to generate the required attribute list dataset
    # implementation is outside the scope of the current example
    # We pretend it returns a pydicom Dataset
    dataset = create_attribute_list(attr)

    # If Display System Management returns an attribute list then the
    # SOP Class UID and SOP Instance UID must always be as given below
    assert(dataset.SOPClassUID == '1.2.840.10008.5.1.1.40')
    assert(dataset.SOPInstanceUID == '1.2.840.10008.5.1.1.40.1')

    # Return status, dataset
    return 0x0000, dataset


ae.on_n_get = on_n_get

# Start listening for incoming association requests
ae.start_server(('', 11112))
