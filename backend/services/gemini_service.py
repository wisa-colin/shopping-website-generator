from google import genai
from google.genai.types import Tool, GenerateContentConfig, Part
import os
import json
import time
import base64
import requests
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
# [스크린샷] 캐시 호출
from main import SCREENSHOT_CACHE
import uuid

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        self.unsplash_access_key = os.getenv("UNSPLASH_ACCESS_KEY")
        if not self.unsplash_access_key:
            print("UNSPLASH_ACCESS_KEY not found, will use fallback(loremflickr) images")
        
        # 객체 시동걸기
        self.client = genai.Client(api_key=api_key)
        
        # 모델 선택, 3.0을 별도로 사용하고 실패 시 2.5로 사용
        self.model_id = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        print(f"Using Gemini model: {self.model_id}")
        
        # api 호출 간격 제한
        self.last_request_time = 0
        self.min_request_interval = 60.0  
        
        # Playwright browser lazy initialization
        self._playwright = None
        self._browser = None
    
    async def _capture_screenshot(self, url: str) -> Optional[bytes]:
        """Capture a screenshot of the given URL using Playwright"""
        return await asyncio.get_event_loop().run_in_executor(None, self._capture_screenshot_sync, url)

    def _capture_screenshot_sync(self, url: str) -> Optional[bytes]:
        """Synchronous implementation of screenshot capture"""
        from playwright.sync_api import sync_playwright

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
                # 봇 아닌척 숨겨보기
                page = browser.new_page(
                    viewport={"width": 1920, "height": 3000},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.7499.41 Safari/537.36"
                )
                
                try:
                    print(f"[{datetime.now()}] Navigating to: {url}")
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)

                    # 페이지 로드될때까지 대기
                    time.sleep(6)
                    
                    print(f"[{datetime.now()}] Attempting to close popups via click...")
                    # 그지같은 팝업 제거 키워드(x는 너무 텍스트 x들을 클릭해대서 제외)
                    popup_keywords = ["오늘 하루 보지않기", "오늘 하루 보지 않기", "오늘 하루 열지 않음", "닫기", "Close", "창 닫기", "Don't show again"]

                    # 팝업 닫기 시도
                    for attempt in range(2):
                        clicked_any = False
                        for keyword in popup_keywords:
                            try:
                                locators = page.get_by_text(keyword)
                                count = locators.count()
                                
                                if count > 0:
                                    # 키워드로 팝업 제거 시도
                                    for i in range(count):
                                        try:
                                            if locators.nth(i).is_visible():
                                                print(f"[{datetime.now()}] [Attempt {attempt+1}] Clicking popup button: '{keyword}'")
                                                locators.nth(i).click(timeout=5000, force=True, no_wait_after=True)
                                                clicked_any = True
                                                # 클릭 후 잠시 대기
                                                time.sleep(0.5)
                                        except Exception as e:
                                            print(f"[{datetime.now()}] Click failed for '{keyword}': {e}")
                                            pass
                            except Exception:
                                pass
                        
                        # 팝업 제거시도 후에 그지같이 또 나올 수 있으니 잠시 대기
                        if clicked_any:
                            print(f"[{datetime.now()}] [Attempt {attempt+1}] Waiting for potential new popups...")
                            time.sleep(1.5)
                        else:
                            # 더 이상 클릭할거 없으면 반복 종료
                            if attempt == 0:
                                print(f"[{datetime.now()}] No popups found on first attempt, trying once more...")
                            break

                    # 스크린샷 찍기전에 잠시 대기
                    time.sleep(3)
                    
                    # 캡쳐 설정
                    screenshot = page.screenshot(
                        type="jpeg",
                        quality=70,
                        clip={"x": 0, "y": 0, "width": 1920, "height": 3000},
                        timeout=60000
                    )
                    
                    try:
                        # [스크린샷] 전역캐시 추가 및 로그에 추가
                        file_id = str(uuid.uuid4())
                        SCREENSHOT_CACHE[file_id] = screenshot
                        print(f"[{datetime.now()}] Screenshot ID: {file_id}. Access URL: /screenshot/{file_id}")
                    except Exception as e:
                        print(f"[{datetime.now()}] Failed to cache screenshot : {e}")
                    
                    print(f"[{datetime.now()}] Screenshot captured: {len(screenshot)} bytes (JPEG/4000px)")
                    return screenshot
                    
                finally:
                    page.close()
                    browser.close()
                    
        except Exception as e:
            import traceback
            print(f"[{datetime.now()}] Screenshot capture failed: {repr(e)}")
            print(traceback.format_exc())
            return None
    
    def _check_rate_limits(self):
        """Simple rate limiting to avoid hitting API limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def _extract_search_keywords(self, product_type: str) -> str:
        """Use Gemini to extract English search keywords from product description"""
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"""
                Translate this product description into 2-3 simple English keywords for stock photo search.
                Input: "{product_type}"
                
                Rules:
                1. Output ONLY the keywords separated by spaces
                2. No punctuation, no explanations
                3. Focus on the visual object (e.g. "warm roasted sweet potato lollipop" -> "lollipop candy dessert")
                """
            )
            keywords = response.text.strip()
            keywords = keywords.replace('"', '').replace('\n', ' ')
            print(f"[{datetime.now()}] Translated '{product_type}' -> '{keywords}'")
            return keywords
        except Exception as e:
            print(f"[{datetime.now()}] Keyword extraction failed: {e}")
            return "beautiful"

    def _clean_html(self, html_content: str) -> str:
        """
        Smart Filtering: Clean HTML to keep only structure and style-relevant tags.
        Removes noise like SVG paths, base64 images, and long text.
        """
        from bs4 import BeautifulSoup, Comment
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # 1. Remove completely useless tags
            for tag in soup(['noscript', 'iframe', 'object', 'embed']):
                tag.decompose()

            # 2. Remove comments
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()

            # 3. Clean SVG: Keep tag but remove paths (too long)
            for svg in soup.find_all('svg'):
                svg.clear() # Remove children (paths)
                svg.attrs = {k: v for k, v in svg.attrs.items() if k in ['class', 'id', 'width', 'height', 'viewbox']}
                svg.string = "SVG_ICON" # Placeholder

            # 4. Clean Images: Remove base64 src
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if src.startswith('data:'):
                    img['src'] = 'BASE64_IMAGE_REMOVED'
                # Remove other attributes except critical ones
                img.attrs = {k: v for k, v in img.attrs.items() if k in ['src', 'class', 'id', 'alt']}

            # 5. Clean Scripts: Keep src (libraries), remove inline content
            for script in soup.find_all('script'):
                if script.get('src'):
                    # Keep external scripts (libraries)
                    script.string = "" 
                else:
                    # Remove inline scripts completely (usually logic, not style)
                    script.decompose()

            # 6. Clean Text: Truncate long text nodes
            for text in soup.find_all(string=True):
                if len(text) > 50 and text.parent.name not in ['style', 'script']:
                    text.replace_with(text[:50] + "...")

            # 7. Clean Attributes: Remove data-*, aria-*, on* events
            for tag in soup.find_all(True):
                attrs = dict(tag.attrs)
                for key in attrs:
                    if key.startswith('data-') or key.startswith('aria-') or key.startswith('on'):
                        del tag.attrs[key]

            return str(soup)

        except Exception as e:
            print(f"[{datetime.now()}] HTML cleaning failed: {e}")
            return html_content[:20000] # Fallback to truncation

    def _get_unsplash_images(self, product_type: str, count: int = 8) -> List[str]:
        """Fetch product images from Unsplash API"""
        if not self.unsplash_access_key:
            print("No Unsplash key, using fallback")
            return []
        
        try:
            # Get optimized English keywords
            search_query = self._extract_search_keywords(product_type)
            
            url = "https://api.unsplash.com/photos/random"
            headers = {
                "Authorization": f"Client-ID {self.unsplash_access_key}"
            }
            params = {
                "query": search_query,
                "count": count,
                "orientation": "landscape"
            }
            
            print(f"[{datetime.now()}] Fetching {count} images from Unsplash for '{search_query}'...")
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                photos = response.json()
                
                image_urls = []
                
                # Handle both single photo and array responses (Unsplash API quirk)
                if isinstance(photos, list):
                    for i, photo in enumerate(photos):
                        try:
                            # Use 'raw' URL for maximum stability, with quality params
                            url = photo.get('urls', {}).get('raw', '')
                            if url:
                                # Add stable parameters to raw URL
                                stable_url = f"{url}&fm=jpg&q=80&w=1200&fit=max"
                                image_urls.append(stable_url)
                                print(f"[{datetime.now()}] Image {i+1}: {stable_url[:80]}...")
                        except Exception as e:
                            print(f"[{datetime.now()}] Failed to extract URL from photo {i+1}: {e}")
                            
                elif isinstance(photos, dict):
                    try:
                        url = photos.get('urls', {}).get('raw', '')
                        if url:
                            stable_url = f"{url}&fm=jpg&q=80&w=1200&fit=max"
                            image_urls.append(stable_url)
                            print(f"[{datetime.now()}] Single image: {stable_url[:80]}...")
                    except Exception as e:
                        print(f"[{datetime.now()}] Failed to extract single photo URL: {e}")
                
                # Filter out empty URLs
                image_urls = [url for url in image_urls if url and len(url) > 50]
                
                print(f"[{datetime.now()}] Successfully processed {len(image_urls)} valid images from Unsplash")
                
                if len(image_urls) < count:
                    print(f"[{datetime.now()}] WARNING: Only got {len(image_urls)} valid images, requested {count}")
                    
                return image_urls
            else:
                print(f"[{datetime.now()}] Unsplash API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"[{datetime.now()}] Error fetching Unsplash images: {e}")
            return []



    async def generate_website_content(self, product_type: str, reference_url: str, design_style: str, mode: str = 'vision') -> dict:
        """
        Generate website content using Gemini with Vision (screenshot analysis).
        
        Args:
            product_type: Type of product for the website
            reference_url: Reference website URL for design inspiration
            design_style: User's design style preferences
            mode: 'vision' (screenshot + Gemini url_context), 'url_context', or 'none'
        """
        print(f"[{datetime.now()}] Received generation request for: {product_type}")
        print(f"[{datetime.now()}] Design style (user request): {design_style}")
        print(f"[{datetime.now()}] Generation Mode: {mode.upper()}")
        
        self._check_rate_limits()

        # vision 또는 hybrid 모드라면 캡쳐 실행
        screenshot_data = None
        effective_mode = mode  # 실제 사용할 모드 (폴백 시 변경됨)
        
        if (mode == 'vision' or mode == 'hybrid') and reference_url and reference_url.strip():
            screenshot_data = await self._capture_screenshot(reference_url)
            
            # 스크린샷 캡쳐 실패 시 url_context로 자동 폴백
            if not screenshot_data:
                print(f"[{datetime.now()}] Screenshot capture failed, falling back to url_context mode")
                effective_mode = 'url_context'

        # unsplash 이미지url 담기
        unsplash_images = self._get_unsplash_images(product_type, count=12)
        
        # 가져온 이미지url을 적절히 알아서 넣음
        if unsplash_images:
            image_instruction = f"""
        IMAGE REQUIREMENTS - USE THESE UNSPLASH URLS:
        You MUST use these pre-fetched Unsplash image URLs in your HTML:
        {chr(10).join([f'        - {url}' for url in unsplash_images])}
        
        Use different images for swipe banner, product gallery, testimonials, etc.
        All images are landscape-oriented and professional quality.
        CRITICAL: Use ONLY these URLs, do not generate or modify them.
        """
        else:
            image_instruction = """
        IMAGE REQUIREMENTS - FALLBACK (Lorem Flickr):
        Use Lorem Flickr for images: https://loremflickr.com/800/600/keyword1,keyword2
        Choose keywords matching the product type (soap, cosmetics, food, etc.)
        """
        
        # Build reference section based on mode
        html_content = ""

        # Vision 모드(스크린샷 찍었을 경우 전달하는 프롬프트)
        if screenshot_data:
            reference_section = f"""
