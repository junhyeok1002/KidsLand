# Create your views here.
import os
import random
from uuid import uuid4
import pytz

import requests
from django.core.serializers import serialize
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from KidsLand.settings import API_KEY, SEND_URL, USER_ID, SEND_NUMBER
from user.models import Reservation, LogHistory

from datetime import datetime, timedelta


class Main(APIView):
    def get(self, request):
        print("겟으로 호출")
        request.session['agreed'] = "false"
        return render(request, "KidsLand/main.html")


class Phone_Verification(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number', None)
        security_number = str(random.randint(0, 999999)).zfill(6)
        request.session['security_number'] = security_number
        request.session['phone_number'] = phone_number

        response_data = {"message": ""}
        try: # try 구문은 checkIn page를 위함
             # 변수 선언 부분에서 checkOut페이지는 예외발생함.
            datepicker = request.data['datepicker']
            nameInput = request.data['nameInput']
            birthInput = request.data['birthInput']

            # 나중에 데이터 픽커 수정할떄 ->  날짜 지난 거 없앴는지 체크해서 reservation 수정

            # validation1 : 부모님번호가 3개 이하로 예약되었는가?
            matching_count = Reservation.objects.filter(parents_number=phone_number).count()
            if (matching_count >= 3):
                response_data["message"] = f"하나의 휴대폰 번호로 최대 3건까지 예약 가능합니다. 현재 건수는 {matching_count}회 입니다"
                return Response(response_data, status=400)

            # validation2 : 한아이가 하루에 1타임만 -> 아이식별(아이이름, 생년월일, 부모님전화번호) 그리고 예약 날짜가 같은 건수가 1건도 없는지
            try: # 매칭되는 게 없을 때 넘어가기 용도
                matching = Reservation.objects.filter(parents_number=phone_number,
                                                      child_name=nameInput,
                                                      child_birth=birthInput,
                                                      reservation_date=datepicker)
                already = matching.first().reservation_time #매칭되는 것이 없으면 여기서 예외 발생
                if (matching.count() > 0): #매칭이 되면서 그 이전의 예약건수가 하나라도 있으면 실행
                    response_data["message"] = f"""한 아이당 하루에 한 타임만 이용할 수 있습니다.\n해당 아이는 {datepicker} {already}타임에 이미 예약되어 있습니다."""
                    print(response_data["message"])
                    return Response(response_data, status=400)
            except Exception as e:
                print(e)

            # validation3 : 생년월일이 합당한가?
            input_date = str(birthInput)
            result = False
            try:
                # 한국 시간대 설정
                kst = pytz.timezone('Asia/Seoul')
                # 현재 날짜와 시간을 한국 시간대로 가져오기
                current_date = datetime.now(kst).date()
                # 6자리 문자열을 변환
                formatted_date = datetime.strptime(input_date, '%y%m%d').date()

                # 입력된 년월일을 한국 시간대로 만들어서 유효성 확인 : 오늘 이전의 존재하는 날짜인가?
                if formatted_date <= current_date:
                    result = True
                else:
                    result = False
            except ValueError:
                result = False

            print(input_date, result)
            if (result == False):
                response_data["message"] = f"{input_date}는 유효하지 않은 생년월일입니다."
                print(response_data["message"])
                return Response(response_data, status=400)

            # validation4 : 약관에 동의했는가?
            print(request.session['agreed'])
            if request.session['agreed'] != 'true':
                response_data["message"] = f"약관에 동의하지 않았습니다. 다시 처음부터 신청해주십시오."
                print(response_data["message"])
                return Response(response_data, status=400)


        except Exception as e:
            print(e)

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

        # 편의 상 지워둠
        # send_response = requests.post(SEND_URL, data=sms_data)  # 요청을 던지는 URL, 현재는 문자보내기
        # if send_response.json()['message'] != 'success':
        #     print(send_response.json())
        #     return Response(status=500)
        # 잘못된 번호입니다 처리 가능할듯??

        return Response(response_data, status=200)


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

        # 현재 타임 스탬프를 년-월-일 시:분:초.마이크로초 형식으로 포맷팅합니다.
        korea_timezone = pytz.timezone("Asia/Seoul")  # 한국 시간대를 설정
        formatted_datetime = datetime.now(korea_timezone).strftime("%Y-%m-%d %H:%M:%S.%f")

        # 예약 현황 넣기
        Reservation.objects.create(timestamp=formatted_datetime,
                                   is_OK=request.session['agreed'],
                                   child_name=nameInput,
                                   child_birth=birthInput,
                                   reservation_date=datepicker,
                                   reservation_time=f'{timeSelect} {time_convert[timeSelect]}',
                                   parents_number=phone_number,
                                   status=reserve_status)

        # 로그에도 넣기
        LogHistory.objects.create(timestamp=formatted_datetime,
                                  is_OK=request.session['agreed'],
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
        matching_reservations = Reservation.objects.filter(parents_number=phone_number)

        # 쿼리셋을 JSON 형식으로 직렬화
        data = serialize('json', matching_reservations)
        print(data)
        print("type ", type(data))
        # JsonResponse를 사용하여 클라이언트에게 응답
        return JsonResponse(data, safe=False)


class IsOK(APIView):
    def post(self, request):
        agreed = request.data.get('agreed', 'false')  # A전송된 동의 여부 값을 가져옴
        request.session['agreed'] = agreed  # 세션에 동의 여부 저장
        return JsonResponse({'message': '약관 동의 여부가 업데이트되었습니다.'})


class CheckIn(APIView):
    def get(self, request):
        agreed = request.session.get('agreed', 'false')
        if agreed == 'true':  # 약관 동의가 체크 되어야만 checkIn페이지로 이동
            # request.session['agreed'] = False  # 뒤로 가기 악용하여 동의한 것 처럼 만드는 것 방지 > 가 아니고 마지막에 확인하는 것으로 변경
            return render(request, "user/checkIn.html")
        return render(request, "KidsLand/main.html")  # 아니면 main으로


class CheckOut(APIView):
    def get(self, request):
        agreed = request.session.get('agreed', False)
        if agreed == 'true':  # 약관 동의가 체크 되어야만 checkOut페이지로 이동
            # request.session['agreed'] = False  # 뒤로 가기 악용하여 동의한 것 처럼 만드는 것 방지 -> 가 아니고 마지막에 확인하는 것으로 변경
            return render(request, "user/checkOut.html")
        return render(request, "KidsLand/main.html")  # 아니면 main으로


class Check_Security_Number(APIView):
    def post(self, request):
        input_security_number = request.data.get('input_security_number', None)
        security_number = request.session['security_number']

        # TODO: 실제 인증번호 확인 로직을 구현
        # 여기서는 간단하게 입력된 인증번호와 특정 값과의 비교
        success = (input_security_number == security_number)

        # 인증 결과를 JSON 응답으로 전송
        return JsonResponse({'success': True})  # 테스트를 편하게 하기 위해 항상 통과 설정


# @method_decorator(csrf_exempt, name='dispatch')
class GetDateInfo(APIView):
    def post(self, request, *args, **kwargs):
        korea_timezone = pytz.timezone("Asia/Seoul")  # 한국 시간대를 설정
        today = datetime.now(korea_timezone)  # 현재 날짜
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


class Delete_Reservation(APIView):
    def post(self, request):
        reservation_id = request.data.get('reservation_id', None)

        if reservation_id:
            try:
                reservation = Reservation.objects.get(pk=reservation_id)
                # 예약 히스토리에도 넣기
                # 현재 타임 스탬프를 년-월-일 시:분:초.마이크로초 형식으로 포맷팅합니다.
                korea_timezone = pytz.timezone("Asia/Seoul")  # 한국 시간대를 설정
                formatted_datetime = datetime.now(korea_timezone).strftime("%Y-%m-%d %H:%M:%S.%f")

                LogHistory.objects.create(timestamp=formatted_datetime,  # 현재 타임 스탬프
                                          is_OK=reservation.is_OK,
                                          child_name=reservation.child_name,
                                          child_birth=reservation.child_name,
                                          reservation_date=reservation.reservation_date,
                                          reservation_time=reservation.reservation_time,
                                          parents_number=reservation.parents_number,
                                          status=f"예약 취소_{reservation.timestamp}")  # 예약 당시의 타임스탬프와 함께 보관
                # 예약 히스토리 이전 후 삭제
                reservation.delete()
                return JsonResponse({'success': True, 'message': '예약이 삭제되었습니다.'})
            except Reservation.DoesNotExist:
                return JsonResponse({'success': False, 'message': '존재하지 않는 예약입니다.'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'예약 삭제 중 오류 발생: {str(e)}'})

        return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'})

class Get_Available(APIView):
    def post(self, request):
        date = request.data.get('selectedDate', None)
        oneTimeMax = 30
        timelist = Reservation.objects.values_list('reservation_time', flat=True)
        timelist = set(timelist)

        response_data = dict()
        for time in timelist:
            reserved = Reservation.objects.filter(reservation_time=time, reservation_date=date).count()
            response_data[time.split()[0]] = f' - {oneTimeMax - reserved}명 예약가능'

        return Response(response_data, status=200)