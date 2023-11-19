from __future__ import absolute_import
import streamlit as st
from dotenv import load_dotenv
import datetime
from streamlit_chat import message
import os
from datetime import datetime
from llama_index import (GPTVectorStoreIndex, ServiceContext,
                         SimpleDirectoryReader)
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
import openai
import streamlit as st
from llama_index import StorageContext, load_index_from_storage
import llama_index
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)

chat_hist = []

class CustomizedBot:
    def __init__(self, bot_name, context_prompt, input_dir):
        self.bot_name = bot_name
        self.context_prompt = context_prompt
        self.doc_dir = input_dir
        self.chat_history = []
        dotenv_path = '.env'
        load_dotenv(dotenv_path)
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.client = QdrantClient(":memory:")
        self.documents = SimpleDirectoryReader(self.doc_dir).load_data()
        self.service_context = ServiceContext.from_defaults(chunk_size=512)
        self.vector_store = QdrantVectorStore(client=self.client, collection_name="Covid19_latest_guidelines")
        self.start = datetime.now()
        print("Started loading content...", self.start)
        self.index = GPTVectorStoreIndex.from_documents(self.documents, vector_store=self.vector_store, service_context=self.service_context, show_progress=True)
        print("Finished loading content...", datetime.now() - self.start)
        self.query_engine = self.index.as_query_engine(similarity_top_k=2)
        self.chat_history_key = f"chat_history_{self.bot_name}"
        if self.chat_history_key not in st.session_state:
            st.session_state[self.chat_history_key] = [SystemMessage(content=context_prompt)]

    def st_centered_text(self, text: str):
        st.markdown(f"<h1 style='text-align: center; color: white;'>{text} 🤖🗣️ </h1>", unsafe_allow_html=True)

    
    def input_run(self, user_input):
        st.session_state[self.chat_history_key].append(HumanMessage(content=user_input))
        with st.spinner("responding..."):
            response = self.query_engine.query(user_input)
        st.session_state[self.chat_history_key].append(AIMessage(content=response.response))
        return response.response
    
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
        chat_history_key = f"chat_history_{self.bot_name}"
        if 'user_input' not in st.session_state:
            st.session_state['user_input'] = ''
        user_input=st.text_input("Please provide your query and dont forget to hit enter: ", key=f"user_input_{self.bot_name}", value=st.session_state['user_input'])
        if user_input:
              # Assuming HumanMessage takes content as an argument
            resp = self.input_run(user_input)
            st.session_state['user_input'] = ''

        clear_button = st.button("Clear the bot", key=f"clear_button_{self.bot_name}")
        if clear_button:
            # Clear the specific bot's chat history in session_state
            st.session_state[self.chat_history_key].clear()
            self.st_centered_text("Chat history is cleared, Thanking you for using")

        if self.chat_history_key in st.session_state:
            for i, msg in enumerate(st.session_state[self.chat_history_key]):
                if isinstance(msg, HumanMessage):
                    message(msg.content, is_user=True, key=f"message_{i}_{self.bot_name}")
                else:
                    message(msg.content, is_user=False, key=f"message_{i}_{self.bot_name}")