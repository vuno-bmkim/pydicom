# pydicom/pynetdicom 
* https://github.com/sisobus/pynetdicom3/commit/c9d3d1b52f17a107566f31e63e0e4d0e8aaacbab 커밋 의미 해석
  * on_c_store을 통해 SCP가 C-STORE service를 수행하는 경우 (SCU로 부터 전송받은 .dcm 파일을 SCP 서버에 저장), pynetdicom > service_class.py StorageServiceClass 클래스의 SCP 함수가 호출됨
  * 이 함수 로직 중에 SCU에서 전송 받은 .dcm 파일을 pydicom.dataset.Dataset 타입 변수에 할당하여 attribute를 하나씩 조회하며 bad tag가 있는 경우 raise처리를 하는 기존 코드가 있음.
  * 이 부분을 주석 처리하여 bad tag가 있는 경우에도 받아지도록 처리됨.
# 정리
 * pydicom은 jupyter notebook 포맷에 관련 정리 사항과 함께 기록하였고, pynetdicom 부분은 python 포맷으로 코드를 일부 추가/수정하여 정리하였습니다. 
