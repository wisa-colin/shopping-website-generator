# Render 무료 플랜 배포 가이드

GitHub를 통해 Render에 쇼핑몰 생성기 앱을 배포하는 상세 가이드입니다.

---

## 📋 사전 준비물

- [x] GitHub 계정
- [x] Render 계정 (https://render.com - 무료 가입)
- [x] Gemini API 키

---

## 🔧 Step 1: GitHub 레포지토리 설정

### 1.1 로컬 git 초기화 (이미 완료)

```bash
cd d:/etc/generating
git status  # 기존 git 확인
```

### 1.2 .gitignore 파일 확인 및 생성

**backend/.gitignore**:
```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.env
*.db
*.sqlite3
```

**frontend/.gitignore**:
```
node_modules/
dist/
.env
.env.local
```

**루트 .gitignore**:
```
# Python
backend/__pycache__/
backend/venv/
backend/.env
backend/*.db

# Node
frontend/node_modules/
frontend/dist/
frontend/.env

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

### 1.3 .gitignore 생성 및 커밋

```bash
# 루트 디렉토리에서
git add .gitignore
git commit -m "Add .gitignore for sensitive files"
```

### 1.4 GitHub 레포지토리 생성

1. GitHub.com 접속 → 로그인
2. 우측 상단 `+` → `New repository` 클릭
3. 레포지토리 정보 입력:
   - **Repository name**: `shopping-website-generator`
   - **Description**: `AI-powered shopping website generator`
   - **Public** 선택 (Render 무료 플랜은 public 필요)
   - **Do NOT** initialize with README, .gitignore, license
4. `Create repository` 클릭

### 1.5 로컬 레포지토리를 GitHub에 푸시

```bash
# GitHub에서 제공하는 명령어 실행
git remote add origin https://github.com/YOUR_USERNAME/shopping-website-generator.git
git branch -M main
git push -u origin main
```

---

## 🎨 Step 2: Frontend 빌드 설정

### 2.1 Render용 빌드 스크립트 추가

**frontend/package.json** 수정:
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview"
  }
}
```

### 2.2 빌드 테스트

```bash
cd frontend
npm run build
```

성공하면 `dist/` 폴더가 생성됩니다.

---

## 🔧 Step 3: Backend 설정

### 3.1 Procfile 생성 (Render용)

**backend/Procfile** 생성:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 3.2 runtime.txt 생성 (Python 버전 명시)

**backend/runtime.txt** 생성:
```
python-3.11.6
```

### 3.3 requirements.txt 확인

**backend/requirements.txt**가 다음 내용을 포함하는지 확인:
```
fastapi
uvicorn[standard]
python-multipart
google-generativeai
python-dotenv
```

### 3.4 변경사항 커밋

```bash
cd d:/etc/generating
git add backend/Procfile backend/runtime.txt
git commit -m "Add Render deployment files"
git push
```

---

## 🌐 Step 4: Render에서 Backend 배포

### 4.1 Render 로그인

1. https://render.com 접속
2. GitHub 계정으로 로그인

### 4.2 Backend Web Service 생성

1. Dashboard → `New` → `Web Service` 클릭
2. GitHub 레포지토리 연결:
   - `Connect a repository` 클릭
   - `shopping-website-generator` 레포지토리 선택
3. 서비스 설정:
   - **Name**: `shopping-generator-backend`
   - **Region**: `Singapore` (또는 가까운 지역)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Plan**: `Free` 선택
5. 환경 변수 설정 (`Environment` 탭):
   - **GEMINI_API_KEY**: `your_gemini_api_key_here`
   - **GEMINI_MODEL**: `gemini-3-pro-preview`

6. `Create Web Service` 클릭

### 4.3 배포 대기

- 배포가 완료될 때까지 5-10분 대기
- `Live` 상태가 되면 성공
- URL 복사: `https://shopping-generator-backend.onrender.com`

---

## 💻 Step 5: Frontend 배포

### 5.1 Frontend API URL 설정

**frontend/.env.production** 생성:
```
VITE_API_URL=https://shopping-generator-backend.onrender.com
```

**frontend/src/pages/** 모든 페이지에서 API URL 수정:

예시 (InputPage.tsx, GeneratingPage.tsx, ResultPage.tsx, GalleryPage.tsx):
```typescript
// 기존
const res = await fetch('http://localhost:8000/generate', ...)

// 변경 후
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const res = await fetch(`${API_URL}/generate`, ...)
```

### 5.2 변경사항 커밋

```bash
git add frontend/.env.production frontend/src/pages/
git commit -m "Update API URLs for production"
git push
```

### 5.3 Frontend Static Site 생성

1. Render Dashboard → `New` → `Static Site` 클릭
2. GitHub 레포지토리 연결
3. 서비스 설정:
   - **Name**: `shopping-generator-frontend`
   - **Region**: `Singapore`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

4. 환경 변수 설정:
   - **VITE_API_URL**: `https://shopping-generator-backend.onrender.com`

5. `Create Static Site` 클릭

### 5.4 배포 완료 대기

- 5-10분 대기
- URL 복사: `https://shopping-generator-frontend.onrender.com`

---

## 🔐 Step 6: CORS 설정 업데이트

### 6.1 Backend CORS 수정

**backend/main.py**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://shopping-generator-frontend.onrender.com",
        "http://localhost:5173"  # 로컬 개발용
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 6.2 커밋 및 푸시

```bash
git add backend/main.py
git commit -m "Update CORS for production"
git push
```

Render가 자동으로 재배포합니다.

---

## ✅ Step 7: 배포 확인

### 7.1 Backend 테스트

브라우저에서:
```
https://shopping-generator-backend.onrender.com/
```

예상 응답:
```json
{
  "message": "API is running",
  "docs": "/docs"
}
```

### 7.2 Frontend 접속

```
https://shopping-generator-frontend.onrender.com
```

### 7.3 전체 워크플로우 테스트

1. 사이트 입력 (3단계)
2. 생성 진행 확인
3. 결과 확인
4. 다운로드 테스트
5. 갤러리 확인

---

## 🐛 문제 해결

### 문제 1: Backend 500 Error

**원인**: 환경 변수 누락  
**해결**:
1. Render Dashboard → Backend Service → `Environment` 탭
2. `GEMINI_API_KEY`, `GEMINI_MODEL` 확인
3. 저장 후 수동 재배포: `Manual Deploy` → `Deploy latest commit`

### 문제 2: Frontend API 연결 실패

**원인**: CORS 또는 API URL 오류  
**해결**:
1. 브라우저 콘솔에서 네트워크 탭 확인
2. CORS 에러 → backend CORS 설정 확인
3. 404 에러 → frontend API_URL 환경 변수 확인

### 문제 3: Database 초기화 오류

**원인**: SQLite 파일 권한  
**해결**:
1. Backend 로그 확인: Render Dashboard → Logs
2. `database.py`의 `DB_PATH = "sites.db"` 확인
3. 필요 시 절대 경로 사용: `/opt/render/project/src/sites.db`

### 문제 4: Cold Start (첫 요청 느림)

**원인**: Render 무료 플랜은 15분 비활동 시 sleep  
**해결**:
- 정상 동작임 (첫 요청만 30초-1분 소요)
- 유료 플랜으로 업그레이드하거나 cron job으로 주기적 ping

---

## 💰 비용 정보

### Render 무료 플랜 제한

**Web Services (Backend)**:
- 750시간/월 무료
- 15분 비활동 시 sleep
- 512MB RAM
- 0.1 CPU

**Static Sites (Frontend)**:
- 무료 (제한 없음)
- Global CDN

**주의사항**:
- 월 750시간 초과 시 서비스 중단
- 데이터베이스는 메모리 내에만 존재 (재시작 시 초기화)

---

## 🔄 업데이트 방법

### 코드 변경 시

```bash
# 로컬에서 작업
git add .
git commit -m "Update feature"
git push
```

Render가 자동으로 감지하고 재배포합니다 (Auto-Deploy).

### 수동 재배포

Render Dashboard → Service → `Manual Deploy` → `Deploy latest commit`

---

## 📊 모니터링

### Logs 확인

Render Dashboard → Service → `Logs` 탭
- Real-time 로그 확인
- 에러 디버깅

### Metrics 확인

Render Dashboard → Service → `Metrics` 탭
- CPU 사용률
- 메모리 사용률
- 요청 수

---

## 🎯 성능 최적화

### Frontend

1. **빌드 최적화**:
   ```bash
   npm run build -- --mode production
   ```

2. **이미지 최적화**:
   - 이미 Lorem Flickr 사용 중 (최적화됨)

### Backend

1. **Gunicorn 사용** (더 나은 성능):
   
   **Procfile** 업데이트:
   ```
   web: gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
   ```
   
   **requirements.txt**에 추가:
   ```
   gunicorn
   ```

2. **캐싱 추가** (선택사항):
   - Redis 추가 (유료)

---

## 🔒 보안 체크리스트

- [x] `.env` 파일이 `.gitignore`에 포함됨
- [x] API 키가 GitHub에 노출되지 않음
- [x] CORS가 특정 도메인만 허용
- [x] Render 환경 변수로 API 키 관리
- [ ] (선택) Rate limiting 추가
- [ ] (선택) HTTPS only 강제

---

## 📝 최종 체크리스트

배포 전:
- [ ] `.gitignore` 설정 완료
- [ ] GitHub 레포지토리 생성
- [ ] 코드 푸시 완료

Backend 배포:
- [ ] Render Web Service 생성
- [ ] 환경 변수 설정 (GEMINI_API_KEY)
- [ ] 배포 상태 `Live` 확인
- [ ] API 엔드포인트 테스트

Frontend 배포:
- [ ] API URL 환경 변수 설정
- [ ] Render Static Site 생성
- [ ] 빌드 성공 확인
- [ ] 사이트 접속 확인

테스트:
- [ ] 전체 워크플로우 테스트
- [ ] 다운로드 기능 확인
- [ ] 갤러리 확인

---

## 🎉 완료!

이제 다음 URL에서 앱에 접속할 수 있습니다:

**Frontend**: `https://shopping-generator-frontend.onrender.com`  
**Backend API**: `https://shopping-generator-backend.onrender.com`

---

## 📚 추가 자료

- [Render Documentation](https://render.com/docs)
- [Render Free Tier](https://render.com/docs/free)
- [Deploy FastAPI on Render](https://render.com/docs/deploy-fastapi)
- [Deploy Vite on Render](https://render.com/docs/deploy-vite)
