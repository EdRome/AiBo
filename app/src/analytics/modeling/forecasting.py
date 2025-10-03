import pandas as pd
import numpy as np
import streamlit as st
from .trends import InventoryRiskAnalyzer
from .recommendations import InferenceEngineInventory

class PyMEForecastDemand:

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.price_col = st.session_state["amount_column"]
        self.product_col = st.session_state["product_column"]
        self.date_col = st.session_state["date_column"]
        self.quantity_col = st.session_state["quantity_column"]
        self.forecast_df = None
        self.inventory_risk_analyzer = InventoryRiskAnalyzer()
        self.inference_engine_inventory = InferenceEngineInventory()
        # self.elasticity_matrix = self._get_elasticity_matrix()

    def smart_forecast(self):
        """Algoritmo inteligente que elige el mejor método por producto"""
        forecasts = {}
        


        for product in self.df[self.product_col].unique():
            algorithm = ""
            product_data = self.df[self.df[self.product_col] == product]
            sales_history = product_data.groupby(pd.Grouper(key=self.date_col, freq="ME"))[self.quantity_col].sum()
            sales_history_values = sales_history.values
            # sales_history = product_data[self.quantity_col]
            
            # Decidir qué método usar según la cantidad de datos
            if len(sales_history_values) >= 12:
                # Si tiene al menos 1 año: Suavizado exponencial
                forecast = self._exponential_smoothing(sales_history_values)
                algorithm = "exponential_smoothing"
            elif len(sales_history_values) >= 6:
                # Si tiene 6-11 meses: Media móvil ponderada
                forecast = self._weighted_moving_avg(sales_history_values)
                algorithm = "weighted_moving_avg"
            elif len(sales_history_values) >= 3:
                # Si tiene 3-5 meses: Promedio simple con tendencia
                forecast = self._simple_with_trend(sales_history_values)
                algorithm = "simple_with_trend"
            else:
                # Menos de 3 meses: Usar el último valor o promedio de similares
                forecast = self._fallback_forecast(product, sales_history_values)
                algorithm = "fallback_forecast"

            trends = self._get_trends(sales_history_values, sales_history_values[-1], max(0, forecast), algorithm)
            # forecasts[product] = [max(0, forecast), tendencia_absoluta, tendencia_porcentual_promedio, crecimiento_total]  # Evitar negativos
            forecasts[product] = trends
        
        self.forecast_df = pd.DataFrame(forecasts).T
        self.forecast_df["forecast_demand"] = self.forecast_df["forecast_demand"].astype(int)
        
        self.inference_engine_inventory.df = self.forecast_df
        recommendations = self.inference_engine_inventory.get_recommendation()

        self.forecast_df["recommendation"] = self.forecast_df.index.map(lambda product: recommendations.get(product)["recommended_action"])
        self.forecast_df["recommendation_explanation"] = self.forecast_df.index.map(lambda product: recommendations.get(product)["explanation"])

        # self.forecast_df = pd.DataFrame(
        #     forecasts
        # ).T.reset_index().rename(
        #     columns={"index": self.product_col, 0: "forecast_quantity", 1: "tendencia_absoluta", 2: "tendencia_porcentual_promedio", 3: "crecimiento_total"}
        # ).astype({
        #     "forecast_quantity": "int32"
        # })

    def get_monthly_sales_history(self):
        self.df["total_sales"] = self.df[self.quantity_col] * self.df[self.price_col]
        return self.df.groupby(pd.Grouper(key=self.date_col, freq="ME"))["total_sales"].sum()

    def get_less_sold_products_last_month(self):

        last_month = self.df[self.date_col].max() - pd.DateOffset(months=1)
        second_last_month = self.df[self.date_col].max() - pd.DateOffset(months=2)

        last_month_df = self.df[self.df[self.date_col] >= last_month]
        second_last_month_df = self.df[(self.df[self.date_col] >= second_last_month) & (self.df[self.date_col] < last_month)]

        last_month_products = last_month_df.groupby(self.product_col)[self.quantity_col].sum()
        second_last_month_products = second_last_month_df.groupby(self.product_col)[self.quantity_col].sum()

        less_sold_products_last_month = last_month_products.sort_values(ascending=True).head(4)
        
        
        comparison_df = less_sold_products_last_month.reset_index().merge(
            second_last_month_products.reset_index(), 
            on=self.product_col, 
            how="left", 
            suffixes=("_last_month", "_second_last_month")
        )

        comparison_df["delta"] = (comparison_df["quantity_last_month"] - comparison_df["quantity_second_last_month"])/comparison_df["quantity_second_last_month"]
        comparison_df["delta"] = comparison_df["delta"].fillna(0)
        comparison_df["delta"] = comparison_df["delta"].apply(lambda x: "{:.2%}".format(x))

        return comparison_df, last_month, second_last_month

    def get_most_sold_products_last_month(self):
        last_month = self.df[self.date_col].max() - pd.DateOffset(months=1)
        second_last_month = self.df[self.date_col].max() - pd.DateOffset(months=2)

        last_month_df = self.df[self.df[self.date_col] >= last_month]
        second_last_month_df = self.df[(self.df[self.date_col] >= second_last_month) & (self.df[self.date_col] < last_month)]

        last_month_products = last_month_df.groupby(self.product_col)[self.quantity_col].sum()
        second_last_month_products = second_last_month_df.groupby(self.product_col)[self.quantity_col].sum()

        less_sold_products_last_month = last_month_products.sort_values(ascending=False).head(4)
        
        
        comparison_df = less_sold_products_last_month.reset_index().merge(
            second_last_month_products.reset_index(), 
            on=self.product_col, 
            how="left", 
            suffixes=("_last_month", "_second_last_month")
        )

        comparison_df["delta"] = (comparison_df["quantity_last_month"] - comparison_df["quantity_second_last_month"])/comparison_df["quantity_second_last_month"]
        comparison_df["delta"] = comparison_df["delta"].fillna(0)
        comparison_df["delta"] = comparison_df["delta"].apply(lambda x: "{:.2%}".format(x))

        return comparison_df, last_month, second_last_month

    def get_last_month_sales_forecast(self):
        try:
            # Asigna el último precio de venta de cada producto del dataframe original
            last_prices = self.df.sort_values(self.date_col).groupby(self.product_col)[self.price_col].last()
            self.forecast_df[self.price_col] = self.forecast_df.index.map(last_prices)
            self.forecast_df["total_sales"] = self.forecast_df["forecast_demand"] * self.forecast_df[self.price_col]

            forecast_value = self.forecast_df["total_sales"].sum()

            return pd.DataFrame(data={self.date_col: [self.df[self.date_col].max() + pd.DateOffset(months=1)], "total_sales": [forecast_value]})
        except Exception as e:
            st.error(e)
            print(e)
            return pd.DataFrame(data={self.date_col: [self.df[self.date_col].max() + pd.DateOffset(months=1)], "total_sales": [0]})

    def _exponential_smoothing(self, sales, alpha=0.3):
        """Suavizado exponencial simple"""
        if len(sales) == 0:
            return 0
        
        forecast = sales[0]
        for sale in sales[1:]:
            forecast = alpha * sale + (1 - alpha) * forecast
        return forecast

    def _weighted_moving_avg(self, sales, weights=[0.5, 0.3, 0.2]):
        """Media móvil ponderada"""
        n = min(len(weights), len(sales))
        recent_sales = sales[-n:]
        current_weights = weights[-n:]
        # Normalizar pesos
        current_weights = [w/sum(current_weights) for w in current_weights]
        return np.dot(recent_sales, current_weights)

    def _simple_with_trend(self, sales):
        """Promedio simple con ajuste de tendencia básico"""
        if len(sales) < 2:
            return sales[0] if len(sales) == 1 else 0
        
        # Calcular tendencia simple (último vs promedio)
        avg_sales = np.mean(sales)
        last_sales = sales[-1]
        trend_factor = 1.0 + (last_sales - avg_sales) / avg_sales if avg_sales > 0 else 1.0
        
        return avg_sales * min(max(trend_factor, 0.8), 1.2)  # Limitar la tendencia

    def _fallback_forecast(self, product, sales):
        """Para productos con muy poca historia"""
        if len(sales) > 0:
            return np.mean(sales)
        else:
            # Promedio de productos similares (si existe categoría)
            return self._similar_products_avg(product)

    def _similar_products_avg(self, product):
        """Promedio de productos similares como fallback"""
        # Implementar lógica según categorías o características
        return self.df[self.quantity_col].mean()  # Fallback general

    def forecast_with_confidence(self):
        """Forecast con intervalo de confianza para PyMEs"""
        results = {}
        
        for product in self.df[self.product_col].unique():
            product_data = self.df[self.df[self.product_col] == product]
            sales = product_data[self.quantity_col].values
            
            if len(sales) >= 4:
                forecast = self._exponential_smoothing(sales)
                
                # Calcular margen de error simple (desviación estándar de últimos valores)
                recent_std = np.std(sales[-min(6, len(sales)):])
                confidence_interval = (max(0, forecast - recent_std), forecast + recent_std)
                
                results[product] = {
                    'forecast': forecast,
                    'low_estimate': confidence_interval[0],
                    'high_estimate': confidence_interval[1],
                    'confidence': 'high' if len(sales) >= 12 else 'medium'
                }
            else:
                results[product] = {
                    'forecast': np.mean(sales) if len(sales) > 0 else 0,
                    'low_estimate': 0,
                    'high_estimate': np.mean(sales) * 2 if len(sales) > 0 else 0,
                    'confidence': 'low'
                }
        
        return results

    def _get_elasticity_matrix(self):
        return self.elasticity.get_cross_elasticity_matrix(type="matrix")

    def _get_trends(self, serie_historica, current_stock, forecast_demand, algorithm):
        """
        Identifica si hay decrecimiento real en las ventas
        """
        analysis = self.inventory_risk_analyzer.analyze_inventory_risk(
            serie_historica, current_stock, forecast_demand
        )

        # inventory_recommendation = self.inference_engine_inventory.get_recommendation(
        #     serie_historica[-1], forecast_demand, analysis['growth_analysis']['cagr'], analysis['stock_analysis']['stock_cover']
        # )

        return {
            # 'product': product,
            'current_stock': current_stock,
            'forecast_demand': forecast_demand,
            'growth_trend': analysis['growth_analysis']['trend'],
            'growth_rate': analysis['growth_analysis']['cagr'],
            # 'stock_coverage': analysis['stock_analysis']['stock_cover'],
            'risk_category': analysis['risk_assessment'],
            # 'trends_recommendation': analysis['recommendation'],
            # 'recommendation': inventory_recommendation,
            'algorithm': algorithm
        }
        
    def get_last_price(self):
        return self.df.groupby(self.product_col)[self.price_col].last().to_dict()

    def get_forecast_df(self, type: str = "dict"):
        if type == "dict":
            return {
                i: self.forecast_df[self.forecast_df[self.product_col] == i]["forecast_quantity"].iloc[0]
                for i in self.df[self.product_col].unique()
            }
        else:
            return self.forecast_df


