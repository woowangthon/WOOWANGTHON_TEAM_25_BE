FROM python:3.13-slim

WORKDIR /app

#필요한거 txt파일에 추가하길 바람
COPY requirements.txt .
#컨테이너에 app 폴더 모든거 다 복사
COPY app/ .

RUN pip install --no-cache-dir -r requirements.txt
#연결 포트
EXPOSE 8000
# 서버 실행 , 현재 --noreload 안 쓰면 Watching for file changes with StatReloader 계속 뜨는데 이유를 모르겠음. 작동은함
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# 디버깅용
#CMD ["sleep", "infinity"]