## 레퍼런스 분석(hybrid/vision 모드)
**필수**: 
1. 첨부된 **스크린샷**을 완벽하게 분석하여 디자인 스타일을 완벽하게 복제(특히 메인 배너 영역)하시오.
2. 첨부된 **스크린샷**이 비어있는 화면이거나 정상적인 웹사이트라고 판단되지 않을 경우 최대한 사용자의 디자인 의견을 따르고 화려하고 부드러운 인터랙션이 가득한 사이트를 제작하시오.
**레퍼런스 URL**: {reference_url}
**스크린샷 분석 가이드**:
1. **레이아웃 & 배치**: 헤더, 배너 위치, 카드 그리드 구조, 카드 모서리 라운드, 카드 내부 구조 등을 시각적으로 파악하십시오.
2. **스타일**: 여백, 비율, 폰트 분위기를 확인하십시오.
3. **구현 규칙**:
   - 스크린샷과 **90% 이상 동일한 레이아웃** 구현
   - Hero section은 최대한 full-width 형태를 **피하고** 스크린샷과 동일한 구조로 구현
   - 팝업/모달은 **무시하고** 본문 디자인만 구현
   - 잘린 하단부는 **자연스럽게 추가 확장(최소 400px이상)**하여 완성(Footer 필수)
"""
            if mode == 'hybrid':
                 reference_section += "\n- **url_context**: 제공되는 url_context tool을 반드시 사용하여 최신 텍스트/데이터의 분위기와 인터랙션등의 분석을 통해 정확성을 보완하십시오."

        # url_context 모드 (또는 vision/hybrid에서 스크린샷 실패 시)
        elif effective_mode == 'url_context' and reference_url:
            fallback_notice = ""
            if mode != effective_mode:
                fallback_notice = f"\n**[자동 폴백]**: 원래 '{mode}' 모드였으나 스크린샷 캡쳐 실패로 url_context 모드로 전환됨.\n"
            
            reference_section = f"""
