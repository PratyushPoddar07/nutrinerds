from PIL import Image
import io
import logging
import streamlit as st
from streamlit_option_menu import option_menu
# from langchain.chains import ConversationChain
# from langchain.chains.conversations.memory import ConversationEntityMemory
# from langchain.chains.conversation.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE
# from langchain.llms import OpenAI

logging.basicConfig(level=logging.INFO)

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

import about, account, home, history

temperature = 0.9

generation_config = {
    "temperature": temperature,
    "top_p": 0.95,
    "top_k": 1,
    "max_output_tokens": 99998,
}


# Define the fixed text logo
fixed_logo = """
<div class="fixed top-0 left-0 w-full bg-white py-4 px-6 z-50">
    <p class="text-lg font-bold text-gray-800">Docify</p>
</div>
"""
st.set_page_config(page_title="Docify", page_icon=":gem:")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
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
                menu_title='DociFy',
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
                home.app()
            if app == 'Account':
                account.app()
            if app == 'History':
                history.app()
            if app == 'About':
                about.app()

        genai.configure(api_key='AIzaSyAdw7cCGn88hEjo-Y15fF2CzRB4-JswEsM')
        select_model = st.radio("Select Type", ["Consultancy", "Image Consultancy"])

        if select_model == "Image Consultancy":
            uploaded_image = st.file_uploader(
                "upload image",
                label_visibility="collapsed",
                accept_multiple_files=False,
                type=["png", "jpg"],
            )
            # st.caption(
            #     "Note: The vision model gemini-pro-vision is not optimized for multi-turn chat."
            # )

            if uploaded_image:
                image_bytes = uploaded_image.read()
            picture = st.camera_input("Take a picture")

            # if picture:
            #     st.image(picture)

            if picture is not None:
                image_bytes = picture.getvalue()

        def get_response(messages, model="gemini-pro"):
            model = genai.GenerativeModel(model)
            res = model.generate_content(messages,
                                        generation_config=generation_config)
            return res


        if "messages" not in st.session_state:
            st.session_state["messages"] = []
        messages = st.session_state["messages"]

        # The vision model gemini-pro-vision is not optimized for multi-turn chat.
        # st.header("Docify")
        # st.write("How can I help you?")

        # Initialize session state for chat history if it doesn't exist
        if messages and select_model != "Image Consultancy":
            for item in messages:
                role, parts = item.values()
                if role == "user":
                    st.chat_message("user").markdown(parts[0])
                elif role == "model":
                    st.chat_message("assistant").markdown(parts[0])
        chat = st.radio("Select one of the following options", ["Common Cold", "Influenza (Flu)", "Pneumonia", "Tuberculosis (TB)", "Hypertension", "Other","none of these"])
        if chat == "Other":
            chat2 = st.text_input("Enter the disease name")
        if chat == "Other":
            chat = chat2

        st.write("How can I help you?")
        chat_message = st.chat_input("Ask me about health related query...")

        if chat == "none of these":
            instruction = " "
        else:
            instruction = "person is in " + chat

        res = None
        if chat_message:
            st.chat_message("user").markdown(chat_message + instruction)
            res_area = st.chat_message("assistant").markdown("...")

            if select_model == "Image Consultancy":
                if "image_bytes" in globals():
                    vision_message = [chat_message,
                                      Image.open(io.BytesIO(image_bytes))]
                    try:
                        res = get_response(vision_message, model="gemini-pro-vision")
                    except google_exceptions.InvalidArgument as e:
                        if "API key not valid" in str(e):
                            st.error("API key not valid. Please pass a valid API key.")
                        else:
                            st.error("An error occurred. Please try again.")
                    except Exception as e:
                        logging.error(e)
                        st.error("Error occurred. Please refresh your page and try again.")
                else:
                    vision_message = [{"role": "user", "parts": [chat_message]}]
                    st.warning(
                        "Since there is no uploaded image, the result is generated by the default gemini-pro model.")
                    try:
                        res = get_response(vision_message)
                    except google_exceptions.InvalidArgument as e:
                        if "API key not valid" in str(e):
                            st.error("API key not valid. Please pass a valid API key.")
                        else:
                            st.error("An error occurred. Please try again.")
                    except Exception as e:
                        logging.error(e)
                        st.error("Error occurred. Please refresh your page and try again.")
            else:
                messages.append(
                    {"role": "user", "parts": [chat_message]},
                )
                try:
                    res = get_response(messages)
                except google_exceptions.InvalidArgument as e:
                    if "API key not valid" in str(e):
                        st.error("API key not valid. Please pass a valid API key.")
                    else:
                        st.error("An error occurred. Please refresh your page and try again.")
                except Exception as e:
                    logging.error(e)
                    st.error("Error occurred. Please refresh your page and try again.")

            if res is not None:
                res_text = ""
                for chunk in res:
                    if chunk.candidates:
                        res_text += chunk.text
                    if res_text == "":
                        res_text = "unappropriate words"
                        st.error("Your words violate the rules that have been set. Please try again!")
                res_area.markdown(res_text)

                if select_model != "Image Consultancy":
                    messages.append({"role": "model", "parts": [res_text]})


# Instantiate the MultiApp class and run the app
app = MultiApp()
app.run()