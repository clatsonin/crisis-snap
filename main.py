import requests
import os
import google.generativeai as genai
from PIL import Image
import io
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure the API key is set
genai_api_key = os.getenv("GENAI_API_KEY")
rapidapi_key = os.getenv("RAPIDAPI_KEY")

if not genai_api_key or not rapidapi_key:
    st.error("API keys are missing. Please check your .env file.")
    st.stop()

genai.configure(api_key=genai_api_key)

# Function to load OpenAI model and get responses
def get_gemini_response(input_text, image):
    model = genai.GenerativeModel('gemini-pro-vision')
    if input_text:
        response = model.generate_content([input_text, image])
    else:
        response = model.generate_content(image)
    return response.text

# Function to prompt user to input location manually
def get_location_input():
    return st.text_input("Enter your current location: ", key="location_input", max_chars=100)

# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
]
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    safety_settings=safety_settings,
    generation_config=generation_config,
)

chat_session = model.start_chat(history=[])

# Initialize our Streamlit app
st.set_page_config(page_title="Crisis Snap📷")

st.header("Crisis Snap📷")
st.subheader("Helpful Tool")

# Create two columns with centered alignment
col1, col2 = st.columns([1, 1])

# File uploader in the first column
with col1:
    st.write("")  # Adding an empty space for vertical alignment
    uploaded_file = st.file_uploader(
        "Upload image here ⚡!", type=["jpg", "jpeg", "png"], key="image_uploader", help="Click here to upload an image."
    )
    image = None
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width=True)

# Location input in the first column
with col1:
    st.write("")  # Adding an empty space for vertical alignment
    location = get_location_input()

# If ask button is clicked and location is given
if location and col1.button("Generate ⚡"):
    if image:
        response = get_gemini_response("Tell me about this pic", image)
        extended_input = response + f" I'm here in {location} which is a disaster. Tell me ways to escape."
        response2 = get_gemini_response(extended_input, image)

        # Response in the second column
        with col2:
            st.subheader("Your Scenario:")
            st.text_area("Response", response, height=200, max_chars=500)

            st.subheader("Steps for Precaution 💡:")
            st.text_area("Precautionary Steps", response2, height=200, max_chars=500)
    else:
        st.error("Please upload an image before submitting.")

# Fetch helpline numbers based on location if provided
if location:
    url = "https://google-search74.p.rapidapi.com/"
    querystring = {
        "query": f"{location} helpline number",
        "limit": "5",
        "related_keywords": "true"
    }

    headers = {
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": "google-search74.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    # Extract JSON response
    data = response.json()

    # Extract descriptions
    descriptions = [result['description'] for result in data['results']]

    # Optionally store the descriptions in a variable for further use
    descriptions_text = "\n".join(descriptions)

    # Send the descriptions along with the location to the model
    response = chat_session.send_message(f"{location} helpline number: " + descriptions_text)

    # Display the response from the model
    st.text_area("Helpful List", response.text, height=200, max_chars=500)