## 레퍼런스 분석 (URL Context){fallback_notice}
**필수**: **URL Context 도구(Gemini URL Context)**를 사용하여 해당 사이트의 최신 정보를 직접 조회하고 반영하십시오.
**URL Context 참고 url** : https://ai.google.dev/gemini-api/docs/url-context.md.txt?_gl=1*o39wau*_up*MQ..*_ga*MjUyMjU5Ny4xNzY1OTQ5ODk3*_ga_P1DBVKWT6V*czE3NjU5NDk4OTckbzEkZzAkdDE3NjU5NDk4OTckajYwJGwwJGgxNjUwNDQwNTM5
**대상 URL**: {reference_url}
**분석 가이드**:
1. 사이트의 구조, 판매 상품, 브랜드 컬러 등을 도구를 통해 파악하십시오.
2. 최대한 파악된 이미지, 배너, 컬러등의 반영된 정보로 레이아웃을 구성하십시오.
"""

        # html 모드 (HTML 소스코드 정제해서 전달)
        elif effective_mode == 'html' and reference_url:
            html_content = ""
            try:
                print(f"[{datetime.now()}] Fetching raw HTML for Smart Filtering from: {reference_url}")
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, lambda: requests.get(reference_url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.7499.41 Safari/537.36'
                }))
                
                if response.status_code == 200:
                    html_content = self._clean_html(response.text)
                    print(f"[{datetime.now()}] Smart Filtering applied. Length: {len(html_content)}")
                else:
                    html_content = f"Error: Failed to fetch URL (Status {response.status_code})"
            except Exception as e:
                html_content = f"Error: {str(e)}"

            reference_section = f"""
