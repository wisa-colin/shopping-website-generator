import google.generativeai as genai
import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup, Comment

class GeminiService:
    def __init__(self):
        # Get API keys from environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.unsplash_access_key = os.getenv("UNSPLASH_ACCESS_KEY")
        if not self.unsplash_access_key:
            print("WARNING: UNSPLASH_ACCESS_KEY not found, will use fallback images")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Get model name from environment or use default
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
        print(f"Using Gemini model: {model_name}")
        
        # Initialize model with generation config
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.8,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 64000,
            }
        )
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # seconds
    
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
            prompt = f"""
            Translate this product description into 2-3 simple English keywords for stock photo search.
            Input: "{product_type}"
            
            Rules:
            1. Output ONLY the keywords separated by spaces
            2. No punctuation, no explanations
            3. Focus on the visual object (e.g. "warm roasted sweet potato lollipop" -> "lollipop candy dessert")
            """
            
            response = self.model.generate_content(prompt)
            keywords = response.text.strip()
            # Remove any accidental quotes or newlines
            keywords = keywords.replace('"', '').replace('\n', ' ')
            print(f"[{datetime.now()}] Translated '{product_type}' -> '{keywords}'")
            return keywords
        except Exception as e:
            print(f"[{datetime.now()}] Keyword extraction failed: {e}")
            # Fallback to simple replacement
            return product_type.replace("천연 재료로 만든 ", "").replace("수제 ", "")

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
    
    def _clean_html(self, html_content: str) -> str:
        """
        Smart Filtering: Clean HTML to keep only structure and style-relevant tags.
        Removes noise like SVG paths, base64 images, and long text.
        """
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

    async def generate_website_content(self, product_type: str, reference_url: str, design_style: str, mode: str = 'smart') -> dict:
        print(f"[{datetime.now()}] Received generation request for: {product_type}")
        print(f"[{datetime.now()}] Design style (user request): {design_style}")
        print(f"[{datetime.now()}] Generation Mode: {mode.upper()}")
        
        self._check_rate_limits()

        # Fetch Reference URL content based on mode
        reference_html = ""
        fetch_success = False
        
        if reference_url and reference_url.strip() and mode != 'none':
            try:
                print(f"[{datetime.now()}] Fetching reference URL content: {reference_url}")
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                resp = requests.get(reference_url, headers=headers, timeout=10)
                
                if resp.status_code == 200:
                    raw_html = resp.text
                    print(f"[{datetime.now()}] Fetched {len(raw_html)} chars")
                    
                    if mode == 'smart':
                        print(f"[{datetime.now()}] Applying Smart Filtering...")
                        reference_html = self._clean_html(raw_html)
                        print(f"[{datetime.now()}] Cleaned HTML length: {len(reference_html)} chars")
                    else: # mode == 'raw'
                        reference_html = raw_html[:60000] # Limit to 60k chars
                        print(f"[{datetime.now()}] Using Raw HTML (truncated to 60k)")
                    
                    fetch_success = True
                else:
                    print(f"[{datetime.now()}] Failed to fetch reference URL: {resp.status_code}")
            except Exception as e:
                print(f"[{datetime.now()}] Error fetching reference URL: {e}")
        
        # Fetch Unsplash images
        unsplash_images = self._get_unsplash_images(product_type, count=8)
        
        # Build image instructions
        if unsplash_images:
            image_instruction = f"""
        IMAGE REQUIREMENTS - USE THESE UNSPLASH URLS:
        You MUST use these pre-fetched Unsplash image URLs in your HTML:
        {chr(10).join([f'        - {url}' for url in unsplash_images])}
        
        Use different images for hero, product gallery, testimonials, etc.
        All images are landscape-oriented and professional quality.
        CRITICAL: Use ONLY these URLs, do not generate or modify them.
        """
        else:
            image_instruction = """
        IMAGE REQUIREMENTS - FALLBACK (Lorem Flickr):
        Use Lorem Flickr for images: https://loremflickr.com/800/600/keyword1,keyword2
        Choose keywords matching the product type (soap, cosmetics, food, etc.)
        """
        
        # Build reference section
        if reference_url and reference_url.strip():
            reference_source_info = ""
            if fetch_success and reference_html:
                reference_source_info = f"""
**참고 사이트 HTML 소스 (스타일 분석용)**:
```html
{reference_html}
```
"""
            elif mode == 'none':
                 reference_source_info = "**참고 사이트 소스 제공 안함 (URL만 참조)**"

            reference_section = f"""
## 레퍼런스 분석 (최우선 - 반드시 수행)

⚠️ **필수**: 아래 URL 및 제공된 소스코드를 분석하여 스타일을 완벽하게 복제하십시오.
**URL**: {reference_url}

{reference_source_info}

**반드시 분석해야 할 항목**:
1. **컬러 팔레트**: 정확한 HEX 코드 추출 (Primary, Secondary, Accent, Background)
2. **폰트**: 사용된 폰트 패밀리, 크기, 굵기
3. **레이아웃**: Max-width, 여백, 섹션 구조, 그리드 시스템
4. **인터랙션**: 애니메이션 종류, 호버 효과, 전환 속도
5. **전체 분위기**: 디자인 톤앤매너

**구현 규칙**:
- 레퍼런스 사이트와 **90% 이상 동일한 스타일**로 구현
- 동일한 컬러 코드, 동일한 레이아웃(mobile only/first 포함) 구조 사용
- 사용된 라이브러리가 있다면 동일하게 적용 (GSAP, Swiper 등)
- 사용자 요청과 충돌 시에만 사용자 요청 우선
"""
        else:
            reference_section = """
## 기본 디자인 참조
- 레퍼런스 없음 → Awwwards E-commerce 수준 퀄리티 적용
- 참고: https://www.awwwards.com/websites/e-commerce/
- UI 참고: https://uiverse.io/elements
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

⚠️ **최우선**: 사용자 요청사항 "{design_style}"은 반드시 100% 구현하시오.

| 순위 | 항목 | 설명 |
|:---:|------|------|
| 1 | **사용자 요청사항** | "{design_style}" - 무조건 반영 |
| 2 | 레퍼런스 스타일 | 80-90% 유사하게 구현 |
| 3 | 기본 디자인 표준 | Awwwards 수준 |

---

# 3. 조건별 실행 규칙

| 상품 | 레퍼런스 | 처리 |
|------|----------|------|
| test/테스트 | 있음 | 레퍼런스 클론 코딩 |
| test/테스트 | 없음 | 최소 기본 사이트 |
| 일반 | 있음 | 레퍼런스 스타일 + 상품 반영 |
| 일반 | 없음 | 창의적 독창 디자인 |

---

# 4. 디자인 시스템

## 🎯 사용자 요청 최우선
**사용자 요청사항 "{design_style}"이 있다면 → 그 요청을 100% 따르시오.**
(단일 hero를 원하면 단일 hero로, 미니멀을 원하면 미니멀로)

## 📐 기본 레이아웃 (사용자 요청이 없거나 애매할 때)
사용자가 특정 레이아웃을 지정하지 않았다면, 다음 중 **창의적으로 선택**:

1. **멀티 배너형** - W컨셉, 무신사 스타일 (배너 3~5개 가로 배열)
2. **그리드 갤러리형** - Pinterest, 29cm 스타일 (다양한 크기 카드 배치)
3. **매거진형** - 에디토리얼 느낌, 큰 이미지 + 텍스트 조합
4. **카드 중심형** - 상품 카드가 주를 이루는 깔끔한 그리드

⚠️ **주의**: 사용자가 명시적으로 요청하지 않는 한, 단순히 큰 이미지 하나만 있는 레이아웃은 피하시오.

## 필수 요소
- **컬러**: 일관된 팔레트 (레퍼런스 있으면 동일 색상)
- **폰트**: 상품/분위기에 어울리는 Google Fonts
- **인터랙션**: 부드럽고 화려한 마이크로 애니메이션 필수
- **호버**: 버튼, 카드, 이미지에 세련된 효과

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
{{"explanation": "...", "key_points": ["..."], "color_palette": ["..."]}}
```

---

# 체크리스트
- [ ] 사용자 요청 100% 반영
- [ ] 레퍼런스 80-90% 유사 (해당 시)
- [ ] 마이크로 인터랙션 적용
- [ ] 레이아웃 제약 준수
- [ ] 프리미엄 퀄리티
"""
        
        # Retry logic
        max_retries = 2
        last_error = None
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"[{datetime.now()}] Retry attempt {attempt + 1}/{max_retries}")
                    
                print(f"[{datetime.now()}] Sending request to Gemini API...")
                response = self.model.generate_content(prompt)
                print(f"[{datetime.now()}] Received response from Gemini")
                
                # Extract text
                raw_text = response.text.strip()
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
                    
                    # Construct final result
                    result = {
                        "html": html_content,
                        "explanation": metadata.get("explanation", ""),
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
                        # ... (legacy parsing logic omitted for brevity, assuming new prompt works)
                        # Actually, let's just treat the whole thing as HTML if it looks like HTML
                        if "<html" in raw_text.lower():
                            print(f"[{datetime.now()}] Treating entire response as HTML")
                            return {
                                "html": raw_text,
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

# Create singleton instance
gemini_service = GeminiService()
