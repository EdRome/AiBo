import pandas as pd
import numpy as np
from sklearn.linear_model import ElasticNet
from sklearn.preprocessing import StandardScaler
import streamlit as st

from src.transformations.feature_engineering.product_group import create_product_group

class Elasticity:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.cross_elasticity_matrix = None
        self.product_col = st.session_state["product_column"]
        self.date_col = st.session_state["date_column"]
        self.amount_col = st.session_state["amount_column"]
        self.quantity_col = st.session_state["quantity_column"]

        self.unique_product = self.df[self.product_col].unique()
        self.errors = []

    def calculate_elasticity(self):
        self.df["log_q"] = np.log(self.df["total_quantity"])
        self.df["log_p"] = np.log(self.df["avg_price"])

        scaler_p = StandardScaler()
        scaler_q = StandardScaler()

        log_p = np.log(self.df["avg_price"])
        log_q = np.log(self.df["total_quantity"])

    def calculate_cross_elasticity(self):
        """
        Calcula la matriz de elasticidad cruzada para todos los productos.
        """
        # product_group_df = create_product_group(self.df)
        product_group_df = self.df.copy()

        product_pivot_df = product_group_df.pivot_table(
            index=self.date_col,
            columns=self.product_col,
            values=["avg_price", "total_quantity"]
        ).fillna(-1)

        scaler_p = StandardScaler()
        scaler_q = StandardScaler()

        log_p = np.log(product_pivot_df["avg_price"])
        log_q = np.log(product_pivot_df["total_quantity"])

        p_scaled = pd.DataFrame(scaler_p.fit_transform(log_p), columns=log_p.columns, index=log_p.index)
        q_scaled = pd.DataFrame(scaler_q.fit_transform(log_q), columns=log_q.columns, index=log_q.index)

        for target_product in log_q.columns:
            try:
                model = ElasticNet(alpha=0.01, l1_ratio=0.5)

                y = q_scaled[target_product].copy()
                X = p_scaled.copy()
                model.fit(X, y)
                elasticities = dict(zip(log_p.columns, model.coef_))

                if self.cross_elasticity_matrix is None:
                    self.cross_elasticity_matrix = pd.DataFrame({target_product: elasticities})
                else:
                    self.cross_elasticity_matrix = self.cross_elasticity_matrix.join(
                        pd.DataFrame({target_product: elasticities})
                    )
            except Exception as e:
                self.errors.append(target_product)
                continue
    
    def simulate_cross_elasticity(self, forecast_df: pd.DataFrame, price_changes):
        df = forecast_df.copy()
        df.set_index(self.product_col, inplace=True)

        # Aseguramos que estén todas las categorías con cambios de precio
        all_categories = df.index.tolist()
        pct_changes = pd.Series(price_changes).reindex(all_categories).fillna(0)

        # Aplicamos fórmula de elasticidad cruzada: DeltaQ_i = Q_i * sum_j(DeltaP_j * E_{i,j})
        def compute_sim_quantity(row_cat):
            base_q = df.loc[row_cat, "forecast_quantity"]
            elasticities = self.cross_elasticity_matrix.loc[row_cat]
            demand_multiplier = 1 + (elasticities * pct_changes).sum()
            return base_q * demand_multiplier

        df["sim_quantity"] = [compute_sim_quantity(cat) for cat in df.index]
        df["new_price"] = df["avg_price"] * (1 + pct_changes)
        df["sim_revenue"] = df["sim_quantity"] * df["new_price"]
        df["pct_price_change"] = pct_changes
        df.reset_index(inplace=True)

        return df[[self.product_col, "forecast_quantity", "pct_price_change", 
                    "sim_quantity", "avg_price", "new_price", "sim_revenue"]]