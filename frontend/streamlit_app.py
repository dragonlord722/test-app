import streamlit as st
from PIL import Image
from google import genai
import json
import logging

# --- NETWORK LOGGING SETUP ---
# Forces the underlying HTTP library to print all network traffic to your terminal
logging.basicConfig(
    format="%(levelname)s [%(name)s] %(message)s", 
    level=logging.DEBUG
)
logging.getLogger("httpx").setLevel(logging.DEBUG)
# -----------------------------

# --- SECURITY: The Password Bouncer ---
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password in session state securely
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input("Enter the app password to continue", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error.
        st.text_input("Enter the app password to continue", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

# --- MAIN APP SETUP ---
st.set_page_config(page_title="AI Recipe Assistant", page_icon="🍳", layout="wide")

# Stop the app completely if the password is not entered
if not check_password():
    st.stop()

# Initialize Gemini Client 
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.title("🍳 What's in my fridge?")
st.write("Upload a picture of your refrigerator, and I'll suggest a recipe!")

# --- UI LAYOUT ---
col1, col2 = st.columns([1, 2])

with col1:
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Your Fridge", use_container_width=True)
        analyze_button = st.button("Analyze Fridge", type="primary", use_container_width=True)

with col2:
    if uploaded_file is not None and analyze_button:
        with st.spinner("Analyzing ingredients and generating recipes..."):
            try:
                # The exact instructions for the AI
                prompt = """You are a culinary AI assistant. Analyze the provided image of a refrigerator or ingredients. 
                Return a valid JSON object with exactly three keys:
                1. 'ingredients': A list of strings of identified food items.
                2. 'missing_essentials': A list of 2-3 common staple items that seem to be missing.
                3. 'recipes': A list of 2-3 suggested pure vegetarian Indian or fusion recipes based heavily on the found ingredients. Each recipe should be an object with 'name' and 'cuisine' keys."""
                
                # Make the API Call
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[image, prompt],
                    config={"response_mime_type": "application/json"}
                )
                
                # --- PRINT FULL PAYLOAD TO TERMINAL ---
                # Dumps the entire response object (including token counts) to your terminal
                print("\n" + "="*50)
                print("GEMINI API RESPONSE PAYLOAD & METADATA:")
                print("="*50)
                print(response.model_dump_json(indent=4))
                print("="*50 + "\n")
                # ---------------------------------------

                # Parse the JSON string into a Python dictionary
                result = json.loads(response.text)
                
                # --- POLISHED UI RENDERING ---
                st.success("Analysis Complete!")
                
                ing_col, miss_col = st.columns(2)
                
                with ing_col:
                    st.subheader("🥬 Found Ingredients")
                    for item in result.get("ingredients", []):
                        st.markdown(f"- {item}")
                        
                with miss_col:
                    st.subheader("🛒 Missing Essentials")
                    for item in result.get("missing_essentials", []):
                        # Generate dynamic search links for missing items
                        search_url = f"https://www.wholefoodsmarket.com/search?text={item.replace(' ', '+')}"
                        st.markdown(f"- {item} [🛒]({search_url})")
                
                st.divider()
                
                st.subheader("👨‍🍳 Recipe Suggestions")
                for recipe in result.get("recipes", []):
                    # Use a container to create a "card" look for the recipes
                    with st.container(border=True):
                        st.markdown(f"#### {recipe['name']}")
                        st.caption(f"Cuisine: {recipe['cuisine']}")
                        
            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")