## 레퍼런스 분석 (html 모드)
**필수**: 아래 제공된 **HTML 소스코드**를 분석하여 구조와 스타일을 최대한 파악하십시오.
**원본 URL**: {reference_url}
**분석 데이터(분석에 불필요한 코드는 정제)**:
```html
{html_content}
```
**분석 가이드**:
1. **구조 파악**: `SVG_ICON`위치, 헤더/푸터 구조, 클래스명, 배너형태, CSS 등을 통해 레이아웃을 파악하십시오.
2. **스타일 추론**: 남겨진 외부 스크립트/CSS 링크와 인라인 스타일을 참고하십시오.
3. **내용 채우기**: 메타 태그와 남겨진 텍스트를 바탕으로 정확한 컨텐츠를 생성하십시오.
"""

        # 레퍼런스 URL 없음
        else:
            reference_section = """
## 기본 디자인 참조
- 레퍼런스 없음 → Awwwards E-commerce 수준 퀄리티 적용
- 사용자의 요청에 따라 자유로우며 부드러운 인터랙션이 적용된 디자인을 구현
"""

        prompt = f"""
# Role
세계 최고의 UI/UX 디자이너이자 프론트엔드 개발자

# Goal
프리미엄 마이크로 인터랙션이 적용된 한국형 이커머스 사이트 생성
- **상품**: {product_type}
- **레퍼런스**: {reference_url if reference_url else "없음"}
- **사용자 요청사항**: {design_style}

