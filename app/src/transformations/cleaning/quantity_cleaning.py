import pandas as pd
import streamlit as st

def fix_quantity_column():
    with st.spinner("Analyzing quantity data..."):
        try:
            df = pd.DataFrame(st.session_state["df"])
            quantity_column = st.session_state["quantity_column"]
            if df[quantity_column].dtype == "object":
                df[quantity_column] = df[quantity_column].str.replace(",", "")
                df[quantity_column] = df[quantity_column].str.replace(" ", "")
                df[quantity_column] = df[quantity_column].str.replace(r"[^0-9.]", "", regex=True)
            
            df[quantity_column] = df[quantity_column].fillna(0)
            df[quantity_column] = pd.to_numeric(df[quantity_column], errors="raise", downcast="integer")

            st.session_state["df"] = df.to_dict(orient="records")
            return None
        except Exception as e:
            return f"**Error**: Quantity column selected has invalid values {e}"