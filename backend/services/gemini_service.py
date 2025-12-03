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
                "temperature": 0.9,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
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
        
        CRITICAL OUTPUT FORMAT - Return ONLY valid JSON (no markdown, no code fences):
        {{
          "html": "complete HTML code here (MUST ESCAPE ALL DOUBLE QUOTES inside the HTML string)",
          "explanation": "1-2 sentences in Korean about design choice",
          "key_points": ["point 1", "point 2", "point 3"],
          "color_palette": ["#hex1", "#hex2", "#hex3", "#hex4"]
        }}
        
        JSON FORMATTING RULES (CRITICAL):
        - The "html" field MUST be a single-line string with ALL newlines escaped as \\n
        - ALL double quotes inside the HTML must be escaped as \\"
        - NO actual line breaks inside the "html" string value
        - Example: "html": "\u003c!DOCTYPE html\u003e\\n\u003chtml\u003e\\n\u003chead\u003e..."
        
        HTML REQUIREMENTS:
        - Max width 1920px, Min height 1500px, Max height 2500px, centered, fully responsive
        - Mobile (320-767px), Tablet (768-1023px), Desktop (1024px-1920px)
        - ALL text in Korean
        - Embedded CSS and JavaScript preferred, but you MAY use CDN libraries for advanced effects (e.g., GSAP, AOS, Swiper, FontAwesome) if needed.
- If using CDN, ensure links are valid and reliable (e.g., cdnjs).
        - IMPORTANT: Since this is inside a JSON string, you MUST escape all double quotes in HTML attributes like class=\"container\"
        
{image_instruction}
        
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
        
        Remember: Output ONLY the JSON object. Ensure all quotes within the HTML string are properly escaped.
        """
        
        # Retry logic for handling intermittent JSON parsing failures
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
                
                # Remove markdown fencing if present
                if raw_text.startswith("```"):
                    # Find the actual JSON content
                    lines = raw_text.split('\n')
                    # Skip first line (```json or ```) and last line (```)
                    if len(lines) > 2:
                        raw_text = '\n'.join(lines[1:-1])
                        # Also remove any remaining partial fencing
                        if raw_text.startswith("json"):
                            raw_text = raw_text[4:].strip()
                
                # Parse JSON
                try:
                    # Use strict=False to allow control characters inside strings
                    result = json.loads(raw_text, strict=False)
                    print(f"[{datetime.now()}] Successfully parsed JSON response")
                    print(f"[{datetime.now()}] HTML length: {len(result.get('html', ''))} chars")
                    print(f"[{datetime.now()}] Explanation: {result.get('explanation', 'N/A')}")
                    print(f"[{datetime.now()}] Color palette: {result.get('color_palette', [])}")
                    return result
                except json.JSONDecodeError as e:
                    print(f"[{datetime.now()}] JSON parsing error: {e}")
                    print(f"[{datetime.now()}] Error position: line {e.lineno} column {e.colno}")
                    print(f"[{datetime.now()}] Raw text preview: {raw_text[:500]}...")
                    
                    # Try to find and extract JSON from the response
                    try:
                        # Look for JSON object boundaries
                        start = raw_text.find('{')
                        end = raw_text.rfind('}') + 1
                        if start != -1 and end > start:
                            json_str = raw_text[start:end]
                            
                            # Try parsing the extracted JSON
                            result = json.loads(json_str, strict=False)
                            print(f"[{datetime.now()}] Successfully extracted and parsed JSON")
                            return result
                    except Exception as extraction_error:
                        print(f"[{datetime.now()}] Extraction also failed: {extraction_error}")
                    
                    # If this was the last attempt, raise the error
                    if attempt == max_retries - 1:
                        raise ValueError(f"Failed to parse Gemini response as JSON after {max_retries} attempts: {str(e)}")
                    else:
                        # Otherwise, retry
                        last_error = e
                        print(f"[{datetime.now()}] Will retry...")
                        continue
                        
            except ValueError:
                # Re-raise ValueError (from JSON parsing failure)
                raise
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
