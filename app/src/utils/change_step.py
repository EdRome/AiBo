import streamlit as st

def change_step_home():
    st.session_state["step"] += 1

def change_backward_step_home():
    st.session_state["step"] -= 1

def change_step_view_data():
    st.session_state["view_data_step"] += 1

def change_backward_step_view_data():
    st.session_state["view_data_step"] -= 1

def return_step_home():
    st.session_state["step"] = 0
    st.session_state["view_data_step"] = 0