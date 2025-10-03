import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

from .fuzzy_logic import FuzzyInferenceSystem

class InferenceEngineInventory:

    def __init__(self):

        self._df = None
        self.dynamic_ranges = None
        self.fis = FuzzyInferenceSystem()
        self._configure_membership_functions()
        self._create_rules()

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, df):
        self._df = df.reset_index().drop(columns=["growth_trend"])
        self._df = self._df.rename(columns={
            "index": "item_name",
            "current_stock": "last_month_sales",
            "growth_rate": "growth_trend",
        })

        # self.dynamic_ranges = {
        #     "last_month_sales": {"min": 0, "max": self.df["last_month_sales"].max()},
        #     "forecast_demand": {"min": 0, "max": self.df["forecast_demand"].max()},
        #     "growth_trend": {"min": -50, "max": self.df["growth_trend"].max()},
        #     "stock_coverage": {"min": 0, "max": self.df["stock_coverage"].max()},
        # }

    def _configure_membership_functions(self):
        self.fis.add_input_variable(
            "last_month_sales",
            universe=np.arange(0, 101, 1),
            memberships={
                "bajas": [0, 25, 50],
                "medias": [40, 60, 80],
                "altas": [70, 100, 100],
            }
        )
        self.fis.add_input_variable(
            "forecast_demand",
            universe=np.arange(0, 101, 1),
            memberships={
                "bajos": [0, 25, 50],
                "medias": [40, 60, 80],
                "altos": [70, 100, 100],
            }
        )
        self.fis.add_input_variable(
            "growth_trend",
            universe=np.arange(-50, 51, 1),
            memberships={
                "decreciente": [-50, -25, 0],
                "estable": [-15, 0, 15],
                "creciente": [0, 25, 50],
            }
        )
        # self.fis.add_input_variable(
        #     "stock_coverage",
        #     universe=np.arange(0, 91, 1),
        #     memberships={
        #         "critico": [0, 0, 10],
        #         "bajo": [5, 15, 25],
        #         "optimo": [20, 40, 60],
        #         "alto": [50, 70, 80],
        #         "excesivo": [75, 90, 90],
        #     }
        # )
        self.fis.add_output_variable(
            "recommendation",
            universe=np.arange(0, 101, 1),
            memberships={
                "reducir": [0, 25, 50],
                "mantener": [40, 50, 60],
                "aumentar": [50, 75, 100],
                "revision_urgente": [0, 50, 100]  # Un conjunto más amplio para "revisión urgente"
            }
        )

    def get_recommendation(self):

        if self.df is None:
            raise ValueError("DataFrame is not set")

        recommendations = {}
        for product in self.df["item_name"].unique():
            product_data = self.df[self.df["item_name"] == product]
            last_month_sales = product_data["last_month_sales"].values[0]
            forecast_demand = product_data["forecast_demand"].values[0]
            growth_trend = product_data["growth_trend"].values[0]

            inputs = {
                "last_month_sales": last_month_sales,
                "forecast_demand": forecast_demand,
                "growth_trend": growth_trend,
            }

            score = self.fis.compute(inputs)
            recommendations[product] = self._interpret_result(score, last_month_sales, forecast_demand, growth_trend)
            # recommendations[product] = score

        return recommendations

    def _interpret_result(self, score, last_month_sales, forecast_demand, growth_trend):

        if score <= 20:
            action = "URGENT INVENTORY REDUCTION"
            explanation = f"Riesgo extremo de sobreinventario. Stock actual: stock_coverage días vs forecast: {forecast_demand} unidaded"
        elif score <= 40:
            action = "INVENTORY REDUCTION"
            explanation = "Alto riesgo de sobreinventario. Considera promociones o ajuste de pedidos"
        elif score <= 60:
            action = "INCREASE INVENTORY"
            explanation = "Riesgo moderado de desabasto. Incrementa órdenes gradualmente"
        else:
            action = "URGENT INVENTORY INCREASE"
            explanation = f"Riesgo extremo de desabasto. Stock: stock_coverage días insuficiente para forecast: {forecast_demand} unidades"

        return {
            "puntuation": round(score, 2),
            "recommended_action": action,
            "explanation": explanation,
            "normalized_values": {
                "last_month_sales": last_month_sales,
                "forecast_demand": forecast_demand,
                "growth_trend": growth_trend
            }
        }

    def _create_rules(self):

        self.fis.add_rule(
            {"last_month_sales": "bajas", "forecast_demand": "bajos", "growth_trend": "decreciente"},
            "reducir"
        )
        self.fis.add_rule(
            {"last_month_sales": "medias", "forecast_demand": "medias", "growth_trend": "estable"},
            "mantener"
        )
        self.fis.add_rule(
            {"last_month_sales": "altas","forecast_demand": "altos", "growth_trend": "creciente"},
            "aumentar"
        )
        self.fis.add_rule(
            {"last_month_sales": "bajas", "forecast_demand": "altos", "growth_trend": "creciente"},
            "revision_urgente"
        )
        self.fis.add_rule(
            {"last_month_sales": "altas", "forecast_demand": "bajos", "growth_trend": "decreciente"},
            "reducir"
        )
        self.fis.add_rule(
            {"last_month_sales": "bajas", "forecast_demand": "medias", "growth_trend": "estable"},
            "mantener"
        )
        self.fis.add_rule(
            {"last_month_sales": "medias", "forecast_demand": "altos", "growth_trend": "creciente"},
            "aumentar"
        )
        self.fis.add_rule(
            {"last_month_sales": "medias", "forecast_demand": "bajos", "growth_trend": "decreciente"},
            "reducir"
        )
        self.fis.add_rule(
            {"last_month_sales": "bajas", "forecast_demand": "bajos"},
            "reducir"
        )
        self.fis.add_rule(
            {"last_month_sales": "altas", "forecast_demand": "altos"},
            "aumentar"
        )


