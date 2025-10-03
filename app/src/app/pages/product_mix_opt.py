import streamlit as st
import pandas as pd
from src.analytics.modeling.optimizing import OptimizeInventory
from src.analytics.reporting.forecast_plot import optimized_sales_inventory_plot

def product_mix_opt_page():
    with st.spinner("Generating product mix optimization..."):
        elasticity = st.session_state["elasticity"]
        forecast = st.session_state["forecast"]
        sub_df = st.session_state["sub_df"]
        product_col = st.session_state["product_column"]

        if elasticity.cross_elasticity_matrix is not None:
            st.write("Optimizing inventory...")
            
            if st.session_state["product_mix_opt"] is None:
                optimize_inventory = OptimizeInventory(sub_df, forecast, elasticity)
                optimize_inventory.optimize_inventory()
                st.session_state["product_mix_opt"] = optimize_inventory
                optimized_df = optimize_inventory.optimized_df
            else:
                optimize_inventory = st.session_state["product_mix_opt"]
                optimized_df = optimize_inventory.optimized_df

            last_date = sub_df[st.session_state["date_column"]].max()
            prev_month = last_date - pd.DateOffset(months=1)
            sub_df_prev_month = sub_df[sub_df[st.session_state["date_column"]] >= prev_month]
            sub_df_prev_month_sales = sub_df_prev_month.groupby(
                st.session_state["product_column"]
            ).agg(
                quantity = (st.session_state["quantity_column"], "sum"),
                amount = (st.session_state["amount_column"], "mean"),
            )

            prev_month_sales = (sub_df_prev_month_sales.quantity * sub_df_prev_month_sales.amount).sum()
            forecast_venta_optimizada = (optimized_df["Precio optimo"] * optimized_df["Demanda esperada"]).sum()
            
            fig = optimized_sales_inventory_plot(forecast_venta_optimizada, prev_month_sales)
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(optimized_df.filter(["item_name","Precio actual", "Precio optimo", "Demanda esperada"]), use_container_width=True)
        else:
            st.write("Process finished before optimizing inventory, because there are no products with enough sales to calculate demand changes")
        

