import streamlit as st
from PIL import Image

# 1. Page Configuration
st.set_page_config(page_title="AI Recipe Assistant", page_icon="🍳", layout="centered")

st.title("What's in my fridge?")
st.write("Upload a picture of your refrigerator, and I'll suggest a recipe!")

# 2. File Uploader Widget
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Your Fridge", use_container_width=True)
    
    # 3. The Action Button
    if st.button("Analyze Fridge"):
        with st.spinner("Analyzing ingredients..."):
            # TODO: This is where we will eventually make an HTTP request to your AWS Lambda function.
            # For now, we use mock data to build the UI.
            
            mock_ingredients = ["Paneer", "Tomatoes", "Onions", "Green Chilies", "Cilantro"]
            mock_missing = ["Garam Masala", "Heavy Cream"]
            mock_recipes = [
                {"name": "Kadai Paneer", "cuisine": "Indian"},
                {"name": "Paneer Tikka Wraps", "cuisine": "Fusion"}
            ]

            # 4. Displaying the Results
            st.divider()
            st.subheader("Detected Ingredients")
            # Display ingredients as a comma-separated string
            st.write(", ".join(mock_ingredients))
            
            st.subheader("Recipe Suggestions")
            for recipe in mock_recipes:
                st.write(f"**{recipe['name']}** ({recipe['cuisine']})")
                
            st.subheader("Missing Essentials")
            for item in mock_missing:
                # Generate a dynamic search link for the missing item
                search_url = f"https://www.wholefoodsmarket.com/search?text={item.replace(' ', '+')}"
                st.markdown(f"* {item} - [Search on Whole Foods]({search_url})")