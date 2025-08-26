import pandas as pd
import streamlit as st


class ForecastDemand:

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.product_col = st.session_state["product_column"]
        self.date_col = st.session_state["date_column"]
        self.quantity_col = st.session_state["quantity_column"]
        self.forecast_df = None

    def _validate_data(self):
        if self.df[self.date_col].dtype != "datetime64[ns]":
            raise ValueError("Date column must be a datetime column")
        if "total_quantity" not in self.df.columns:
            raise ValueError("Total quantity column must be present in the dataframe")

    def rolling_average(self, window: int = 3):
        self.forecast_df = self.df.copy()
        self.forecast_df["forecast_quantity"] = (
            self.forecast_df
            .groupby(self.product_col)[self.quantity_col]
            .transform(lambda x: x.rolling(window=window, min_periods=1).mean())
        )

        self.forecast_df = (
            self.forecast_df
            .reset_index()
            .sort_values(self.date_col)
            .groupby(self.product_col)
            .tail(1)
            .reset_index(drop=True)
            .drop(columns=["index"])
        )