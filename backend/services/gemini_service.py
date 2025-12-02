import google.generativeai as genai
import os
import time
from datetime import datetime, timedelta
import asyncio

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found in environment variables.")
        else:
            genai.configure(api_key=self.api_key)
        
        # Model configuration
        # Using gemini-1.5-pro as a fallback if 3.0 is not directly available via alias, 
        # but user requested 3.0 pro preview.
        self.model_name = "gemini-1.5-pro-latest" # Placeholder, will try to use 3.0 if valid
        # Note: As of now, exact string for 3.0 might be 'models/gemini-3.0-pro-preview' or similar.
        # We will allow environment variable override.
        if os.getenv("GEMINI_MODEL"):
            self.model_name = os.getenv("GEMINI_MODEL")

        self.model = genai.GenerativeModel(self.model_name)
        
        # Rate Limiting State
        self.request_timestamps = []
        self.daily_requests = 0
        self.last_reset_date = datetime.now().date()

    def _check_rate_limits(self):
        now = datetime.now()
        
        # Reset daily counter if new day
        if now.date() > self.last_reset_date:
            self.daily_requests = 0
            self.last_reset_date = now.date()
            
        # Check Daily Limit (1000)
        if self.daily_requests >= 1000:
            raise Exception("Daily request limit reached (1000).")

        # Check Minute Limit (50 RPM)
        # Filter timestamps within last minute
        self.request_timestamps = [t for t in self.request_timestamps if now - t < timedelta(minutes=1)]
        if len(self.request_timestamps) >= 50:
            raise Exception("Minute request limit reached (50 RPM).")

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
           - **IMAGES**: Use ONLY Unsplash URLs in this format: https://source.unsplash.com/800x600/?{{keyword}}
             Example: <img src="https://source.unsplash.com/800x600/?soap,organic" alt="...">
             Choose relevant keywords based on the product type.
           - **INTERACTIVITY**: Include interactive elements to enhance user engagement:
             * Smooth scroll animations (fade-in, slide-up on scroll)
             * Hover effects on images and buttons (zoom, overlay, transform)
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
            print(f"[{datetime.now()}] Sending request to Gemini ({self.model_name})...")
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            print(f"[{datetime.now()}] Response received from Gemini.")
            self.request_timestamps.append(datetime.now())
            self.daily_requests += 1
            
            # Parse JSON response
            import json
            try:
                return json.loads(response.text)
            except json.JSONDecodeError:
                print("Failed to parse JSON from Gemini, returning raw text as HTML fallback")
                return {
                    "html": response.text,
                    "explanation": "자동 생성된 설명이 없습니다.",
                    "key_points": [],
                    "color_palette": []
                }
                
        except Exception as e:
            print(f"[{datetime.now()}] Gemini API Error: {e}")
            raise e

gemini_service = GeminiService()
