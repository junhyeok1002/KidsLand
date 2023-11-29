from django.urls import path
from .views import Phone_Verification, CheckIn, Phone_Message, Check_Security_Number, CheckOut, GetDateInfo, \
    Get_ReservationDB, IsOK, Delete_Reservation

urlpatterns = [
    path('Phone_Verification/', Phone_Verification.as_view()),       # 휴대폰 인증 번호 생성 및 발신
    path('checkIn/', CheckIn.as_view()),                             # 신청페이지 이동
    path('checkOut/', CheckOut.as_view()),                           # 신청확인/취소 페이지 이동
    path('isOK/', IsOK.as_view()),                                   # 약관 동의 정보 세션 저장용
    path('Phone_Message/', Phone_Message.as_view()),                 # 예약정보 휴대폰 메세지 발신
    path('check_security_number/', Check_Security_Number.as_view()), # 인증 번호 확인
    path('Get_ReservationDB/', Get_ReservationDB.as_view()),         # 예약 DB정보 호출
    path('getDateInfo/', GetDateInfo.as_view()),                     # 예약 가능 날짜 정보
    path('delete_reservation/', Delete_Reservation.as_view()),       # 새로운 예약 삭제 URL 패턴
]