---

# 1. 분석 (Analysis)

## 상품 분석
- 핵심 키워드 추출 → 어울리는 컬러 팔레트 선정
{reference_section}

---

# 2. 우선순위 (Priority)

**최우선**: 사용자 요청사항 "{design_style}"은 반드시 100% 구현하시오.

| 순위 | 항목 | 설명 |
|:---:|------|------|
-| 1 | **사용자 요청사항** | "{design_style}" - 무조건 반영 |
-| 2 | 레퍼런스 스타일 | 90%이상 유사하게 구현 |
-| 3 | 기본 디자인 표준 | Awwwards 수준에 부드러운 인터랙션이 적용된 고퀄리티 디자인 |

---

# 3. 조건별 실행 규칙

| 상품 | 레퍼런스 | 처리 |
|------|----------|------|
-| test/테스트 | 있음 | 레퍼런스 클론 코딩 |
-| test/테스트 | 없음 | 최소 기본 사이트 |
-| 일반 | 있음 | 레퍼런스 스타일 + 상품 반영 |
-| 일반 | 없음 | 창의적 독창 디자인 |

---

# 4. 디자인 시스템

## 사용자 요청 최우선
**사용자 요청사항 "{design_style}"이 있다면 → 그 요청을 100% 따르시오.**
- Hero section에 대한 요청이 없을 경우 단일 full width의 hero는 최대한 피하십시오.

## 기본 레이아웃 (사용자 요청이 없거나 애매할 때)
사용자가 특정 레이아웃을 지정하지 않았다면, 다음 중 **창의적으로 선택**:

1. **멀티 배너형** - W컨셉, 무신사 스타일 (배너 3~5개 가로 배열로 무한 캐러셀)
2. **그리드 갤러리형** - Pinterest, 29cm 스타일 (다양한 크기 카드 배치)
3. **매거진형** - 에디토리얼 느낌, 큰 이미지 + 텍스트 조합
4. **카드 중심형** - 상품 카드가 주를 이루는 깔끔한 그리드
5. **자유 제작형** - 학습된 스타일 중 가장 창의적이고 독창적인 스타일

## 필수 요소
- **컬러**: 일관된 팔레트 (레퍼런스 있으면 동일 색상)
- **폰트**: 상품/분위기에 어울리는 Google Fonts 중 하나
- **인터랙션**: 부드럽고 화려한 마이크로 애니메이션 필수
- **호버**: 버튼, 카드, 이미지에 세련된 효과

## 기술적 구현 가이드 (오류 방지 필수)
1. **Swiper.js를 쓸 경우 (캐러셀) 안전 구현**:
   - `loop: true` 옵션 사용 시 반드시 **슬라이드 개수를 충분히(최소 4개 이상)** 확보하십시오. (복제된 슬라이드 부족 오류 방지)
   - Swiper 초기화(`new Swiper(...)`)는 반드시 `<body>` 닫는 태그 직전의 `<script>` 안에서 수행하십시오.
   - `pagination`이나 `navigation` 요소가 HTML에 실제로 존재하는지 확인하십시오.
   - 이외에 다른 라이브러리가 가능할 경우 사용하여 다양한 인터랙션 캐러샐을 시도합니다.
