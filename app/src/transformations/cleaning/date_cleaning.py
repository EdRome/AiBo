import hidateinfer 
import pandas as pd
import streamlit as st

def date_column_cleaning():
    with st.spinner("Analyzing date data..."):
        try:
            df = pd.DataFrame(st.session_state["df"])
            df_col = df[st.session_state["date_column"]]

            if df_col.dtype == "object":

                # Ensure all date values are objects
                df_col = df_col.astype(str)
                

                # Verifica el formato de la fecha por primera vez, si hay un timezone, lo elimina
                date_format = hidateinfer.infer(df_col.sample(10, random_state=1).tolist())
                # Remove timezone
                if "-%z" in date_format:
                    df_col = df_col.str.replace("( -\d{1,})", "", regex=True)

                # Remove seconds
                if "%S" in date_format:
                    df_col = df_col.str[:-3]

                if df_col.str.split(":").str.len().max() > 2:
                    df_col[df_col.str.split(":").str.len() > 2] = df_col[df_col.str.split(":").str.len() > 2].str[:-3]

                # Verifica el formato de la fecha nuevamente para poder convertir a datetime
                date_format = hidateinfer.infer(df_col.sample(10, random_state=1).tolist())
                new_df_col = pd.to_datetime(df_col, errors="coerce", format=date_format)

                # Si el formato de fecha no coincide para todos los casos, intenta convertir 
                # los valores que no coinciden utilizando el motor interno de pandas
                if new_df_col.isna().sum() > 0:
                    df_col[new_df_col.isna()] = pd.to_datetime(df_col[new_df_col.isna()], errors="coerce")

                    st.session_state["df"] = df.to_dict(orient="records")
            
            st.session_state["df"] = df.to_dict(orient="records")
            return None
        except Exception as e:
            return f"**Error**: Date column selected has invalid values {e}"