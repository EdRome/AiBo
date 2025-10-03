import streamlit as st
from src.data.readers.upload_file import upload_file_page

t = st.session_state["translations"]

st.markdown(
    f"""
    # {t["home-mk-title"]}

    {t["home-mk-description"]}

    > {t["home-mk-note"]}
    """
)

with st.spinner(t["home-mk-spinner"]):
    df = upload_file_page()
    st.session_state["df"] = df

if st.session_state["df"] is not None:
    st.switch_page("pages/view_data.py")