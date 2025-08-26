import pandas as pd
import streamlit as st

def find_empty_values(df: pd.DataFrame):
    validate_columns = df.dropna(subset=[st.session_state["date_column"]]).isna().any()
    return validate_columns[validate_columns].to_dict()

def fill_empty_values(df: pd.DataFrame):
    fillna_dict = df[[
        st.session_state["order_identifier_column"],
        st.session_state["date_column"], 
    ]].dropna().set_index(
        st.session_state["order_identifier_column"]
    ).to_dict()[st.session_state["date_column"]]

    df[st.session_state["date_column"]] = df[st.session_state["order_identifier_column"]].map(fillna_dict)
    df.dropna(subset=[st.session_state["date_column"]], inplace=True)
    df.fillna({st.session_state["product_column"]: "Vacio"}, inplace=True)

    return df