# pagemain.py
import streamlit as st
from streamlit_chat import message
import os
from general_bot import ChatBot
from customized_bot import CustomizedBot
from covid_bot import CovidBot

class UnifiedBot:
    def __init__(self):
        self.page = 'home'
        self.bot_name = ''
        self.bot_model = ''
        self.bot_context_prompt = ''
        self.bot_temperature = 0.5
        self.uploaded_files = []

    def save_uploaded_files(self, directory, uploaded_files):
        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # List to hold the names of the files
        saved_files = []
        
        for uploaded_file in uploaded_files:
            # Combine the directory with the filename
            file_path = os.path.join(directory, uploaded_file.name)
            # Write the file to the specified directory
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_files.append(file_path)
        return saved_files
    
    def st_centered_text(self, text: str):
         st.markdown(f"<h1 style='text-align: center; color: white;'><big><b><u>{text} 🤖🗣️</u></b></big></h1>", unsafe_allow_html=True)

    def st_bigtext(self, text: str):
         st.markdown(f"<h1 style='text-align: left; color: white;'<b>{text}</b></h1>", unsafe_allow_html=True)

    def run(self):
        with st.sidebar:
            self.st_centered_text('Unified Bot')
            st.write("choose a bot from below options:")

            if 'page' not in st.session_state:
                st.session_state.page = 'home'

            self.st_bigtext("This is a general_bot")
            if st.sidebar.button('General_bot'):
                st.session_state.page = 'General_bot'

            self.st_bigtext("A covid protocol bot")
            if st.sidebar.button('Covid_bot'):
                st.session_state.page = 'Covid_bot'

            self.st_bigtext("Customize your own bot")
            if st.sidebar.button('Customized_bot'):
                st.session_state.page = 'Customized_bot'

        # Now call the run function based on the page state
        if st.session_state.page == 'General_bot':
            self.bot_name = st.sidebar.text_input("Enter bot name:")
            self.bot_model = st.sidebar.selectbox("Choose bot model:", ["gpt-4", "gpt-3.5-turbo"])
            self.bot_context_prompt = st.sidebar.text_area("Enter bot's initial state:")
            self.bot_temperature = st.sidebar.slider("Set bot response randomness:", 0.0, 1.0, 0.5)
            chat_bot = ChatBot(self.bot_name, self.bot_model, self.bot_context_prompt, self.bot_temperature)
            chat_bot.run()

        elif st.session_state.page == 'Covid_bot':
            covid_bot= CovidBot()
            covid_bot.run()

        elif st.session_state.page == 'Customized_bot':
            self.bot_name = st.sidebar.text_input("Enter bot name:")
            self.uploaded_files = st.sidebar.file_uploader("Upload additional knowledge bases for the bot:", accept_multiple_files=True)
            if self.uploaded_files:
                saved_files = self.save_uploaded_files('/Users/abhinavnagaboyina/Desktop/new/files', self.uploaded_files)
                for file_path in saved_files:
                    st.sidebar.write(f"Saved file location: {file_path}")
                customized_bot = CustomizedBot(self.bot_name)
                customized_bot.run()

bot = UnifiedBot()
bot.run()
