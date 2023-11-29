# Create your views here.
import os
import random
from datetime import datetime
from uuid import uuid4

import requests
from django.core.serializers import serialize
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.views import APIView
# from .models import User
from django.contrib.auth.hashers import make_password
from KidsLand.settings import MEDIA_ROOT, API_KEY, SEND_URL, USER_ID, SEND_NUMBER
from user.models import Reservation, LogHistory

from datetime import datetime, timedelta


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
        request.session['phone_number'] = phone_number

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

        send_response = requests.post(SEND_URL, data=sms_data)  # 요청을 던지는 URL, 현재는 문자보내기
        if send_response.json()['message'] != 'success':
            print(send_response.json())
            return Response(status=500)

        return Response(status=200)


class Phone_Message(APIView):  # 클래스의 post함수가 너무 뚱뚱해서 나중에 최소기능 단위로 리팩토링하기
    def post(self, request):
        datepicker = request.data.get('datepicker', None)
        timeSelect = request.data.get('timeSelect', None)
        nameInput = request.data.get('nameInput', None)
        birthInput = request.data.get('birthInput', None)
        phone_number = request.session['phone_number']
        reserve_status = request.data.get('status', None)

        time_convert = {"A": "1:30-3:30", "B": "4:00-6:00"}

        Message = f"[키즈랜드 {reserve_status}] {nameInput}\n{datepicker} {time_convert[timeSelect]}\n대전새중앙교회 1층 웰컴카페 옆"

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
        send_response = requests.post(SEND_URL, data=sms_data)  # 요청을 던지는 URL, 현재는 문자보내기
        print(send_response.json())

        # 현재 날짜와 시간을 얻습니다.
        now = datetime.now()
        # 현재 날짜와 시간을 포함한 타임 스탬프를 얻습니다 (년월일 시분초 마이크로초).
        timestamp_with_microseconds = now.timestamp() + now.microsecond / 1_000_000
        # 타임 스탬프를 년-월-일 시:분:초.마이크로초 형식으로 포맷팅합니다.
        formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S.%f")

        # 여기에 최종 밸리데이션 코드 넣기
        validation = True  # 임시용 나중에 함수로 만들기
        if validation:
            Reservation.objects.create(timestamp=formatted_datetime,
                                       is_OK="Ok",
                                       child_name=nameInput,
                                       child_birth=birthInput,
                                       reservation_date=datepicker,
                                       reservation_time=f'{timeSelect} {time_convert[timeSelect]}',
                                       parents_number=phone_number,
                                       status=reserve_status)
        else:  # 나중에 함수 분리하고 리팩토링하면서 else 없애기
            reason = "예약 실패 사유 메세지"  # 나중에 밸리데이션 후 예약 실패 사유메세지를 여기에
            reserve_status = f"예약 실패_{reason}"  # 예약 실패 사유를 나중에 분석할 용도

        # 로그에도 넣기
        LogHistory.objects.create(timestamp=formatted_datetime,
                                  is_OK="Ok",
                                  child_name=nameInput,
                                  child_birth=birthInput,
                                  reservation_date=datepicker,
                                  reservation_time=f'{timeSelect} {time_convert[timeSelect]}',
                                  parents_number=phone_number,
                                  status=reserve_status)

        return Response(status=200)


class Get_ReservationDB(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number', None)
        # parents_number와 phone_number가 같은 데이터 가져오기
        matching_reservations = Reservation.objects.filter(parents_number= phone_number)

        # 쿼리셋을 JSON 형식으로 직렬화
        data = serialize('json', matching_reservations)
        print(data)
        print("type ", type(data))
        # JsonResponse를 사용하여 클라이언트에게 응답
        return JsonResponse(data, safe=False)


class CheckIn(APIView):
    def get(self, request):
        return render(request, "user/checkIn.html")


class CheckOut(APIView):
    def get(self, request):
        return render(request, "user/CheckOut.html")


class Check_Security_Number(APIView):
    def post(self, request):
        input_security_number = request.data.get('input_security_number', None)
        security_number = request.session['security_number']

        # TODO: 실제 인증번호 확인 로직을 구현
        # 여기서는 간단하게 입력된 인증번호와 특정 값과의 비교
        success = (input_security_number == security_number)

        # 인증 결과를 JSON 응답으로 전송
        return JsonResponse({'success': success})


# @method_decorator(csrf_exempt, name='dispatch')
class GetDateInfo(APIView):
    def post(self, request, *args, **kwargs):
        today = datetime.now()  # 현재 날짜
        disabled_dates = list()  # 안되는 날짜를 담을 리스트
        abled_dates = list()  # 되는 날짜를 담을 리스트

        # 오늘부터 7일 뒤까지 예약 가능
        start_date = today.strftime("%Y-%m-%d")
        end_date = (today + timedelta(days=7)).strftime("%Y-%m-%d")

        # 그러나 주말과 예약이 꽉찬 날은 예약 안됨
        for i in range(7):
            current_day = today + timedelta(days=i)

            # 주말인지 확인 (0: 월요일, 6: 일요일)
            if current_day.weekday() in (5, 6):  # 0부터 4까지가 월요일부터 금요일까지의 인덱스
                formatted_day = current_day.strftime("%Y-%m-%d")
                disabled_dates.append(formatted_day)
            # 예약이 차있는지 없는지 확인하는 코드 여기에

            # 오늘이라면 시간이 지났는지 여부 확인하여 닫을지 말지 여부 결정

            else:
                formatted_day = current_day.strftime("%Y-%m-%d")
                abled_dates.append(formatted_day)

        # JSON 형식으로 응답
        response_data = {
            'start_date': start_date,
            'end_date': end_date,
            'disabled_dates': disabled_dates,
            'abled_dates': abled_dates,
        }
        return JsonResponse(response_data)
