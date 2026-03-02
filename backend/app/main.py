import os
import json
import base64
from io import BytesIO
from PIL import Image
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from google import genai

# --- 1. INITIALIZATION & RATE LIMITER ---
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Fridge AI Backend")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- 2. CORS POLICY ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ravi-fridge-chef.streamlit.app"], 
    allow_methods=["POST"],
    allow_headers=["*"],
)

# --- 3. DATA MODELS & HELPERS ---
class ImagePayload(BaseModel):
    image_base64: str

def decode_image(base64_string: str) -> Image.Image:
    try:
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        image_data = base64.b64decode(base64_string)
        return Image.open(BytesIO(image_data))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image encoding")

# --- 4. SECURITY MIDDLEWARE ---
PORTFOLIO_TOKEN = os.environ.get("X_PORTFOLIO_TOKEN", "fallback-secret-for-local-dev")

@app.middleware("http")
async def verify_portfolio_token(request: Request, call_next):
    if request.url.path == "/analyze":
        token = request.headers.get("X-Portfolio-Token")
        if token != PORTFOLIO_TOKEN:
            # FIX: Must RAISE, not return
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Unauthorized: Invalid Portfolio Token"
            )
    response = await call_next(request)
    return response

# --- 5. THE ENDPOINT ---
@app.post("/analyze")
@limiter.limit("5/minute") # FIX: Added the actual rate limit decorator
async def analyze_fridge(payload: ImagePayload, request: Request): # Added request param for Limiter
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="LLM API Key not configured.")
    
    try:
        image = decode_image(payload.image_base64)
        client = genai.Client(api_key=api_key)
        
        prompt = """You are a culinary AI assistant. Analyze the image. 
        Return JSON with: ingredients (list), missing_essentials (list), 
        recipes (list of objects with 'name' and 'cuisine'). 
        Focus on pure vegetarian Indian or fusion."""
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[image, prompt],
            config={"response_mime_type": "application/json"} 
        )
        
        return json.loads(response.text)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))