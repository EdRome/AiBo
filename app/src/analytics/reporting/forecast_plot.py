import streamlit as st
import plotly.graph_objects as go
import math

def forecast_plot(forecast_df, product_col, start_idx, end_idx, item_name, TOTAL_ITEMS):


    # Crear gráfico
    fig = go.Figure()

    if item_name is not None or item_name != "":
        data = forecast_df[forecast_df[product_col] == item_name][product_col]
        values = forecast_df[forecast_df[product_col] == item_name]["forecast_quantity"]

        fig.add_trace(go.Bar(
            x=data,
            y=values,
            name=f"Forecast {item_name}"
        ))

    if item_name is None or item_name == "":
        fig.add_trace(go.Bar(
            x = forecast_df.iloc[start_idx:end_idx][product_col],
            y = forecast_df.iloc[start_idx:end_idx]["forecast_quantity"],
            name="Forecast"
        ))

    fig.update_layout(
        title=f"Products {start_idx+1}-{min(end_idx, TOTAL_ITEMS)} of {TOTAL_ITEMS}",
        xaxis_title="Products",
        yaxis_title="Forecast Quantity",
        height=600
    )

    return fig