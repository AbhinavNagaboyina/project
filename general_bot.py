import streamlit as st
from streamlit_chat import message
from dotenv import load_dotenv
import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

load_dotenv()
chat_history = []

class ChatBot:
    def __init__(self, bot_name, bot_model, bot_context_prompt, bot_temperature):
        self.bot_name = bot_name
        self.bot_model = bot_model
        self.bot_context_prompt = bot_context_prompt
        self.bot_temperature = bot_temperature
        self.llm = ChatOpenAI(model=bot_model, temperature=bot_temperature, verbose=True, streaming=True)
        
        if "messages" not in st.session_state:
            st.session_state["messages"] = [SystemMessage(content=bot_context_prompt)]


    def st_centered_text(self, text: str):
        st.markdown(f"<h1 style='text-align: center; color: white;'>{text} 🤖🗣️ </h1>", unsafe_allow_html=True)

    def process_input(self, user_input):
        st.session_state["messages"].append(HumanMessage(content=user_input))
        response = self.llm(st.session_state["messages"])
        st.session_state["messages"].append(AIMessage(content=response.content))
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

        user_input=st.text_input("Please provide your query and dont forget to hit enter: ", key="user_input")
        clear_button= st.button("Clear the bot")

        if user_input:
            chat_history.append(user_input)
            resp = self.process_input(user_input)
            chat_history.append(resp.content)

            if clear_button:
                st.session_state["messages"].clear()
                chat_history.clear()
                self.st_centered_text("Chat history is cleared, Thanking you for using")
                
        for i,msg in enumerate(chat_history):
            if i%2==0:
                message(msg, is_user= True)
            else:
                message(msg, is_user= False)
        
        