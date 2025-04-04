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
from user.models import Reservation, LogHistory, DisableDay, Admin_Phone, Agree_Term

from datetime import datetime, timedelta

# 전역 변수
oneTimeMax = 30
timelist = {"A 1:30-3:30", "B 4:00-6:00"}  # set으로 설정
afterNdays = 30


# 전역 함수
def change_SEND_NUMBER():
    global SEND_NUMBER
    # 전송 번호 처리 : 디비에 없으면 부목사님 번호로 기본 전송, 디비에 설정 하면 마지막 입력된 번호로 전송
    try:
        last_admin_phone = Admin_Phone.objects.last()
        if last_admin_phone:  # 디비에 있으면
            SEND_NUMBER = last_admin_phone.number
        else:
            SEND_NUMBER = SEND_NUMBER  # 호출 시 마다 다시 갱신하여 DB수정 시 uginx, uwsgi를 재시작하지 않아도 되게끔하는 목적
    except Exception as e:
        print(e)


def update_ReservationDB():  # 예약현황 디비 업데이트 함수
    # 어제(전날 이전)까지의 예약 정보는 디비에서 삭제(최신화)
    ktz = pytz.timezone('Asia/Seoul')  # 한국 시간
    current_time = datetime.now(ktz)  # 현재 시간 타입
    current_date_str = current_time.strftime("%Y-%m-%d")  # 시간을 문자열 포멧팅
    reservations_to_delete = Reservation.objects.filter(reservation_date__lt=current_date_str)  # 어제 이전은 삭제
    print("어제 것 삭제", reservations_to_delete.count())  # 개수 확인용 출력
    reservations_to_delete.delete()

    # 오늘까지의 예약은 현재 시간에 맞추어 디비에서 삭제(최신화)
    year, month, day = [int(i) for i in current_date_str.split("-")]  # 현재 시간 구하기

    # A,B마감 시간과 비교하여, 지났으면 오늘이라도 해당 시간을 닫어버림.
    today_A = ktz.localize(datetime(year, month, day, 15, 30))
    if today_A < current_time:  # A타임이 지났으므로
        reservations_to_delete_A = Reservation.objects.filter(reservation_date=current_date_str,  # 오늘 것 중에
                                                              reservation_time__startswith='A')  # A로 시작하는 것 삭제
        print("오늘 A타임 삭제", reservations_to_delete_A.count())  # 개수 확인용 출력
        reservations_to_delete_A.delete()

    today_B = ktz.localize(datetime(year, month, day, 18, 00))
    if today_B < current_time:  # B타임이 지났으므로
        reservations_to_delete_B = Reservation.objects.filter(reservation_date=current_date_str,  # 오늘 것 중에
                                                              reservation_time__startswith='B')  # B로 시작하는 것 삭제
        print("오늘 B타임 삭제", reservations_to_delete_B.count())  # 개수 확인용 출력
        reservations_to_delete_B.delete()


def get_Agree_terms():
    # 빈 리스트 생성
    items = list()

    # 약관 데이터 베이스에서 최신 약관을 불러옴
    last_agree_term = Agree_Term.objects.last().term

    # 줄바꿈 기준으로 나누어서 리스트 안에 사전을 넣어 반환
    terms = last_agree_term.split("\n")
    terms = [term for term in terms if term.strip()]  # 좌우 공백 제거

    for i, j in enumerate(terms):
        temp = {'number': i + 1, 'content': j.strip()}
        items.append(temp)
    return items



# 클래스 : 화면 View 담당
class Main(APIView):
    def get(self, request):
        print("Main 호출 : get")

        # 초기 세팅 1 : 동의 여부 - 안함
        request.session['agreed'] = "false"

        # 초기 세팅 2 : 시간이 지난 예약은 자동으로 삭제
        update_ReservationDB()

        # 초기 세팅 3 : 최신 약관 불러오기
        items = get_Agree_terms()

        return render(request, "KidsLand/main.html", {'items': items})


class CheckIn(APIView):
    def get(self, request):
        print("CheckIn 호출 : get")
        agreed = request.session.get('agreed', 'false')
        if agreed == 'true':  # 약관 동의가 체크 되어야만 checkIn페이지로 이동
            # request.session['agreed'] = False  # 뒤로 가기 악용하여 동의한 것 처럼 만드는 것 방지 > 가 아니고 마지막에 확인하는 것으로 변경
            return render(request, "user/checkIn.html")
        return render(request, "KidsLand/main.html", {'items': get_Agree_terms()})

        # return render(request, "KidsLand/main.html")  # 아니면 main으로
        # return Main().get(request)  # 아니면 main으로
        # return redirect("/main/")


class CheckOut(APIView):
    def get(self, request):
        print("CheckOut 호출 : get")

        agreed = request.session.get('agreed', False)
        if agreed == 'true':  # 약관 동의가 체크 되어야만 checkOut페이지로 이동
            # request.session['agreed'] = False  # 뒤로 가기 악용하여 동의한 것 처럼 만드는 것 방지 -> 가 아니고 마지막에 확인하는 것으로 변경
            return render(request, "user/checkOut.html")
        return render(request, "KidsLand/main.html", {'items': get_Agree_terms()})




