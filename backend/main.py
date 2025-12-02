from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# Import services
from services.gemini_service import gemini_service
import database

# Initialize DB
database.init_db()

app = FastAPI(title="Responsive Shopping Website Generator")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    product_type: str
    reference_url: Optional[str] = None
    design_style: str

class GenerateResponse(BaseModel):
    id: str
    status: str
    message: str

@app.get("/")
async def root():
    return {"message": "API is running", "docs": "/docs"}

@app.post("/generate", response_model=GenerateResponse)
async def generate_site(request: GenerateRequest, background_tasks: BackgroundTasks):
    site_id = str(uuid.uuid4())
    
    # Create pending record immediately
    database.create_pending_site(site_id, request.dict())
    
    async def process_generation(site_id: str, req: GenerateRequest):
        try:
            print(f"Starting generation for {site_id}...")
            # Call Gemini
            result = await gemini_service.generate_website_content(
                product_type=req.product_type,
                reference_url=req.reference_url or "None",
                design_style=req.design_style
            )
            
            html_content = result.get("html", "")
            
            # Update metadata with design info
            req_data = req.dict()
            req_data.update({
                "explanation": result.get("explanation"),
                "key_points": result.get("key_points"),
                "color_palette": result.get("color_palette")
            })
            
            # Update DB on success
            database.update_site_success_with_meta(site_id, html_content, req_data)
            print(f"Site {site_id} generated successfully.")
            
        except Exception as e:
            print(f"Generation failed for {site_id}: {e}")
            # Update DB on error
            database.update_site_error(site_id, str(e))
            
    background_tasks.add_task(process_generation, site_id, request)
    
    return {"id": site_id, "status": "pending", "message": "Generation started"}

@app.get("/results/{site_id}")
async def get_result(site_id: str):
    site = database.get_site(site_id)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site

@app.get("/gallery")
async def get_gallery():
    return database.get_all_sites()

@app.delete("/sites/{site_id}")
async def delete_site(site_id: str):
    """Delete a site by ID"""
    deleted = database.delete_site(site_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Site not found")
    return {"message": "Site deleted successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
