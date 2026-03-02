import streamlit as st
import requests
import base64
from PIL import Image
import io

# Configuration from Secrets/Environment
BACKEND_URL = "https://fridge-backend-service-845166114793.us-central1.run.app"
# This will raise an informative error in Streamlit UI if you forgot to add it to the Secrets tab
PORTFOLIO_TOKEN = st.secrets.get("X_PORTFOLIO_TOKEN", "")

def compress_image(uploaded_file):
    img = Image.open(uploaded_file)
    # Resize so the max dimension is 1024px
    img.thumbnail((1024, 1024)) 
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85) # Convert to optimized JPEG
    return buf.getvalue()


st.set_page_config(page_title="AI Fridge Chef", page_icon="🍳", layout="centered")
st.title("🍳 AI Fridge Chef")
st.markdown("### Applied AI Portfolio: Enterprise Microservice Edition 🚀")

st.write("Upload a picture of your fridge, and our cloud backend will generate recipes!")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Your Fridge", use_container_width=True)

    if st.button("Generate Recipes"):
        if not PORTFOLIO_TOKEN:
            st.error("Missing X_PORTFOLIO_TOKEN in Secrets. Please configure the app settings.")
            st.stop()

        with st.spinner("Analyzing ingredients and planning your meal..."):
            try:
                # 1. Base64 Encoding
                image_bytes = compress_image(uploaded_file)
                base64_string = base64.b64encode(image_bytes).decode('utf-8')
                
                # 2. Secure Request Construction
                payload = {"image_base64": base64_string}
                headers = {"X-Portfolio-Token": PORTFOLIO_TOKEN}
                
                # 3. Microservice Call
                response = requests.post(
                    f"{BACKEND_URL}/analyze", 
                    json=payload, 
                    headers=headers,
                    timeout=90 # Staff Tip: Always set a timeout for cloud requests
                )
                
                # 4. Result Processing
                if response.status_code == 200:
                    result = response.json()
                    st.success("Recipes generated successfully!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### 🛒 Found")
                        for item in result.get("ingredients", []):
                            st.write(f"- {item}")
                    with col2:
                        st.markdown("### ⚠️ Missing")
                        for missing in result.get("missing_essentials", []):
                            st.write(f"- {missing}")
                        
                    st.divider()
                    st.markdown("### 👨‍🍳 Chef's Recommendations")
                    for recipe in result.get("recipes", []):
                        with st.expander(f"📖 {recipe.get('name', 'Recipe')}"):
                            st.write(f"**Cuisine:** {recipe.get('cuisine', 'Fusion')}")
                
                elif response.status_code == 429:
                    st.warning("Rate limit exceeded. Please wait a minute before trying again.")
                elif response.status_code == 401:
                    st.error("Authentication failed. The Portfolio Token is incorrect.")
                else:
                    st.error(f"Backend Error (Status {response.status_code})")
                    
            except requests.exceptions.Timeout:
                st.error("Request timed out. The backend is likely warming up.")
            except requests.exceptions.RequestException as e:
                st.error(f"Network error: {e}")