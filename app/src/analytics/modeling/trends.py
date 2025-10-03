import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


class InventoryRiskAnalyzer:

    def __init__(self, growth_threshold_high=15, growth_threshold_low=-10, confidence_level=0.8):
        self.growth_threshold_high = growth_threshold_high
        self.growth_threshold_low = growth_threshold_low
        self.confidence_level = confidence_level

    def analyze_inventory_risk(self, historical_sales, current_stock, forecast_demand):
        """
        Analiza riesgo de inventario basado en crecimiento porcentual
        """
        growth_analysis = self._calculate_growth_trend(historical_sales)
        stock_analysis = self._calculate_stock_metrics(current_stock, forecast_demand)
        
        # Combinar análisis para determinar riesgo
        risk_assessment = self._assess_inventory_risk(growth_analysis, stock_analysis)
        
        return {
            'growth_analysis': growth_analysis,
            'stock_analysis': stock_analysis,
            'risk_assessment': risk_assessment,
            'recommendation': self._generate_recommendation(risk_assessment, current_stock, forecast_demand)
        }

    def _calculate_growth_trend(self, sales_series):
        """Calcula tendencia de crecimiento porcentual"""
        if len(sales_series) < 3:
            return {'trend': 'INSUFFICIENT_DATA', 'growth_rate': 0, 'confidence': 'LOW'}
        
        # Calcular crecimiento porcentual compuesto
        initial_sales = sales_series[0]
        final_sales = sales_series[-1]
        
        if initial_sales > 0:
            total_growth = ((final_sales - initial_sales) / initial_sales) * 100
            periods = len(sales_series) - 1
            cagr = ((final_sales / initial_sales) ** (1/periods) - 1) * 100
        else:
            total_growth = 0
            cagr = 0
        
        # Calcular tendencia con regresión
        X = np.arange(len(sales_series)).reshape(-1, 1)
        y = sales_series
        
        model = LinearRegression()
        model.fit(X, y)
        slope = model.coef_[0]
        
        # Determinar dirección y fuerza de la tendencia
        if cagr > self.growth_threshold_high:
            trend = 'STRONG_GROWTH'
        elif cagr > 0:
            trend = 'MODERATE_GROWTH'
        elif cagr < self.growth_threshold_low:
            trend = 'STRONG_DECLINE'
        elif cagr < 0:
            trend = 'MODERATE_DECLINE'
        else:
            trend = 'STABLE'
        
        return {
            'trend': trend,
            'cagr': cagr,
            'total_growth': total_growth,
            'absolute_slope': slope,
            # 'confidence': self._calculate_confidence(sales_series)
        }

    def _calculate_stock_metrics(self, current_stock, forecast_demand):
        """Calcula métricas clave de inventario"""
        if forecast_demand <= 0:
            return {'stock_cover': float('inf'), 'risk_level': 'LOW'}
        
        # Días de stock coverage
        stock_cover = current_stock / forecast_demand * 30  # Asumiendo 30 días
        
        # Nivel de servicio esperado
        service_level = min(1.0, current_stock / forecast_demand)
        
        return {
            'stock_cover': stock_cover,
            'service_level': service_level,
            'surplus_risk': self._calculate_surplus_risk(stock_cover, forecast_demand),
            'shortage_risk': self._calculate_shortage_risk(stock_cover, forecast_demand)
        }
    
    def _calculate_surplus_risk(self, stock_cover, forecast_demand):
        """Calcula riesgo de inventario sobrante"""
        if stock_cover > 60:  # Más de 2 meses de stock
            return 'VERY_HIGH'
        elif stock_cover > 45:  # 1.5-2 meses
            return 'HIGH'
        elif stock_cover > 30:  # 1-1.5 meses
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _calculate_shortage_risk(self, stock_cover, forecast_demand):
        """Calcula riesgo de inventario faltante"""
        if stock_cover < 7:  # Menos de 1 semana
            return 'VERY_HIGH'
        elif stock_cover < 15:  # 1-2 semanas
            return 'HIGH'
        elif stock_cover < 22:  # 2-3 semanas
            return 'MEDIUM'
        else:
            return 'LOW'

    def _assess_inventory_risk(self, growth_analysis, stock_analysis):
        """Evalúa el riesgo combinado de inventario"""
        growth_trend = growth_analysis['trend']
        stock_cover = stock_analysis['stock_cover']
        
        # Matriz de riesgo: crecimiento vs cobertura de stock
        risk_matrix = {
            'STRONG_GROWTH': {
                'VERY_HIGH': 'CRITICAL_SHORTAGE_RISK',
                'HIGH': 'HIGH_SHORTAGE_RISK',
                'MEDIUM': 'MEDIUM_SHORTAGE_RISK',
                'LOW': 'LOW_RISK'
            },
            'MODERATE_GROWTH': {
                'VERY_HIGH': 'HIGH_SURPLUS_RISK',
                'HIGH': 'MEDIUM_SURPLUS_RISK',
                'MEDIUM': 'LOW_RISK',
                'LOW': 'LOW_RISK'
            },
            'STABLE': {
                'VERY_HIGH': 'VERY_HIGH_SURPLUS_RISK',
                'HIGH': 'HIGH_SURPLUS_RISK',
                'MEDIUM': 'MEDIUM_SURPLUS_RISK',
                'LOW': 'LOW_RISK'
            },
            'MODERATE_DECLINE': {
                'VERY_HIGH': 'VERY_HIGH_SURPLUS_RISK',
                'HIGH': 'HIGH_SURPLUS_RISK',
                'MEDIUM': 'MEDIUM_SURPLUS_RISK',
                'LOW': 'LOW_SURPLUS_RISK'
            },
            'STRONG_DECLINE': {
                'VERY_HIGH': 'CRITICAL_SURPLUS_RISK',
                'HIGH': 'VERY_HIGH_SURPLUS_RISK',
                'MEDIUM': 'HIGH_SURPLUS_RISK',
                'LOW': 'MEDIUM_SURPLUS_RISK'
            }
        }
        
        return risk_matrix.get(growth_trend, {}).get(stock_analysis['surplus_risk'], 'UNKNOWN_RISK')

    def _generate_recommendation(self, risk_assessment, current_stock, forecast_demand):
        """Genera recomendaciones específicas basadas en el riesgo"""
        recommendations = {
            'CRITICAL_SHORTAGE_RISK': f"URGENTE: Aumentar stock inmediatamente. Necesitas {forecast_demand - current_stock:.0f} unidades adicionales",
            'HIGH_SHORTAGE_RISK': f"Alerta: Stock insuficiente. Considerar pedido de {forecast_demand * 0.3:.0f} unidades extra",
            'MEDIUM_SHORTAGE_RISK': "Monitorizar: Stock bajo. Planificar próximo pedido con anticipación",
            'LOW_SHORTAGE_RISK': "Situación normal con ligero déficit de stock. Mantener políticas actuales",
            
            'VERY_HIGH_SURPLUS_RISK': f"URGENTE: Exceso crítico de stock ({current_stock} unidades). Implementar promociones agresivas",
            'HIGH_SURPLUS_RISK': f"Alerta: Stock muy alto. Considerar descuentos del 20-30% para liquidar",
            'MEDIUM_SURPLUS_RISK': "Precaución: Stock elevado. Revisar políticas de reorden",

            'LOW_SURPLUS_RISK': "Situación normal con ligero exceso de stock. Mantener políticas actuales",
            'LOW_RISK': "Situación normal. Mantener políticas actuales",
            'UNKNOWN_RISK': "Datos insuficientes. Monitorizar estrechamente"
        }
        
        return recommendations.get(risk_assessment, "Evaluación de riesgo no disponible")