FROM python:3.13-slim

WORKDIR /app

#필요한거 txt파일에 추가하길 바람
COPY requirements.txt .
#컨테이너에 app 폴더 모든거 다 복사
COPY app/ .

RUN pip install --no-cache-dir -r requirements.txt
#빌드 되는지 테스트 하는 용도
CMD ["python", "test.py"]