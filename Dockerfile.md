도커를 쓰기에는 가벼운 프로그램이라 인간이 실행할 도커파일 수기 작성하기

# 이동 (없으면 mkdir)
cd /home/ubuntu 

# git 설치 및 clone
sudo apt update
sudo apt install git
git clone "이 레포지토리"

# git ignore 된 것들 SFTP로 이전
cd /home/ubuntu 에 .local ( .gitconfig .git_credential )
cd /home/ubuntu/KidsLand 에 static, staticfiles, media, uwsgi.ini, db.sqlite3, .gitignore, .env

참고) uwsgi.ini 이동 시 고려할 사항
[uwsgi] 아래의 것들을 특히 조심
socket = /home/ubuntu/uwsgi.sock ## 소켓위치
chdir = /home/ubuntu/KidsLand ## 프로젝트 경로
wsgi-file = KidsLand/wsgi.py ## wsgi 위치
pythonpath = /home/ubuntu/.local/lib/python3.8/site-packages ## 파이썬 3.8경로

# 로컬 http 테스트 하고자 할때는
setting.py의 Debug = True 설정

# 이동 후 환경 세팅 및 설치 => 웬만하면 가상환경만들어서 3.8.10 버전으로 하기(근데 그냥 ubuntu22 디폴트인 3.10으로 난 했음)
cd home/ubuntu/KidsLand # 이동
sudo apt update # 먼저하고
sudo apt install python3-pip # 입력합니다.

(이 타이밍에서 가상환경 만들기)
3.10으로 그냥 가상 환경 만들고, 그 파이썬 버전은 그 안에서 쇼부 본다음 아래의 명령어 진행 하는 것으로
sudo apt install python3-venv
python3 -m venv venv # venv라는 이름으로 가상환경 생성
source venv/bin/activate # 활성화
deactivate # 비활성화

활성화 상태에서 파이썬 3.8.10으로 변경
sudo apt install curl
curl https://pyenv.run | bash
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
pyenv install 3.8.10
pyenv local 3.8.10
python --version ## 확인
python -m pip install --upgrade pip ## 파이썬 버전으로 pip 버전도 맞추기 => 가상환경에서 pip 버전을 맞추었으므로 pip3가 아닌 pip사용

pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate

# 그냥 실행해보려면 
python manage.py runserver 0.0.0.0:8000으로 실행

# uwsgi, nginx 세팅
pip install uwsgi

# 프로젝트 파일 바깥에서 실행 (ubuntu 폴더에서)
cd /home/ubuntu/
sudo apt-get install nginx

# uwsgi 세팅
cd /lib/systemd/system
sudo vi uwsgi.service # 파일 작성 => 이 파일 그대로 옮기기(아래의 경로만 신경 써서)
참고) uwsgi 경로 찾기 : find / -name uwsgi 2>&1 | grep -v Permission
참고) uwsgi.ini 경로 찾기 : find / -name uwsgi.ini 2>&1 | grep -v Permission

cd /etc/systemd/system
sudo ln -s /lib/systemd/system/uwsgi.service uwsgi.service
sudo systemctl daemon-reload
sudo systemctl enable uwsgi
sudo systemctl start uwsgi

systemctl | grep uwsgi # 잘 실행되는지 확인

# nginx 세팅
cd /etc/nginx/sites-available
sudo vi KidsLand # 파일작성 => 이 파일 그대로 옮기기 소켓 위치, ssl(let's encrypt) 고려해서 가져오기
sudo rm -f default
sudo mv django_zero default
sudo systemctl start nginx

# 포트 80, 8000, 443 다 뚫기
