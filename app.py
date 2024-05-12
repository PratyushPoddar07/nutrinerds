


import io
import logging
import textwrap
from PIL import Image
import streamlit as st
from streamlit_option_menu import option_menu
import google.generativeai as genai

logging.basicConfig(level=logging.INFO)

# Configure Generative AI API Key
genai.configure(api_key='AIzaSyAdw7cCGn88hEjo-Y15fF2CzRB4-JswEsM')

# Function to format text as Markdown
def to_markdown(text):
    text = text.replace('•', '  *')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

# Function to generate text from a text prompt
def generate_text(prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text

# chat_message =st.chat_input("Ask me about anything...")

# Function to generate text from image bytes
def generate_text_from_image(image_bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        model = genai.GenerativeModel('gemini-pro-vision')
        response = model.generate_content([img], stream=True)
        response.resolve()
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# Streamlit App
st.set_page_config(page_title="Docify", page_icon=":gem:")
st.title("Docify 🩺")

class MultiApp:
    def init(self):
        self.apps = []

    def add_app(self, title, function):
        self.apps.append({
            "title": title,
            "function": function
        })

    def run(self):
        with st.sidebar:
            app = option_menu(
                menu_title='Docify',
                options=['Home', 'Account', 'History', 'About'],
                icons=['house-fill', 'person-circle', 'clock-history', 'chat-fill'],
                menu_icon='chat-text-fill',
                default_index=1,
                styles={
                    "container": {"padding": "5!important", "background-color": '#C3F1DB'},
                    "icons": {"color": "white", "font-size": "23px"},
                    "nav-link": {"color": "black", "font-size": "20px", "text-align": "left", "margin": "0px"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                }
            )
            if app == 'Home':
                self.home()
            elif app == 'Account':
                self.account()
            elif app == 'History':
                self.history()
            elif app == 'About':
                self.about()

    def home(self):
        st.write("Welcome to the Home page!")

    def account(self):
        st.write("Welcome to the Account page!")

    def history(self):
        st.write("Welcome to the History page!")

    def about(self):
        st.write("Welcome to the About page!")

app = MultiApp()
app.run()

# Main App Logic
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

select_model = st.radio("Select Type", ["Text Consultancy", "Image Consultancy", "Image Consultancy (Capture)"])

if select_model == "Text Consultancy":
    text_prompt = st.text_input("Enter your Query:")
    
    if st.button("Enter"):
        generated_text = generate_text(text_prompt)
        st.markdown(to_markdown(generated_text))

elif select_model == "Image Consultancy":
    uploaded_image = st.file_uploader(
        "Upload Image",
        type=["png", "jpg"],
        accept_multiple_files=False
    )

    if uploaded_image:
        image_bytes = uploaded_image.read()
        st.image(image_bytes, caption="Uploaded Image", use_column_width=True)

        if st.button("Enter"):
            generated_text = generate_text_from_image(image_bytes)
            st.markdown(to_markdown(generated_text))

    
elif select_model == "Image Consultancy (Capture)":
    st.write("Click below to capture an image using your camera:")
    # camera_image = st.image("", channels="BGR", use_column_width=True)
    picture = st.camera_input("Take a picture")

    if picture:
        # image_bytes = picture.read()
        st.image(picture,caption="Captured image",use_column_width=True)


        if st.button("Enter"):
            generated_text = generate_text_from_image(picture.getvalue())
            st.markdown(to_markdown(generated_text))

    # if picture:
    #     st.image(picture)

    # if picture is not None:
    #     image_bytes = picture.getvalue()


    # if st.button("Capture Image"):
    #     camera = st.camera()
    #     if camera:
    #         captured_image = Image.fromarray(camera.astype("uint8"))
    #         st.image(captured_image, caption="Captured Image", use_column_width=True)

    #         if st.button("Generate Text"):
    #             captured_image_bytes = io.BytesIO()
    #             captured_image.save(captured_image_bytes, format="PNG")
    #             generated_text = generate_text_from_image(captured_image_bytes.getvalue())
    #             st.markdown(to_markdown(generated_text))

else:
    st.write("Select a consultancy type to proceed.")