import streamlit as st
import streamlit_antd_components as sac
from src.app.pages.home import home_page
from streamlit_searchbox import st_searchbox

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

def search_item(searchterm: str) -> list:
    items = st.session_state["unique_items"]
    return [item for item in items if searchterm.lower() in item.lower()]

def sort_items(sort_by: str):
    if sort_by == "demand":
        st.session_state["forecast"].forecast_df = st.session_state["forecast"].forecast_df.sort_values(by="forecast_quantity", ascending=False)
    elif sort_by == "name":
        st.session_state["forecast"].forecast_df = st.session_state["forecast"].forecast_df.sort_values(by=st.session_state["product_column"], ascending=True)

def sidebar():
    # with st.sidebar:
    st.session_state["step"] = sac.steps(
        items=[
            sac.StepsItem(
                title="Upload your data"),
            sac.StepsItem(
                title="View your data"),
            sac.StepsItem(
                title="Optimize your inventory"),
        ],
        index=st.session_state["step"], 
        return_index=True,
        size="lg", 
        key="step-sidebar",
        placement="vertical"
    )

    if st.session_state["forecast"] is not None:

        page_num = st.number_input(
            "Go to page", 
            min_value=1, 
            max_value=st.session_state["TOTAL_PAGES"], 
            value=st.session_state.current_page,
            key="page_selector"
        )

        st.session_state["ITEMS_PER_PAGE"] = st.selectbox(
            "Items per page", 
            [10, 20, 50], 
            index=0,
            key="items_per_page"
        )

        item_name = st_searchbox(
            search_item,
            placeholder="Search item",
            # label="Search item"
        )

        col1, col2 = st.columns(2)
        with col1:
            st.button("Sort by demand", on_click=sort_items, key="sort_items_button_demand", args=("demand",))
        with col2:
            st.button("Sort by item name", on_click=sort_items, key="sort_items_button_name", args=("name",))

        if item_name != st.session_state["item_selector"]:
            st.session_state["item_selector"] = item_name
            st.rerun()

        if page_num != st.session_state.current_page:
            st.session_state.current_page = page_num
            st.rerun()

# try:
with st.sidebar:
    sidebar()
home_page()
# except Exception as e:
#     st.error("Ocurrió un error al cargar el archivo")
#     st.error(e)