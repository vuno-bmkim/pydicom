from pynetdicom import AE
from pynetdicom.sop_class import VerificationSOPClass

"""
- SCU (Service Class User) :  DICOM은 Server/Client 모델이며, 여기서 Client 역할을 하는 AE
"""

# Initialise the Application Entity
ae = AE()

# Add a requested presentation context
ae.add_requested_context(VerificationSOPClass)


# Associate with peer AE at IP 127.0.0.1 and port 11112
assoc = ae.associate('127.0.0.1', 11112)
# 앞서 SCP의 port를 11112로 설정했음. 
# 11112 포트는 DICOM 표준 포트로 IANA(ICANN)에서 할당해뒀음.

if assoc.is_established:
    # Use the C-ECHO service to send the request
    # returns the response status a pydicom Dataset
    status = assoc.send_c_echo()
    # status의 type은 'pydicom.dataset.Dataset' 임
    
    # Check the status of the verification request
    if status:
        # If the verification request succeeded this will be 0x0000
        print('C-ECHO request status: 0x{0:04x}'.format(status.Status))
    else:
        print('Connection timed out, was aborted or received invalid response')

    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')