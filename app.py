# pagemain.py
import streamlit as st
from streamlit_chat import message
import os
from general_bot import ChatBot
from customized_bot import CustomizedBot
import shutil

class BotManager:
    def __init__(self):
        if 'bots' not in st.session_state:
            st.session_state['bots'] = {}

    def save_bot(self, name, details):
        st.session_state['bots'][name] = details

    def delete_bot(self, name):
        if name in st.session_state['bots']:
            bot_details = st.session_state['bots'][name]
            # Reset or adjust selected_bot_details
            if bot_details['type'] == 'Customized Bot' and 'input_dir' in bot_details:
                directory = bot_details['input_dir']
                if os.path.exists(directory) and os.path.isdir(directory):
                    shutil.rmtree(directory)  # Remove the directory
            del st.session_state['bots'][name]

            if 'selected_bot_details' in st.session_state and st.session_state['selected_bot_details']['name'] == name:
                if st.session_state['bots']:
                    # Optional: Select a previous bot, e.g., the first in the list
                    st.session_state['selected_bot_details'] = next(iter(st.session_state['bots'].values()))
                else:
                    # If no bots are left, clear the selection
                    del st.session_state['selected_bot_details']
    
    def display_bots(self):
        for name, details in list(st.session_state['bots'].items()):
            if st.sidebar.button(f"Click to start the {name} bot", key=f"start_{name}"):
                st.session_state['selected_bot_details'] = details
            if st.sidebar.button(f"Delete {name}", key=f"delete_{name}"):
                self.delete_bot(name)
                st.experimental_rerun()
    def initialize_new_bot(self):
        # Reset the input field in the session state
        st.session_state['user_input'] = ''

botmanager = BotManager()


def st_centered_text(text: str):
        st.markdown(f"<h1 style='text-align: center; color: white;'><big><b><u>{text} 🤖🗣️</u></b></big></h1>", unsafe_allow_html=True)

def st_bigtext(text: str):
        st.markdown(f"<h1 style='text-align: left; color: white;'<b>{text}</b></h1>", unsafe_allow_html=True)

with st.sidebar:
    st_centered_text('Unified Bot')
    st_bigtext("Create your own Chatbot:")
    if st.button("Create New Bot"):
        st.session_state['show_create_bot_form'] = True

    if st.session_state.get('show_create_bot_form', False):
        bot_type = st.radio("Choose the type of bot you want to create:", ('General Bot', 'Customized Bot'))
        if bot_type == 'General Bot':
            with st.form(key='new_bot_form', clear_on_submit=True):
                name = st.text_input("Name (Unique identifier for each bot):")
                model = st.selectbox("Model",["gpt-4", "gpt-3.5-turbo"])
                context_prompt = st.text_area("Context Prompt:")
                temperature = st.slider("Temperature (Control the randomness of bot responses):", 0.0, 1.0, 0.5)
                submit_button = st.form_submit_button("Create Bot")
                if submit_button:
                    if not name:
                        st.warning("Please fill in all required fields.")
                    else:
                        bot_details = {
                            'name':name,
                            'type':bot_type,
                            'model':model,
                            'context_prompt':context_prompt,
                            'temperature':temperature
                        }
                        botmanager.save_bot(name, bot_details)
                        botmanager.initialize_new_bot()
                    st.session_state['show_create_bot_form'] = False

        if bot_type == 'Customized Bot':
            with st.form("bot_creation_form", clear_on_submit=True):

                name = st.text_input("Name (Unique identifier for each bot):")
                context_prompt = st.text_area("Context Prompt:")
                documents = st.file_uploader("Upload additional knowledge bases for the bot:", accept_multiple_files=True)
                create_button = st.form_submit_button("Create Bot")
                if create_button:
                    if not name:
                        st.warning("Please fill in all required fields.")
                    else:
                        if documents:
                            DATA_DIR = os.path.join('files', name)
                            if not os.path.exists(DATA_DIR):
                                os.makedirs(DATA_DIR)
                            for document in documents:
                                file_path = os.path.join(DATA_DIR, document.name)
                                with open(file_path, "wb") as f:
                                    f.write(document.getbuffer())
                            input_dir = DATA_DIR
                            bot_details = {'name': name, 'type': bot_type,'context_prompt':context_prompt, 'input_dir': input_dir}
                            botmanager.save_bot(name, bot_details)
                            botmanager.initialize_new_bot()
                    st.session_state['show_create_bot_form'] = False
    botmanager.display_bots()
    print("bots")

if 'selected_bot_details' in st.session_state:
    botmanager.initialize_new_bot()  # Clear input field when a bot is selected
    selected_bot_details = st.session_state['selected_bot_details']    
    if selected_bot_details['type'] == 'General Bot':
        chat_bot = ChatBot(selected_bot_details['name'], selected_bot_details['model'], 
                        selected_bot_details['context_prompt'], selected_bot_details['temperature'])
    elif selected_bot_details['type'] == 'Customized Bot':
        # Assuming Customized Bot has different parameters or initialization
        chat_bot = CustomizedBot(selected_bot_details['name'],selected_bot_details['context_prompt'], selected_bot_details['input_dir'])
    chat_bot.run()
