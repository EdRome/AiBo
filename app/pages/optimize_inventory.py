import time
import logging
import streamlit as st
import plotly.graph_objects as go

from src.analytics.modeling.elasticity import Elasticity
from src.analytics.modeling.forecasting import PyMEForecastDemand

from src.analytics.exploratory.slicing import slice_df

from src.transformations.feature_engineering.product_group import create_product_group
from src.transformations.cleaning.date_cleaning import date_column_cleaning
from src.transformations.cleaning.amount_cleaning import fix_amount_column
from src.transformations.cleaning.quantity_cleaning import fix_quantity_column
from src.transformations.cleaning.product_cleaning import standarize_product_column

try:
    st.markdown(
        """
        # Demand forecasting

        What you should expect:

        - After uploading and reviewing your data, the app will analyze your data and forecast your demand.
        - The results will be displayed in 3 different tables to ease the analysis of the results.
            - The first table will show the products with shortage risk. *If no products with shortage risk, this table will not be displayed.*
            - The second table will show the products with surplus risk. *If no products with surplus risk, this table will not be displayed.*
            - The third table will show the complete forecast data.

        ## What you can do:

        - You can download the complete forecast data by hovering over the table and clicking on the download button.
        - You can also see the sales forecast following your current stock demand and pricing.
        - The forecast plot will show the forecast sales for **the next month**.
        """
    )

    if not st.session_state["analysis_complete"]:
        progress_bar = st.progress(5, text="Analyzing data...")
        subdf = slice_df(st.session_state["df"])

        progress_bar.progress(10, text="Understanding your data... **DON'T CLOSE OR REFRESH THIS WINDOW**")

        res = fix_quantity_column()
        if res:
            st.error(res)
        progress_bar.progress(20, text="Understanding your data... **DON'T CLOSE OR REFRESH THIS WINDOW**")
        res = fix_amount_column()
        if res:
            st.error(res)
        progress_bar.progress(30, text="Understanding your data... **DON'T CLOSE OR REFRESH THIS WINDOW**")
        res = date_column_cleaning()
        if res:
            st.error(res)
        progress_bar.progress(40, text="Understanding your data... **DON'T CLOSE OR REFRESH THIS WINDOW**")
        res = standarize_product_column()
        if res:
            st.error(res)

        progress_bar.progress(50, text="Evaluating demand... **DON'T CLOSE OR REFRESH THIS WINDOW**")
        product_group_df = create_product_group(subdf)

        elasticity = Elasticity(product_group_df)

        # COMENTADO POR AHORA, ESTO ES UN TRABAJO EN PROCESO
        # progress_bar.progress(60, text="Evaluating demand... **DON'T CLOSE OR REFRESH THIS WINDOW**")
        # elasticity.calculate_cross_elasticity()
        # st.session_state["elasticity"] = elasticity
        # st.session_state["unique_items"] = elasticity.unique_product

        # # Show errors for products that don't have enough sales to calculate demand changes
        # if len(elasticity.errors) > 0:

        #     elasticity_errors = "\n- ".join(elasticity.errors)
        #     elasticity_errors = "- " + elasticity_errors

        #     sac.alert(
        #         label="Warning",
        #         description=f"Following products were not able to calculate demand changes, main reason is that they don't have enough sales: \n{elasticity_errors}",
        #         color="yellow",
        #         closable=True,
        #         variant="quote-light"
        #     )

        progress_bar.progress(90, text="Forecasting demand... **DON'T CLOSE OR REFRESH THIS WINDOW**")
        forecast = PyMEForecastDemand(subdf)
        forecast.smart_forecast()
        st.session_state["forecast"] = forecast

        progress_bar.progress(100, text="Data analysis completed!")
        st.session_state["analysis_complete"] = True

        time.sleep(0.5)
        progress_bar.empty()

    if st.session_state["analysis_complete"] and st.session_state["forecast"] is not None:

        with st.spinner("Generating forecast plot..."):

            product_shortage = st.session_state["forecast"].forecast_df.query("risk_category.str.contains('SHORTAGE_RISK')")
            product_surplus = st.session_state["forecast"].forecast_df.query("risk_category.str.contains('SURPLUS_RISK')")

            if len(product_shortage) > 0:
                
                st.markdown("""
                ### Products with shortage risk

                Here you can see products with shortage risk, each product will show the current stock, the forecast demand and the recommendation to adjust the risk of shortage.
                """)
                st.dataframe(product_shortage.filter(["current_stock","forecast_demand","recommendation"]))
            
            if len(product_surplus) > 0:
                st.divider()
                st.markdown("""
                ### Products with surplus risk

                Here you can see products with surplus risk, each product will show the current stock, the forecast demand and the recommendation to adjust the risk of surplus.
                """)
                st.dataframe(product_surplus.filter(["current_stock","forecast_demand","recommendation"]))

            st.divider()
            st.markdown("""
            ### Forecast data
            You can find the complete forecast data for the next month in this table, you can download it by hovering over the table and clicking on the download button.
            """)

            st.dataframe(
                st.session_state["forecast"].forecast_df.filter([
                    "current_stock","forecast_demand","growth_trend","risk_category","recommendation"
                ]).rename(columns={
                    "current_stock": "Current Stock",
                    "forecast_demand": "Forecast Demand",
                    "recommendation": "Recommendation",
                    "growth_trend": "Growth Trend",
                    "risk_category": "Risk Category",
                })
            )

            st.divider()
            st.markdown("""
            ### Sales forecast
            """)

            monthly_sales_history = st.session_state["forecast"].get_monthly_sales_history()
            monthly_sales_history = monthly_sales_history[-6:]
            last_month_sales_forecast = st.session_state["forecast"].get_last_month_sales_forecast()
            last_month_sales_forecast = last_month_sales_forecast[-6:]

            less_sold_products, last_month, second_last_month = st.session_state["forecast"].get_less_sold_products_last_month()

            st.markdown("""
            #### Less sold products last month

            The comparision between {second_last_month_sales} and {last_month_sales}. 
            
            > It does not include the forecast.
            """.format(
                last_month_sales=last_month.strftime("%B %Y"),
                second_last_month_sales=second_last_month.strftime("%B %Y")
            ))

            a, b = st.columns(2)
            c, d = st.columns(2)

            less_sold_products_list = [a, b, c, d]
            for product, col in zip(less_sold_products[st.session_state["product_column"]], less_sold_products_list):
                col.metric(
                    product, 
                    value=less_sold_products[less_sold_products[st.session_state["product_column"]] == product]["quantity_last_month"].values[0],
                    delta=less_sold_products[less_sold_products[st.session_state["product_column"]] == product]["delta"].values[0],
                    border=True
                )
            

            most_sold_products, last_month, second_last_month = st.session_state["forecast"].get_most_sold_products_last_month()

            st.markdown("""
            #### Most sold products last month

            The comparision between {second_last_month_sales} and {last_month_sales}. 
            
            > It does not include the forecast.
            """.format(
                last_month_sales=last_month.strftime("%B %Y"),
                second_last_month_sales=second_last_month.strftime("%B %Y")
            ))
            
            a, b = st.columns(2)
            c, d = st.columns(2)

            most_sold_products_list = [a, b, c, d]
            for product, col in zip(most_sold_products[st.session_state["product_column"]], most_sold_products_list):
                col.metric(
                    product, 
                    value=most_sold_products[most_sold_products[st.session_state["product_column"]] == product]["quantity_last_month"].values[0],
                    delta=most_sold_products[most_sold_products[st.session_state["product_column"]] == product]["delta"].values[0],
                    border=True
                )

            st.markdown("""
            #### Half year sales history
            """)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=monthly_sales_history.index, 
                y=monthly_sales_history.values, 
                name="Sales",
                text=monthly_sales_history.values,
                texttemplate='$%{text:,.0f}',
                textposition='outside'
            ))
            fig.add_trace(go.Bar(
                x=last_month_sales_forecast.date, 
                y=last_month_sales_forecast.total_sales, 
                name="Forecast",
                text=last_month_sales_forecast.total_sales,
                texttemplate='$%{text:,.0f}',
                textposition='outside'
            ))
            fig.update_layout(
                xaxis_title="Month", 
                yaxis_title="Sales",
                plot_bgcolor='white',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig)

except Exception as e:
    # st.switch_page("pages/home.py")
    st.error(e)
    logging.exception(e)