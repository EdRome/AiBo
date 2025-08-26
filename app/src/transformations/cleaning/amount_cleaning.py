import pandas as pd
import streamlit as st

def fix_amount_column():
    with st.spinner("Analyzing amount data..."):
        try:
            df = pd.DataFrame(st.session_state["df"])
            amount_column = st.session_state["amount_column"]
            if df[amount_column].dtype == "object":
                df[amount_column] = df[amount_column].str.replace(",", "")
                df[amount_column] = df[amount_column].str.replace(" ", "")
                df[amount_column] = df[amount_column].str.replace(r"[^0-9.]", "", regex=True)

            df[amount_column] = df[amount_column].fillna(0)
            df[amount_column] = pd.to_numeric(df[amount_column], errors="raise", downcast="float")

            st.session_state["df"] = df.to_dict(orient="records")
        except Exception as e:
            return f"**Error**: Amount column selected has invalid values {e}"