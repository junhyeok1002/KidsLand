from django.urls import path
from .views import Phone_Verification, CheckIn, Phone_Message, Check_Security_Number

urlpatterns = [
    path('Phone_Verification/', Phone_Verification.as_view()),
    path('checkIn/', CheckIn.as_view()),
    path('checkOut/', CheckIn.as_view()),
    path('Phone_Message/', Phone_Message.as_view()),
    path('check_security_number/', Check_Security_Number.as_view())

]
