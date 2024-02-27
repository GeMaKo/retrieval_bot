import logging

import streamlit as st

logger = logging.getLogger(__name__)


st.set_page_config(page_title="Langchain Chatbot", page_icon="💬", layout="wide")

st.header("Chatbot Implementations with Langchain")
st.write(
    """
- **Chatbot with Internet Access**: An internet-enabled (transdev.de, d-ticket.info) chatbot capable of answering user queries about recent events.

"""
)
