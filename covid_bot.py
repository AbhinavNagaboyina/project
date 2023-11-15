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
import json


class CovidBot:
    def __init__(self):
        self.client = QdrantClient(":memory:")
        self.documents = SimpleDirectoryReader('data/').load_data()
        self.service_context = ServiceContext.from_defaults(chunk_size=512)
        self.vector_store = QdrantVectorStore(client=self.client, collection_name="Covid19_latest_guidelines")
        self.start = datetime.now()
        print("Started loading content...", self.start)
        self.index = GPTVectorStoreIndex.from_documents(self.documents, vector_store=self.vector_store, service_context=self.service_context, show_progress=True)
        print("Finished loading content...", datetime.now() - self.start)
        self.query_engine = self.index.as_query_engine(similarity_top_k=2)

        if "messages" not in st.session_state:
            st.session_state.messages= ["Hello Sir/Mam, I am a protocol bot that provides information and guidance on COVID-19 based on recommendations from U.S. health agencies"]

    def run(self):
        st.header("A covid19 protocol Bot🤖🗣️ ")
        dotenv_path = '.env'
        load_dotenv(dotenv_path)
        openai.api_key = os.getenv("OPENAI_API_KEY")
        user_input = str(st.sidebar.text_input("Enter your query:"))
        submit = st.sidebar.button("Generate_Response")

        if user_input:
            st.session_state.messages.append(user_input)
            with st.spinner("Am Thinking..."):
                response = self.query_engine.query(user_input)
            st.session_state.messages.append(response.response)

        messages=st.session_state.messages
        for i, msg in enumerate(messages):
            if i % 2 == 0:
                message(msg, is_user=False)
            else:
                message(msg, is_user=True)
