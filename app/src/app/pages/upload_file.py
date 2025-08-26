import streamlit as st
from src.data.readers.read_files import read_file

st.cache_data
def upload_file_page():

    upload_file = st.file_uploader("Upload your file", type=["csv", "xlsx", "xls"])

    if upload_file is not None:
        df = read_file(upload_file)

        return df