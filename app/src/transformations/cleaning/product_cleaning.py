import pandas as pd
import streamlit as st
import unidecode

def standarize_product_column():
    with st.spinner("Analyzing product data..."):
        try:
            df = pd.DataFrame(st.session_state["df"])
            df_col = df[st.session_state["product_column"]]
            df_col.fillna("", inplace=True)

            df_col = df_col.str.strip()
            df_col = df_col.str.lower()
            df_col = df_col.str.replace("-", "")
            df_col = df_col.str.replace(".", "")
            df_col = df_col.str.replace("(", "")
            df_col = df_col.str.replace(")", "")
            df_col = df_col.str.replace("\"", "")
            df_col = df_col.str.replace("\'", "")

            df_col = df_col.apply(unidecode.unidecode)
            df[st.session_state["product_column"]] = df_col

            st.session_state["df"] = df.to_dict(orient="records")
            return None
        except Exception as e:
            return f"**Error**: Product column selected has invalid values {e}"