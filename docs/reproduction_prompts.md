# 쇼핑몰 사이트 생성기 재현 프롬프트 가이드

이 문서는 동일한 앱을 처음부터 다시 만들기 위해 AI 어시스턴트에게 제공할 프롬프트입니다.

---

## 🎯 초기 프롬프트

### Phase 1: 프로젝트 설정

```
React + TypeScript + Vite로 프론트엔드를, FastAPI + Python으로 백엔드를 가진 쇼핑몰 웹사이트 생성기를 만들어줘.

요구사항:
1. 사용자가 3가지 정보를 입력:
   - 상품명 (필수)
   - 디자인 스타일/요구사항 (필수)  
   - 레퍼런스 URL (선택)

2. Gemini API를 사용해서 완전한 반응형 쇼핑몰 HTML을 생성

3. 생성된 사이트를 미리보고, 다운로드하고, 저장할 수 있어야 함

4. 모든 UI는 한국어로

tech stack:
- Frontend: React 19, TypeScript, Vite, React Router
- Backend: FastAPI, SQLite, Python 3.11+
- AI: Google Gemini API
- 스타일: 인라인 스타일 (TailwindCSS 사용 안 함)

프로젝트 구조를 만들고 기본 설정을 시작해줘.
```

---

## Phase 2: 입력 페이지 구현

```
InputPage를 3단계 위저드 방식으로 만들어줘:

디자인 요구사항:
- 전체 화면 레이아웃 (position: fixed, 100vw/100vh)
- 흰색 카드 형태의 중앙 정렬 폼
- 상단 헤더: 제목 + "갤러리" 버튼 (검은색)
- 프로그레스 바 (3단계)

단계별 내용:
1. 단계 1: 상품명 입력
   - 예시: "천연 재료로 만든 수제 비누"
2. 단계 2: 디자인 스타일 입력 (textarea)
   - 예시: "전체적으로 자연스러운 베이지 톤으로 따뜻한 느낌을 주고..."
3. 단계 3: 레퍼런스 URL (선택)
   - 예시: "https://www.example-shop.com"

각 단계마다 "이전", "다음" 버튼
마지막 단계에서 "생성 시작하기" 버튼

폰트: Inter, 색상: 검은색 버튼, #fafafa 배경
애니메이션: fadeIn 0.3s
```

---

## Phase 3: 생성 페이지 구현

```
GeneratingPage를 만들어줘:

기능:
1. POST /generate API 호출
2. 2초마다 GET /results/{id} 폴링
3. 경과 시간 표시 (분:초)
4. 시간별 재치있는 메시지:
   - 0-10초: "멋진 디자인을 구상하고 있어요 ✨"
   - 10-30초: "완벽한 색상 조합을 찾는 중이에요 🎨"
   - 30-60초: "레이아웃을 세심하게 배치하고 있어요 📐"
   - 60-90초: "인터랙션을 추가하고 있어요 ⚡"
   - 90-120초: "마지막 손질을 하고 있어요 🔧"
   - 120초+: "거의 다 됐어요! 조금만 더 기다려주세요 🎉"

UI:
- 중앙에 펄스 애니메이션 아이콘
- 프로그레스 바 (좌우 이동 애니메이션)
- 하단에 입력한 상품 정보 표시
- 평균 소요시간: "약 2분 내외"
```

---

## Phase 4: 결과 페이지 구현

```
ResultPage를 만들어줘:

레이아웃:
- position: fixed 전체 화면
- 상단: 컨트롤 바
- 하단: iframe 미리보기 (100% 너비/높이)

상단 컨트롤:
- 왼쪽: "갤러리" 버튼 (검은색), "정보" 버튼, "컬러" 버튼
- 중앙: Mobile/Tablet/Desktop 전환 버튼
- 오른쪽: "다운로드" 버튼 (검은색), "삭제" 버튼 (빨간색 #dc2626)

정보 모달 (클릭 시 표시):
- 상품명
- 디자인 스타일
- 레퍼런스 URL (있을 경우)
- 디자인 의도

컬러 팔레트 모달:
- 색상 사각형 (클릭하면 HEX 코드 복사)
- alert로 "복사됨!" 표시

iframe 크기:
- Desktop: 100% 너비/높이
- Tablet: 768px
- Mobile: 375px

삭제 버튼: confirm 다이얼로그 후 DELETE /sites/{id} 호출, 갤러리로 이동
```

---

## Phase 5: 갤러리 페이지 구현

```
GalleryPage를 만들어줘:

기능:
- GET /gallery로 모든 사이트 가져오기
- 그리드 레이아웃 (auto-fill, minmax(320px, 1fr))
- 페이지네이션: 한 페이지당 8개

카드 디자인:
- 상단: 썸네일 미리보기 (iframe을 transform: scale(0.32)로 축소)
- 하단: 상품명, 디자인 스타일, 생성 날짜
- 호버: translateY(-4px), 그림자 강화
- 상단 그라데이션 바: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899)

페이지네이션:
- 이전/다음 버튼 (ChevronLeft/Right 아이콘)
- 페이지 번호 버튼
- 현재 페이지: 검은색 배경

빈 상태:
- "아직 생성된 사이트가 없습니다"
- "시작하기" 버튼
```

---

## Phase 6: Gemini 서비스 구현