2. **페이지 완성도**:
   - 코드가 중간에 잘리지 않게 하십시오.
   - 반드시 `<footer`> 태그로 끝나야 합니다.

{image_instruction}

---

# 5. 출력 형식

```
<!DOCTYPE html>
<html lang="ko">
<head>...</head>
<body>...</body>
</html>
<<<METADATA_SEPARATOR>>>
{{"explanation": "디자인 의도를 자연스러운 문장형 서술로 작성하세요 (번호 매기기 금지).", "key_points": ["..."], "color_palette": ["..."]}}
```

---

# 체크리스트
- [ ] 사용자 요청 100% 반영
- [ ] 레퍼런스 80-90% 유사 (해당 시)
- [ ] 마이크로 인터랙션 적용
- [ ] 레이아웃 제약 준수
- [ ] 프리미엄 퀄리티
"""
        
        # Build content with optional screenshot
        contents = []
        
        if screenshot_data:
            # Add screenshot as image part
            print(f"[{datetime.now()}] Adding screenshot to Gemini request")
            contents.append(Part.from_bytes(data=screenshot_data, mime_type="image/png"))
            contents.append(prompt)
        else:
            contents.append(prompt)
        
        # Configure tools - Enable URL Context based on mode
        tools = []
        # effective_mode 기준으로 url_context tool 활성화 (폴백 케이스 포함)
        if (effective_mode == 'hybrid' or effective_mode == 'url_context') and reference_url and reference_url.strip():
            tools.append({"url_context": {}})
            print(f"[{datetime.now()}] Enabled URL Context tool for {effective_mode} analysis: {reference_url}")
        
        # Retry logic
        max_retries = 2
        last_error = None
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"[{datetime.now()}] Retry attempt {attempt + 1}/{max_retries}")
                    
                print(f"[{datetime.now()}] Sending request to Gemini API...")
                
                # Generate content with or without tools
                config_params = {
                    "temperature": 0.8,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 64000,
                }
                
                if tools:
                    config_params["tools"] = tools
                
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=contents,
                    config=GenerateContentConfig(**config_params)
                )
                
                # Log metadata (Grounding / URL Context)
                if response.candidates:
                    candidate = response.candidates[0]
                    
                    # 1. Check Grounding Metadata (Common for Search/URL)
                    if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                        print(f"[{datetime.now()}] 🔍 Grounding Metadata Found: {candidate.grounding_metadata}")
                    
                    # 2. Check URL Context Metadata (Specific)
                    if hasattr(candidate, 'url_context_metadata'):
                        meta_val = candidate.url_context_metadata
                        if meta_val:
                            print(f"[{datetime.now()}] 🔗 URL Context Metadata: {meta_val}")
                
                print(f"[{datetime.now()}] Received response from Gemini")
                
                # Extract text safely (handling tool use responses)
                raw_text = ""
                try:
                    if response.text:
                        raw_text = response.text.strip()
                except Exception:
                    # Fallback: iterate through parts if .text property fails (common with tools)
                    try:
                        if response.candidates and response.candidates[0].content.parts:
                            for part in response.candidates[0].content.parts:
                                if part.text:
                                    raw_text += part.text
                        raw_text = raw_text.strip()
                    except Exception as e:
                        print(f"[{datetime.now()}] Failed to extract text parts: {e}")

                if not raw_text:
                    print(f"[{datetime.now()}] Error: Empty response text received")
                    raise ValueError("Empty response text from Gemini")

                print(f"[{datetime.now()}] Raw response length: {len(raw_text)} chars")
                
                # Clean up markdown fencing if present (sometimes Gemini still adds it)
                if raw_text.startswith("```html"):
                    raw_text = raw_text[7:]
                elif raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                
                raw_text = raw_text.strip()
                
                # Parse using the separator
                separator = "<<<METADATA_SEPARATOR>>>"
                
                if separator in raw_text:
                    parts = raw_text.split(separator)
                    html_content = parts[0].strip()
                    json_part = parts[1].strip()
                    
                    # Clean up JSON part if it has markdown
                    if json_part.startswith("```json"):
                        json_part = json_part[7:]
                    if json_part.endswith("```"):
                        json_part = json_part[:-3]
                    json_part = json_part.strip()
                    
                    try:
                        metadata = json.loads(json_part, strict=False)
                        print(f"[{datetime.now()}] Successfully parsed metadata JSON")
                    except json.JSONDecodeError as je:
                        print(f"[{datetime.now()}] Metadata JSON parsing failed: {je}")
                        # Fallback metadata
                        metadata = {
                            "explanation": "디자인 생성 완료 (메타데이터 파싱 실패)",
                            "key_points": ["반응형 디자인", "모던 스타일", "인터랙티브 요소"],
                            "color_palette": ["#333333", "#ffffff"]
                        }
                    
                    # Clean HTML: Remove any text before <!DOCTYPE or <html
                    html_clean = html_content
                    prefix_explanation = ""
                    
                    # Find the start of actual HTML
                    doctype_pos = html_content.lower().find("<!doctype")
                    html_tag_pos = html_content.lower().find("<html")
                    
                    if doctype_pos != -1:
                        start_pos = doctype_pos
                    elif html_tag_pos != -1:
                        start_pos = html_tag_pos
                    else:
                        start_pos = 0
                    
                    if start_pos > 0:
                        prefix_explanation = html_content[:start_pos].strip()
                        html_clean = html_content[start_pos:]
                        print(f"[{datetime.now()}] Removed {len(prefix_explanation)} chars of prefix text from HTML")
                    
                    # Construct final result
                    result = {
                        "html": html_clean,
                        "explanation": metadata.get("explanation", prefix_explanation or ""),
                        "key_points": metadata.get("key_points", []),
                        "color_palette": metadata.get("color_palette", [])
                    }
                    
                    print(f"[{datetime.now()}] HTML length: {len(result['html'])} chars")
                    return result
                    
                else:
                    # Fallback: Maybe Gemini returned just JSON or just HTML?
                    # Try to parse as JSON (old way) just in case
                    try:
                        print(f"[{datetime.now()}] Separator not found, trying legacy JSON parse...")
                        # Actually, let's just treat the whole thing as HTML if it looks like HTML
                        if "<html" in raw_text.lower():
                            print(f"[{datetime.now()}] Treating entire response as HTML")
                            
                            # Clean HTML: Remove any text before <!DOCTYPE or <html
                            html_clean = raw_text
                            doctype_pos = raw_text.lower().find("<!doctype")
                            html_tag_pos = raw_text.lower().find("<html")
                            
                            if doctype_pos != -1:
                                start_pos = doctype_pos
                            elif html_tag_pos != -1:
                                start_pos = html_tag_pos
                            else:
                                start_pos = 0
                            
                            if start_pos > 0:
                                html_clean = raw_text[start_pos:]
                                print(f"[{datetime.now()}] Removed prefix text from HTML (fallback)")
                            
                            return {
                                "html": html_clean,
                                "explanation": "자동 생성된 디자인",
                                "key_points": [],
                                "color_palette": []
                            }
                        else:
                             raise ValueError("Response format invalid: Separator not found and not HTML")
                    except Exception as e:
                        raise ValueError(f"Failed to parse response: {str(e)}")

            except Exception as e:
                print(f"[{datetime.now()}] Error during generation: {type(e).__name__}: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                last_error = e
                print(f"[{datetime.now()}] Will retry...")
                continue
        
        # If we get here, all retries failed
        raise ValueError(f"Failed to generate content after {max_retries} attempts. Last error: {last_error}")
    
    async def cleanup(self):
        """Clean up browser resources"""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        print(f"[{datetime.now()}] Playwright browser cleaned up")

# Create singleton instance
gemini_service = GeminiService()
