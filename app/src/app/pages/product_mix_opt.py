import streamlit as st
import pandas as pd
from src.analytics.modeling.optimizing import OptimizeInventory
import plotly.graph_objects as go


def product_mix_opt_page():
    with st.spinner("Generating product mix optimization..."):
        elasticity = st.session_state["elasticity"]
        forecast = st.session_state["forecast"]
        sub_df = st.session_state["sub_df"]

        if elasticity.cross_elasticity_matrix is not None:
            st.write("Optimizing inventory...")
            optimize_inventory = OptimizeInventory(sub_df, forecast, elasticity)
            optimized_df = optimize_inventory.optimize_inventory()

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

            st.write(prev_month_sales)

            fig = go.Figure(go.Indicator(
                domain = {"x": [0, 1], "y": [0, 1]},
                value = forecast_venta_optimizada,
                mode = "gauge+number+delta",
                title = {"text": "Forecast venta optimizada"},
                delta = {"reference": prev_month_sales},
                gauge = {"axis": {"range": [None, max(forecast_venta_optimizada, prev_month_sales)*1.1]},
                    "steps": [
                        {"range": [0, 250], "color": "lightgray"},
                        {"range": [250, 500], "color": "gray"}
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 2},
                        "thickness": 0.75,
                        "value": prev_month_sales
                    }
                }
            ))
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(optimized_df.filter(["Precio actual", "Precio optimo", "Demanda esperada"]), use_container_width=True)
        else:
            st.write("Process finished before optimizing inventory, because there are no products with enough sales to calculate demand changes")
        

