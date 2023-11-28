from django.urls import path
from .views import Phone_Verification, CheckIn, Phone_Message

urlpatterns = [
    path('Phone_Verification/', Phone_Verification.as_view()),
    path('checkIn/', CheckIn.as_view()),
    path('checkOut/', CheckIn.as_view()),
    path('Phone_Message/', Phone_Message.as_view())
]
