import streamlit as st
from src.utils.localization import get_user_location, get_language_from_location, translations

if "step" not in st.session_state:
    st.session_state["step"] = 0
if "df" not in st.session_state:
    st.session_state["df"] = None
if "product_column" not in st.session_state:
    st.session_state["product_column"] = None
if "date_column" not in st.session_state:
    st.session_state["date_column"] = None
if "amount_column" not in st.session_state:
    st.session_state["amount_column"] = None
if "quantity_column" not in st.session_state:
    st.session_state["quantity_column"] = None
if "view_data_step" not in st.session_state:
    st.session_state["view_data_step"] = 0
if "order_identifier_column" not in st.session_state:
    st.session_state["order_identifier_column"] = None
if "slice_df" not in st.session_state:
    st.session_state["slice_df"] = None
if "paginated_products" not in st.session_state:
    st.session_state["paginated_products"] = None
if "analysis_complete" not in st.session_state:
    st.session_state["analysis_complete"] = False
if "forecast" not in st.session_state:
    st.session_state["forecast"] = None
if "elasticity" not in st.session_state:
    st.session_state["elasticity"] = None
if "product_mix_opt" not in st.session_state:
    st.session_state["product_mix_opt"] = None
if "sub_df" not in st.session_state:
    st.session_state["sub_df"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = 1
if "item_selector" not in st.session_state:
    st.session_state["item_selector"] = ""
if "unique_items" not in st.session_state:
    st.session_state["unique_items"] = []
if "TOTAL_PAGES" not in st.session_state:
    st.session_state["TOTAL_PAGES"] = 1
if "ITEMS_PER_PAGE" not in st.session_state:
    st.session_state["ITEMS_PER_PAGE"] = 10
if "language" not in st.session_state:
    st.session_state["language"] = ""
if "translations" not in st.session_state:
    st.session_state["translations"] = {}

country_code = get_user_location()
language = get_language_from_location(country_code)
st.session_state["language"] = language
st.session_state["translations"] = translations[language]

t = st.session_state["translations"]

pages = {
    t["Step 1"]: [st.Page("pages/home.py", title=t["Upload your data"])],
    t["Step 2"]: [st.Page("pages/view_data.py", title=t["Review your data and select the columns"])],
    t["Step 3"]: [st.Page("pages/optimize_inventory.py", title=t["Forecasting your demand"])],
    # "Product Mix Optimization": st.Page("pages/product_mix_optimization.py", title="Product Mix Optimization")
}

page = st.navigation(pages, position="sidebar")
page.run()