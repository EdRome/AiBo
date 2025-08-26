import pandas as pd
import streamlit as st

def create_product_group(df: pd.DataFrame):
    date_col = st.session_state["date_column"]
    product_col = st.session_state["product_column"]
    amount_col = st.session_state["amount_column"]
    quantity_col = st.session_state["quantity_column"]

    df[date_col] = pd.to_datetime(df[date_col])
    # st.write(df[date_col].dtype)
    # st.write(df[product_col].dtype)

    product_group_df = df.groupby(
        [product_col, pd.Grouper(key=date_col, freq="ME")]
    ).agg(
        avg_price = (amount_col, "mean"),
        total_quantity = (quantity_col, "sum"),
    )

    product_group_df.reset_index(inplace=True)

    return product_group_df