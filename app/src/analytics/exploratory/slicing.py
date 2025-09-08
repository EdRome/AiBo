import pandas as pd
import streamlit as st

def slice_df(df):

    df = pd.DataFrame(df)

    return df.filter([
        st.session_state["order_identifier_column"],
        st.session_state["date_column"],
        st.session_state["product_column"],
        st.session_state["amount_column"],
        st.session_state["quantity_column"]
    ])