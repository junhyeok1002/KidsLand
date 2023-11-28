

# Create your views here.
import os
import random
from datetime import datetime
from uuid import uuid4

import requests
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
# from .models import User
from django.contrib.auth.hashers import make_password
from KidsLand.settings import MEDIA_ROOT, API_KEY, SEND_URL, USER_ID, SEND_NUMBER
from user.models import Reservation


class Main(APIView):
    def get(self, request):
        print("겟으로 호출")
        return render(request, "KidsLand/main.html")
    def post(self, request):
        print("포스트로 호출")
        return render(request, "KidsLand/main.html")


class Phone_Verification(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number', None)

        security_number = str(random.randint(0, 999999)).zfill(6)
        request.session['security_number'] = security_number

        # ================================================================== 문자 보낼 때 필수 key값
        # API key, userid, sender, receiver, msg
        # API키, 알리고 사이트 아이디, 발신번호, 수신번호, 문자내용
        sms_data = {'key': API_KEY,  # api key
                    'userid': USER_ID,  # 알리고 사이트 아이디
                    'sender': SEND_NUMBER,  # 발신번호
                    'receiver': phone_number,  # 수신번호 (,활용하여 1000명까지 추가 가능)
                    'msg': f'[키즈랜드] 인증번호 [{security_number}]를 입력해 주세요.',  # 문자 내용
                    'msg_type': 'SMS',  # 메세지 타입 (SMS, LMS)
                    'title': '[키즈랜드 발신]',  # 메세지 제목 (장문에 적용)
                    'destination': f'{phone_number}|이름',  # %고객명% 치환용 입력
                    # 'rdate' : '예약날짜',
                    # 'rtime' : '예약시간',
                    # 'testmode_yn' : '' #테스트모드 적용 여부 Y/N
                    }
        send_response = requests.post(SEND_URL, data=sms_data)
        print(send_response.json())

        return Response(status=200)


class Phone_Message(APIView):
    def post(self, request):
        datepicker = request.data.get('datepicker', None)
        timeSelect = request.data.get('timeSelect', None)
        nameInput = request.data.get('nameInput', None)
        birthInput = request.data.get('birthInput', None)
        phone_number = request.data.get('phone_number', None)
        status = request.data.get('status', None)

        time_convert = {"A": "1:30-3:30", "B": "4:00-6:00"}

        Message = f"[키즈랜드 {status}] {nameInput}\n{datepicker} {time_convert[timeSelect]}\n대전새중앙교회 1층 웰컴카페 옆"

        # ================================================================== 문자 보낼 때 필수 key값
        # API key, userid, sender, receiver, msg
        # API키, 알리고 사이트 아이디, 발신번호, 수신번호, 문자내용


        sms_data = {'key': API_KEY,  # api key
                    'userid': USER_ID,  # 알리고 사이트 아이디
                    'sender': SEND_NUMBER,  # 발신번호
                    'receiver': phone_number,  # 수신번호 (,활용하여 1000명까지 추가 가능)
                    'msg': Message,  # 문자 내용
                    'msg_type': 'SMS',  # 메세지 타입 (SMS, LMS)
                    'title': '[키즈랜드 발신]',  # 메세지 제목 (장문에 적용)
                    'destination': f'{phone_number}|이름',  # %고객명% 치환용 입력
                    # 'rdate' : '예약날짜',
                    # 'rtime' : '예약시간',
                    # 'testmode_yn' : '' #테스트모드 적용 여부 Y/N
                    }
        send_response = requests.post(SEND_URL, data=sms_data) # 요청을 던지는 URL, 현재는 문자보내기
        print(send_response.json())

        # 현재 날짜와 시간을 얻습니다.
        now = datetime.now()
        # 현재 날짜와 시간을 포함한 타임 스탬프를 얻습니다 (년월일 시분초 마이크로초).
        timestamp_with_microseconds = now.timestamp() + now.microsecond / 1_000_000
        # 타임 스탬프를 년-월-일 시:분:초.마이크로초 형식으로 포맷팅합니다.
        formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S.%f")

        Reservation.objects.create(timestamp=formatted_datetime,
                                   is_OK="Ok",
                                   child_name=nameInput,
                                   child_birth=birthInput,
                                   reservation_date=datepicker,
                                   reservation_time=f'{timeSelect} {time_convert[timeSelect]}',
                                   parents_number=phone_number,
                                   status=status)


        return Response(status=200)


class CheckIn(APIView):
    def get(self, request):
        return render(request, "user/checkIn.html")

    # def post(self, request):
    #     return render(request, "user/checkIn.html")
    #     # TODO 회원가입
    #     #        email = request.data.get('email', None)
    #     check_type = request.GET.get('type', '')
    #
    #     if check_type == 'checkIn':
    #         pass
    #         # return HttpResponse('Check In')
    #
    #     return Response(status=200)


class Check_Security_Number(APIView):
    def post(self, request):
        input_security_number = request.data.get('input_security_number', None)
        security_number = request.session['security_number']

        # TODO: 실제 인증번호 확인 로직을 구현
        # 여기서는 간단하게 입력된 인증번호와 특정 값과의 비교
        success = (input_security_number == security_number)

        # 인증 결과를 JSON 응답으로 전송
        return JsonResponse({'success': success})