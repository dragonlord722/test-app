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
from google.genai import types
import logging
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List

# Load the .env file explicitly
load_dotenv()

# Setup Logging
logging.basicConfig(level=logging.INFO)

class Recipe(BaseModel):
    name: str = Field(description="A creative name for the recipe")
    description: str = Field(description="A 2-sentence appetizing summary")
    ingredients_needed: List[str] = Field(description="List of items required from the fridge")
    instructions: str = Field(description="Step-by-step cooking guide")

class AnalysisResponse(BaseModel):
    is_valid_fridge_image: bool
    error_message: str
    ingredients: List[str] = Field(description="List of all visible food items")
    missing_essentials: List[str]
    recipes: List[Recipe] = Field(
        description="Provide at least 2-3 creative recipes based ONLY on the found ingredients."
    )

def load_prompt(version: str):
    # Ensure we look in the 'backend/prompts' directory relative to this file
    base_path = os.path.dirname(os.path.dirname(__file__))
    prompt_path = os.path.join(base_path, "prompts", f"{version}.md")
    
    try:
        with open(prompt_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"❌ Prompt file not found at {prompt_path}")
        return "Analyze this fridge image and return JSON." # Safe fallback

# --- 1. INITIALIZATION ---
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Fridge AI Backend")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- 2. CORS POLICY ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Staff Tip: Use "*" for local dev, restrict in prod
    allow_methods=["POST"],
    allow_headers=["*"],
)

# --- 3. DATA MODELS ---
class ImagePayload(BaseModel):
    image_base64: str

# --- 4. SECURITY MIDDLEWARE ---
PORTFOLIO_TOKEN = os.getenv("X_PORTFOLIO_TOKEN", "fallback-secret-for-local-dev")

@app.middleware("http")
async def verify_portfolio_token(request: Request, call_next):
    if request.url.path == "/analyze":
        token = request.headers.get("X-Portfolio-Token")
        if token != PORTFOLIO_TOKEN:
            # We return a JSONResponse here because Middleware 
            # handles exceptions differently than endpoints
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized: Invalid Portfolio Token"}
            )
    return await call_next(request)

# --- 5. THE ENDPOINT ---
@app.post("/analyze")
@limiter.limit("5/minute")
async def analyze_image(request: Request, payload: ImagePayload): # FIX: Use ImagePayload
    # 1. Load Prompt Version
    system_prompt = load_prompt(os.getenv("PROMPT_VERSION", "v2_guardrail"))

    # 2. Check API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="LLM API Key not configured.")

    try:
        # 3. Process Base64 String
        base64_str = payload.image_base64
        if "," in base64_str:
            base64_str = base64_str.split(",")[1]
        
        image_data = base64.b64decode(base64_str)
        image = Image.open(BytesIO(image_data))

        # 4. Call Gemini
        client = genai.Client(api_key=api_key)
        
        # Note: Ensure you are using the correct model string for your SDK version
        # Change from 'gemini-2.0-flash' to:
        config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema= AnalysisResponse,
        thinking_config=types.ThinkingConfig(
            include_thoughts=True, # Valid for 2.5 models
            thinking_budget=1024   # Valid for 2.5 models
            )
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=[image, system_prompt],        
            config=config
        )
        
        return response.parsed

       
    except Exception as e:
        logging.error(f"Prediction Error: {str(e)}")
        raise HTTPException(status_code=500, detail="AI processing failed.")