class Phone_Verification(APIView):
    def post(self, request):
        print("Phone_Verification 호출 : post")
        phone_number = request.data.get('phone_number', None)
        security_number = str(random.randint(0, 999999)).zfill(6)
        request.session['security_number'] = security_number
        request.session['phone_number'] = phone_number
        print(type(request.data), request.data)

        response_data = {"message": ""}
        try:  # try 구문은 checkIn page를 위함
            # 변수 선언 부분에서 checkOut페이지는 예외발생함.
            datepicker = request.data['datepicker']
            nameInput_list = request.data.getlist('nameInput[]')
            birthInput_list = request.data.getlist('birthInput[]')

            unique_NameBirth = set([nameInput_list[i]+birthInput_list[i] for i in range(len(nameInput_list))])
            if len(unique_NameBirth) != len(nameInput_list):
                response_data["message"] = f"중복된 아이의 정보가 있습니다."
                return Response(response_data, status=400)

            # 입력된 아이의 수 만큼 밸리데이션 진행
            for i in range(len(nameInput_list)):
                # 이름과 생년월일 입력
                nameInput = nameInput_list[i]
                birthInput = birthInput_list[i]

                # validation1 : 부모님번호가 3개 이하로 예약되었는가?
                matching_count = Reservation.objects.filter(parents_number=phone_number).count()
                if (matching_count + len(nameInput_list) > 3):
                    response_data["message"] = f"하나의 휴대폰 번호로 최대 3건까지 예약 가능합니다. 현재 예약된 건수는 {matching_count}회, 예약하려는 건수는 {len(nameInput_list)}회 입니다"
                    return Response(response_data, status=400)

                # validation2 : 한아이가 하루에 1타임만 -> 아이식별(아이이름, 생년월일, 부모님전화번호) 그리고 예약 날짜가 같은 건수가 1건도 없는지
                try:  # 매칭되는 게 없을 때 넘어가기 용도
                    matching = Reservation.objects.filter(parents_number=phone_number,
                                                          child_name=nameInput,
                                                          child_birth=birthInput,
                                                          reservation_date=datepicker)
                    already = matching.first().reservation_time  # 매칭되는 것이 없으면 여기서 예외 발생
                    if (matching.count() > 0):  # 매칭이 되면서 그 이전의 예약건수가 하나라도 있으면 실행
                        response_data[
                            "message"] = f"""한 아이당 하루에 한 타임만 이용할 수 있습니다.\n{nameInput} 님은 {datepicker} {already}타임에 이미 예약되어 있습니다."""
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

                # validation4 : 나이가 맞는가?
                else:
                    birthYear = int(str(birthInput)[:2])

                    # 현재 날짜와 시간을 한국 시간대로 가져온 후, 년도를 뒤에 두 글자만 문자열로 만들기
                    current_datetime = datetime.now(pytz.timezone('Asia/Seoul'))
                    CurrentYear = int(current_datetime.year % 100)

                    age = CurrentYear - birthYear + 1
                    if age > 11 or age < 0:
                        # 출생년도가 11년 이상 지났을 때
                        response_data["message"] = f"11살까지만 입장 가능합니다.({nameInput} 님)"
                        print(response_data["message"])
                        return Response(response_data, status=400)

                # validation5 : 약관에 동의했는가?
                print(request.session['agreed'])
                if request.session['agreed'] != 'true':
                    response_data["message"] = f"약관에 동의하지 않았습니다. 다시 처음부터 신청해주십시오."
                    print(response_data["message"])
                    return Response(response_data, status=400)

        except Exception as e:
            print(f"An exception occurred: {str(e)}")

        # ================================================================== 문자 보낼 때 필수 key값
        # API key, userid, sender, receiver, msg
        # API키, 알리고 사이트 아이디, 발신번호, 수신번호, 문자내용
        change_SEND_NUMBER()  # 발신 번호가 DB에 있으면 가져오는 함수
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

        # 잘못된 번호입니다 처리 가능할듯?? -> 추후 리팩토링

        send_response = requests.post(SEND_URL, data=sms_data)  # 요청을 던지는 URL, 현재는 문자보내기
        if send_response.json()['message'] != 'success':
            print(send_response.json())
            return Response(status=500)

        return Response(response_data, status=200)


