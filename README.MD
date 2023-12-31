## 필요한 페이지
- [ X ]main 페이지 : 키즈랜드 , 접수하기, 접수화인/취소하기
- [ X ] 약관동의 + 보호자 휴대폰 인증 페이지 : 부모님 전화번호
- [ X ] 접수 페이지2 : 날짜, 시간, 아이 이름, 접수버튼 -> 접수 완료 후 문자
    - [ X ] 날짜선택 밸리데이션 
    - [ X ] 시간선택 밸리데이션
    - [ X ] 아이 이름, 생년월일 (한번에 3개까지)
    - [ X ] 휴대폰번호 벨리데이션
    - [ X ] DB와 연동하여(날짜, 시간, 휴대폰 번호) 확인
- [ X ] 확인/취소 페이지 : 목록 뜨고 최대 3개

## 요구사항
- [ X ] 반드시 하루에 한 아이당 1타임(2시간)만 가능
- [ X ] 한 부모님당 3개의 예약 가능
- [ X ]예약 가능 일자는 오늘로부터 7일 뒤까지(평일은 제외)
- [ X ]11세까지만 입장
- [ X ]한 타임에 30

- [ X ] 날짜,시간 지나면 스테이징 디비 변하도록
- [ X ] 연휴, 사역 있는 날 관리자 페이지에서 직접 제외하도록 설정하기
- [  ] 디비에서 연락처 

## 변수 관리
- 부모님 휴대폰 번호(인증용)
- 약관 동의 여부
- 예약 당시 타임 스탬프
- 아이이름
- 아이 생년월일
- 예약 상태(취소시 예약 타임스탬프도)
- 예약 날짜
- 예약 시간

## DB 및 로그 관리
- [ X ] 예약/취소/확인 활동 전체 DB
- [ X ] 예약 현황 DB
- [ X ] 안되는 날짜 막기 용도

## 구현 순서
  - [ X ]디비 : 스테이징 디비와 로그 디비 각각 만들기
  - [ X ] 스테이징 디비를 기반으로, 예약 확인 취소 페이지 먼저 만들기
  - [ X ] 예약 확인 취소 페이지 디자인하깋
  - [ X ] 스테이징 디비를 기반으로, 예약 페이지 다시 요구사항 맞추기 + 빡센 밸리데이션
    - 인증번호 생성 시에 밸리데이션하기
      - [ X ] 부모님 번호로 3개 이하 등록했는가?
      - [ X ] 부모님 번호+아이이름을 아이디로 보았을때 하루에 한 타임만 신청했는가?
      - [ X ] 생년월일이 합당한가?
      - [ X ] 동의 했는가?
      - [ X ] DB등록하며 날짜/시간 인원이 그 사이에 꽉차진 않았는지 확인하며 DB등록
      - [ X ] 날짜 밸리데이션
  - [  ] 다하면 테스트

# 리팩토링
- [  ] 일단 아이 3명까지 동시 입력은 다 구현하고 남으면 한다
- [  ] 함수 분리 및 변수명 수정
- [  ] html, css, js(with csrf) : static으로 분리 

# (완료) 동의 안하고 예학 할 수 있는 방법 차단하기
1. 처음 접속 후 동의 X -> 알림
2. 처음 접속 후 url로 돌파시도 -> 동의 세션없으면 메인으로
3. 처음 접속 후 동의한 상태(동의 세션 on)
   - 동의를 해제하면 히스토리 삭제후 main이동해서 동의 해제하면 못 뚫음
   - 동의하고 다음페이지 가는 건 OK
4. 동의 후 다음페이지에서 뒤로가기 후, 새로고침하면 ?
   - 동의 세션은 체크를 해야만 바뀌어서 그대로인데 동의 체크 해제 된 페이지가 나옴 -> 넘어가짐 
   - 이것을 해결하기 위해 메인으로 접속(새로고침이든 첫 접속이든)하면 동의 세션을 false로 변경 
5. 이외에도 뚫을 수 있는 방법이 있을까? 나는 그것이 궁금하다... 일단 넘어가자...

# 우분투 서버와 나의 로컬 및 레포지토리와 다른점, gitignore된 파일
1. static, staticfiles
2. db.sqlite
3. .env
4. media