import logging

import streamlit as st

logger = logging.getLogger(__name__)


st.set_page_config(page_title="Langchain Chatbot", page_icon="💬", layout="wide")

st.header("Chatbot Implementations with Langchain")
st.write(
    """
- **Chatbot with Internet Access**: An internet-enabled chatbot capable of answering user queries about recent events.
- **Chat with your documents** Empower the chatbot with the ability to access custom documents, enabling it to provide answers to user queries based on the referenced information.

"""
)
