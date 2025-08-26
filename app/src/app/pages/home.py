import streamlit as st
import streamlit_antd_components as sac

from src.app.pages.upload_file import upload_file_page
from src.app.pages.view_data import view_data_page
from src.app.pages.optimize_inventory import optimize_inventory_page
from src.utils.change_step import change_step_home


def home_page():
    st.markdown(
        f"""
        # Inventory Management and Sales Forecasting

        This tool is designed to help you optimize your inventory management and sales forecasting.
        """
    )

    match st.session_state["step"]:
        case 0:
            with st.spinner("Uploading file **DON'T** refresh this page..."):
                df = upload_file_page()
                st.session_state["df"] = df

            if st.session_state["df"] is not None:
                st.dataframe(df.head(100))

            st.button("Next", on_click=change_step_home, disabled=st.session_state["df"] is None, key="next_button", type="primary")

        case 1:
            view_data_page()

        case 2:
            optimize_inventory_page()