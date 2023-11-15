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
    def __init__(self, bot_name):
        self.bot_name = bot_name
        dotenv_path = '.env'
        load_dotenv(dotenv_path)
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.client = QdrantClient(":memory:")
        self.documents = SimpleDirectoryReader('files/').load_data()
        self.service_context = ServiceContext.from_defaults(chunk_size=512)
        self.vector_store = QdrantVectorStore(client=self.client, collection_name="Covid19_latest_guidelines")
        self.start = datetime.now()
        print("Started loading content...", self.start)
        self.index = GPTVectorStoreIndex.from_documents(self.documents, vector_store=self.vector_store, service_context=self.service_context, show_progress=True)
        print("Finished loading content...", datetime.now() - self.start)
        self.query_engine = self.index.as_query_engine(similarity_top_k=2)

    def st_centered_text(self, text: str):
        st.markdown(f"<h1 style='text-align: center; color: white;'>{text} 🤖🗣️ </h1>", unsafe_allow_html=True)

    
    def input_run(self, user_input):
        with st.spinner("responding..."):
            response = self.query_engine.query(user_input)
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

        user_input=st.text_input("Please provide your query and dont forget to hit enter: ", key="user_input")
        clear_button= st.button("Clear the bot")
        if user_input:
            chat_hist.append(user_input)
            resp = self.input_run(user_input)
            chat_hist.append(resp)
            if clear_button:
                chat_hist.clear()
                self.st_centered_text("Chat history is cleared, Thanking you for using")
        
        for i, msg in enumerate(chat_hist):
            if i % 2 == 0:
                message(msg, is_user=True)
            else:
                message(msg, is_user=False)