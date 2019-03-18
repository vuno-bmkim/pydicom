import time

from pynetdicom import AE, VerificationPresentationContexts


"""
- AE (Application Entity) : DICOM 통신시에 통신을 할 수 있는 대상의 단위 (ex: 서버, 클라이언트)
- Presentation context : Abstract Syntax (SOP Class. 무엇에 대해 어떠한 작업을 할 것인지) + Transfer Syntax (작업의 처리 방식)
- SCP (Service Class Provider) : DICOM은 Server/Client 모델이며, 여기서 Server 역할을 하는 AE (요청에 대기했다가 요청이 오면 응답)
- C-Service(DIMSE-C) & N-Service(DIMSE-N) : C는 복합된 정보를 가지고 있는 것에 대한 행위, N은 단일한 정보만을 가지고 있는 것에 대한 행위
- C-ECHO Service : 연결되는 DIMSE-service-user와의 end-to-end communication을 검증하는 서비스
"""

# Initialise the Application Entity and specify the listen port
ae = AE()

# Add the supported presentation context
# from pynetdicom.sop_class import VerificationSOPClass
# ae.add_supported_context(VerificationSOPClass) # SOP UID : 1.2.840.10008.1.1
ae.supported_contexts = VerificationPresentationContexts  # 위에 코드와 동일


def on_c_echo(context, info):
    """Respond to a C-ECHO service request.

    Parameters
    ----------
    context : namedtuple
        The presentation context that the verification request was sent under.
    info : dict
        Information about the association and verification request.

    Returns
    -------
    status : int or pydicom.dataset.Dataset
        The status returned to the peer AE in the C-ECHO response. Must be
        a valid C-ECHO status value for the applicable Service Class as
        either an ``int`` or a ``Dataset`` object containing (at a
        minimum) a (0000,0900) *Status* element.
    """
    print("C-ECHO")

    # return하는 값이 C_ECHO한 SCU에게 콜백으로 회신됨
    return 0x0000


ae.on_c_echo = on_c_echo

# Start listening for incoming association requests in non-blocking mode
scp = ae.start_server(('', 11112), block=False)

# Zzzzz
time.sleep(60)

# Shutdown the listen server
scp.shutdown()
