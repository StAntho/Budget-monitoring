import streamlit as st
from dotenv import load_dotenv
import os

st.set_page_config(
    page_title="Budget monitoring",
    page_icon="💰",
)

st.title("BM - Data extraction")


# === API ===
load_dotenv()
API_URL = os.getenv("STREAMLIT_URL_API")