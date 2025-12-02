import google.generativeai as genai
import os
import json
import time
from datetime import datetime
from typing import Dict, Any

class GeminiService:
    def __init__(self):
        # Get API key from environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
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
    
    async def generate_website_content(self, product_type: str, reference_url: str, design_style: str) -> dict:
        print(f"[{datetime.now()}] Received generation request for: {product_type}")
        self._check_rate_limits()
        
        prompt = f"""
        You are a world-class UI/UX designer and frontend developer.
        
        **Goal**: Create a responsive shopping website for a product and explain your design choices.
        
        **Input Details**:
        - Product Type: {product_type}
        - Design Style/Description: {design_style}
        - Reference URL: {reference_url}
        
        **CRITICAL: REFERENCE URL ANALYSIS**
        If a reference URL is provided (not "None"), you MUST mention in your "explanation" whether you were able to consider it.
        Example: "레퍼런스 사이트의 미니멀한 레이아웃을 참고하여 디자인했습니다." or "레퍼런스 URL을 참고할 수 없었지만..."
        
        **CRITICAL REQUIREMENTS**:
        1. **Output Format**: Return a valid **JSON object** (no markdown fencing) with the following structure:
           {{
             "html": "<!DOCTYPE html>...", 
             "explanation": "MAXIMUM 1-2 sentences explaining the design choice AND mentioning if reference URL was considered.",
             "key_points": ["Point 1", "Point 2", "Point 3"],
             "color_palette": ["#Hex1", "#Hex2", "#Hex3", "#Hex4", "#Hex5"]
           }}
        
        2. **HTML Content ("html" field)**:
           - Max width 1000px, centered.
           - **RESPONSIVE**: Must adapt perfectly to Mobile (320px-767px), Tablet (768px-1023px), and Desktop (1024px+).
           
           - **IMAGES - ABSOLUTE CRITICAL REQUIREMENTS**:
             ⚠️ MUST USE REAL PHOTOGRAPHS ONLY - NO ICONS, NO ILLUSTRATIONS, NO PLACEHOLDERS
             
             Use Lorem Flickr which provides REAL PHOTOS from Flickr based on keywords:
             Format: https://loremflickr.com/WIDTH/HEIGHT/KEYWORD1,KEYWORD2
             
             **KEYWORD SELECTION RULES** (CRITICAL):
             - Choose keywords that EXACTLY match the product type
             - Use specific, descriptive keywords (not generic terms)
             - Multiple keywords separated by commas (no spaces)
             - Keywords should be in English
             
             **EXAMPLES BY PRODUCT TYPE**:
             
             Natural/Organic Soap:
             - https://loremflickr.com/800/600/soap,natural,handmade
             - https://loremflickr.com/800/600/spa,organic,wellness
             
             Cosmetics/Beauty Products:
             - https://loremflickr.com/800/600/cosmetics,beauty,skincare
             - https://loremflickr.com/800/600/makeup,organic,natural
             
             Food Products:
             - https://loremflickr.com/800/600/food,gourmet,artisan
             - https://loremflickr.com/800/600/sauce,cooking,kitchen
             
             Fashion/Bags:
             - https://loremflickr.com/800/600/handbag,leather,fashion
             - https://loremflickr.com/800/600/bag,accessory,style
             
             Candles:
             - https://loremflickr.com/800/600/candle,aromatherapy,home
             - https://loremflickr.com/800/600/candle,decor,ambiance
             
             Pet Products:
             - https://loremflickr.com/800/600/dog,pet,puppy
             - https://loremflickr.com/800/600/cat,pet,kitten
             
             **CRITICAL RULES**:
             1. ALWAYS analyze the product type and choose relevant keywords
             2. Use different keyword combinations for variety (e.g., first image: soap,natural,spa / second image: soap,handmade,organic)
             3. Keep keywords specific and directly related to the product
             4. NO generic keywords like "product" or "item"
             5. Each image must use different dimensions or keyword combinations for cache-busting
             
             **Example HTML**:
             ```html
             <img src="https://loremflickr.com/800/600/soap,natural,handmade" 
                  alt="천연 수제 비누" 
                  loading="lazy"
                  style="width: 100%; border-radius: 12px;" />
             ```
             
             **For Multiple Images**:
             Use slightly different keywords or dimensions:
             - Image 1: https://loremflickr.com/800/600/soap,natural,spa
             - Image 2: https://loremflickr.com/800/500/soap,handmade,organic  
             - Image 3: https://loremflickr.com/700/600/soap,artisan,wellness
             
           - **INTERACTIVITY**: Include interactive elements to enhance user engagement:
             * Smooth scroll animations (fade-in, slide-up on scroll)
             * Hover effects on images (zoom, overlay effects)
             * Animated navigation menu (hamburger menu for mobile)
             * Product image gallery with click-to-enlarge or carousel
             * Smooth transitions between sections
             * Interactive shopping cart icon with badge animation
             * Form validation with visual feedback
             Use vanilla JavaScript for all interactions - NO external libraries.
             
           - **Language**: ALL text content in Korean.
           - **Quality**: "World Class", award-winning e-commerce design with modern interactions.
           - **Self-contained**: All CSS and JS must be embedded in the HTML.
        
        3. **Design Rationale**:
           - "explanation": 1-2 sentences in Korean, MUST mention reference URL consideration if provided.
           - "key_points": 3-5 key design decisions in Korean.
           - "color_palette": Extract 4-5 main hex color codes used in the design (MUST include this!).
        
        **Design Direction**:
        - Analyze the product type and create an appropriate shopping experience.
        - If reference URL provided, try to incorporate similar design philosophy.
        - Use modern design trends: clean typography, ample whitespace, high-quality imagery.
        """
        
        try:
            print(f"[{datetime.now()}] Sending request to Gemini API...")
            response = self.model.generate_content(prompt)
            print(f"[{datetime.now()}] Received response from Gemini")
            
            # Extract text
            raw_text = response.text.strip()
            print(f"[{datetime.now()}] Raw response length: {len(raw_text)} chars")
            
            # Remove markdown fencing if present
            if raw_text.startswith("```"):
                lines = raw_text.split('\n')
                raw_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else raw_text
            
            # Parse JSON
            try:
                result = json.loads(raw_text)
                print(f"[{datetime.now()}] Successfully parsed JSON response")
                print(f"[{datetime.now()}] HTML length: {len(result.get('html', ''))} chars")
                print(f"[{datetime.now()}] Explanation: {result.get('explanation', 'N/A')}")
                print(f"[{datetime.now()}] Color palette: {result.get('color_palette', [])}")
                return result
            except json.JSONDecodeError as e:
                print(f"[{datetime.now()}] JSON parsing error: {e}")
                print(f"[{datetime.now()}] Raw text preview: {raw_text[:500]}...")
                raise ValueError(f"Failed to parse Gemini response as JSON: {str(e)}")
                
        except Exception as e:
            print(f"[{datetime.now()}] Error during generation: {type(e).__name__}: {str(e)}")
            raise

# Create singleton instance
gemini_service = GeminiService()
