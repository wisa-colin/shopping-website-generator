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
        
        Create a responsive shopping website for: {product_type}
        Design style: {design_style}
        Reference URL: {reference_url}
        
        CRITICAL OUTPUT FORMAT - Return ONLY valid JSON (no markdown, no code fences):
        {{
          "html": "complete HTML code here",
          "explanation": "1-2 sentences in Korean about design choice",
          "key_points": ["point 1", "point 2", "point 3"],
          "color_palette": ["#hex1", "#hex2", "#hex3", "#hex4"]
        }}
        
        HTML REQUIREMENTS:
        - Max width 1000px, centered, fully responsive
        - Mobile (320-767px), Tablet (768-1023px), Desktop (1024px+)
        - ALL text in Korean
        - Embedded CSS and JavaScript only
        
        IMAGE REQUIREMENTS - CRITICAL:
        Use Lorem Flickr for REAL PHOTOS based on product keywords.
        Format: https://loremflickr.com/800/600/keyword1,keyword2,keyword3
        
        Choose keywords that match the product type exactly:
        - For soap: soap,natural,handmade or spa,organic,wellness
        - For cosmetics: cosmetics,beauty,skincare or makeup,organic,natural
        - For food: food,gourmet,artisan or sauce,cooking,kitchen
        - For bags: handbag,leather,fashion or bag,accessory,style
        - For candles: candle,aromatherapy,home or candle,decor,ambiance
        - For pet products: dog,pet,puppy or cat,pet,kitten
        
        Use different keyword combinations for each image for variety.
        Example: First image uses soap,natural,spa and second uses soap,handmade,organic
        
        INTERACTIVE FEATURES:
        - Smooth scroll animations
        - Hover effects on images and buttons
        - Hamburger menu for mobile
        - Shopping cart with badge animation
        - All interactions in vanilla JavaScript
        
        DESIGN RATIONALE:
        - If reference URL provided, mention if you considered it in explanation (in Korean)
        - Provide 3-5 key design decisions in Korean
        - Extract 4-5 main hex color codes from your design
        
        Remember: Output ONLY the JSON object, no other text.
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
                result = json.loads(raw_text)
                print(f"[{datetime.now()}] Successfully parsed JSON response")
                print(f"[{datetime.now()}] HTML length: {len(result.get('html', ''))} chars")
                print(f"[{datetime.now()}] Explanation: {result.get('explanation', 'N/A')}")
                print(f"[{datetime.now()}] Color palette: {result.get('color_palette', [])}")
                return result
            except json.JSONDecodeError as e:
                print(f"[{datetime.now()}] JSON parsing error: {e}")
                print(f"[{datetime.now()}] Raw text preview: {raw_text[:500]}...")
                # Try to find and extract JSON from the response
                try:
                    # Look for JSON object boundaries
                    start = raw_text.find('{')
                    end = raw_text.rfind('}') + 1
                    if start != -1 and end > start:
                        json_str = raw_text[start:end]
                        result = json.loads(json_str)
                        print(f"[{datetime.now()}] Successfully extracted and parsed JSON")
                        return result
                except:
                    pass
                raise ValueError(f"Failed to parse Gemini response as JSON: {str(e)}")
                
        except Exception as e:
            print(f"[{datetime.now()}] Error during generation: {type(e).__name__}: {str(e)}")
            raise

# Create singleton instance
gemini_service = GeminiService()
