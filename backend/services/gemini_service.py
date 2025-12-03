import google.generativeai as genai
import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, Any, List

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
                "temperature": 1,
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
                
                # Handle both single photo and array responses (Unsplash API quirk)
                if isinstance(photos, list):
                    image_urls = [photo['urls']['regular'] for photo in photos]
                elif isinstance(photos, dict):
                    image_urls = [photos['urls']['regular']]
                else:
                    image_urls = []
                
                print(f"[{datetime.now()}] Successfully fetched {len(image_urls)} images from Unsplash")
                
                if len(image_urls) < count:
                    print(f"[{datetime.now()}] WARNING: Only got {len(image_urls)} images, requested {count}")
                    
                return image_urls
            else:
                print(f"[{datetime.now()}] Unsplash API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"[{datetime.now()}] Error fetching Unsplash images: {e}")
            return []
    
    async def generate_website_content(self, product_type: str, reference_url: str, design_style: str) -> dict:
        print(f"[{datetime.now()}] Received generation request for: {product_type}")
        self._check_rate_limits()
        
        # Fetch Unsplash images first
        unsplash_images = self._get_unsplash_images(product_type, count=8)
        
        # Build image instructions based on whether we have Unsplash images
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
        

        prompt = f"""
        You are a world-class UI/UX designer and frontend developer.
        
        Create a responsive shopping website for: {product_type}
        Design style: {design_style}
        Reference URL: {reference_url}
        
        CRITICAL OUTPUT FORMAT:
        1. First, output the COMPLETE HTML code directly. Do NOT wrap it in markdown code fences. Do NOT put it inside JSON.
        2. Then, output exactly this separator string: <<<METADATA_SEPARATOR>>>
        3. Finally, output the metadata in valid JSON format.
        
        Example Output Structure:
        <!DOCTYPE html>
        <html>
        ...
        </html>
        <<<METADATA_SEPARATOR>>>
        {{
          "explanation": "1-2 sentences in Korean...",
          "key_points": ["point 1", "point 2"],
          "color_palette": ["#hex1", "#hex2"]
        }}
        
        HTML REQUIREMENTS:
        - Max width 1920px, Min height 1500px, Max height 2500px, centered, fully responsive
        - Mobile (320-767px), Tablet (768-1023px), Desktop (1024px-1920px)
        - ALL text in Korean
        - Embedded CSS and JavaScript preferred, but you MAY use CDN libraries for advanced effects (e.g., GSAP, AOS, Swiper, FontAwesome) if needed.
        - If using CDN, ensure links are valid and reliable (e.g., cdnjs).
        
        
{image_instruction}
        
        IMPORTANT: To prevent output truncation, please MINIMIZE your HTML/CSS/JS where possible (remove excessive comments, use concise CSS).
        
        INTERACTIVE FEATURES (MAKE IT FEEL ALIVE AND DYNAMIC):
        - MANDATORY: Animated gradient background OR floating shapes/particles that continuously move
        - MANDATORY: At least 2-3 elements with infinite CSS animations (e.g., floating icons, pulsing buttons, rotating badges)
        - MANDATORY: Rich CSS animations (fade-in, slide-up, bounce) for all major sections
        - MANDATORY: Scroll-triggered reveal effects using Intersection Observer on ALL content sections
        - MANDATORY: Sophisticated hover effects on product cards (scale + shadow + tilt), buttons (glow/gradient shift), and images (zoom + overlay)
        - MANDATORY: Parallax scrolling on hero section (background moves slower than content)
        - Smooth hamburger menu animation for mobile (slide-in with backdrop blur)
        - Shopping cart icon with bounce/shake animation when interacted
        - Smooth transitions on all interactive elements (transition: all 0.3s ease)
        - GOAL: The site should feel PREMIUM and ALIVE with subtle continuous motion, not static like a boring template
        
        DESIGN RATIONALE:
        - If reference URL provided, mention if you considered it in explanation (in Korean)
        - Provide 3-5 key design decisions in Korean
        - Extract 4-5 main hex color codes from your design
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
