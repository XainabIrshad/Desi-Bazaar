import streamlit as st
import requests
import os
from PIL import Image

# Path to your images folder
IMAGES_FOLDER = r"D:\J_search_project\J_Scrapping\Images"

# Streamlit app
st.title("🌟 Desi bazaar 🌟")
st.write("Find the best clothing according to your need!")

query = st.text_input("Enter your search query:")

if query:
    # Fetch data from the API
    response = requests.get('http://127.0.0.1:5000/search', params={'query': query})
    
    if response.status_code == 200:
        results = response.json()
        
        if results:
            st.write(f"### Top **{len(results)}** results:")
            for item in results:
                st.markdown(f"#### 🔗 [Product Link]({item['link']})")
                
                # Display images as a collage with spacing
                code = item['code']
                images = []
                for i in range(1, 3):  #shwoing only 2 images
                    image_path = os.path.join(IMAGES_FOLDER, f"{code}_{i}.jpg")
                    if os.path.exists(image_path):
                        images.append(image_path)
                    else:
                        break

                if images:
                    cols = st.columns(len(images))
                    for col, img_path in zip(cols, images):
                        image = Image.open(img_path)
                        col.image(image, use_column_width=True)
                        col.write("")  # Adds some space below each image
                else:
                    st.write("No images found for this product.")
        else:
            st.write("No results found.")
    else:
        st.write("Error in fetching results. Please try again.")

# Custom CSS for better UI
st.markdown("""
<style>
    body {
        background-color: #e0f7fa;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stTextInput > div > input {
        background-color: #f1f1f1;
        border: 2px solid #4caf50;
        border-radius: 10px;
        padding: 10px;
    }
    .stButton > button {
        background-color: #4caf50;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    .st-markdown h3 {
        color: #00695c;
    }
    .st-markdown a {
        color: #00796b;
        text-decoration: none;
    }
    .st-markdown a:hover {
        color: #004d40;
        text-decoration: underline;
    }
    .css-1v3fvcr img {  /* Target the image containers */
        margin: 5px;  /* Add margin to create space between images */
        border-radius: 10px; /* Optional: Add rounded corners to images */
        border: 2px solid #ddd;  /* Optional: Add border to images */
    }

</style>
""", unsafe_allow_html=True)
