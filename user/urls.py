from django.urls import path
from .views import Phone_Verification, CheckIn, Phone_Message, Check_Security_Number, CheckOut, GetDateInfo, \
    Get_ReservationDB, isOK

urlpatterns = [
    path('Phone_Verification/', Phone_Verification.as_view()),
    path('checkIn/', CheckIn.as_view()),
    path('checkOut/', CheckOut.as_view()),
    path('isOK/', isOK.as_view()),
    path('Phone_Message/', Phone_Message.as_view()),
    path('check_security_number/', Check_Security_Number.as_view()),
    path('Get_ReservationDB/', Get_ReservationDB.as_view()),
    path('getDateInfo/', GetDateInfo.as_view()),
]
