# 1. Python 3.13 베이스 이미지 사용
FROM python:3.13-slim

# 2. 시스템 패키지 설치 (Root 권한으로 실행됨)
# Playwright와 Chromium 실행에 필요한 필수 라이브러리들입니다.
RUN DEBIAN_FRONTEND=noninteractive apt-get update --fix-missing && apt-get install -y \
    wget \
    gnupg \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm-dev \
    libxkbcommon-x11-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm-dev \
    libasound2 \
    libgtk-3-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# 3. 작업 디렉토리 설정
WORKDIR /app

# 4. Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Playwright 브라우저 설치
# 환경 변수를 설정하여 프로젝트 내부에 설치되도록 합니다.
ENV PLAYWRIGHT_BROWSERS_PATH=/app/playwright_browsers
RUN python -m playwright install chromium

# 6. 소스 코드 복사
COPY . .

# 7. 실행 명령 (Start Command)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]