class InferenceEngineInventoryOld:

    def __init__(self):

        # self.rangos_reales = {
        #     "last_month_sales": {"min": 0, "max": 1000},
        #     "forecast_demand": {"min": 0, "max": 1000},
        #     "growth_trend": {"min": 0, "max": 1000},
        #     "stock_coverage": {"min": 0, "max": 1000},
        # }

        self._df = None
        self.dynamic_ranges = None
        
        self.last_month_sales = ctrl.Antecedent(np.arange(0, 101, 1), "last_month_sales")
        self.forecast_demand = ctrl.Antecedent(np.arange(0, 101, 1), "forecast_demand")
        self.growth_trend = ctrl.Antecedent(np.arange(-50, 51, 1), "growth_trend")
        self.stock_coverage = ctrl.Antecedent(np.arange(0, 91, 1), "stock_coverage")

        self.recommendation = ctrl.Consequent(np.arange(0, 101, 1), "recommendation")

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, df):
        self._df = df.reset_index().drop(columns=["growth_trend"])
        self._df = self._df.rename(columns={
            "index": "item_name",
            "current_stock": "last_month_sales",
            "growth_rate": "growth_trend",
        })

        self.dynamic_ranges = {
            "last_month_sales": {"min": 0, "max": self.df["last_month_sales"].max()},
            "forecast_demand": {"min": 0, "max": self.df["forecast_demand"].max()},
            "growth_trend": {"min": -50, "max": self.df["growth_trend"].max()},
            "stock_coverage": {"min": 0, "max": self.df["stock_coverage"].max()},
        }

        self._configure_membership_functions()

        self._create_rules()

        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulator = ctrl.ControlSystemSimulation(self.control_system)

    def _normalize_values(self, true_value, variable):
        """
        Normalize a real value to its corresponding antecedent range based on min-max scaling.
        """
        min_real = self.dynamic_ranges[variable]["min"]
        max_real = self.dynamic_ranges[variable]["max"]

        # Evitar división por cero si max_real == min_real
        if max_real == min_real:
            return 0
        
        normalized_value = ((true_value - min_real) / (max_real - min_real)) * 100

        # Asegura que el valor esté dentro del rango [0, 100]
        return max(0, min(100, normalized_value))

        # """
        # Normalize a real value to its corresponding antecedent range

        # Args:
        #     true_value: Value in real units
        #     variable: Variable name to obtain the range

        # Returns:
        #     float: Normalized value
        # """

        # rango = self.dynamic_ranges[variable]

        # if variable == "growth_trend":
        #     return max(-50, min(50, true_value/2))
        # elif variable == "stock_coverage":
        #     return max(0, min(90, true_value/10))
        # else:
        #     max_range = rango["max"]
        #     return max(0, min(100, (true_value / max_range) * 100))

    def _denormalize_values(self, normalized_value, variable):
        """
        Convert a normalized value back to its real units
        """
        rango = self.rangos_reales[variable]

        if variable == "growth_trend":
            return normalized_value * 2
        elif variable == "stock_coverage":
            return normalized_value * 10
        else:
            max_range = self.rangos_reales[variable]["max"]
            return (normalized_value / 100) * max_range
            
    def _configure_membership_functions(self):
        """
        Configure membership functions for each antecedent
        """
        self.last_month_sales["muy_bajas"] = fuzz.trimf(self.last_month_sales.universe, [0, 0, 20])
        self.last_month_sales["bajas"] = fuzz.trimf(self.last_month_sales.universe, [10, 30, 50])
        self.last_month_sales["medias"] = fuzz.trimf(self.last_month_sales.universe, [40, 60, 80])
        self.last_month_sales["altas"] = fuzz.trimf(self.last_month_sales.universe, [70, 90, 100])
        self.last_month_sales["muy_altas"] = fuzz.trimf(self.last_month_sales.universe, [90, 100, 100])

        self.forecast_demand["muy_bajo"] = fuzz.trimf(self.forecast_demand.universe, [0, 0, 25])
        self.forecast_demand["bajo"] = fuzz.trimf(self.forecast_demand.universe, [15, 35, 55])
        self.forecast_demand["moderado"] = fuzz.trimf(self.forecast_demand.universe, [45, 65, 85])
        self.forecast_demand["alto"] = fuzz.trimf(self.forecast_demand.universe, [75, 90, 100])
        self.forecast_demand["muy_alto"] = fuzz.trimf(self.forecast_demand.universe, [90, 100, 100])

        self.growth_trend["muy_decreciente"] = fuzz.trimf(self.growth_trend.universe, [-50, -50, -30])
        self.growth_trend["decreciente"] = fuzz.trimf(self.growth_trend.universe, [-40, -20, 0])
        self.growth_trend["estable"] = fuzz.trimf(self.growth_trend.universe, [-10, 0, 10])
        self.growth_trend["creciente"] = fuzz.trimf(self.growth_trend.universe, [0, 20, 40])
        self.growth_trend["muy_creciente"] = fuzz.trimf(self.growth_trend.universe, [30, 50, 50])

        self.stock_coverage["critico"] = fuzz.trimf(self.stock_coverage.universe, [0, 0, 10])
        self.stock_coverage["bajo"] = fuzz.trimf(self.stock_coverage.universe, [5, 15, 25])
        self.stock_coverage["optimo"] = fuzz.trimf(self.stock_coverage.universe, [20, 40, 60])
        self.stock_coverage["alto"] = fuzz.trimf(self.stock_coverage.universe, [50, 70, 80])
        self.stock_coverage["excesivo"] = fuzz.trimf(self.stock_coverage.universe, [75, 90, 90])

        self.recommendation["reducir_urgente"] = fuzz.trimf(self.recommendation.universe, [0, 0, 20])
        self.recommendation["reducir"] = fuzz.trimf(self.recommendation.universe, [10, 30, 50])
        self.recommendation["mantener"] = fuzz.trimf(self.recommendation.universe, [40, 50, 60])
        self.recommendation["aumentar"] = fuzz.trimf(self.recommendation.universe, [50, 70, 90])
        self.recommendation["aumentar_urgente"] = fuzz.trimf(self.recommendation.universe, [80, 100, 100])

    def _create_rules(self):
        self.rules = [
            # ========== REGLAS DE EMERGENCIA ==========
            # 1. Situación crítica: Stock crítico + demanda alta + tendencia creciente
            ctrl.Rule(
                self.stock_coverage['critico'] & 
                (self.forecast_demand['alto'] | self.forecast_demand['muy_alto']) &
                (self.growth_trend['creciente'] | self.growth_trend['muy_creciente']),
                self.recommendation['aumentar_urgente']
            ),
            
            # 2. Situación crítica: Stock excesivo + demanda baja + tendencia decreciente
            ctrl.Rule(
                self.stock_coverage['excesivo'] & 
                (self.forecast_demand['bajo'] | self.forecast_demand['muy_bajo']) &
                (self.growth_trend['decreciente'] | self.growth_trend['muy_decreciente']),
                self.recommendation['reducir_urgente']
            ),
            
            # ========== REGLAS DE RIESGO ALTO ==========
            # 3. Riesgo alto de stockout
            ctrl.Rule(
                self.stock_coverage['bajo'] & 
                self.forecast_demand['alto'] &
                self.growth_trend['creciente'],
                self.recommendation['aumentar_urgente']
            ),
            
            # 4. Riesgo alto de sobreinventario
            ctrl.Rule(
                self.stock_coverage['alto'] & 
                self.forecast_demand['bajo'] &
                self.growth_trend['decreciente'],
                self.recommendation['reducir_urgente']
            ),
            
            # ========== REGLAS BASADAS EN VENTAS HISTÓRICAS ==========
            # 5. Ventas altas históricas con tendencia positiva
            ctrl.Rule(
                (self.last_month_sales['altas'] | self.last_month_sales['muy_altas']) &
                self.growth_trend['creciente'] &
                self.stock_coverage['optimo'],
                self.recommendation['aumentar']
            ),
            
            # 6. Ventas bajas históricas con tendencia negativa
            ctrl.Rule(
                (self.last_month_sales['bajas'] | self.last_month_sales['muy_bajas']) &
                self.growth_trend['decreciente'] &
                self.stock_coverage['optimo'],
                self.recommendation['reducir']
            ),
            
            # ========== REGLAS DE EQUILIBRIO ==========
            # 7. Situación óptima - mantener
            ctrl.Rule(
                self.stock_coverage['optimo'] &
                self.forecast_demand['moderado'] &
                self.growth_trend['estable'],
                self.recommendation['mantener']
            ),
            
            # 8. Situación estable con buen coverage
            ctrl.Rule(
                self.stock_coverage['optimo'] &
                self.forecast_demand['moderado'] &
                (self.growth_trend['estable'] | self.growth_trend['creciente']),
                self.recommendation['mantener']
            ),
            
            # ========== REGLAS DE AJUSTE PREVENTIVO ==========
            # 9. Ajuste preventivo para crecimiento
            ctrl.Rule(
                self.growth_trend['muy_creciente'] &
                self.forecast_demand['alto'] &
                (self.stock_coverage['optimo'] | self.stock_coverage['bajo']),
                self.recommendation['aumentar']
            ),
            
            # 10. Ajuste preventivo para decrecimiento
            ctrl.Rule(
                self.growth_trend['muy_decreciente'] &
                self.forecast_demand['bajo'] &
                (self.stock_coverage['optimo'] | self.stock_coverage['alto']),
                self.recommendation['reducir']
            ),
            
            # ========== REGLAS DE COMPENSACIÓN ==========
            # 11. Compensar coverage bajo con demanda estable
            ctrl.Rule(
                self.stock_coverage['bajo'] &
                self.forecast_demand['moderado'] &
                self.growth_trend['estable'],
                self.recommendation['aumentar']
            ),
            
            # 12. Compensar coverage alto con demanda estable
            ctrl.Rule(
                self.stock_coverage['alto'] &
                self.forecast_demand['moderado'] &
                self.growth_trend['estable'],
                self.recommendation['reducir']
            ),
            
            # ========== REGLAS DE TENDENCIA FUERTE ==========
            # 13. Tendencia muy creciente override
            ctrl.Rule(
                self.growth_trend['muy_creciente'] &
                (self.forecast_demand['alto'] | self.forecast_demand['muy_alto']),
                self.recommendation['aumentar_urgente']
            ),
            
            # 14. Tendencia muy decreciente override
            ctrl.Rule(
                self.growth_trend['muy_decreciente'] &
                (self.forecast_demand['bajo'] | self.forecast_demand['muy_bajo']),
                self.recommendation['reducir_urgente']
            ),
            
            # ========== REGLAS DE DEMANDA EXTREMA ==========
            # 15. Demanda muy alta con cualquier coverage
            ctrl.Rule(
                self.forecast_demand['muy_alto'] &
                (self.stock_coverage['bajo'] | self.stock_coverage['optimo']),
                self.recommendation['aumentar_urgente']
            ),
            
            # 16. Demanda muy baja con cualquier coverage
            ctrl.Rule(
                self.forecast_demand['muy_bajo'] &
                (self.stock_coverage['alto'] | self.stock_coverage['excesivo']),
                self.recommendation['reducir_urgente']
            ),
            
            # ========== REGLAS DE COVERAGE EXTREMO ==========
            # 17. Coverage crítico con cualquier demanda
            ctrl.Rule(
                self.stock_coverage['critico'] &
                (self.forecast_demand['moderado'] | self.forecast_demand['alto']),
                self.recommendation['aumentar_urgente']
            ),
            
            # 18. Coverage excesivo con cualquier demanda
            ctrl.Rule(
                self.stock_coverage['excesivo'] &
                (self.forecast_demand['moderado'] | self.forecast_demand['bajo']),
                self.recommendation['reducir_urgente']
            ),
            
            # ========== REGLAS CONSERVADORAS ==========
            # 19. En duda, mantener (regla conservadora)
            ctrl.Rule(
                (self.stock_coverage['optimo'] | self.stock_coverage['bajo'] | self.stock_coverage['alto']) &
                (self.forecast_demand['moderado'] | self.forecast_demand['bajo'] | self.forecast_demand['alto']) &
                (self.growth_trend['estable'] | self.growth_trend['creciente'] | self.growth_trend['decreciente']),
                self.recommendation['mantener']
            ),
            
            # 20. Situación ambigua con tendencia neutral
            ctrl.Rule(
                self.growth_trend['estable'] &
                self.forecast_demand['moderado'] &
                (self.stock_coverage['bajo'] | self.stock_coverage['alto']),
                self.recommendation['mantener']
            )
        ]

    # def get_recommendation(self, last_month_sales, forecast_demand, growth_trend, stock_coverage):
    def get_recommendation(self):
        """
        Get recommendation based on the input values

        Args:
            last_month_sales: Last month sales
            forecast_demand: Forecast demand
            growth_trend: Growth trend (%)
            stock_coverage: Stock coverage in real days

        Returns:
            dict: Recommendation with details
        """
        try:
            if self.df is None:
                raise ValueError("DataFrame is not set")

            recommendations = {}
            for product in self.df["item_name"].unique():
                product_data = self.df[self.df["item_name"] == product]
                last_month_sales = product_data["last_month_sales"].values[0]
                forecast_demand = product_data["forecast_demand"].values[0]
                growth_trend = product_data["growth_trend"].values[0]
                stock_coverage = product_data["stock_coverage"].values[0]

                sales_norm = self._normalize_values(last_month_sales, "last_month_sales")
                forecast_norm = self._normalize_values(forecast_demand, "forecast_demand")
                growth_norm = self._normalize_values(growth_trend, "growth_trend")
                stock_norm = self._normalize_values(stock_coverage, "stock_coverage")

                print(sales_norm, forecast_norm, growth_norm, stock_norm)

                self.simulator.input["last_month_sales"] = sales_norm
                self.simulator.input["forecast_demand"] = forecast_norm
                self.simulator.input["growth_trend"] = growth_norm
                self.simulator.input["stock_coverage"] = stock_norm

                membership_activation = self.get_membership_values(self.last_month_sales, sales_norm)                
                print(membership_activation)

                self.simulator.compute()

                print(self.simulator.output)
                result = self.simulator.output["recommendation"]
                recommendations[product] = self._interpret_result(result, last_month_sales, forecast_demand, growth_trend, stock_coverage)

            return recommendations
        except Exception as e:
            print(e)
            return {"error": str(e)}

    def get_membership_values(self, antecedent, normalized_value):
        """
        Calculates the degree of membership for a normalized value across all
        fuzzy sets of a given antecedent.

        Args:
            antecedent: The skfuzzy.control.Antecedent object (e.g., self.last_month_sales)
            normalized_value: The normalized input value (e.g., sales_norm)

        Returns:
            dict: A dictionary with each fuzzy set and its membership value.
        """
        membership_values = {}
        universe = antecedent.universe
        
        print(antecedent.terms.items())

        for term, mf in antecedent.terms.items():
            # Get the membership function points (e.g., [0, 0, 20])
            mf_points = mf.points
            
            # Calculate the degree of membership for the given value
            degree = fuzz.interp_membership(universe, mf_points, normalized_value)
            
            membership_values[term] = degree
            
        return membership_values

    def _interpret_result(self, puntuation, last_month_sales, forecast_demand, growth_trend, stock_coverage):

        if puntuation <= 20:
            action = "URGENT INVENTORY REDUCTION"
            explanation = f"Riesgo extremo de sobreinventario. Stock actual: {stock_coverage} días vs forecast: {forecast_demand} unidaded"
        elif puntuation <= 40:
            action = "INVENTORY REDUCTION"
            explanation = "Alto riesgo de sobreinventario. Considera promociones o ajuste de pedidos"
        elif puntuation <= 60:
            action = "INCREASE INVENTORY"
            explanation = "Riesgo moderado de desabasto. Incrementa órdenes gradualmente"
        else:
            action = "URGENT INVENTORY INCREASE"
            explanation = f"Riesgo extremo de desabasto. Stock: {stock_coverage} días insuficiente para forecast: {forecast_demand} unidades"

        return {
            "puntuation": round(puntuation, 2),
            "recommended_action": action,
            "explanation": explanation,
            "normalized_values": {
                "last_month_sales": round(self._normalize_values(last_month_sales, "last_month_sales"), 2),
                "forecast_demand": round(self._normalize_values(forecast_demand, "forecast_demand"), 2),
                "growth_trend": round(self._normalize_values(growth_trend, "growth_trend"), 2),
                "stock_coverage": round(self._normalize_values(stock_coverage, "stock_coverage"), 2)
            }
        }