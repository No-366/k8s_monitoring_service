FROM python:3.11-slim

# 시스템 패키지 업데이트 및 필요한 도구 설치
RUN apt-get update && apt-get install -y \
    procps \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY . .

# 비루트 사용자 생성
RUN useradd -m -u 1000 collector && \
    chown -R collector:collector /app

# 사용자 전환
USER collector

# 애플리케이션 실행
CMD ["python", "collector.py"]