```
backend/services/gemini_service.py를 만들어줘:

Gemini API 설정:
- 모델: gemini-3-pro-preview (환경변수)
- temperature: 0.9
- max_output_tokens: 8192

프롬프트 구조:
1. 역할: "World-class UI/UX designer and frontend developer"
2. 입력: product_type, design_style, reference_url
3. 출력: JSON 형식
   {
     "html": "...",
     "explanation": "1-2문장 한국어 설명",
     "key_points": ["포인트1", "포인트2", "포인트3"],
     "color_palette": ["#hex1", "#hex2", "#hex3", "#hex4"]
   }

HTML 요구사항:
- 최대 너비 1000px, 중앙 정렬
- 반응형: Mobile(320-767px), Tablet(768-1023px), Desktop(1024px+)
- 이미지: Lorem Flickr 사용
  - 형식: https://loremflickr.com/800/600/keyword1,keyword2,keyword3
  - 제품 타입에 맞는 키워드 자동 선택
  - 예: soap,natural,handmade / cosmetics,organic,beauty
- 인터랙션: 스크롤 애니메이션, 호버 효과, 햄버거 메뉴, 카트, 폼 검증
- 모든 텍스트 한국어
- CSS/JS 임베디드

JSON 추출 로직:
- 마크다운 펜싱 제거
- 파싱 실패 시 {와 } 사이 텍스트 추출 재시도
```

---

## Phase 7: 백엔드 API 구현

```
backend/main.py에 FastAPI 엔드포인트 구현:

POST /generate:
- 요청: GenerateRequest (product_type, design_style, reference_url)
- pending 레코드 생성
- 백그라운드에서 Gemini API 호출
- 응답: {id, status, message}

GET /results/{site_id}:
- site 정보 반환 (id, html_content, status, meta_data, created_at)

GET /gallery:
- 모든 completed 사이트 반환 (html_content 포함)

DELETE /sites/{site_id}:
- 사이트 삭제
- 404 처리

CORS: allow_origins=["*"] (개발용)
```

---

## Phase 8: 데이터베이스 구현

```
backend/database.py에 SQLite 함수 구현:

테이블:
CREATE TABLE sites (
    id TEXT PRIMARY KEY,
    product_type TEXT,
    design_style TEXT,
    reference_url TEXT,
    html_content TEXT,
    status TEXT DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP,
    meta_data TEXT
);

함수:
- init_db(): 테이블 생성
- create_pending_site(site_id, data): pending 레코드 생성
- update_site_success_with_meta(site_id, html, meta): 완료 업데이트
- update_site_error(site_id, error): 에러 업데이트
- get_site(site_id): 사이트 조회
- get_all_sites(): 모든 completed 사이트 (html_content 포함)
- delete_site(site_id): 사이트 삭제
```

---

## Phase 9: 스타일링 및 UI 개선

```
모든 페이지를 일관된 디자인 톤으로 통일:

공통 스타일:
- 배경: #fafafa
- 카드: 흰색, border-radius: 16px, box-shadow
- 버튼: 검은색 배경, 흰색 텍스트, border-radius: 8px
- 폰트: Inter
- 제목: 1.75rem, 800 weight
- 본문: 0.875rem

애니메이션:
- 버튼 호버: translateY(-1px)
- 카드 호버: translateY(-4px), shadow 강화
- 트랜지션: 0.2s ease

아이콘:
- lucide-react 사용
- Plus, Grid, Sparkles, ArrowLeft/Right, Download, X, Info, Palette, Monitor, Smartphone, Tablet, Calendar, Tag, ChevronLeft/Right
```

---

## Phase 10: 최종 최적화

```
다음 항목들을 최적화:

1. 이미지 로딩:
   - Lorem Flickr로 최종 확정
   - 키워드 기반 실제 사진 제공

2. JSON 파싱 개선:
   - 프롬프트 단순화
   - 에러 핸들링 강화

3. 삭제 기능:
   - 확인 다이얼로그
   - 백엔드 DELETE 엔드포인트 연동

4. 페이지네이션 버그 수정:
   - [...Array(totalPages)].map() 사용
   - 빈 버튼 제거

5. StrictMode 제거:
   - 중복 API 호출 방지

6. framer-motion 제거:
   - 사용하지 않는 의존성 정리
```

---

## 환경 변수 설정

```
backend/.env 파일 생성:

GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3-pro-preview
```

---

## 실행 명령어

**Backend**:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

---

## 핵심 원칙

재현 시 반드시 지켜야 할 원칙:

1. **단순성**: 복잡한 라이브러리 의존 최소화
2. **인라인 스타일**: TailwindCSS 사용 안 함
3. **한국어**: 모든 UI와 생성 콘텐츠
4. **실제 이미지**: Lorem Flickr 키워드 기반
5. **반응형**: 모든 디바이스 완벽 대응
6. **에러 처리**: JSON 파싱 에러 대비
7. **사용자 경험**: 재치있는 메시지, 부드러운 애니메이션

---

## 최종 체크리스트

- [ ] 3단계 입력 시스템 작동
- [ ] Gemini API 통합 및 사이트 생성
- [ ] 생성 진행 상황 실시간 표시
- [ ] 결과 페이지 디바이스 전환
- [ ] 정보/컬러 모달 작동
- [ ] 다운로드 기능
- [ ] 삭제 기능 (확인 포함)
- [ ] 갤러리 썸네일 미리보기
- [ ] 페이지네이션 (8개/페이지)
- [ ] 모든 텍스트 한국어
- [ ] Lorem Flickr 이미지 정상 로드
- [ ] 일관된 디자인 톤

---

이 가이드를 순서대로 따라가면 동일한 앱을 재현할 수 있습니다.
