from pulp import *
import pandas as pd
from .forecasting import ForecastDemand
from .elasticity import Elasticity
import streamlit as st

class OptimizeInventory:

    def __init__(self, df: pd.DataFrame, forecast: ForecastDemand, elasticity: Elasticity):
        self.date_col = st.session_state["date_column"]
        self.df = df
        self.forecast = forecast
        self.elasticity = elasticity
        # self._validate_data()

    def optimize_inventory(self):
        beta = self.elasticity.get_cross_elasticity_matrix(type="dict")
        p_actual = self.forecast.get_last_price()
        F = self.forecast.get_forecast_df(type="dict")
        products = st.session_state["unique_items"]

        prob = LpProblem("Maximizar_Ventas", LpMaximize)
        p = LpVariable.dicts("Precio", products, lowBound=0)
        for j in products:
            p[j].lowBound = 0.8 * p_actual[j]
            p[j].upBound = 1.2 * p_actual[j]

        d = {}
        for i in products:
            d[i] = self.demanda_ajustada(i, p, F, p_actual, products, beta)
        
        prob += lpSum(d[i] for i in products)

        # Para agregar la restricción de margen mínimo del 20% necesito los costos de los productos
        # for j in products:
        #     prob += (p[j] - c[j]) / p[j] >= 0.2 

        prob.solve()

        st.write("Status:", LpStatus[prob.status])
        optimizacion = {j: [
            p[j].varValue, 
            self.demanda_ajustada(j, p, F, p_actual, products, beta).value(),
            p_actual[j]
            ] for j in products
        }
        optimizacion_df = pd.DataFrame(optimizacion).T.rename(columns={0: "Precio optimo", 1: "Demanda esperada", 2: "Precio actual"})
        optimizacion_df["Demanda esperada"] = optimizacion_df["Demanda esperada"].astype(int)
        return optimizacion_df
        # st.write(f"Ventas totales optimizadas: {value(prob.objective)}")

    def demanda_ajustada(self, i, p, F, p_actual, products, beta):
        demanda = F[i] * (1 + sum(
            beta.get((i,j), 0) * (p[j] - p_actual[j]) / p_actual[j]
            for j in products
        ))

        return demanda

    def _validate_data(self):
        if self.df[self.date_col].dtype != "datetime64[ns]":
            raise ValueError("Date column must be a datetime column")
        if "total_quantity" not in self.df.columns:
            raise ValueError("Total quantity column must be present in the dataframe")