class Phone_Message(APIView):  # 클래스의 post함수가 너무 뚱뚱해서 나중에 최소기능 단위로 리팩토링하기
    def post(self, request):
        print("Phone_Message 호출 : post")

        datepicker = request.data.get('datepicker', None)
        timeSelect = request.data.get('timeSelect', None)
        nameInput_list = request.data.getlist('nameInput[]')
        birthInput_list = request.data.getlist('birthInput[]')
        phone_number = request.session['phone_number']
        reserve_status = request.data.get('status', None)

        time_convert = {"A": "1:30-3:30", "B": "4:00-6:00"}

        # 입력된 아이의 수 만큼 루프를 돌면서 문자를 보냄
        for i in range(len(nameInput_list)):
            # 이름과 생년월일
            nameInput = nameInput_list[i]
            birthInput = birthInput_list[i]

            Message = f"[키즈랜드 {reserve_status}] {nameInput}\n{datepicker} {time_convert[timeSelect]}\n대전새중앙교회 1층 웰컴카페 옆"

            # ================================================================== 문자 보낼 때 필수 key값
            # API key, userid, sender, receiver, msg
            # API키, 알리고 사이트 아이디, 발신번호, 수신번호, 문자내용

            change_SEND_NUMBER()  # 발신 번호가 DB에 있으면 가져오는 함수
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

            # 이 타이밍 : 예약 추가 직전에 그 사이에 누군가가 예약했다는 것을
            last_check = Reservation.objects.filter(reservation_date=datepicker,
                                                    reservation_time=f'{timeSelect} {time_convert[timeSelect]}')
            if last_check.count() >= oneTimeMax:
                return Response(status=400)

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
        print("Get_ReservationDB 호출 : post")

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
        print("IsOK 호출 : post")

        agreed = request.data.get('agreed', 'false')  # A전송된 동의 여부 값을 가져옴
        request.session['agreed'] = agreed  # 세션에 동의 여부 저장
        return JsonResponse({'message': '약관 동의 여부가 업데이트되었습니다.'})


class Check_Security_Number(APIView):
    def post(self, request):
        print("Check_Security_Number 호출 : post")
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
        print("GetDateInfo 호출 : post")
        korea_timezone = pytz.timezone("Asia/Seoul")  # 한국 시간대를 설정
        today = datetime.now(korea_timezone)  # 현재 날짜
        disabled_dates = list()  # 안되는 날짜를 담을 리스트
        abled_dates = list()  # 되는 날짜를 담을 리스트

        # 오늘부터 7일 뒤까지 예약 가능
        start_date = today.strftime("%Y-%m-%d")
        end_date = (today + timedelta(days=afterNdays)).strftime("%Y-%m-%d")

        # 그러나 주말과 예약이 꽉찬 날은 예약 안됨
        for i in range(afterNdays + 1):  # 오늘 부터 7일 뒤까지
            current_day = today + timedelta(days=i)
            formatted_day = current_day.strftime("%Y-%m-%d")

            # 오늘이라면 마감 시간(18시)가 지났는지 여부 확인하여 닫을지 말지 여부 결정
            if i == 0:
                current_time = datetime.now(korea_timezone)

                # custom_datetime을 현재 날짜와 시간을 기반으로 생성하고 한국 시간대로 설정
                temp_time = datetime(current_time.year, current_time.month, current_time.day, 18, 0)
                custom_datetime = korea_timezone.localize(temp_time)

                if custom_datetime < current_time:
                    disabled_dates.append(formatted_day)

            # 주말인지 확인 (0: 월요일, 6: 일요일)
            if current_day.weekday() in ([6]):  # 0부터 5까지가 월요일부터 토요일까지의 인덱스
                disabled_dates.append(formatted_day)

            check = False
            for time in timelist:
                reserved = Reservation.objects.filter(reservation_date=formatted_day, reservation_time=time).count()
                if reserved < oneTimeMax: check = True
            if check == False:
                disabled_dates.append(formatted_day)

        print(disabled_dates)
        # 전도사님들이 관리자 페이지DB에서 안되는 날짜(공휴일, 사역)제거한 것 반영 목적
        disable = list(set(DisableDay.objects.values_list('disable', flat=True)))
        disabled_dates.extend(disable)

        disabled_dates = list(set(disabled_dates))

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
        print("Delete_Reservation 호출 : post")
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
                                          child_birth=reservation.child_birth,
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
        print("Get_Available 호출 : post")
        # 데이터 받아와서 연월일 분리
        date = request.data.get('selectedDate', None)
        year, month, day = [int(i) for i in date.split("-")]

        # 그 날의 예약타임을 돌면서 예약가능 인원 확인하기
        response_data = dict()
        for time in timelist:
            reserved = Reservation.objects.filter(reservation_time=time, reservation_date=date).count()
            response_data[time.split()[0]] = oneTimeMax - reserved

        # 현재 시간 구하기
        korea_timezone = pytz.timezone("Asia/Seoul")
        current_time = datetime.now(korea_timezone)

        # A,B마감 시간과 비교하여, 지났으면 오늘이라도 해당 시간을 닫어버림.
        today_A = korea_timezone.localize(datetime(year, month, day, 15, 30))
        if today_A < current_time:
            response_data['A'] = 0

        today_B = korea_timezone.localize(datetime(year, month, day, 18, 00))
        if today_B < current_time:
            response_data['B'] = 0

        return Response(response_data, status=200)
