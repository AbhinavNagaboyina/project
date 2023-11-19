import streamlit as st
from streamlit_chat import message
from dotenv import load_dotenv
import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import time

load_dotenv()
class ChatBot:
    def __init__(self, bot_name, bot_model, bot_context_prompt, bot_temperature):
        self.bot_name = bot_name
        self.bot_model = bot_model
        self.bot_context_prompt = bot_context_prompt
        self.bot_temperature = bot_temperature
        self.chat_history = [] 
        self.llm = ChatOpenAI(model=bot_model, temperature=bot_temperature, verbose=True, streaming=True)
        self.chat_history_key = f"chat_history_{bot_name}"
        if self.chat_history_key not in st.session_state:
            st.session_state[self.chat_history_key] = [SystemMessage(content=bot_context_prompt)]
    def st_centered_text(self, text: str):
        st.markdown(f"<h1 style='text-align: center; color: white;'>{text} 🤖🗣️ </h1>", unsafe_allow_html=True)
    def clear_input(self):
        st.session_state.user_input = ""
    def process_input(self, user_input):
        st.session_state[self.chat_history_key].append(HumanMessage(content=user_input))
        response = self.llm(st.session_state[self.chat_history_key])
        st.session_state[self.chat_history_key].append(AIMessage(content=response.content))
        return response

    def run(self):
        self.st_centered_text(self.bot_name)

        st.markdown("""
        <style>
        .reportview-container .main footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            padding: 15rem;
            background-color: var(--main-bg);
            z-index: 999;
        }
        /* Push everything else up to make space for the footer */
        .reportview-container .main .block-container {
            padding-bottom: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
        if 'user_input' not in st.session_state:
            st.session_state['user_input'] = ''
        user_input_key = f"user_input_{len(self.chat_history)}"
        user_input=st.text_input("Please provide your query and dont forget to hit enter: ", key=f"user_input_{self.bot_name}",on_change=self.clear_input,value=st.session_state['user_input'])
        
        # Generate a unique key for the clear button
        clear_button_key = f"clear_button_{len(self.chat_history)}"

        # Create the clear button using the unique key
        clear_button = st.button("Clear the bot", key=clear_button_key)

        if user_input:
            resp = self.process_input(user_input)
            st.session_state['user_input'] = ''

        if clear_button:
        # Clear the chat history stored in session_state
            st.session_state[self.chat_history_key].clear()

            # Clear the instance-specific chat history
            self.chat_history.clear()

            # Display a message after clearing the history
            self.st_centered_text("Chat history is cleared, Thanking you for using")
            
        for i, msg in enumerate(st.session_state[self.chat_history_key]):
            timestamp = time.time()
            unique_key = f"chat_{i}_{timestamp}"
            if isinstance(msg, HumanMessage):
                # Display user message
                message(msg.content, is_user=True, key=unique_key)
            elif isinstance(msg, AIMessage):
                # Display AI (bot) message
                message(msg.content, is_user=False, key=unique_key)
            # Ensure SystemMessage is handled correctly if needed
