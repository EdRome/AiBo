import streamlit as st
import requests
import json

translations = {
    "es": {
        "Step 1":"Paso 1",
        "Step 2":"Paso 2",
        "Step 3":"Paso 3",
        "Upload your data":"Cargar tus datos",
        "Review your data and select the columns":"Revisa tus datos y selecciona las columnas",
        "Forecasting your demand":"Predecir tu demanda",
        "home-mk-title":"Gestión de Inventario y Predicción de Ventas",
        "home-mk-description":"Esta herramienta está diseñada para ayudarte a optimizar tu gestión de inventario y predicción de ventas.",
        "home-mk-note":"Durante el proceso, no cierres o actualices esta página. No almacenamos ningún dato en el servidor, por lo que si cierras o actualizas la página, perderás tus datos.",
        "home-mk-spinner":"Cargando archivo **NO** refrescar esta página...",
        "view-error-no-data":"No hay datos para analizar",
        "view-select-order-identifier":"Selecciona la columna asociada al identificador de orden",
        "view-back-button":"Atrás",
        "view-next-button":"Siguiente",
    },
    "en": {
        "Step 1":"Step 1",
        "Step 2":"Step 2",
        "Step 3":"Step 3",
        "Upload your data":"Upload your data",
        "Review your data and select the columns":"Review your data and select the columns",
        "Forecasting your demand":"Forecasting your demand",
        "home-mk-title":"Inventory Management and Sales Forecasting",
        "home-mk-description":"This tool is designed to help you optimize your inventory management and sales forecasting.",
        "home-mk-note":"During the process, don't close or refresh this page. We don't store any data in the server, so if you close or refresh the page, you will lose your data.",
        "home-mk-spinner":"Uploading file **DON'T** refresh this page...",
        "view-error-no-data":"No data to analyze",
        "view-select-order-identifier":"Select the column associated to the order identifier",
        "view-back-button":"Back",
        "view-next-button":"Next",
    }
}

def get_user_location():
    """Obtiene la ubicación del usuario basado en su dirección IP"""
    try:
        response = requests.get("https://ipapi.co/json/", timeout=5)
        data = response.json()
        return data.get("country_code","US").upper()
    except Exception as e:
        return "US"

def get_language_from_location(country_code):
    """Determina el idioma basado en el código de país"""
    spanish_speaking_countries = [
        'ES', 'MX', 'AR', 'CO', 'CL', 'PE', 'VE', 'EC', 'GT', 'CU', 
        'BO', 'DO', 'HN', 'PY', 'SV', 'NI', 'CR', 'PA', 'UY', 'GQ'
    ]

    if country_code in spanish_speaking_countries:
        return "es"
    else:
        return "en"