class ForecastDemand:

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.product_col = st.session_state["product_column"]
        self.date_col = st.session_state["date_column"]
        self.quantity_col = st.session_state["quantity_column"]
        self.price_col = st.session_state["amount_column"]
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

    def get_last_price(self):
        return self.df.groupby(self.product_col)[self.price_col].last().to_dict()

    def get_forecast_df(self, type: str = "dict"):
        if type == "dict":
            return {
                i: self.forecast_df[self.forecast_df[self.product_col] == i]["forecast_quantity"].iloc[0]
                for i in self.df[self.product_col].unique()
            }
        else:
            return self.forecast_df

    def simple_exponential_smoothing(self, alpha=0.3):
        """Suavizado exponencial simple - ideal para poca data"""
        forecasts = {}
        
        for product in self.df[self.product_col].unique():
            product_data = self.df[self.df[self.product_col] == product]
            sales = product_data[self.quantity_col].values
            
            if len(sales) >= 3:  # Mínimo 3 periodos
                # Inicializar con promedio simple
                forecast = np.mean(sales[:3])
                
                # Aplicar suavizado exponencial
                for sale in sales[3:]:
                    forecast = alpha * sale + (1 - alpha) * forecast
                
                forecasts[product] = max(0, forecast)
            else:
                # Para productos muy nuevos
                forecasts[product] = np.mean(sales) if len(sales) > 0 else 0
        
        return forecasts

    def weighted_moving_average(self, weights=[0.5, 0.3, 0.2]):
        """Da más peso a los periodos más recientes"""
        forecasts = {}
        
        for product in self.df[self.product_col].unique():
            product_data = self.df[self.df[self.product_col] == product]
            sales = product_data[self.quantity_col].tail(len(weights)).values
            
            if len(sales) >= len(weights):
                forecast = np.dot(sales, weights)
            else:
                # Si no hay suficiente historia, usar promedio simple
                forecast = np.mean(sales) if len(sales) > 0 else 0
            
            forecasts[product] = max(0, forecast)
        
        return forecasts