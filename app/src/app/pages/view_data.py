import streamlit as st
import pandas as pd
import streamlit_antd_components as sac

from ...utils.change_step import change_step_home, change_step_view_data, change_backward_step_home, change_backward_step_view_data

def view_data_page():
    df = pd.DataFrame(st.session_state["df"])

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
                "Select the column associated to the order identifier", 
                df.columns, 
                key="order_identifier_column_selectbox",
            )
            st.session_state["order_identifier_column"] = select_order_identifier_column
            left, _, right = st.columns(3, gap="large", vertical_alignment="bottom")
            with right:
                st.button(
                    "Back", 
                    on_click=change_backward_step_home, 
                    key="back_button_order_identifier")
            with left:
                st.button(
                    "Next", 
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
            with right:
                st.button(
                    "Back", 
                    on_click=change_backward_step_view_data, 
                    key="back_button_prod")
            with left:
                st.button(
                    "Next", 
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
            with right:
                st.button(
                    "Back", 
                    on_click=change_backward_step_view_data, 
                    key="back_button_date")
            with left:
                st.button(
                    "Next", 
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
            with right:
                st.button(
                    "Back", 
                    on_click=change_backward_step_view_data, 
                    key="back_button_amount")
            with left:
                st.button(
                    "Next", 
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
            with right:
                st.button(
                    "Back", 
                    on_click=change_backward_step_view_data, 
                    key="back_button_quantity")
            with left:
                st.button(
                    "Next", 
                    on_click=lambda: (
                        st.session_state.update({"quantity_column": selected_quantity_column}), 
                        change_step_home()
                    ),
                    disabled=selected_quantity_column is None, 
                    key="next_button_quantity",
                    type="primary",
                )

    st.dataframe(df.head(10))
