import streamlit as st
import pandas as pd
import streamlit_antd_components as sac

from src.utils.change_step import change_step_view_data, change_backward_step_home, change_backward_step_view_data

t = st.session_state["translations"]
df = pd.DataFrame(st.session_state["df"])

if df.empty:
    st.error(t["view-error-no-data"])
    st.switch_page("pages/home.py")

view_steps = sac.steps([
        sac.StepsItem(
            title="Select order identifier"
        ),
        sac.StepsItem(
            title="Select product name",
        ),
        sac.StepsItem(
            title="Select sales date",
        ),
        sac.StepsItem(
            title="Select unit price",
        ),
        sac.StepsItem(
            title="Select sold quantity",
        )
    ], 
    key="view_data_steps", 
    return_index=True, 
    dot=True, 
    index=st.session_state["view_data_step"]
)

match view_steps:
    # Select order identifier
    case 0:
        select_order_identifier_column = st.selectbox(
            t["view-select-order-identifier"], 
            df.columns, 
            key="order_identifier_column_selectbox",
        )
        st.session_state["order_identifier_column"] = select_order_identifier_column
        left, _, right = st.columns(3, gap="large", vertical_alignment="bottom")
        with left:
            button_back_home = st.button(
                t["view-back-button"], 
                key="back_button_order_identifier")
            if button_back_home:
                st.switch_page("main.py")
        with right:
            st.button(
                t["view-next-button"],
                on_click=lambda: (
                    st.session_state.update({"order_identifier_column": select_order_identifier_column}), 
                    change_step_view_data()
                ),
                disabled=select_order_identifier_column is None, 
                key="next_button_order_identifier",
                type="primary"
            )
    # Select product column
    case 1:
        selected_product_column = st.selectbox(
            "Select the column associated to your product name or SKU", 
            df.columns, 
            key="product_column_selectbox",
        )
        st.session_state["product_column"] = selected_product_column
        left, _, right = st.columns(3, gap="large", vertical_alignment="bottom")
        with left:
            st.button(
                t["view-back-button"],
                on_click=change_backward_step_view_data, 
                key="back_button_prod")
        with right:
            st.button(
                t["view-next-button"],
                on_click=lambda: (
                    st.session_state.update({"product_column": selected_product_column}), 
                    change_step_view_data()
                ),
                disabled=selected_product_column is None, 
                key="next_button_prod",
                type="primary",
            )
    # Select date column
    case 2:
        selected_date_column = st.selectbox(
            "Select the column associated to the sale date or date of delivery", 
            df.columns, 
            key="date_column_selectbox",
        )
        st.session_state["date_column"] = selected_date_column
        left, _, right = st.columns(3, gap="large", vertical_alignment="bottom")
        with left:
            st.button(
                t["view-back-button"],
                on_click=change_backward_step_view_data, 
                key="back_button_date")
        with right:
            st.button(
                t["view-next-button"],
                on_click=lambda: (
                    st.session_state.update({"date_column": selected_date_column}), 
                    change_step_view_data()
                ),
                disabled=selected_date_column is None, 
                key="next_button_date",
                type="primary",
            )
    # Select amount column
    case 3:
        selected_amount_column = st.selectbox(
            "Select the column associated to the unit price", 
            df.columns, 
            key="amount_column_selectbox",
        )
        st.session_state["amount_column"] = selected_amount_column
        left, _, right = st.columns(3, gap="large", vertical_alignment="bottom")
        with left:
            st.button(
                t["view-back-button"],
                on_click=change_backward_step_view_data, 
                key="back_button_amount")
        with right:
            st.button(
                t["view-next-button"],
                on_click=lambda: (
                    st.session_state.update({"amount_column": selected_amount_column}), 
                    change_step_view_data()
                ),
                disabled=selected_amount_column is None, 
                key="next_button_amount",
                type="primary",
            )
    # Select quantity column
    case 4:
        selected_quantity_column = st.selectbox(
            "Select the column associated to the quantity sold", 
            df.columns, 
            key="quantity_column_selectbox",
        )
        st.session_state["quantity_column"] = selected_quantity_column
        left, _, right = st.columns(3, gap="large", vertical_alignment="bottom")
        with left:
            st.button(
                t["view-back-button"],
                on_click=change_backward_step_view_data, 
                key="back_button_quantity")
        with right:
            next_page = st.button(
                t["view-next-button"],
                on_click=lambda: (
                    st.session_state.update({"quantity_column": selected_quantity_column}), 
                    
                ),
                disabled=selected_quantity_column is None, 
                key="next_button_quantity",
                type="primary",
            )

        if next_page:
            st.switch_page("pages/optimize_inventory.py")

st.dataframe(df.head(10))
