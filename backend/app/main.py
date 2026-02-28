from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
import os
import json
import base64
from io import BytesIO
from PIL import Image

# 1. THE ROUTER (FastAPI)
# We initialize the FastAPI application. This is the engine that will handle HTTP requests.
app = FastAPI(
    title="Fridge AI Backend", 
    description="Stateless microservice for multimodal recipe generation",
    version="1.0"
)

# 2. THE CONTRACT (Pydantic)
# This defines the EXACT schema we expect from the frontend. 
# If a request hits our API without the "image_base64" key, Pydantic intercepts it 
# and returns a 422 Unprocessable Entity error automatically. We don't have to write validation logic.
class ImagePayload(BaseModel):
    image_base64: str

def decode_image(base64_string: str) -> Image.Image:
    """Helper function: Safely decodes a base64 string into a PIL Image."""
    try:
        # Frontends often prepend metadata like "data:image/jpeg;base64,". We strip that out if it exists.
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
            
        image_data = base64.b64decode(base64_string)
        return Image.open(BytesIO(image_data))
    except Exception as e:
        # If the string isn't a valid image, we catch it here before it ever reaches the LLM.
        raise ValueError("Invalid base64 image encoding")

# 3. THE ENDPOINT
# We define a POST route. The `payload: ImagePayload` argument tells FastAPI to use our Pydantic contract.
@app.post("/analyze")
async def analyze_fridge(payload: ImagePayload):
    
    # SECURITY: We pull the API key from the environment, NOT a local file. 
    # This ensures that when deployed to GCP, Cloud Run can inject the secret securely.
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="LLM API Key not configured in environment.")
    
    try:
        # 4. THE CORE LOGIC (google-genai)
        image = decode_image(payload.image_base64)
        client = genai.Client(api_key=api_key)
        
        prompt = """You are a culinary AI assistant. Analyze the provided image of a refrigerator or ingredients. 
        Return a valid JSON object with exactly three keys:
        1. 'ingredients': A list of strings of identified food items.
        2. 'missing_essentials': A list of 2-3 common staple items that seem to be missing.
        3. 'recipes': A list of 2-3 suggested pure vegetarian Indian or fusion recipes based heavily on the found ingredients. Each recipe should be an object with 'name' and 'cuisine' keys."""
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[image, prompt],
            # Enforcing strict JSON output at the API level
            config={"response_mime_type": "application/json"} 
        )
        
        # We parse the string response into a Python dictionary, and FastAPI automatically 
        # converts it into a proper JSON HTTP response for the client.
        return json.loads(response.text)
        
    except ValueError as ve:
        # Catches the base64 decoding errors (Client Error)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Catches API or LLM processing errors (Server Error)
        raise HTTPException(status_code=500, detail=str(e))
    