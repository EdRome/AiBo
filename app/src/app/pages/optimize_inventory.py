import math
from tkinter import W
import plotly.graph_objects as go
import streamlit as st
import streamlit_antd_components as sac
from streamlit_searchbox import st_searchbox

from src.analytics.modeling.elasticity import Elasticity
from src.analytics.modeling.forecasting import ForecastDemand
from src.analytics.reporting.forecast_plot import forecast_plot
from src.analytics.exploratory.empty_values import find_empty_values, fill_empty_values
from src.analytics.exploratory.slicing import slice_df
from src.transformations.feature_engineering.product_group import create_product_group
from src.utils.change_step import return_step_home
from ...transformations.cleaning.date_cleaning import date_column_cleaning
from ...transformations.cleaning.amount_cleaning import fix_amount_column
from ...transformations.cleaning.quantity_cleaning import fix_quantity_column
from ...transformations.cleaning.product_cleaning import standarize_product_column


def optimize_inventory_page():

    if not st.session_state["analysis_complete"]:
        with st.status("Analyzing data...", expanded=True) as status:
            subdf = slice_df(st.session_state["df"])

            st.write("Understanding your data...")
            res = fix_quantity_column()
            if res:
                st.error(res)
                return
            res = fix_amount_column()
            if res:
                st.error(res)
                return
            res = date_column_cleaning()
            if res:
                st.error(res)
                return
            res = standarize_product_column()
            if res:
                st.error(res)
                return

            empty_values_dict = find_empty_values(subdf)
            sub_df = fill_empty_values(subdf)

            st.write("Evaluating demand...")
            product_group_df = create_product_group(sub_df)

            elasticity = Elasticity(product_group_df)
            elasticity.calculate_cross_elasticity()
            st.session_state["elasticity"] = elasticity
            st.session_state["unique_items"] = elasticity.unique_product

            # Show errors for products that don't have enough sales to calculate demand changes
            if len(elasticity.errors) > 0:

                elasticity_errors = "\n- ".join(elasticity.errors)
                elasticity_errors = "- " + elasticity_errors

                sac.alert(
                    label="Warning",
                    description=f"Following products were not able to calculate demand changes, main reason is that they don't have enough sales: \n{elasticity_errors}",
                    color="yellow",
                    closable=True,
                    variant="quote-light"
                )

            # If the cross elasticity matrix could be calculated, then forecast demand
            if elasticity.cross_elasticity_matrix is not None:
                st.write("Forecasting demand...")
                forecast = ForecastDemand(sub_df)
                forecast.rolling_average()
                st.session_state["forecast"] = forecast
            else:
                sac.alert(
                    label="Warning",
                    description="Process finished before forecasting demand, because there are no products with enough sales to calculate demand changes",
                    color="yellow",
                    closable=True,
                    variant="quote-light"
                )
                if st.button(
                    "Retry", 
                    on_click=return_step_home,
                    key="retry_button_optimize_inventory",
                    type="primary"
                ):
                    st.session_state["analysis_complete"] = False
                    st.rerun(scope="fragment")

            status.update(label="Data analysis completed!", state="complete", expanded=False)
            st.session_state["analysis_complete"] = True
            st.rerun()

    if st.session_state["analysis_complete"] and st.session_state["forecast"] is not None:
        st.markdown("> Due to the high number of products, the forecast plot is paginated. You can navigate through the products by clicking on the arrows on the bottom right of the plot.")

        with st.spinner("Generating forecast plot..."):

            data = st.session_state["forecast"].forecast_df[st.session_state["forecast"].product_col]
            TOTAL_ITEMS = len(data)
            TOTAL_PAGES = math.ceil(TOTAL_ITEMS / st.session_state["ITEMS_PER_PAGE"])
            st.session_state["TOTAL_PAGES"] = TOTAL_PAGES


            with st.form(key='pagination_form'):
                col1, col2, col3, _ = st.columns([1,1,1,5])
                
                with col1:
                    prev_clicked = st.form_submit_button("Previous", width="stretch")
                
                with col2:
                    st.write(f"Page: {st.session_state.current_page} / {TOTAL_PAGES}")
                
                with col3:
                    next_clicked = st.form_submit_button("Next")
                
                # Manejar clics de paginación
                if prev_clicked and st.session_state.current_page > 1:
                    st.session_state.current_page -= 1
                if next_clicked and st.session_state.current_page < TOTAL_PAGES:
                    st.session_state.current_page += 1

            # Calcular índices
            start_idx = (st.session_state.current_page - 1) * st.session_state["ITEMS_PER_PAGE"]
            end_idx = start_idx + st.session_state["ITEMS_PER_PAGE"]

            fig = forecast_plot(
                st.session_state["forecast"].forecast_df, 
                st.session_state["product_column"], 
                start_idx, end_idx, st.session_state["item_selector"], TOTAL_ITEMS
            )

            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### Forecast data")
            st.dataframe(st.session_state["forecast"].forecast_df)
            